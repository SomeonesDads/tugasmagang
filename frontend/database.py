import sqlite3
import os

DB_PATH = os.path.join("data", "rca_monitoring.db")


def get_connection():
    return sqlite3.connect(DB_PATH)

def create_district_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS districts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT UNIQUE,
            nama TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()

def create_engineer_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engineers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            telegram_id INTEGER,
            district_id INTEGER,
            FOREIGN KEY(district_id) REFERENCES districts(id)
        )
    """)

    conn.commit()
    conn.close()


def create_ticket_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            incident TEXT UNIQUE,

            district_id INTEGER,

            customer_name TEXT,

            address TEXT,

            trouble TEXT,

            status TEXT,

            engineer_id INTEGER,

            rca TEXT,

            rca_detail TEXT,

            open_time TEXT,

            solve_time TEXT,

            FOREIGN KEY(district_id) REFERENCES districts(id),

            FOREIGN KEY(engineer_id) REFERENCES engineers(id)
        )
    """)

    conn.commit()
    conn.close()

def create_database():
    create_district_table()
    create_engineer_table()
    create_ticket_table()

    print("Database berhasil dibuat.")

if __name__ == "__main__":
    create_database()