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


# ── GET /api/engineers ────────────────────────────────────────────────────────

@app.get("/api/engineers", summary="List engineer telegram IDs [SCAFFOLD]")
def get_engineers():
    """
    SCAFFOLD — returns the list of engineer telegram IDs.
    Engineer ↔ district mapping table is not yet set up.
    Replace this body with a real DB query once the table exists.
    """
    # TODO: SELECT tele_id, name FROM mba_sumbagut.engineer WHERE is_active = true
    return {"engineers": []}


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
