# app/crud.py
from typing import Optional, List, Dict, Any
from .db import get_conn


def get_supplier_id_by_name(name: str) -> Optional[int]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM suppliers WHERE name = ?", (name,))
        row = cur.fetchone()
    return row[0] if row else None


def create_or_get_supplier(name: str, contact: str = "") -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM suppliers WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            "INSERT INTO suppliers (name, contact) VALUES (?, ?)",
            (name, contact),
        )
        conn.commit()
        return cur.lastrowid


def list_medicines() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.id, m.name, m.price, m.quantity, s.name, m.expiry
            FROM medicines m
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            ORDER BY m.name
            """
        )
        rows = cur.fetchall()

    result: List[Dict[str, Any]] = []
    for r in rows:
        result.append(
            {
                "id": r[0],
                "name": r[1],
                "price": r[2],
                "quantity": r[3],
                "supplier_name": r[4],
                "expiry": r[5],
            }
        )
    return result


def create_medicine(
    name: str,
    price: float,
    quantity: int,
    supplier_name: Optional[str],
    expiry: Optional[str],
) -> Dict[str, Any]:
    supplier_id: Optional[int] = None
    if supplier_name:
        supplier_id = get_supplier_id_by_name(supplier_name)
        if supplier_id is None:
            supplier_id = create_or_get_supplier(supplier_name, "")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO medicines (name, price, quantity, supplier_id, expiry)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, price, quantity, supplier_id, expiry),
        )
        med_id = cur.lastrowid
        conn.commit()

    return {
        "id": med_id,
        "name": name,
        "price": price,
        "quantity": quantity,
        "supplier_name": supplier_name,
        "expiry": expiry,
    }
