import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Connect to Postgres
conn = psycopg2.connect(
    host=os.environ["PG_HOST"],
    port=os.environ["PG_PORT"],
    user=os.environ["PG_USER"],
    password=os.environ["PG_PASSWORD"],
    database=os.environ["PG_DB"]
)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS barcode_records (
    id SERIAL PRIMARY KEY,
    serial_number TEXT,
    symbology TEXT,
    confidence REAL,
    created_at TIMESTAMP
)
""")
conn.commit()

# Ensure 'notes' column exists
cur.execute("""
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns 
        WHERE table_name='barcode_records' AND column_name='notes'
    ) THEN
        ALTER TABLE barcode_records ADD COLUMN notes TEXT;
    END IF;
END
$$;
""")
conn.commit()


def insert_record(data):
    try:
        record = {
            "serial_number": data.get("serial_number") or None,
            "symbology": data.get("symbology") or None,
            "confidence": float(data.get("confidence") or 0.0),
            "notes": data.get("notes") or ""
        }

        cur.execute("""
            INSERT INTO barcode_records (serial_number, symbology, confidence, notes, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (record["serial_number"], record["symbology"], record["confidence"],
              record["notes"], datetime.now()))
        conn.commit()
        row = cur.fetchone()
        if row:
            return row[0]
        return None

    except Exception as e:
        conn.rollback()  # Rollback transaction so future queries work
        print("Insert error:", e)
        return None


def fetch_all_records():
    try:
        cur.execute("""
            SELECT id, serial_number, symbology, confidence, notes, created_at
            FROM barcode_records
            ORDER BY id DESC
        """)
        return cur.fetchall()
    except Exception as e:
        conn.rollback()
        print("Fetch error:", e)
        return []
