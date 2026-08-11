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
  "Active" = ticket exists AND ticket_service.end_day IS NULL.

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
import os
import sys
from datetime import date, timedelta

import psycopg2
from settings import settings

logging.basicConfig(
    level=getattr(logging, os.getenv("PIPELINE_LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s  [%(levelname)s]  %(message)s",
)
log = logging.getLogger(__name__)


#  Database connection 

def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
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


def _tracking_add_ticket(cur, ticket_id: int) -> None:
    """Increment total-ticket tracking for a newly created ticket."""
    cur.execute("""
        SELECT COALESCE(district_operation_do, 'UNASSIGNED'), site_id
        FROM mba_sumbagut.ticket
        WHERE ticket_id = %s
    """, (ticket_id,))
    row = cur.fetchone()
    if row is None:
        return
    district, site_id = row

    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_summary
            (district, count_problems, solved_rca, solved_service, updated_at)
        VALUES (%s, 1, 0, 0, now())
        ON CONFLICT (district) DO UPDATE
        SET count_problems = tracking_summary.count_problems + 1,
            updated_at = now()
    """, (district,))
    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_summary_site
            (site_id, count_problems, solved_rca, solved_service, updated_at)
        VALUES (%s, 1, 0, 0, now())
        ON CONFLICT (site_id) DO UPDATE
        SET count_problems = tracking_summary_site.count_problems + 1,
            updated_at = now()
    """, (site_id,))


def _tracking_record_service(cur, ticket_id: int) -> None:
    """Record one newly closed service phase in tracking aggregates."""
    cur.execute("""
        SELECT COALESCE(t.district_operation_do, 'UNASSIGNED'), t.site_id,
               r.rca_id, s.end_day - s.start_day AS service_days
        FROM mba_sumbagut.ticket t
        JOIN mba_sumbagut.ticket_service s ON s.ticket_id = t.ticket_id
        LEFT JOIN mba_sumbagut.ticket_rca r ON r.ticket_id = t.ticket_id
        WHERE t.ticket_id = %s AND s.end_day IS NOT NULL
    """, (ticket_id,))
    row = cur.fetchone()
    if row is None:
        return
    district, site_id, rca_id, service_days = row

    for table, key, value in (
        ("tracking_summary", "district", district),
        ("tracking_summary_site", "site_id", site_id),
    ):
        cur.execute(f"""
            UPDATE mba_sumbagut.{table}
            SET solved_service = solved_service + 1,
                solved_service_avg_time =
                    (COALESCE(solved_service_avg_time, 0) * solved_service + %s)
                    / (solved_service + 1),
                updated_at = now()
            WHERE {key} = %s
        """, (service_days, value))

    if rca_id is not None:
        cur.execute("""
            UPDATE mba_sumbagut.tracking_detail
            SET solved_service = solved_service + 1,
                solved_service_avg_time =
                    (COALESCE(solved_service_avg_time, 0) * solved_service + %s)
                    / (solved_service + 1),
                updated_at = now()
            WHERE district = %s AND rca_id = %s
        """, (service_days, district, rca_id))
        cur.execute("""
            UPDATE mba_sumbagut.tracking_detail_site
            SET solved_service = solved_service + 1,
                solved_service_avg_time =
                    (COALESCE(solved_service_avg_time, 0) * solved_service + %s)
                    / (solved_service + 1),
                updated_at = now()
            WHERE site_id = %s AND rca_id = %s
        """, (service_days, site_id, rca_id))


def _tracking_record_rca(cur, ticket_id: int) -> None:
    """Record one newly submitted RCA in tracking aggregates."""
    cur.execute("""
        SELECT COALESCE(t.district_operation_do, 'UNASSIGNED'), t.site_id,
               t.created_date, r.end_day, r.rca_id,
               s.end_day IS NOT NULL, s.end_day - s.start_day
        FROM mba_sumbagut.ticket t
        JOIN mba_sumbagut.ticket_rca r ON r.ticket_id = t.ticket_id
        LEFT JOIN mba_sumbagut.ticket_service s ON s.ticket_id = t.ticket_id
        WHERE t.ticket_id = %s AND r.submitted_at IS NOT NULL
    """, (ticket_id,))
    row = cur.fetchone()
    if row is None:
        return
    district, site_id, created_date, rca_end_day, rca_id, serviced, service_days = row
    analysis_days = (rca_end_day - created_date).days

    for table, key, value in (
        ("tracking_summary", "district", district),
        ("tracking_summary_site", "site_id", site_id),
    ):
        cur.execute(f"""
            UPDATE mba_sumbagut.{table}
            SET solved_rca = solved_rca + 1,
                solved_rca_avg_time =
                    (COALESCE(solved_rca_avg_time, 0) * solved_rca + %s)
                    / (solved_rca + 1),
                updated_at = now()
            WHERE {key} = %s
        """, (analysis_days, value))

    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_detail
            (district, rca_id, count_problems, solved_rca, solved_service,
             solved_rca_avg_time, solved_service_avg_time, updated_at)
        VALUES (%s, %s, 1, 1, %s, %s, %s, now())
        ON CONFLICT (district, rca_id) DO UPDATE
        SET count_problems = tracking_detail.count_problems + 1,
            solved_rca = tracking_detail.solved_rca + 1,
            solved_service = tracking_detail.solved_service + EXCLUDED.solved_service,
            solved_rca_avg_time =
                (COALESCE(tracking_detail.solved_rca_avg_time, 0) * tracking_detail.solved_rca + %s)
                / (tracking_detail.solved_rca + 1),
            solved_service_avg_time = CASE WHEN EXCLUDED.solved_service = 1 THEN
                (COALESCE(tracking_detail.solved_service_avg_time, 0) * tracking_detail.solved_service + %s)
                / (tracking_detail.solved_service + 1)
                ELSE tracking_detail.solved_service_avg_time END,
            updated_at = now()
    """, (district, rca_id, int(serviced), analysis_days,
           service_days if serviced else None, analysis_days,
           service_days if serviced else 0))
    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_detail_site
            (site_id, rca_id, count_problems, solved_rca, solved_service,
             solved_rca_avg_time, solved_service_avg_time, updated_at)
        VALUES (%s, %s, 1, 1, %s, %s, %s, now())
        ON CONFLICT (site_id, rca_id) DO UPDATE
        SET count_problems = tracking_detail_site.count_problems + 1,
            solved_rca = tracking_detail_site.solved_rca + 1,
            solved_service = tracking_detail_site.solved_service + EXCLUDED.solved_service,
            solved_rca_avg_time =
                (COALESCE(tracking_detail_site.solved_rca_avg_time, 0) * tracking_detail_site.solved_rca + %s)
                / (tracking_detail_site.solved_rca + 1),
            solved_service_avg_time = CASE WHEN EXCLUDED.solved_service = 1 THEN
                (COALESCE(tracking_detail_site.solved_service_avg_time, 0) * tracking_detail_site.solved_service + %s)
                / (tracking_detail_site.solved_service + 1)
                ELSE tracking_detail_site.solved_service_avg_time END,
            updated_at = now()
    """, (site_id, rca_id, int(serviced), analysis_days,
           service_days if serviced else None, analysis_days,
           service_days if serviced else 0))


