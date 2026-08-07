"""Seed the normalized RCA lookup tables.

Run from the backend directory with:
    python seed_rca.py

The operation is idempotent: existing category/detail names are preserved and
new definitions are inserted without changing the ticket schema.
"""

import psycopg2

from settings import settings


RCA_DETAILS = {
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


def main():
    conn = psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=settings.database_password,
    )
    try:
        with conn.cursor() as cur:
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
        conn.commit()
    finally:
        conn.close()
    print(f"Seeded {len(RCA_DETAILS)} RCA categories and {sum(map(len, RCA_DETAILS.values()))} details.")


if __name__ == "__main__":
    main()
