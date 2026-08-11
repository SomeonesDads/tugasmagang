"""Seed manager tracking aggregates for a demo without creating tickets.

The tracking tables are normally rebuilt from ticket lifecycle data.  This
script intentionally writes only the four tracking tables so the manager UI
can be demonstrated with realistic, hundreds-scale numbers while leaving the
ticket tables untouched.

Examples:
    python seed_demo_tracking.py
    python seed_demo_tracking.py --district "TO RANTAU PRAPAT" \
        --sites RNT001,RNT002,RNT003,RNT004
"""

import argparse
from datetime import datetime, timezone

import psycopg2

from settings import settings


DEFAULT_DISTRICT = "TO RANTAU PRAPAT"
DEFAULT_SITES = ("RNT001", "RNT002", "RNT003", "RNT004", "RNT005")


def connect():
    return psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )


def _demo_rows(rca_ids, sites):
    # Every row is deterministic, but each site has a different profile.
    site_rows = []
    detail_rows = []
    for site_index, site_id in enumerate(sites):
        total = 145 + site_index * 31
        solved_rca = total - (18 + site_index * 2)
        solved_service = solved_rca - (9 + site_index)
        site_rows.append((
            site_id, total, solved_rca, solved_service,
            7.5 + site_index * 1.3, 12.0 + site_index * 1.8,
        ))

        remaining = total
        for rca_index, rca_id in enumerate(rca_ids):
            count = remaining if rca_index == len(rca_ids) - 1 else max(1, total // (rca_index + 3))
            remaining -= count
            detail_rows.append((
                site_id, rca_id, count,
                min(count, round(count * 0.72)),
                min(count, round(count * 0.61)),
                4.0 + rca_index * 2.5 + site_index * 0.4,
                9.0 + rca_index * 3.0 + site_index * 0.6,
            ))
    return site_rows, detail_rows


def seed_demo_tracking(district: str, sites: tuple[str, ...]) -> None:
    if not sites:
        raise ValueError("At least one site is required.")

    with connect() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT rca_id
            FROM mba_sumbagut.rca
            WHERE active
            ORDER BY rca_id
            LIMIT 4
        """)
        rca_ids = [row[0] for row in cur.fetchall()]
        if not rca_ids:
            raise RuntimeError("No active RCA categories found. Seed RCA data first.")

        site_rows, detail_rows = _demo_rows(rca_ids, sites)
        now = datetime.now(timezone.utc)

        # Clear only this demo district's aggregate rows. Tickets are never
        # inserted or deleted by this script.
        cur.execute("DELETE FROM mba_sumbagut.tracking_detail WHERE district = %s", (district,))
        cur.execute("DELETE FROM mba_sumbagut.tracking_summary WHERE district = %s", (district,))
        cur.execute("DELETE FROM mba_sumbagut.tracking_detail_site WHERE site_id = ANY(%s)", (list(sites),))
        cur.execute("DELETE FROM mba_sumbagut.tracking_summary_site WHERE site_id = ANY(%s)", (list(sites),))

        total = sum(row[1] for row in site_rows)
        solved_rca = sum(row[2] for row in site_rows)
        solved_service = sum(row[3] for row in site_rows)
        cur.execute("""
            INSERT INTO mba_sumbagut.tracking_summary
                (district, count_problems, solved_rca, solved_service,
                 solved_rca_avg_time, solved_service_avg_time, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (district, total, solved_rca, solved_service, 9.8, 18.6, now))

        for rca_index, rca_id in enumerate(rca_ids):
            rows = [row for row in detail_rows if row[1] == rca_id]
            cur.execute("""
                INSERT INTO mba_sumbagut.tracking_detail
                    (district, rca_id, count_problems, solved_rca, solved_service,
                     solved_rca_avg_time, solved_service_avg_time, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                district, rca_id, sum(row[2] for row in rows),
                sum(row[3] for row in rows), sum(row[4] for row in rows),
                5.0 + rca_index * 2.0, 10.0 + rca_index * 2.5, now,
            ))

        cur.executemany("""
            INSERT INTO mba_sumbagut.tracking_summary_site
                (site_id, count_problems, solved_rca, solved_service,
                 solved_rca_avg_time, solved_service_avg_time, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [(*row, now) for row in site_rows])
        cur.executemany("""
            INSERT INTO mba_sumbagut.tracking_detail_site
                (site_id, rca_id, count_problems, solved_rca, solved_service,
                 solved_rca_avg_time, solved_service_avg_time, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [(*row, now) for row in detail_rows])
        conn.commit()

    print(f"Seeded demo tracking for {district}: {total} problems across {len(sites)} sites.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--district", default=DEFAULT_DISTRICT)
    parser.add_argument("--sites", default=",".join(DEFAULT_SITES))
    args = parser.parse_args()
    sites = tuple(site.strip() for site in args.sites.split(",") if site.strip())
    seed_demo_tracking(args.district.strip(), sites)


if __name__ == "__main__":
    main()
