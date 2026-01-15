# Pharmacy Management System (SQLite) — CLI + FastAPI API

A lightweight pharmacy operations system built with **Python + SQLite**, delivered in two interfaces:

- **CLI app** for day-to-day pharmacy workflows (inventory, suppliers, sales, prescriptions, reports).
- **FastAPI REST API** exposing a medicines endpoint with interactive Swagger docs.

---

## Demo

- API docs (Swagger): `http://127.0.0.1:8000/docs`
- The screen recording shows:
  - FastAPI running on `127.0.0.1:8000`
  - `GET /medicines` + `POST /medicines`
  - CLI menu: supplier add, stock list, sell medicine, today’s sales, exit

> Tip: Add your screen recording to the repo (e.g., `demo/demo.mov`) and link it here for recruiters.

---

## Tech Stack

- **Python 3**
- **SQLite**
- **FastAPI + Uvicorn**
- (CLI) Python standard library `sqlite3`

---

## Features

### 1) CLI App (`pharmacy_cli/pharmacy_cli_sqlite.py`)

Menu (as implemented in the CLI):

1. Add Supplier  
2. Add Medicine  
3. Show Stock  
4. Sell Medicine  
5. Generate Bill  
6. Record Prescription  
7. Show Suppliers  
8. Show Today’s Sales  
9. Search Medicine  
10. Delete Medicine  
11. Show Low-Stock & Expired Report  
12. Exit  

Key workflows:
- **Suppliers**: add + list
- **Inventory**:
  - add medicines (price, quantity, supplier, expiry)
  - search medicine by name
  - delete medicine
  - show stock (with status flags like *low stock / expired* depending on your rules)
- **Sales**:
  - sell medicine (updates stock and records a transaction)
  - show **today’s sales total**
- **Prescriptions**:
  - record prescriptions (customer + requested medicines)
- **Reports**:
  - low-stock and expired medicines report

> Note: The CLI prints amounts using the ₹ symbol in the demo. You can change currency formatting easily if required.

---

### 2) FastAPI Web API (`pharmacy_web/app/main.py`)

Interactive API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Current endpoints (as shown in Swagger):
- `GET /medicines` — list medicines
- `POST /medicines` — create a medicine

Request body schema (from Swagger):
```json
{
  "name": "string",
  "price": 0,
  "quantity": 0,
  "supplier_name": "string",
  "expiry": "string"
}
```
Depending on your implementation, the CLI and API may use the same SQLite file or separate ones. 
Document the DB path(s) if you want “single shared DB.”
---
## Architecture
             ┌──────────────────────────┐
             │        CLI (Python)      │
             │  pharmacy_cli_sqlite.py  │
             └─────────────┬────────────┘
                           │ sqlite3
                           ▼
                     ┌───────────┐
                     │  SQLite   │
                     │   .db     │
                     └───────────┘
                           ▲
                           │
             ┌─────────────┴────────────┐
             │   FastAPI (Uvicorn)      │
             │  /medicines GET + POST   │
             └──────────────────────────┘



---
## Project Structure

pharmacy-project/
  README.md

  pharmacy_cli/
    pharmacy_cli_sqlite.py

  pharmacy_web/
    app/
      main.py        # FastAPI app + routes
      # other modules (db helpers / models / crud) if present

---

## Getting Started

# Prerequisites

- Python 3.10+ recommended

# Install dependencies

From repo root:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the CLI

cd pharmacy_cli
python pharmacy_cli_sqlite.py

# Example flow (as shown in the recording):

- Add supplier: ABC Pharmacy
- Add medicines: Dolo 650, Amoxicillin
- Show stock (prints medicine, price, qty, supplier, expiry)
- Sell medicine: Dolo 650 quantity 2
- Show today’s sales
- Exit

---

## Run the Web API

cd pharmacy_web
uvicorn app.main:app --reload

# Open:
http://127.0.0.1:8000/docs

---

## API Usage (cURL)

# Create a medicine

curl -X POST "http://127.0.0.1:8000/medicines" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dolo 650",
    "price": 20,
    "quantity": 117,
    "supplier_name": "ABC Pharmacy",
    "expiry": "2026-12-31"
  }'
  
# List medicines

curl "http://127.0.0.1:8000/medicines"

---
## Design Notes

- Uses SQLite for local persistence (simple, portable, zero-config).
- CLI is optimized for fast operator workflows (menu-driven).
- API exposes a clean contract via OpenAPI/Swagger, making integration/testing easy.

---
## Limitations

- No authentication/roles (admin vs pharmacist) yet.
- API currently exposes only the medicines routes shown in Swagger.
- No automated tests yet (recommended next).

---

## Roadmap (upgrades)

- Expand API: suppliers, sales, prescriptions, reports
- Add validation: expiry date parsing, non-negative quantity, unique constraints
- Add tests: pytest + API tests for /medicines
- Add Docker: one-command run
- Add CI: GitHub Actions (lint + tests)
---

