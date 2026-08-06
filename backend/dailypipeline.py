"""
dailypipeline.py
Ticket generation pipeline for SRI ZP / ZT anomalies.

Two entry points
────────────────
  seed_pipeline()   — Run ONCE to bootstrap from historical feed data.
                      Scans the most recent feed date, finds all cells with no
                      open ticket, and computes accurate historical aging by
                      walking back consecutive dates in the feed tables.

  daily_pipeline()  — Run every day after seeding.
                      Any cell that's still a problem already has an open ticket
                      from the seed (or a previous daily run) — the ticket table
                      is the source of truth for dedup.  New cells reaching this
                      point are genuinely new problems, so aging starts at 1.
                      Also closes service tickets whose cell has cleared.

Deduplication (both modes)
──────────────────────────
  We check the ticket table for an active open ticket, not the feed table.
  "Active" = ticket exists AND (no ticket_service row yet OR end_day IS NULL).

  Scenarios:
    • No open ticket → create.
    • Open ticket exists → skip (ongoing problem).
    • Ticket exists but service is closed → create new (problem recurred).

Usage
─────
  python dailypipeline.py           → daily mode (default)
  python dailypipeline.py --seed    → seed mode (run once on first deploy)
"""

import logging
import sys
from datetime import date, timedelta

import psycopg2
from dotenv import dotenv_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
)
log = logging.getLogger(__name__)


#  Database connection 

