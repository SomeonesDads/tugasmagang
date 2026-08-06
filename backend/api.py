"""
api.py
FastAPI REST API for the SRI ZP/ZT ticket system.

Run with:
    uvicorn api:app --reload           (dev)
    uvicorn api:app --host 0.0.0.0     (prod)

The FastAPI lifespan starts an APScheduler job that fires daily_pipeline()
every day at PIPELINE_HOUR:PIPELINE_MINUTE (from .env, default 02:00).
No separate scheduler process is needed.

Endpoints
─────────
  GET  /api/engineers              — SCAFFOLD: placeholder until engineer table
                                     is set up by your team. Returns empty list.
  GET  /api/tickets/{district_id}  — All tickets for a district.
                                     `district_id` = district_operation_do string.
                                     Once engineers ↔ districts are mapped, swap
                                     the path param for tele_id and resolve here.
  PATCH /api/tickets/{ticket_id}   — Submit RCA + RCA detail for a ticket.
                                     Also inserts the ticket_service row.
"""

import logging
from contextlib import asynccontextmanager
from datetime import date
from enum import Enum
from typing import Optional

import psycopg2
import psycopg2.extras
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import dotenv_values
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from dailypipeline import daily_pipeline

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
)


# ── Scheduler lifespan ────────────────────────────────────────────────────────

