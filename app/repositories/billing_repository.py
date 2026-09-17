from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.bill_item import BillItem
from datetime import datetime


class BillingRepository:

    def create_bill(
        self,
        db: Session,
        customer_id: int | None = None,
        idempotency_key: str | None = None,
    ) -> Bill:
        bill = Bill(
            customer_id=customer_id,
            status="DRAFT",
            subtotal=Decimal("0.00"),
            cgst=Decimal("0.00"),
            sgst=Decimal("0.00"),
            total=Decimal("0.00"),
            idempotency_key=idempotency_key,
        )

        db.add(bill)
        db.flush()

        return bill

    def get_bill(
        self,
        db: Session,
        bill_id: int,
    ) -> Bill | None:
        return db.get(Bill, bill_id)

    def add_item(
        self,
        db: Session,
        bill_id: int,
        product_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        cost_price: Decimal,
        gst_rate: Decimal,
        hsn_code: str | None,
        taxable_amount: Decimal,
        cgst_amount: Decimal,
        sgst_amount: Decimal,
        total_amount: Decimal,
    ) -> BillItem:

        item = BillItem(
            bill_id=bill_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            cost_price=cost_price,
            gst_rate=gst_rate,
            hsn_code=hsn_code,
            taxable_amount=taxable_amount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            total_amount=total_amount,
        )

        db.add(item)
        db.flush()

        return item

    def get_bill_items(
        self,
        db: Session,
        bill_id: int,
    ) -> list[BillItem]:
        return (
            db.query(BillItem)
            .filter(BillItem.bill_id == bill_id)
            .all()
        )

    def update_bill_totals(
        self,
        db: Session,
        bill_id: int,
        subtotal: Decimal,
        cgst: Decimal,
        sgst: Decimal,
        total: Decimal,
    ) -> Bill | None:
        bill = db.get(Bill, bill_id)

        if bill is None:
            return None

        bill.subtotal = subtotal
        bill.cgst = cgst
        bill.sgst = sgst
        bill.total = total

        db.flush()

        return bill

    def update_bill_status(
        self,
        db: Session,
        bill_id: int,
        status: str,
    ) -> Bill | None:
        bill = db.get(Bill, bill_id)

        if bill is None:
            return None

        bill.status = status

        db.flush()

        return bill

    def finalize_bill(
        self,
        db: Session,
        bill_id: int,
        payment_method: str | None = None,
        payment_reference: str | None = None,
    ) -> Bill | None:

        bill = db.get(Bill, bill_id)

        if bill is None:
            return None

        bill.status = "FINALIZED"
        bill.payment_method = payment_method
        bill.payment_reference = payment_reference
        bill.finalized_at = datetime.utcnow()

        db.flush()

        return bill

    def get_bill_item(
        self,
        db: Session,
        bill_id: int,
        item_id: int,
    ) -> BillItem | None:

        return (
            db.query(BillItem)
            .filter(
                BillItem.id == item_id,
                BillItem.bill_id == bill_id,
            )
            .first()
        )

    def update_bill_item_quantity(
        self,
        db: Session,
        item_id: int,
        quantity,
    ) -> BillItem | None:

        item = db.get(BillItem, item_id)

        if item is None:
            return None

        item.quantity = quantity

        db.flush()

        return item

    def delete_bill_item(
        self,
        db: Session,
        item_id: int,
    ) -> bool:

        item = db.get(BillItem, item_id)

        if item is None:
            return False

        db.delete(item)
        db.flush()

        return True