def get_connection() -> psycopg2.extensions.connection:
    cfg = dotenv_values(".env")
    return psycopg2.connect(
        host=cfg.get("host", "localhost"),
        port=int(cfg.get("port", 5432)),
        dbname=cfg.get("dbname", "postgres"),
        user=cfg.get("user", "postgres"),
        password=cfg.get("password", ""),
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_feed_date(cur, table: str) -> date | None:
    """Return the most recent date present in a feed table."""
    cur.execute(f'SELECT MAX("date") FROM mba_sumbagut.{table}')
    row = cur.fetchone()
    return row[0] if row else None


def resolve_district(cur, site_id: str) -> str | None:
    """
    Resolve district_operation_do for a site_id from the most recent
    pipeline_run snapshot in site_reference.
    """
    cur.execute("""
        SELECT sr.district_operation_do
        FROM mba_sumbagut.site_reference sr
        JOIN mba_sumbagut.pipeline_runs pr
          ON pr.pipeline_run_id = sr.pipeline_run_id
        WHERE sr.site_id = %s
        ORDER BY pr.started_at DESC
        LIMIT 1
    """, (site_id,))
    row = cur.fetchone()
    return row[0] if row else None


def compute_aging(cur, table: str, filters: dict, today: date) -> int:
    """
    Count how many *consecutive* days ending on `today` the given cell
    appears in `table`.  Returns at least 1.

    Used only by seed_pipeline().  The daily pipeline doesn't need this
    because any cell that has been recurring already has an open ticket —
    only genuinely new cells reach the insert step, so aging = 1 there.

    `filters` is a dict of {column_name: value} used as WHERE conditions.
    Example for ZP:  {'enodeb_id': 100, 'cell_id': 5, 'site_id': 'ABCD'}
    Example for ZT:  {'lac': 300, 'ci': 7, 'site_id': 'ABCD'}

    No row limit — the streak is naturally bounded by what's in the table.
    An arbitrary cap would silently undercount long-running problems.
    """
    where_clause = " AND ".join(f'"{col}" = %s' for col in filters)
    where_vals   = list(filters.values())

    cur.execute(f"""
        SELECT DISTINCT "date"
        FROM mba_sumbagut.{table}
        WHERE {where_clause}
          AND "date" <= %s
        ORDER BY "date" DESC
    """, (*where_vals, today))

    dates = [row[0] for row in cur.fetchall()]

    if not dates or dates[0] != today:
        # Shouldn't happen during normal seed flow, but guard anyway.
        return 1

    count = 1
    for i in range(1, len(dates)):
        if (dates[i - 1] - dates[i]).days == 1:
            count += 1
        else:
            break   # gap found — consecutive streak ends here

    return count


# ── Shared: ticket + ticket_rca insert ────────────────────────────────────────

def _insert_ticket_and_rca(cur, ticket_params: tuple, start_day: date) -> int | None:
    """
    Insert one ticket row and its corresponding ticket_rca skeleton.
    Returns the new ticket_id, or None if a conflict occurred (already exists).
    """
    cur.execute("""
        INSERT INTO mba_sumbagut.ticket
            (ticket_type, enodeb_id, cell_id, lac, ci,
             site_id, district_operation_do, created_date, aging)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING ticket_id
    """, ticket_params)

    result = cur.fetchone()
    if result is None:
        return None  # partial-unique index prevented duplicate

    ticket_id = result[0]

    cur.execute("""
        INSERT INTO mba_sumbagut.ticket_rca (ticket_id, start_day)
        VALUES (%s, %s)
    """, (ticket_id, start_day))

    return ticket_id


# ── Shared: dedup query — cells in today's feed with NO active open ticket ────

_ZP_NEW_CELLS_SQL = """
    SELECT DISTINCT zp.enodeb_id, zp.cell_id, zp.site_id
    FROM mba_sumbagut.sri_zp_daily zp
    WHERE zp."date" = %s
      AND zp.enodeb_id IS NOT NULL
      AND zp.cell_id   IS NOT NULL
      AND NOT EXISTS (
          SELECT 1
          FROM mba_sumbagut.ticket t
          LEFT JOIN mba_sumbagut.ticket_service ts ON ts.ticket_id = t.ticket_id
          WHERE t.ticket_type = 'ZP'
            AND t.enodeb_id   = zp.enodeb_id
            AND t.cell_id     = zp.cell_id
            AND t.site_id     = zp.site_id
            AND (ts.ticket_id IS NULL OR ts.end_day IS NULL)
      )
"""

_ZT_NEW_CELLS_SQL = """
    SELECT DISTINCT zt.lac, zt.ci, zt.site_id
    FROM mba_sumbagut.sri_zt_daily zt
    WHERE zt."date" = %s
      AND zt.lac    IS NOT NULL
      AND zt.ci     IS NOT NULL
      AND NOT EXISTS (
          SELECT 1
          FROM mba_sumbagut.ticket t
          LEFT JOIN mba_sumbagut.ticket_service ts ON ts.ticket_id = t.ticket_id
          WHERE t.ticket_type = 'ZT'
            AND t.lac         = zt.lac
            AND t.ci          = zt.ci
            AND t.site_id     = zt.site_id
            AND (ts.ticket_id IS NULL OR ts.end_day IS NULL)
      )
"""


# ══════════════════════════════════════════════════════════════════════════════
# SEED PIPELINE
# Run once on first deploy (or to re-bootstrap after a gap).
# Finds all cells in the most recent feed date that have no open ticket and
# computes accurate historical aging by walking back consecutive dates.
# ══════════════════════════════════════════════════════════════════════════════

def _seed_zp_pass(cur, today: date) -> tuple[int, int]:
    """
    Seed pass for ZP: create tickets for all cells in today's feed
    that have no active open ticket, with aging computed from feed history.
    """
    log.info(f"[SEED/ZP] Pass  today={today}")
    cur.execute(_ZP_NEW_CELLS_SQL, (today,))
    rows = cur.fetchall()
    created = skipped = 0

    for enodeb_id, cell_id, site_id in rows:
        try:
            district = resolve_district(cur, site_id)
            aging = compute_aging(
                cur, "sri_zp_daily",
                {"enodeb_id": enodeb_id, "cell_id": cell_id, "site_id": site_id},
                today,
            )
            params = ("ZP", enodeb_id, cell_id, None, None,
                      site_id, district, today, aging)
            tid = _insert_ticket_and_rca(cur, params, today)
            if tid:
                created += 1
                log.debug(f"  [SEED/ZP] #{tid}  enodeb={enodeb_id}  cell={cell_id}  "
                          f"site={site_id}  aging={aging}")
            else:
                skipped += 1
        except Exception:
            log.exception(f"  [SEED/ZP] Failed  enodeb={enodeb_id}  cell={cell_id}  site={site_id}")
            raise

    log.info(f"[SEED/ZP] Done  created={created}  skipped={skipped}")
    return created, skipped


def _seed_zt_pass(cur, today: date) -> tuple[int, int]:
    """
    Seed pass for ZT: same logic using lac/ci and sri_zt_daily history.
    """
    log.info(f"[SEED/ZT] Pass  today={today}")
    cur.execute(_ZT_NEW_CELLS_SQL, (today,))
    rows = cur.fetchall()
    created = skipped = 0

    for lac, ci, site_id in rows:
        try:
            district = resolve_district(cur, site_id)
            aging = compute_aging(
                cur, "sri_zt_daily",
                {"lac": lac, "ci": ci, "site_id": site_id},
                today,
            )
            params = ("ZT", None, None, lac, ci,
                      site_id, district, today, aging)
            tid = _insert_ticket_and_rca(cur, params, today)
            if tid:
                created += 1
                log.debug(f"  [SEED/ZT] #{tid}  lac={lac}  ci={ci}  site={site_id}  aging={aging}")
            else:
                skipped += 1
        except Exception:
            log.exception(f"  [SEED/ZT] Failed  lac={lac}  ci={ci}  site={site_id}")
            raise

    log.info(f"[SEED/ZT] Done  created={created}  skipped={skipped}")
    return created, skipped


def seed_pipeline() -> None:
    """
    Bootstrap the ticket table from historical feed data.
    Safe to re-run — the unique indexes on ticket prevent duplicates.
    """
    log.info("=" * 60)
    log.info("SEED pipeline starting")
    log.info("=" * 60)

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                zp_date = get_feed_date(cur, "sri_zp_daily")
                zt_date = get_feed_date(cur, "sri_zt_daily")

                if zp_date is None and zt_date is None:
                    log.warning("No data in either feed table. Nothing to seed.")
                    return

                today = max(d for d in [zp_date, zt_date] if d is not None)
                log.info(f"Seeding from feed date: {today}")

                zp_created = zp_skipped = 0
                zt_created = zt_skipped = 0

                if zp_date == today:
                    zp_created, zp_skipped = _seed_zp_pass(cur, today)
                else:
                    log.warning(f"[SEED/ZP] Feed date {zp_date} ≠ {today} — skipping")

                if zt_date == today:
                    zt_created, zt_skipped = _seed_zt_pass(cur, today)
                else:
                    log.warning(f"[SEED/ZT] Feed date {zt_date} ≠ {today} — skipping")

                refresh_tracking(cur)

        log.info("=" * 60)
        log.info(
            f"SEED complete\n"
            f"  ZP : {zp_created:>4} created  {zp_skipped:>4} skipped\n"
            f"  ZT : {zt_created:>4} created  {zt_skipped:>4} skipped"
        )
        log.info("=" * 60)

    except Exception:
        log.exception("SEED failed — transaction rolled back")
        raise
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# DAILY PIPELINE
# Run every day after seeding.
# Any cell that's been recurring already has an open ticket — it gets skipped
# by the dedup check.  Only genuinely new cells reach the insert step, so
# aging is always 1 here (no feed-table history lookup needed).
# ══════════════════════════════════════════════════════════════════════════════

def _daily_zp_pass(cur, today: date) -> tuple[int, int]:
    """
    Daily ZP pass: create tickets (aging=1) for cells that are new today
    and have no active open ticket.
    """
    log.info(f"[DAILY/ZP] Pass  today={today}")
    cur.execute(_ZP_NEW_CELLS_SQL, (today,))
    rows = cur.fetchall()
    created = skipped = 0

    for enodeb_id, cell_id, site_id in rows:
        try:
            district = resolve_district(cur, site_id)
            # aging = 1: this cell has no open ticket, meaning it's a genuinely
            # new problem.  If it had been recurring, the seed or a previous
            # daily run would already have an open ticket for it.
            params = ("ZP", enodeb_id, cell_id, None, None,
                      site_id, district, today, 1)
            tid = _insert_ticket_and_rca(cur, params, today)
            if tid:
                created += 1
                log.debug(f"  [DAILY/ZP] #{tid}  enodeb={enodeb_id}  cell={cell_id}  site={site_id}")
            else:
                skipped += 1
        except Exception:
            log.exception(f"  [DAILY/ZP] Failed  enodeb={enodeb_id}  cell={cell_id}  site={site_id}")
            raise

    log.info(f"[DAILY/ZP] Done  created={created}  skipped={skipped}")
    return created, skipped


def _daily_zt_pass(cur, today: date) -> tuple[int, int]:
    """
    Daily ZT pass: same logic using lac/ci.
    """
    log.info(f"[DAILY/ZT] Pass  today={today}")
    cur.execute(_ZT_NEW_CELLS_SQL, (today,))
    rows = cur.fetchall()
    created = skipped = 0

    for lac, ci, site_id in rows:
        try:
            district = resolve_district(cur, site_id)
            params = ("ZT", None, None, lac, ci,
                      site_id, district, today, 1)
            tid = _insert_ticket_and_rca(cur, params, today)
            if tid:
                created += 1
                log.debug(f"  [DAILY/ZT] #{tid}  lac={lac}  ci={ci}  site={site_id}")
            else:
                skipped += 1
        except Exception:
            log.exception(f"  [DAILY/ZT] Failed  lac={lac}  ci={ci}  site={site_id}")
            raise

    log.info(f"[DAILY/ZT] Done  created={created}  skipped={skipped}")
    return created, skipped


def _run_close_pass(cur, today: date) -> int:
    """
    Close ticket_service rows where the problematic cell no longer appears
    in today's feed.  Minimum service duration = 1 day (feed is daily).
    Returns count of tickets closed.
    """
    log.info("[CLOSE] Service ticket close pass")
    closed = 0

    # ── Close ZP service tickets ─────────────────────────────────────────────
    cur.execute("""
        SELECT ts.ticket_id, t.enodeb_id, t.cell_id, t.site_id
        FROM mba_sumbagut.ticket_service ts
        JOIN mba_sumbagut.ticket t ON t.ticket_id = ts.ticket_id
        WHERE ts.end_day   IS NULL
          AND t.ticket_type = 'ZP'
    """)
    for ticket_id, enodeb_id, cell_id, site_id in cur.fetchall():
        cur.execute("""
            SELECT 1 FROM mba_sumbagut.sri_zp_daily
            WHERE "date"    = %s
              AND enodeb_id = %s
              AND cell_id   = %s
              AND site_id   = %s
            LIMIT 1
        """, (today, enodeb_id, cell_id, site_id))
        if cur.fetchone() is None:
            cur.execute("""
                UPDATE mba_sumbagut.ticket_service
                SET end_day = %s, updated_at = now()
                WHERE ticket_id = %s
            """, (today, ticket_id))
            closed += 1
            log.debug(f"  [CLOSE/ZP] #{ticket_id} closed")

    # ── Close ZT service tickets ─────────────────────────────────────────────
    cur.execute("""
        SELECT ts.ticket_id, t.lac, t.ci, t.site_id
        FROM mba_sumbagut.ticket_service ts
        JOIN mba_sumbagut.ticket t ON t.ticket_id = ts.ticket_id
        WHERE ts.end_day   IS NULL
          AND t.ticket_type = 'ZT'
    """)
    for ticket_id, lac, ci, site_id in cur.fetchall():
        cur.execute("""
            SELECT 1 FROM mba_sumbagut.sri_zt_daily
            WHERE "date"  = %s
              AND lac      = %s
              AND ci       = %s
              AND site_id  = %s
            LIMIT 1
        """, (today, lac, ci, site_id))
        if cur.fetchone() is None:
            cur.execute("""
                UPDATE mba_sumbagut.ticket_service
                SET end_day = %s, updated_at = now()
                WHERE ticket_id = %s
            """, (today, ticket_id))
            closed += 1
            log.debug(f"  [CLOSE/ZT] #{ticket_id} closed")

    log.info(f"[CLOSE] Done  closed={closed}")
    return closed


def daily_pipeline() -> None:
    """
    Standard daily pipeline. Run after seed_pipeline() has been executed once.
    """
    log.info("=" * 60)
    log.info("DAILY pipeline starting")
    log.info("=" * 60)

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                zp_date = get_feed_date(cur, "sri_zp_daily")
                zt_date = get_feed_date(cur, "sri_zt_daily")

                if zp_date is None and zt_date is None:
                    log.warning("No data in either feed table. Nothing to do.")
                    return

                today = max(d for d in [zp_date, zt_date] if d is not None)
                log.info(f"Feed date: {today}")

                zp_created = zp_skipped = 0
                zt_created = zt_skipped = 0

                if zp_date == today:
                    zp_created, zp_skipped = _daily_zp_pass(cur, today)
                else:
                    log.warning(f"[DAILY/ZP] Feed date {zp_date} ≠ {today} — skipping")

                if zt_date == today:
                    zt_created, zt_skipped = _daily_zt_pass(cur, today)
                else:
                    log.warning(f"[DAILY/ZT] Feed date {zt_date} ≠ {today} — skipping")

                closed = _run_close_pass(cur, today)
                refresh_tracking(cur)

        log.info("=" * 60)
        log.info(
            f"DAILY complete\n"
            f"  ZP : {zp_created:>4} created  {zp_skipped:>4} skipped\n"
            f"  ZT : {zt_created:>4} created  {zt_skipped:>4} skipped\n"
            f"  Service tickets closed : {closed}"
        )
        log.info("=" * 60)

    except Exception:
        log.exception("DAILY pipeline failed — transaction rolled back")
        raise
    finally:
        conn.close()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--seed" in sys.argv:
        seed_pipeline()
    else:
        daily_pipeline()
