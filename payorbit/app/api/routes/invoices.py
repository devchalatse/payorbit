"""Invoice endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceRead
from app.services.invoices import create_invoice, get_invoice, issue_invoice, list_invoices

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def post_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)) -> Invoice:
    return create_invoice(payload, db)


@router.get("", response_model=list[InvoiceRead])
def get_invoices(business_id: UUID, db: Session = Depends(get_db)) -> list[Invoice]:
    return list_invoices(business_id, db)


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice_by_id(invoice_id: UUID, db: Session = Depends(get_db)) -> Invoice:
    return get_invoice(invoice_id, db)


@router.post("/{invoice_id}/issue", response_model=InvoiceRead)
def post_issue_invoice(invoice_id: UUID, db: Session = Depends(get_db)) -> Invoice:
    return issue_invoice(invoice_id, db)
