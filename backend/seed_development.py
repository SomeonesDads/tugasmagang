"""Create and seed the disposable development database.

This script uses only proposedtables.sql. It intentionally does not execute
currentschema.sql or start the production feed pipeline.
"""

from datetime import date
from pathlib import Path

import psycopg2

from seed_rca import RCA_DETAILS
from settings import settings


SAMPLE_ASSIGNMENTS = [
    (8887960178, "Medan", "engineer"),
    (8510386982, "Medan", "engineer"),
    (7000000001, "Medan", "manager"),
]

SAMPLE_TICKETS = [
    ("ZP", 41001, 1, None, None, "MDN001", "Medan", 5),
    ("ZP", 41002, 2, None, None, "MDN002", "Medan", 4),
    ("ZT", None, None, 52001, 62001, "MDN003", "Medan", 3),
]
SEED_DATE = date(2026, 1, 1)


def connect():
    return psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )


def main():
    if settings.node_env != "development":
        raise RuntimeError("seed_development.py may only run with NODE_ENV=development")

    schema_path = Path(__file__).with_name("proposedtables.sql")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('mba_sumbagut.ticket')")
            if cur.fetchone()[0] is None:
                cur.execute(schema_path.read_text(encoding="utf-8"))

            for category, details in RCA_DETAILS.items():
                cur.execute("""
                    INSERT INTO mba_sumbagut.rca (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO UPDATE SET active = true
                    RETURNING rca_id
                """, (category,))
                rca_id = cur.fetchone()[0]
                for detail in details:
                    cur.execute("""
                        INSERT INTO mba_sumbagut.rca_detail (rca_id, name)
                        VALUES (%s, %s)
                        ON CONFLICT (rca_id, name) DO UPDATE SET active = true
                    """, (rca_id, detail))

            cur.executemany("""
                INSERT INTO mba_sumbagut.telegram_district_role
                    (telegram_id, district_operation_do, role)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, SAMPLE_ASSIGNMENTS)

            for ticket in SAMPLE_TICKETS:
                cur.execute("""
                    INSERT INTO mba_sumbagut.ticket
                        (ticket_type, enodeb_id, cell_id, lac, ci,
                         site_id, district_operation_do, aging, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING ticket_id
                """, (*ticket, SEED_DATE))
                row = cur.fetchone()
                if row is None:
                    cur.execute("""
                        SELECT ticket_id
                        FROM mba_sumbagut.ticket
                        WHERE site_id = %s AND created_date = %s
                    """, (ticket[5], SEED_DATE))
                    row = cur.fetchone()
                cur.execute("""
                    INSERT INTO mba_sumbagut.ticket_rca (ticket_id, start_day)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (row[0], SEED_DATE))
        conn.commit()

    print("Development schema and seed are ready.")


if __name__ == "__main__":
    main()
