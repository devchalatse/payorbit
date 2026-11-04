"""Create the original PayOrbit billing schema (pre-auth tables)."""

from alembic import op

from app.db.base import Base
from app.models import Business, Customer, Invoice, InvoiceItem  # noqa: F401

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

INITIAL_TABLES = ("businesses", "customers", "invoices", "invoice_items")


def upgrade() -> None:
    tables = [Base.metadata.tables[name] for name in INITIAL_TABLES]
    Base.metadata.create_all(bind=op.get_bind(), tables=tables)


def downgrade() -> None:
    tables = [Base.metadata.tables[name] for name in reversed(INITIAL_TABLES)]
    Base.metadata.drop_all(bind=op.get_bind(), tables=tables)
