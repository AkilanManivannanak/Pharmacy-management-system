import sqlite3
from datetime import date, datetime
from typing import Dict, Any, Optional


DB_NAME = "pharmacy.db"


class Pharmacy:
    """
    Pharmacy management system using SQLite for persistence.

    Tables:
    - suppliers
    - customers
    - medicines
    - prescriptions, prescription_items
    - sales, sale_items
    """

    def __init__(self, db_path: str = DB_NAME) -> None:
        self.db_path = db_path
        self._init_db()

    # ---------------- DB helpers ---------------- #

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        # Enforce foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
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

    # ---------------- Suppliers ---------------- #

    def add_supplier(self, name: str, contact: str) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO suppliers (name, contact) VALUES (?, ?)",
                    (name, contact),
                )
                conn.commit()
                print(f"Supplier '{name}' added.")
            except sqlite3.IntegrityError:
                print("Supplier already exists, updating contact.")
                cur.execute(
                    "UPDATE suppliers SET contact = ? WHERE name = ?",
                    (contact, name),
                )
                conn.commit()

    def _get_supplier_id(self, name: str) -> Optional[int]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM suppliers WHERE name = ?", (name,))
            row = cur.fetchone()
            return row[0] if row else None

    def show_suppliers(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, contact FROM suppliers ORDER BY name")
            rows = cur.fetchall()

        print("\nRegistered Suppliers:")
        if not rows:
            print("No suppliers registered.")
            return
        for name, contact in rows:
            print(f"- {name} - Contact: {contact}")

    # ---------------- Customers ---------------- #

    def _get_or_create_customer(self, name: str, phone: Optional[str]) -> int:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM customers WHERE name = ? AND (phone = ? OR phone IS NULL)",
                (name, phone),
            )
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(
                "INSERT INTO customers (name, phone) VALUES (?, ?)",
                (name, phone),
            )
            conn.commit()
            return cur.lastrowid

    # ---------------- Medicines ---------------- #

    def add_medicine(
        self,
        name: str,
        price: float,
        quantity: int,
        supplier_name: Optional[str],
        expiry: Optional[str] = None,
    ) -> None:
        supplier_id = None
        if supplier_name:
            supplier_id = self._get_supplier_id(supplier_name)
            if supplier_id is None:
                print(
                    f"Supplier '{supplier_name}' not found. "
                    "Add the supplier first or leave supplier blank."
                )

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, quantity FROM medicines WHERE name = ?",
                (name,),
            )
            row = cur.fetchone()
            if row:
                med_id, current_qty = row
                new_qty = current_qty + quantity
                cur.execute(
                    """
                    UPDATE medicines
                    SET price = ?, quantity = ?, supplier_id = ?, expiry = ?
                    WHERE id = ?
                    """,
                    (price, new_qty, supplier_id, expiry, med_id),
                )
                print(f"Updated {name}: new quantity {new_qty}.")
            else:
                cur.execute(
                    """
                    INSERT INTO medicines (name, price, quantity, supplier_id, expiry)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (name, price, quantity, supplier_id, expiry),
                )
                print(f"Inserted {quantity} units of {name}.")
            conn.commit()

    def display_stock(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT m.name, m.price, m.quantity, s.name, m.expiry
                FROM medicines m
                LEFT JOIN suppliers s ON m.supplier_id = s.id
                ORDER BY m.name
                """
            )
            rows = cur.fetchall()

        print("\nAvailable Medicines:")
        if not rows:
            print("No medicines in stock.")
            return

        today = date.today()
        for name, price, qty, supplier_name, expiry_str in rows:
            status_parts = []

            # Expiry
            if expiry_str:
                try:
                    exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if exp_date < today:
                        status_parts.append("EXPIRED")
                except ValueError:
                    status_parts.append("INVALID_EXPIRY")

            # Low stock
            if qty < 5:
                status_parts.append("LOW_STOCK")

            status = f" ({', '.join(status_parts)})" if status_parts else ""
            supplier_label = supplier_name or "N/A"
            expiry_label = expiry_str or "N/A"
            print(
                f"- {name} - ₹{price} | Qty: {qty} | "
                f"Supplier: {supplier_label} | Expiry: {expiry_label}{status}"
            )

    def search_medicine(self, query: str) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            like = f"%{query}%"
            cur.execute(
                """
                SELECT m.name, m.price, m.quantity, s.name, m.expiry
                FROM medicines m
                LEFT JOIN suppliers s ON m.supplier_id = s.id
                WHERE m.name LIKE ?
                ORDER BY m.name
                """,
                (like,),
            )
            rows = cur.fetchall()

        print(f"\nSearch results for '{query}':")
        if not rows:
            print("No medicines found.")
            return
        for name, price, qty, supplier_name, expiry_str in rows:
            supplier_label = supplier_name or "N/A"
            expiry_label = expiry_str or "N/A"
            print(
                f"- {name} | ₹{price} | Qty: {qty} | "
                f"Supplier: {supplier_label} | Expiry: {expiry_label}"
            )

    def delete_medicine(self, name: str) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM medicines WHERE name = ?", (name,))
            if cur.rowcount == 0:
                print("Medicine not found, nothing deleted.")
            else:
                print(f"Medicine '{name}' deleted.")
            conn.commit()

    def show_critical_stock(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name, quantity, expiry FROM medicines ORDER BY name"
            )
            rows = cur.fetchall()

        today = date.today()
        low_stock = []
        expired = []

        for name, qty, expiry_str in rows:
            if qty < 5:
                low_stock.append((name, qty))
            if expiry_str:
                try:
                    exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if exp_date < today:
                        expired.append((name, expiry_str))
                except ValueError:
                    continue

        print("\nLow-stock medicines (qty < 5):")
        if not low_stock:
            print("None.")
        else:
            for name, qty in low_stock:
                print(f"- {name}: Qty {qty}")

        print("\nExpired medicines:")
        if not expired:
            print("None.")
        else:
            for name, exp in expired:
                print(f"- {name}: Expired on {exp}")

    def _get_medicine(self, name: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, price, quantity, expiry
                FROM medicines
                WHERE name = ?
                """,
                (name,),
            )
            row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "price": row[1],
            "quantity": row[2],
            "expiry": row[3],
        }

    # ---------------- Sales ---------------- #

    def sell_medicine(self, name: str, quantity: int) -> Optional[float]:
        med = self._get_medicine(name)
        if not med:
            print("Medicine not available.")
            return None

        if med["quantity"] < quantity:
            print("Not enough stock.")
            return None

        # Expiry check
        expiry_str = med.get("expiry")
        if expiry_str:
            try:
                exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                if exp_date < date.today():
                    print("Cannot sell this medicine. It is expired.")
                    return None
            except ValueError:
                print("Warning: invalid expiry date stored; proceeding with sale.")

        total_price = med["price"] * quantity

        with self._get_conn() as conn:
            cur = conn.cursor()

            # Update stock
            new_qty = med["quantity"] - quantity
            cur.execute(
                "UPDATE medicines SET quantity = ? WHERE id = ?",
                (new_qty, med["id"]),
            )

            # Insert sale + sale_item
            sale_date = date.today().isoformat()
            cur.execute(
                "INSERT INTO sales (sale_date, total_amount) VALUES (?, ?)",
                (sale_date, total_price),
            )
            sale_id = cur.lastrowid

            cur.execute(
                """
                INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                (sale_id, med["id"], quantity, med["price"]),
            )

            conn.commit()

        print(f"Sold {quantity} units of {name}. Total: ₹{total_price}")
        return total_price

    def generate_bill(self, purchases: Dict[str, int]) -> float:
        print("\nGenerating Bill...")
        subtotal = 0.0

        # First compute subtotal and check availability
        meds_info: Dict[str, Dict[str, Any]] = {}
        for name, qty in purchases.items():
            med = self._get_medicine(name)
            if not med:
                print(f"{name} not found. Skipping.")
                continue
            if med["quantity"] < qty:
                print(f"Not enough stock for {name}. Skipping.")
                continue
            meds_info[name] = med

        for name, qty in purchases.items():
            if name not in meds_info:
                continue
            med = meds_info[name]
            amount = med["price"] * qty
            print(f"{name} x{qty} = ₹{amount}")
            subtotal += amount

        print(f"Subtotal: ₹{subtotal}")

        tax_rate = 0.05  # 5%
        tax = subtotal * tax_rate

        discount = 0.0
        if subtotal >= 1000:
            discount = subtotal * 0.10  # 10% discount

        total = subtotal + tax - discount
        print(f"Tax (5%): ₹{tax}")
        if discount > 0:
            print(f"Discount (10% over 1000): -₹{discount}")
        print(f"Total Bill Amount: ₹{total}")

        if subtotal == 0.0:
            return 0.0

        # Record sale and items + update stock
        today_str = date.today().isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO sales (sale_date, total_amount) VALUES (?, ?)",
                (today_str, total),
            )
            sale_id = cur.lastrowid

            for name, qty in purchases.items():
                if name not in meds_info:
                    continue
                med = meds_info[name]
                cur.execute(
                    """
                    INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?)
                    """,
                    (sale_id, med["id"], qty, med["price"]),
                )
                new_qty = med["quantity"] - qty
                cur.execute(
                    "UPDATE medicines SET quantity = ? WHERE id = ?",
                    (new_qty, med["id"]),
                )

            conn.commit()

        print("Bill recorded as a sale in the database.")
        return total

    def show_today_sales(self) -> None:
        today_str = date.today().isoformat()
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT total_amount FROM sales WHERE sale_date = ?",
                (today_str,),
            )
            rows = cur.fetchall()

        if not rows:
            print("\nNo sales recorded for today.")
            return

        amounts = [r[0] for r in rows]
        total = sum(amounts)
        print(
            f"\nToday's total sales: ₹{total} "
            f"(from {len(amounts)} transactions)"
        )

    # ---------------- Prescriptions ---------------- #

    def record_prescription(self, customer: str, phone: Optional[str], items: Dict[str, int]) -> None:
        customer_id = self._get_or_create_customer(customer, phone)
        now_str = datetime.now().isoformat(timespec="seconds")

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO prescriptions (customer_id, customer_name, created_at)
                VALUES (?, ?, ?)
                """,
                (customer_id, customer, now_str),
            )
            prescription_id = cur.lastrowid

            for name, qty in items.items():
                med = self._get_medicine(name)
                if not med:
                    print(f"{name} not found, not added to prescription.")
                    continue
                cur.execute(
                    """
                    INSERT INTO prescription_items
                    (prescription_id, medicine_id, quantity)
                    VALUES (?, ?, ?)
                    """,
                    (prescription_id, med["id"], qty),
                )

            conn.commit()

        print(f"Prescription for {customer} recorded.")


# ---------------- Utility input helpers ---------------- #

def read_int(prompt: str) -> int:
    while True:
        value = input(prompt)
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid integer.")


def read_float(prompt: str) -> float:
    while True:
        value = input(prompt)
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


# ---------------- CLI main loop ---------------- #

def main() -> None:
    shop = Pharmacy()

    while True:
        print("\n====== Pharmacy Management System (SQLite Advanced) ======")
        print("1. Add Supplier")
        print("2. Add Medicine")
        print("3. Show Stock")
        print("4. Sell Medicine")
        print("5. Generate Bill")
        print("6. Record Prescription")
        print("7. Show Suppliers")
        print("8. Show Today's Sales")
        print("9. Search Medicine")
        print("10. Delete Medicine")
        print("11. Show Low-Stock & Expired Report")
        print("12. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            name = input("Supplier name: ")
            contact = input("Contact info: ")
            shop.add_supplier(name, contact)

        elif choice == "2":
            name = input("Medicine name: ")
            price = read_float("Price: ₹")
            qty = read_int("Quantity: ")
            supplier = input("Supplier name (or leave blank): ").strip()
            supplier = supplier or None
            expiry = input("Expiry date (YYYY-MM-DD, or leave blank): ").strip()
            expiry = expiry or None
            shop.add_medicine(name, price, qty, supplier, expiry)

        elif choice == "3":
            shop.display_stock()

        elif choice == "4":
            name = input("Medicine to sell: ")
            qty = read_int("Quantity: ")
            shop.sell_medicine(name, qty)

        elif choice == "5":
            purchases: Dict[str, int] = {}
            while True:
                name = input("Enter medicine (or 'done' to finish): ").strip()
                if name.lower() == "done":
                    break
                qty = read_int("Enter quantity: ")
                purchases[name] = purchases.get(name, 0) + qty
            shop.generate_bill(purchases)

        elif choice == "6":
            customer = input("Customer name: ")
            phone = input("Customer phone (or leave blank): ").strip() or None
            items: Dict[str, int] = {}
            while True:
                name = input("Enter medicine for prescription (or 'done'): ").strip()
                if name.lower() == "done":
                    break
                qty = read_int("Enter quantity: ")
                items[name] = items.get(name, 0) + qty
            shop.record_prescription(customer, phone, items)

        elif choice == "7":
            shop.show_suppliers()

        elif choice == "8":
            shop.show_today_sales()

        elif choice == "9":
            query = input("Search text: ").strip()
            shop.search_medicine(query)

        elif choice == "10":
            name = input("Medicine name to delete: ").strip()
            shop.delete_medicine(name)

        elif choice == "11":
            shop.show_critical_stock()

        elif choice == "12":
            print("Exiting system. Thank you!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