def _run_pipeline_safe() -> None:
    """Wrapper so a pipeline exception never crashes the scheduler thread."""
    try:
        daily_pipeline()
    except Exception:
        log.exception("[SCHEDULER] Pipeline run failed — will retry on next scheduled run")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the daily scheduler when uvicorn starts; stop it on shutdown."""
    cfg    = dotenv_values(".env")
    hour   = int(cfg.get("PIPELINE_HOUR",   2))
    minute = int(cfg.get("PIPELINE_MINUTE", 0))

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _run_pipeline_safe,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="daily_pipeline",
        name="Daily ticket pipeline",
        misfire_grace_time=3600,  # run even if missed by up to 1 h
        coalesce=True,            # only one run if multiple were missed
    )
    scheduler.start()
    log.info(f"[SCHEDULER] Daily pipeline scheduled at {hour:02d}:{minute:02d} every day")

    yield   # API runs here

    scheduler.shutdown(wait=False)
    log.info("[SCHEDULER] Scheduler stopped")


app = FastAPI(title="SRI Ticket API", version="0.1.0", lifespan=lifespan)


# ── DB connection ─────────────────────────────────────────────────────────────

def get_db():
    cfg = dotenv_values(".env")
    conn = psycopg2.connect(
        host=cfg.get("host", "localhost"),
        port=int(cfg.get("port", 5432)),
        dbname=cfg.get("dbname", "postgres"),
        user=cfg.get("user", "postgres"),
        password=cfg.get("password", ""),
    )
    try:
        yield conn
    finally:
        conn.close()


# ── RCA enum (matches CHECK constraint in ticket_rca) ─────────────────────────

class RCACategory(str, Enum):
    software    = "Software Problem"
    activity    = "Activity Project"
    hardware    = "Hardware Problem"
    power       = "Power Problem"
    transmition = "Transmition Problem"
    stolen      = "Stolen"
    force_majure = "Force Majure"
    comcase     = "Comcase"
    sleeping_cell = "Sleeping Cell"
    no_traffic  = "No Traffic/User"
    dismantled  = "Dismantled"


# The bot reads this endpoint so its choices always match the database CHECK
# constraints.  Keep it next to RCACategory whenever the official RCA list is
# revised.
RCA_OPTIONS = {
    "Software Problem": ["Configuration Problem", "Database"],
    "Activity Project": ["Cell Locked", "Activity Event", "Activity Upgrade", "Activity Downgrade", "Activity Blacksite"],
    "Hardware Problem": ["DAS Problem", "Hardware Hang, No Alarm", "Baseband Problem", "UMPT/UBBP Problem", "Antenna Problem", "Antenna Port Problem", "Flexible Jumper", "RRU Problem", "SFP Problem", "GPS Problem", "Optic Problem"],
    "Power Problem": ["Rectifier Problem", "Kabel Power Problem", "Genset Problem", "Pemadaman PLN"],
    "Transmition Problem": ["NPU Problem", "MMU Problem", "RAU Problem", "Metro-E Problem", "VLAN Problem", "Impact Simpul", "Fading"],
    "Stolen": ["stolen Baseband", "Stolen RRU", "Stolen BBU", "Stolen UBBP", "Stolen UMPT", "Stolen UBBP + UMPT", "Stolen Cable Power"],
    "Force Majure": ["Banjir", "Site Rubuh", "Perangkat Terbakar"],
    "Comcase": ["Comcase"],
    "Sleeping Cell": ["Sleeping Cell"],
    "No Traffic/User": ["No Traffic/User"],
    "Dismantled": ["Dismantled"],
}

MOCK_ENGINEER_TICKETS = {
    8887960178: {
        "district": "DISTRICT-8887960178",
        "tickets": [
            {"ticket_id": 10001 + index, "ticket_type": "ZP", "site_id": f"MDN{index + 1:03d}",
             "identifiers": {"enodeb_id": 41001 + index, "cell_id": index + 1},
             "aging": 5 - index, "status": {"rca": False, "serviced": False}}
            for index in range(5)
        ],
    },
    8510386982: {
        "district": "DISTRICT-8510386982",
        "tickets": [
            {"ticket_id": 10006 + index, "ticket_type": "ZT", "site_id": f"BJM{index + 1:03d}",
             "identifiers": {"lac": 52001 + index, "ci": 62001 + index},
             "aging": 5 - index, "status": {"rca": False, "serviced": False}}
            for index in range(5)
        ],
    },
}


# ── Response / Request models ─────────────────────────────────────────────────

class TicketStatus(BaseModel):
    rca: bool       # True once engineer has submitted RCA (ticket_rca.submitted_at IS NOT NULL)
    serviced: bool  # True once problem has cleared from feed (ticket_service.end_day IS NOT NULL)


class Identifiers(BaseModel):
    """
    Exactly one pair will be populated depending on ticket_type.
      ZP → enodeb_id + cell_id
      ZT → lac      + ci
    """
    enodeb_id: Optional[int] = None
    cell_id:   Optional[int] = None
    lac:       Optional[int] = None
    ci:        Optional[int] = None


class TicketOut(BaseModel):
    ticket_id:   int
    ticket_type: str          # "ZP" or "ZT"
    site_id:     str
    identifiers: Identifiers
    aging:       int
    status:      TicketStatus


class TicketsResponse(BaseModel):
    district: str             # district_operation_do — bot uses this as the message header
    tickets:  list[TicketOut]


class RCAPatch(BaseModel):
    rca:        RCACategory   # validated here; DB CHECK constraint is the final guard
    rca_detail: str           # free text; DB CHECK constraint validates allowed values


@app.get("/api/rca-options", summary="RCA categories and valid detail values")
def get_rca_options():
    """Return the valid RCA values for API consumers such as the Telegram bot."""
    return RCA_OPTIONS


# ── GET /api/engineers ────────────────────────────────────────────────────────

@app.get("/api/engineers", summary="List engineer telegram IDs [MOCK]")
def get_engineers():
    """
    Temporary mock data while the engineer table and Telegram ID mapping are
    not available. Replace this body with a DB query once the mapping exists.
    """
    return {"engineers": [8887960178, 8510386982]}


@app.get(
    "/api/mock/engineers/{telegram_id}/tickets",
    response_model=TicketsResponse,
    summary="Five mock tickets assigned to an engineer",
)
def get_mock_engineer_tickets(telegram_id: int):
    """Temporary ticket assignment used to test Telegram notifications."""
    assignment = MOCK_ENGINEER_TICKETS.get(telegram_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail=f"Engineer {telegram_id} not found.")
    return {
        "district": assignment["district"],
        "tickets": assignment["tickets"],
    }


# ── GET /api/tickets/{district_id} ────────────────────────────────────────────

@app.get(
    "/api/tickets/{district_id}",
    response_model=TicketsResponse,
    summary="All tickets for a district",
)
def get_tickets(district_id: str, conn=Depends(get_db)):
    """
    Returns all tickets whose `district_operation_do` matches `district_id`,
    ordered by aging (highest first) then by creation date (newest first).

    Note: `serviced=true` tickets are included for now.
    Once the system is stable, filter them out here.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT
                t.ticket_id,
                t.ticket_type,
                t.site_id,
                t.enodeb_id,
                t.cell_id,
                t.lac,
                t.ci,
                t.aging,
                t.district_operation_do,
                (r.submitted_at IS NOT NULL)  AS rca_done,
                (s.end_day      IS NOT NULL)  AS serviced_done
            FROM mba_sumbagut.ticket t
            LEFT JOIN mba_sumbagut.ticket_rca     r ON r.ticket_id = t.ticket_id
            LEFT JOIN mba_sumbagut.ticket_service  s ON s.ticket_id = t.ticket_id
            WHERE t.district_operation_do = %s
            ORDER BY t.aging DESC, t.created_date DESC
        """, (district_id,))

        rows = cur.fetchall()

    tickets = []
    for row in rows:
        if row["ticket_type"] == "ZP":
            identifiers = Identifiers(
                enodeb_id=row["enodeb_id"],
                cell_id=row["cell_id"],
            )
        else:
            identifiers = Identifiers(
                lac=row["lac"],
                ci=row["ci"],
            )

        tickets.append(TicketOut(
            ticket_id=row["ticket_id"],
            ticket_type=row["ticket_type"],
            site_id=row["site_id"],
            identifiers=identifiers,
            aging=row["aging"],
            status=TicketStatus(
                rca=bool(row["rca_done"]),
                serviced=bool(row["serviced_done"]),
            ),
        ))

    return TicketsResponse(district=district_id, tickets=tickets)


# ── PATCH /api/tickets/{ticket_id} ────────────────────────────────────────────

@app.patch("/api/tickets/{ticket_id}", summary="Submit RCA for a ticket")
def patch_ticket(ticket_id: int, body: RCAPatch, conn=Depends(get_db)):
    """
    Submit RCA + RCA detail for a ticket.

    On success:
    - ticket_rca.rca, rca_detail, submitted_at, end_day are set to today.
    - A ticket_service row is inserted with start_day = today.

    Returns 404 if the ticket doesn't exist.
    Returns 409 if RCA was already submitted for this ticket.
    Returns 422 if rca_detail violates the DB CHECK constraint.
    """
    today = date.today()

    with conn.cursor() as cur:
        # ── Guard: ticket must exist and have no RCA yet ──────────────────────
        cur.execute("""
            SELECT r.submitted_at
            FROM mba_sumbagut.ticket_rca r
            WHERE r.ticket_id = %s
        """, (ticket_id,))
        row = cur.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Ticket {ticket_id} not found.",
            )
        if row[0] is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Ticket {ticket_id} already has an RCA submitted.",
            )

        # ── Update ticket_rca ─────────────────────────────────────────────────
        try:
            cur.execute("""
                UPDATE mba_sumbagut.ticket_rca
                SET rca          = %s,
                    rca_detail   = %s,
                    submitted_at = now(),
                    end_day      = %s,
                    updated_at   = now()
                WHERE ticket_id = %s
            """, (body.rca.value, body.rca_detail, today, ticket_id))

            # ── Insert ticket_service ─────────────────────────────────────────
            # start_day = today = ticket_rca.end_day
            cur.execute("""
                INSERT INTO mba_sumbagut.ticket_service (ticket_id, start_day)
                VALUES (%s, %s)
                ON CONFLICT (ticket_id) DO NOTHING
            """, (ticket_id, today))

            conn.commit()

        except psycopg2.errors.CheckViolation as e:
            conn.rollback()
            raise HTTPException(
                status_code=422,
                detail=f"Invalid rca_detail value: {e.diag.message_detail or str(e)}",
            )
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "ticket_id":  ticket_id,
        "status":     "rca_submitted",
        "end_day":    today,
    }
