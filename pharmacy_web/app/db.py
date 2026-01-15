# app/db.py
import sqlite3

DB_NAME = "pharmacy.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
