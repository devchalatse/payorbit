"""Invoice request and response schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.invoice import InvoiceStatus


class InvoiceItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=240)
    quantity: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    unit_price_cents: int = Field(ge=0)


class InvoiceCreate(BaseModel):
    business_id: UUID
    customer_id: UUID
    due_date: date
    currency: str = Field(default="ZAR", min_length=3, max_length=3)
    tax_cents: int = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=1000)
    items: list[InvoiceItemCreate] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_currency(self):
        self.currency = self.currency.upper()
        return self


class InvoiceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str
    quantity: Decimal
    unit_price_cents: int
    line_total_cents: int


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    customer_id: UUID
    invoice_number: str
    status: InvoiceStatus
    currency: str
    subtotal_cents: int
    tax_cents: int
    total_cents: int
    issue_date: date | None
    due_date: date
    notes: str | None
    created_at: datetime
    items: list[InvoiceItemRead]
