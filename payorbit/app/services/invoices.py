"""Invoice domain operations."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.business import Business
from app.models.customer import Customer
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.schemas.invoice import InvoiceCreate


def _to_minor_units(quantity: Decimal, unit_price_cents: int) -> int:
    amount = quantity * Decimal(unit_price_cents)
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def create_invoice(payload: InvoiceCreate, db: Session) -> Invoice:
    business = db.get(Business, payload.business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found.")

    customer = db.get(Customer, payload.customer_id)
    if customer is None or customer.business_id != business.id:
        raise HTTPException(status_code=404, detail="Customer not found for this business.")

    if payload.due_date < date.today():
        raise HTTPException(status_code=422, detail="Due date cannot be in the past.")

    items = [
        InvoiceItem(
            description=item.description,
            quantity=item.quantity,
            unit_price_cents=item.unit_price_cents,
            line_total_cents=_to_minor_units(item.quantity, item.unit_price_cents),
        )
        for item in payload.items
    ]
    subtotal = sum(item.line_total_cents for item in items)
    invoice = Invoice(
        business_id=business.id,
        customer_id=customer.id,
        invoice_number=f"INV-{date.today():%Y%m%d}-{uuid4().hex[:8].upper()}",
        status=InvoiceStatus.DRAFT,
        currency=payload.currency,
        subtotal_cents=subtotal,
        tax_cents=payload.tax_cents,
        total_cents=subtotal + payload.tax_cents,
        due_date=payload.due_date,
        notes=payload.notes,
        items=items,
    )
    db.add(invoice)
    db.commit()
    return get_invoice(invoice.id, db)


def get_invoice(invoice_id: UUID, db: Session) -> Invoice:
    statement = select(Invoice).options(selectinload(Invoice.items)).where(Invoice.id == invoice_id)
    invoice = db.scalar(statement)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return invoice


def list_invoices(business_id: UUID, db: Session) -> list[Invoice]:
    if db.get(Business, business_id) is None:
        raise HTTPException(status_code=404, detail="Business not found.")
    statement = (
        select(Invoice)
        .options(selectinload(Invoice.items))
        .where(Invoice.business_id == business_id)
        .order_by(Invoice.created_at.desc())
    )
    return list(db.scalars(statement).all())


def issue_invoice(invoice_id: UUID, db: Session) -> Invoice:
    invoice = get_invoice(invoice_id, db)
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=409,
            detail=(\n                f"Only draft invoices can be issued; current status is '{invoice.status.value}'."\n            ),
        )
    invoice.status = InvoiceStatus.ISSUED
    invoice.issue_date = date.today()
    db.commit()
    return get_invoice(invoice.id, db)