# ── Shared: ticket + ticket_rca insert ────────────────────────────────────────

def _insert_ticket_and_rca(cur, ticket_params: tuple, start_day: date, *, update_tracking: bool = True) -> int | None:
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

    # Service tracking is independent from RCA. A cell can clear from the
    # daily feed before an engineer submits the root cause analysis.
    cur.execute("""
        INSERT INTO mba_sumbagut.ticket_service (ticket_id, start_day)
        VALUES (%s, %s)
    """, (ticket_id, start_day))
    if update_tracking:
        _tracking_add_ticket(cur, ticket_id)

    return ticket_id


def _ensure_service_rows(cur) -> None:
    """Backfill service tracking for tickets created before this lifecycle fix."""
    cur.execute("""
        INSERT INTO mba_sumbagut.ticket_service (ticket_id, start_day)
        SELECT t.ticket_id, t.created_date
        FROM mba_sumbagut.ticket t
        LEFT JOIN mba_sumbagut.ticket_service ts ON ts.ticket_id = t.ticket_id
        WHERE ts.ticket_id IS NULL
        ON CONFLICT (ticket_id) DO NOTHING
    """)


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

def _seed_zp_pass(cur, today: date, *, update_tracking: bool = False) -> tuple[int, int]:
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
            tid = _insert_ticket_and_rca(cur, params, today, update_tracking=update_tracking)
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


