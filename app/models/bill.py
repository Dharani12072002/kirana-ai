from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from app.database.connection import Base


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="DRAFT"
    )

    subtotal = Column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    cgst = Column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    sgst = Column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    total = Column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    payment_method = Column(
        String(20),
        nullable=True
    )

    payment_reference = Column(
        String(100),
        nullable=True
    )

    idempotency_key = Column(
        String(100),
        unique=True,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    finalized_at = Column(
        DateTime,
        nullable=True
    )