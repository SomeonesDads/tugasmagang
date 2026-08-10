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
  GET  /api/engineers              — All engineer Telegram IDs and districts.
  GET  /api/tickets/{telegram_id}  — Tickets for the engineer's assigned district.
  PATCH /api/tickets/{ticket_id}   — Submit RCA + RCA detail for a ticket.
                                     Also inserts the ticket_service row.
"""

import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

import psycopg2
import psycopg2.extras
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from dailypipeline import _tracking_record_rca, daily_pipeline
from settings import settings

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
    if not settings.pipeline_enabled:
        log.info("[SCHEDULER] Disabled for NODE_ENV=%s", settings.node_env)
        yield
        return

    hour = settings.pipeline_hour
    minute = settings.pipeline_minute

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
    conn = psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )
    try:
        yield conn
    finally:
        conn.close()


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
    site_class:  str
 

class TicketGroups(BaseModel):
    need_service: list[TicketOut]
    need_analysis: list[TicketOut]


class TicketsResponse(BaseModel):
    district: str             # district_operation_do — bot uses this as the message header
    tickets: TicketGroups


class RCAPatch(BaseModel):
    rca:        str
    rca_detail: str


def getsiteclass(site_id: str) -> str:
    """Temporary site-class provider until the site reference query is finalized."""
    return "bronze"


def _aging_score(aging: int) -> int:
    if aging < 4:
        return 1
    if aging <= 7:
        return 2
    if aging <= 14:
        return 3
    if aging <= 30:
        return 4
    return 5


def _quantity_cell_score(active_count: int) -> int:
    if active_count < 3:
        return 1
    if active_count <= 6:
        return 3
    return 5


def _site_class_score(site_class: str) -> int:
    scores = {"bronze": 1, "silver": 1, "gold": 2, "platinum": 2, "diamond": 3}
    return scores.get(site_class.strip().lower(), 1)


@app.get("/api/rca-options", summary="RCA categories and valid detail values")
def get_rca_options(conn=Depends(get_db)):
    """Read active RCA categories and details from normalized lookup tables."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.name, d.name
            FROM mba_sumbagut.rca r
            LEFT JOIN mba_sumbagut.rca_detail d
              ON d.rca_id = r.rca_id AND d.active
            WHERE r.active
            ORDER BY r.rca_id, d.rca_detail_id
        """)
        options = {}
        for category, detail in cur.fetchall():
            options.setdefault(category, [])
            if detail is not None:
                options[category].append(detail)
    return options


# ── GET /api/engineers ───────────────────────────────────────────────────────

@app.get("/api/engineers", summary="List all engineers and districts")
def get_engineers(conn=Depends(get_db)):
    """Return all engineer Telegram IDs with their assigned district."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT telegram_id, district_operation_do
            FROM mba_sumbagut.telegram_district_role
            WHERE role = 'engineer'
            ORDER BY district_operation_do, telegram_id
        """)
        return {
            "engineers": [
                {"telegram_id": row[0], "district_id": row[1]}
                for row in cur.fetchall()
            ]
        }


@app.get(
    "/api/mock/engineers/{telegram_id}/tickets",
    response_model=None,
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


# ── GET /api/tickets/{telegram_id} ───────────────────────────────────────────

@app.get(
    "/api/tickets/{telegram_id}",
    response_model=TicketsResponse,
    summary="All tickets for an engineer's district",
)
def get_tickets(telegram_id: int, conn=Depends(get_db)):
    """
    Resolve the engineer's district from the standalone Telegram assignment,
    then return all tickets in that district ordered by aging and creation date.

    Note: `serviced=true` tickets are included for now.
    Once the system is stable, filter them out here.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT district_operation_do
            FROM mba_sumbagut.telegram_district_role
            WHERE telegram_id = %s AND role = 'engineer'
        """, (telegram_id,))
        assignments = cur.fetchall()
        if not assignments:
            raise HTTPException(
                status_code=404,
                detail=f"Engineer Telegram ID {telegram_id} is not assigned to a district.",
            )
        districts = {row["district_operation_do"] for row in assignments}
        if len(districts) > 1:
            raise HTTPException(
                status_code=409,
                detail=f"Engineer Telegram ID {telegram_id} has multiple district assignments.",
            )
        district_id = districts.pop()

        cur.execute("""
            WITH ticket_state AS (
                SELECT t.ticket_id, t.ticket_type, t.site_id,
                       t.enodeb_id, t.cell_id, t.lac, t.ci, t.aging,
                       (r.submitted_at IS NOT NULL) AS rca_done,
                       (s.end_day IS NOT NULL) AS serviced_done,
                       COUNT(*) FILTER (
                           WHERE r.end_day IS NULL OR s.end_day IS NULL
                       ) OVER (PARTITION BY t.site_id) AS active_site_tickets
                FROM mba_sumbagut.ticket t
                LEFT JOIN mba_sumbagut.ticket_rca r ON r.ticket_id = t.ticket_id
                LEFT JOIN mba_sumbagut.ticket_service s ON s.ticket_id = t.ticket_id
                WHERE t.district_operation_do = %s
            )
            SELECT * FROM ticket_state
            WHERE NOT (rca_done AND serviced_done)
        """, (district_id,))

        rows = cur.fetchall()

    need_service = []
    need_analysis = []
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

        ticket = TicketOut(
            ticket_id=row["ticket_id"],
            ticket_type=row["ticket_type"],
            site_id=row["site_id"],
            identifiers=identifiers,
            aging=row["aging"],
            status=TicketStatus(
                rca=bool(row["rca_done"]),
                serviced=bool(row["serviced_done"]),
            ),
            site_class=getsiteclass(row["site_id"]),
        )
        priority = (
            0.4 * _aging_score(ticket.aging)
            + 0.4 * _quantity_cell_score(row["active_site_tickets"])
            + 0.2 * _site_class_score(getsiteclass(ticket.site_id))
        )
        if row["rca_done"] and not row["serviced_done"]:
            need_service.append((priority, ticket))
        elif not row["rca_done"]:
            need_analysis.append((priority, ticket))

    def priority_order(item):
        priority, ticket = item
        return (-priority, -ticket.aging, ticket.ticket_id)

    need_service.sort(key=priority_order)
    need_analysis.sort(key=priority_order)
    return TicketsResponse(
        district=district_id,
        tickets=TicketGroups(
            need_service=[ticket for _, ticket in need_service],
            need_analysis=[ticket for _, ticket in need_analysis],
        ),
    )


# ── PATCH /api/tickets/{ticket_id} ────────────────────────────────────────────

@app.patch("/api/tickets/{ticket_id}", summary="Submit RCA for a ticket")
def patch_ticket(ticket_id: int, body: RCAPatch, conn=Depends(get_db)):
    """
    Submit RCA + RCA detail for a ticket.

    On success:
    - ticket_rca.rca, rca_detail, submitted_at, end_day are set to today.
    - RCA fields are updated; service tracking is maintained independently by
      the pipeline and may already be solved.

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

        cur.execute("""
            SELECT r.rca_id, d.rca_detail_id
            FROM mba_sumbagut.rca r
            JOIN mba_sumbagut.rca_detail d ON d.rca_id = r.rca_id
            WHERE r.active AND d.active AND r.name = %s AND d.name = %s
        """, (body.rca, body.rca_detail))
        lookup = cur.fetchone()
        if lookup is None:
            raise HTTPException(status_code=422, detail="Invalid RCA or RCA detail.")
        rca_id, rca_detail_id = lookup

        # ── Update ticket_rca ─────────────────────────────────────────────────
        try:
            cur.execute("""
                UPDATE mba_sumbagut.ticket_rca
                SET rca_id       = %s,
                    rca_detail_id = %s,
                    submitted_at = now(),
                    end_day      = %s,
                    updated_at   = now()
                WHERE ticket_id = %s
            """, (rca_id, rca_detail_id, today, ticket_id))

            # ── Insert ticket_service ─────────────────────────────────────────
            _tracking_record_rca(cur, ticket_id)
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
