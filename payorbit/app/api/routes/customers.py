"""Customer endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import Business
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerRead

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> Customer:
    if db.get(Business, payload.business_id) is None:
        raise HTTPException(status_code=404, detail="Business not found.")
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=list[CustomerRead])
def list_customers(
    business_id: UUID, db: Session = Depends(get_db)
) -> list[Customer]:
    if db.get(Business, business_id) is None:
        raise HTTPException(status_code=404, detail="Business not found.")
    statement = (
        select(Customer)
        .where(Customer.business_id == business_id)
        .order_by(Customer.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return customer
