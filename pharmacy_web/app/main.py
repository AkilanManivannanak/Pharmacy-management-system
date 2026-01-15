# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from .models_sql import init_db
from . import crud

app = FastAPI(title="Pharmacy Management API")


class MedicineCreate(BaseModel):
    name: str
    price: float
    quantity: int
    supplier_name: Optional[str] = None
    expiry: Optional[str] = None


class Medicine(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    supplier_name: Optional[str] = None
    expiry: Optional[str] = None


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/medicines", response_model=List[Medicine])
def list_medicines_endpoint():
    meds = crud.list_medicines()
    return [Medicine(**m) for m in meds]


@app.post("/medicines", response_model=Medicine)
def create_medicine_endpoint(med: MedicineCreate):
    created = crud.create_medicine(
        med.name,
        med.price,
        med.quantity,
        med.supplier_name,
        med.expiry,
    )
    return Medicine(**created)
