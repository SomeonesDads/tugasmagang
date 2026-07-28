"""
Daily ticket lifecycle pipeline for mba_sumbagut.sri_zp_daily.

Three operations, meant to be called in this order as part of a daily job,
plus one operation triggered ad-hoc whenever an engineer submits an RCA
via the Telegram bot:

    1. create_daily_tickets(conn)        -- run once, after sri_zp_daily is loaded for the day
    2. submit_rca(conn, ticket_id, ...)   -- run whenever an engineer replies with RCA/RCA_DETAIL
    3. check_service_completion(conn)     -- run once, after sri_zp_daily is loaded for the day
                                             (after create_daily_tickets, since it reads the same feed)

Assumes psycopg2 and a connection to the mba_sumbagut schema. All functions
take an open connection and manage their own transaction (commit on success,
rollback on exception) so they can be called independently or wired into a
scheduler (cron, Airflow, etc.) without the caller needing to know the
internals of each step.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional

import psycopg2
import psycopg2.extras

logger = logging.getLogger("ticket_pipeline")


# ---------------------------------------------------------------------------
# Data shapes returned to callers (e.g. the bot layer that pushes to Telegram)
# ---------------------------------------------------------------------------

@dataclass
class NewTicket:
    ticket_id: int
    enodeb_id: int
    cell_id: int
    site_id: str
    district_id: Optional[int]
    engineer_telegram_ids: list[int]


@dataclass
class ClosedTicket:
    ticket_id: int
    enodeb_id: int
    cell_id: int
    site_id: str
    start_day: date
    end_day: date


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@contextmanager
def _transaction(conn):
    """Wrap a block in commit/rollback so each public function is atomic."""
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def _get_engineers_for_site(cur, site_id: str) -> tuple[Optional[int], list[int]]:
    """
    Resolve a site to its district, then to the telegram_id of every active
    engineer assigned to that district (0, 1, or 2 of them).

    Returns (district_id, [telegram_id, ...]). district_id is None if the
    site has no mapping yet -- this should be logged and handled by the
    caller (e.g. flagged for manual district assignment), not silently
    dropped.
    """
    cur.execute(
        """
        SELECT district_id
        FROM site_district_map
        WHERE site_id = %s
        """,
        (site_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None, []

    district_id = row["district_id"]

    cur.execute(
        """
        SELECT fe.telegram_id
        FROM district_engineer de
        JOIN field_engineer fe ON fe.id = de.engineer_id
        WHERE de.district_id = %s
          AND fe.is_active = TRUE
        """,
        (district_id,),
    )
    telegram_ids = [r["telegram_id"] for r in cur.fetchall()]
    return district_id, telegram_ids


# ---------------------------------------------------------------------------
# 1. Ticket creation
# ---------------------------------------------------------------------------

def create_daily_tickets(conn, run_date: Optional[date] = None) -> list[NewTicket]:
    """
    For every distinct (enodeb_id, cell_id, site_id) fed into sri_zp_daily
    for run_date (defaults to today), create a new ticket unless one is
    already open for that same triple.

    "Already tracked" means an existing ticket row with status != 'CLOSED'
    for that (enodeb_id, cell_id, site_id) -- not literally "an entry
    yesterday" -- so a problem that keeps appearing in the feed day after
    day does not spawn a new ticket each time.

    Returns the list of newly created tickets, each with the engineers who
    should be notified, so the caller can push Telegram messages without
    re-querying.
    """
    run_date = run_date or date.today()
    created: list[NewTicket] = []

    with _transaction(conn):
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            """
            SELECT DISTINCT enodeb_id, cell_id, site_id
            FROM mba_sumbagut.sri_zp_daily
            WHERE date = %s
              AND enodeb_id IS NOT NULL
              AND cell_id IS NOT NULL
              AND site_id IS NOT NULL
            """,
            (run_date,),
        )
        todays_triples = cur.fetchall()

        for row in todays_triples:
            enodeb_id, cell_id, site_id = row["enodeb_id"], row["cell_id"], row["site_id"]

            cur.execute(
                """
                SELECT id
                FROM ticket
                WHERE enodeb_id = %s AND cell_id = %s AND site_id = %s
                  AND status <> 'CLOSED'
                """,
                (enodeb_id, cell_id, site_id),
            )
            if cur.fetchone() is not None:
                # Already being tracked, nothing to do.
                continue

            district_id, telegram_ids = _get_engineers_for_site(cur, site_id)
            if district_id is None:
                logger.warning(
                    "site_id=%s has no district mapping; ticket created but "
                    "no engineer will be notified until site_district_map is updated",
                    site_id,
                )

            cur.execute(
                """
                INSERT INTO ticket (enodeb_id, cell_id, site_id, district_id, status, created_day)
                VALUES (%s, %s, %s, %s, 'RCA', %s)
                RETURNING id
                """,
                (enodeb_id, cell_id, site_id, district_id, run_date),
            )
            ticket_id = cur.fetchone()["id"]

            cur.execute(
                """
                INSERT INTO ticket_rca (ticket_id, start_day)
                VALUES (%s, %s)
                """,
                (ticket_id, run_date),
            )

            created.append(
                NewTicket(
                    ticket_id=ticket_id,
                    enodeb_id=enodeb_id,
                    cell_id=cell_id,
                    site_id=site_id,
                    district_id=district_id,
                    engineer_telegram_ids=telegram_ids,
                )
            )

        cur.close()

    logger.info("create_daily_tickets: created %d ticket(s) for %s", len(created), run_date)
    return created


# ---------------------------------------------------------------------------
# 2. RCA input (triggered by the bot when an engineer replies)
# ---------------------------------------------------------------------------

def submit_rca(conn, ticket_id: int, rca: str, rca_detail: str, submitted_day: Optional[date] = None) -> None:
    """
    Record an engineer's RCA input for a ticket, close out ticket_rca,
    flip the ticket to SERVICE, and open the matching ticket_service row.

    Raises ValueError if the ticket doesn't exist or isn't currently in
    RCA status (e.g. already serviced, or closed) -- this should surface
    as a "this ticket can't accept RCA right now" message back to the bot
    rather than silently corrupting state.
    """
    submitted_day = submitted_day or date.today()

    with _transaction(conn):
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("SELECT status FROM ticket WHERE id = %s FOR UPDATE", (ticket_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"ticket {ticket_id} does not exist")
        if row["status"] != "RCA":
            raise ValueError(f"ticket {ticket_id} is not awaiting RCA (status={row['status']})")

        cur.execute(
            """
            UPDATE ticket_rca
            SET end_day = %s, rca = %s, rca_detail = %s
            WHERE ticket_id = %s
            """,
            (submitted_day, rca, rca_detail, ticket_id),
        )

        cur.execute(
            "UPDATE ticket SET status = 'SERVICE' WHERE id = %s",
            (ticket_id,),
        )

        cur.execute(
            """
            INSERT INTO ticket_service (ticket_id, start_day)
            VALUES (%s, %s)
            """,
            (ticket_id, submitted_day),
        )

        cur.close()

    logger.info("submit_rca: ticket %d moved RCA -> SERVICE on %s", ticket_id, submitted_day)


# ---------------------------------------------------------------------------
# 3. Service completion check
# ---------------------------------------------------------------------------

def check_service_completion(conn, run_date: Optional[date] = None) -> list[ClosedTicket]:
    """
    For every ticket currently in SERVICE, check whether today's
    sri_zp_daily feed still contains its (enodeb_id, cell_id, site_id).

    - If it still appears: the problem persists, leave the ticket open.
    - If it no longer appears: the problem cleared. Close out
      ticket_service.end_day and mark the ticket CLOSED.

    Because start_day is set the same day the RCA is submitted, and this
    check can only run again on a later day's feed, end_day - start_day
    is guaranteed to be >= 1.

    Returns the list of tickets closed in this run.
    """
    run_date = run_date or date.today()
    closed: list[ClosedTicket] = []

    with _transaction(conn):
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            """
            SELECT t.id AS ticket_id, t.enodeb_id, t.cell_id, t.site_id, ts.start_day
            FROM ticket t
            JOIN ticket_service ts ON ts.ticket_id = t.id
            WHERE t.status = 'SERVICE'
            """
        )
        open_service_tickets = cur.fetchall()

        for row in open_service_tickets:
            cur.execute(
                """
                SELECT 1
                FROM mba_sumbagut.sri_zp_daily
                WHERE date = %s AND enodeb_id = %s AND cell_id = %s AND site_id = %s
                LIMIT 1
                """,
                (run_date, row["enodeb_id"], row["cell_id"], row["site_id"]),
            )
            still_present = cur.fetchone() is not None
            if still_present:
                continue

            cur.execute(
                """
                UPDATE ticket_service
                SET end_day = %s
                WHERE ticket_id = %s
                """,
                (run_date, row["ticket_id"]),
            )
            cur.execute(
                """
                UPDATE ticket
                SET status = 'CLOSED', closed_day = %s
                WHERE id = %s
                """,
                (run_date, row["ticket_id"]),
            )

            closed.append(
                ClosedTicket(
                    ticket_id=row["ticket_id"],
                    enodeb_id=row["enodeb_id"],
                    cell_id=row["cell_id"],
                    site_id=row["site_id"],
                    start_day=row["start_day"],
                    end_day=run_date,
                )
            )

        cur.close()

    logger.info("check_service_completion: closed %d ticket(s) for %s", len(closed), run_date)
    return closed


# ---------------------------------------------------------------------------
# Orchestration entry point for the daily scheduler
# ---------------------------------------------------------------------------

def run_daily_job(conn, run_date: Optional[date] = None) -> dict:
    """
    Convenience wrapper for a scheduler (cron/Airflow) to call once a day,
    after sri_zp_daily has finished loading. Order matters:
    completion-checking first (against yesterday's open SERVICE tickets),
    then creation for today's feed -- reversing this would let a ticket
    that's cleared and recreated on the same day look like it was never
    closed. Adjust if your feed-load timing differs.
    """
    run_date = run_date or date.today()

    closed = check_service_completion(conn, run_date)
    created = create_daily_tickets(conn, run_date)

    return {
        "run_date": run_date,
        "tickets_closed": closed,
        "tickets_created": created,
    }


if __name__ == "__main__":
    import os

    logging.basicConfig(level=logging.INFO)

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        dbname=os.environ.get("PGDATABASE", "postgres"),
        user=os.environ.get("PGUSER", "robyput"),
        password=os.environ.get("PGPASSWORD", ""),
        options="-c search_path=mba_sumbagut,public",
    )
    try:
        result = run_daily_job(conn)
        print(f"Closed: {len(result['tickets_closed'])}, Created: {len(result['tickets_created'])}")
    finally:
        conn.close()