def _seed_zt_pass(cur, today: date, *, update_tracking: bool = False) -> tuple[int, int]:
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
            tid = _insert_ticket_and_rca(cur, params, today, update_tracking=update_tracking)
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
                cur.execute(
                    'SELECT DISTINCT "date" '
                    'FROM mba_sumbagut.sri_zp_daily '
                    'WHERE "date" IS NOT NULL '
                    'ORDER BY "date"'
                )
                zp_dates = {row[0] for row in cur.fetchall()}
                cur.execute(
                    'SELECT DISTINCT "date" '
                    'FROM mba_sumbagut.sri_zt_daily '
                    'WHERE "date" IS NOT NULL '
                    'ORDER BY "date"'
                )
                zt_dates = {row[0] for row in cur.fetchall()}
                feed_dates = sorted(zp_dates | zt_dates)

                if not feed_dates:
                    log.warning("No data in either feed table. Nothing to seed.")
                    return

                _ensure_service_rows(cur)
                zp_created = zp_skipped = 0
                zt_created = zt_skipped = 0
                total_closed = 0

                # Replay the complete feed history. Closing before inserting
                # today's cells allows a cell that returned after a gap to get
                # a new ticket instead of being blocked by its old one.
                for feed_date in feed_dates:
                    closed = _run_close_pass(cur, feed_date, update_tracking=False)
                    total_closed += closed
                    if feed_date in zp_dates:
                        created, skipped = _seed_zp_pass(cur, feed_date, update_tracking=False)
                        zp_created += created
                        zp_skipped += skipped
                    if feed_date in zt_dates:
                        created, skipped = _seed_zt_pass(cur, feed_date, update_tracking=False)
                        zt_created += created
                        zt_skipped += skipped

                refresh_tracking(cur)

        log.info("=" * 60)
        log.info(
            f"SEED complete\n"
            f"  ZP : {zp_created:>4} created  {zp_skipped:>4} skipped\n"
            f"  ZT : {zt_created:>4} created  {zt_skipped:>4} skipped\n"
            f"  Service tickets closed : {total_closed}"
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


def _run_close_pass(cur, today: date, *, update_tracking: bool = True) -> int:
    """
    Close ticket_service rows where the problematic cell no longer appears
    in today's feed.  Minimum service duration = 1 day (feed is daily).
    Returns count of tickets closed.
    """
    log.info("[CLOSE] Service ticket close pass")
    closed_ids = []

    # ── Close ZP service tickets ─────────────────────────────────────────────
    cur.execute("""
        UPDATE mba_sumbagut.ticket_service ts
        SET end_day = %s, updated_at = now()
        FROM mba_sumbagut.ticket t
        WHERE t.ticket_id = ts.ticket_id
          AND ts.end_day IS NULL AND t.ticket_type = 'ZP'
          AND NOT EXISTS (
              SELECT 1 FROM mba_sumbagut.sri_zp_daily d
              WHERE d."date" = %s AND d.enodeb_id = t.enodeb_id
                AND d.cell_id = t.cell_id AND d.site_id = t.site_id
          )
        RETURNING ts.ticket_id
    """, (today, today))
    closed_ids.extend(row[0] for row in cur.fetchall())

    # ── Close ZT service tickets ─────────────────────────────────────────────
    cur.execute("""
        UPDATE mba_sumbagut.ticket_service ts
        SET end_day = %s, updated_at = now()
        FROM mba_sumbagut.ticket t
        WHERE t.ticket_id = ts.ticket_id
          AND ts.end_day IS NULL AND t.ticket_type = 'ZT'
          AND NOT EXISTS (
              SELECT 1 FROM mba_sumbagut.sri_zt_daily d
              WHERE d."date" = %s AND d.lac = t.lac
                AND d.ci = t.ci AND d.site_id = t.site_id
          )
        RETURNING ts.ticket_id
    """, (today, today))
    closed_ids.extend(row[0] for row in cur.fetchall())

    if update_tracking:
        for ticket_id in closed_ids:
            _tracking_record_service(cur, ticket_id)

    log.info(f"[CLOSE] Done  closed={len(closed_ids)}")
    return len(closed_ids)


def refresh_tracking(cur) -> None:
    """Rebuild manager tracking aggregates from ticket lifecycle tables."""
    log.info("[TRACKING] Refreshing tracking aggregates")

    # These tables are derived data. Rebuilding them removes stale groups after
    # historical backfills and keeps all four manager views consistent.
    cur.execute("DELETE FROM mba_sumbagut.tracking_detail_site")
    cur.execute("DELETE FROM mba_sumbagut.tracking_detail")
    cur.execute("DELETE FROM mba_sumbagut.tracking_summary_site")
    cur.execute("DELETE FROM mba_sumbagut.tracking_summary")

    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_summary
            (district, count_problems, solved_rca, solved_service,
             solved_rca_avg_time, solved_service_avg_time, updated_at)
        SELECT COALESCE(t.district_operation_do, 'UNASSIGNED'), COUNT(*),
               COUNT(*) FILTER (WHERE r.submitted_at IS NOT NULL),
               COUNT(*) FILTER (WHERE s.end_day IS NOT NULL),
               AVG((r.end_day - t.created_date)::numeric)
                   FILTER (WHERE r.end_day IS NOT NULL),
               AVG((s.end_day - s.start_day)::numeric)
                   FILTER (WHERE s.end_day IS NOT NULL), now()
        FROM mba_sumbagut.ticket t
        LEFT JOIN mba_sumbagut.ticket_rca r ON r.ticket_id = t.ticket_id
        LEFT JOIN mba_sumbagut.ticket_service s ON s.ticket_id = t.ticket_id
        GROUP BY COALESCE(t.district_operation_do, 'UNASSIGNED')
    """)

    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_detail
            (district, rca_id, count_problems, solved_rca, solved_service,
             solved_rca_avg_time, solved_service_avg_time, updated_at)
        SELECT COALESCE(t.district_operation_do, 'UNASSIGNED'), r.rca_id,
               COUNT(*), COUNT(*) FILTER (WHERE r.submitted_at IS NOT NULL),
               COUNT(*) FILTER (WHERE s.end_day IS NOT NULL),
               AVG((r.end_day - t.created_date)::numeric)
                   FILTER (WHERE r.end_day IS NOT NULL),
               AVG((s.end_day - s.start_day)::numeric)
                   FILTER (WHERE s.end_day IS NOT NULL), now()
        FROM mba_sumbagut.ticket t
        JOIN mba_sumbagut.ticket_rca r
          ON r.ticket_id = t.ticket_id AND r.rca_id IS NOT NULL
        LEFT JOIN mba_sumbagut.ticket_service s ON s.ticket_id = t.ticket_id
        GROUP BY COALESCE(t.district_operation_do, 'UNASSIGNED'), r.rca_id
    """)

    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_summary_site
            (site_id, count_problems, solved_rca, solved_service,
             solved_rca_avg_time, solved_service_avg_time, updated_at)
        SELECT t.site_id, COUNT(*),
               COUNT(*) FILTER (WHERE r.submitted_at IS NOT NULL),
               COUNT(*) FILTER (WHERE s.end_day IS NOT NULL),
               AVG((r.end_day - t.created_date)::numeric)
                   FILTER (WHERE r.end_day IS NOT NULL),
               AVG((s.end_day - s.start_day)::numeric)
                   FILTER (WHERE s.end_day IS NOT NULL), now()
        FROM mba_sumbagut.ticket t
        LEFT JOIN mba_sumbagut.ticket_rca r ON r.ticket_id = t.ticket_id
        LEFT JOIN mba_sumbagut.ticket_service s ON s.ticket_id = t.ticket_id
        GROUP BY t.site_id
    """)

    cur.execute("""
        INSERT INTO mba_sumbagut.tracking_detail_site
            (site_id, rca_id, count_problems, solved_rca, solved_service,
             solved_rca_avg_time, solved_service_avg_time, updated_at)
        SELECT t.site_id, r.rca_id, COUNT(*),
               COUNT(*) FILTER (WHERE r.submitted_at IS NOT NULL),
               COUNT(*) FILTER (WHERE s.end_day IS NOT NULL),
               AVG((r.end_day - t.created_date)::numeric)
                   FILTER (WHERE r.end_day IS NOT NULL),
               AVG((s.end_day - s.start_day)::numeric)
                   FILTER (WHERE s.end_day IS NOT NULL), now()
        FROM mba_sumbagut.ticket t
        JOIN mba_sumbagut.ticket_rca r
          ON r.ticket_id = t.ticket_id AND r.rca_id IS NOT NULL
        LEFT JOIN mba_sumbagut.ticket_service s ON s.ticket_id = t.ticket_id
        GROUP BY t.site_id, r.rca_id
    """)

    log.info("[TRACKING] Refresh complete")


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
                _ensure_service_rows(cur)
                # Close yesterday's service state before creating today's
                # tickets, so a cell returning after a gap gets a new ticket.
                closed = _run_close_pass(cur, today)

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
