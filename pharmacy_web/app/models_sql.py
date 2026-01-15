# app/models_sql.py
import sqlite3
from .db import DB_NAME, get_conn


def init_db() -> None:
    """
    Initialize SQLite database with required tables.
    Safe to call at startup; uses IF NOT EXISTS.
    """
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                contact TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                UNIQUE(name, phone)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                supplier_id INTEGER,
                expiry TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS prescription_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date TEXT NOT NULL,
                total_amount REAL NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
            """
        )

        conn.commit()
