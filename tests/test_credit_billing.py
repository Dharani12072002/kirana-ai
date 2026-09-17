from decimal import Decimal
from uuid import uuid4

from app.database.connection import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.payment import Payment
from app.services.inventory_service import InventoryService
from app.services.billing_service import BillingService
from app.services.khata_service import KhataService


def run_test():
    db = SessionLocal()

    try:
        unique_id = uuid4().hex[:8]

        # ---------------------------------------------
        # Create customer
        # ---------------------------------------------

        khata_service = KhataService()

        customer = khata_service.create_customer(
            db=db,
            name=f"Ravi Credit {unique_id}",
            phone=f"91111{unique_id[:5]}",
        )

        db.commit()
        db.refresh(customer)

        print(f"Customer: {customer.name}")

        # ---------------------------------------------
        # Create product
        # ---------------------------------------------

        product = Product(
            name=f"Credit Test Rice {unique_id}",
            sku=f"CREDIT-RICE-{unique_id}",
            category="Groceries",
            unit="kg",
            cost_price=Decimal("80.00"),
            selling_price=Decimal("100.00"),
            mrp=Decimal("110.00"),
            quantity=Decimal("10"),
            reorder_level=Decimal("2"),
            gst_rate=Decimal("18.00"),
            hsn_code="1006",
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        # ---------------------------------------------
        # Create credit bill
        # ---------------------------------------------

        billing_service = BillingService()

        bill = billing_service.create_draft(
            db=db,
            customer_id=customer.id,
        )

        item = billing_service.add_item(
            db=db,
            bill_id=bill.id,
            product_id=product.id,
            quantity=Decimal("2"),
        )

        bill = billing_service.calculate_bill(
            db=db,
            bill_id=bill.id,
        )

        db.commit()

        print(f"Bill total: ₹{bill.total}")

        assert bill.total == Decimal("236.00")

        # Stock must still be 10 kg before finalization
        db.refresh(product)
        assert product.quantity == Decimal("10")

        # ---------------------------------------------
        # Finalize as CREDIT
        # ---------------------------------------------

        bill = billing_service.finalize_bill(
            db=db,
            bill_id=bill.id,
            payment_method="CREDIT",
            payment_reference="CREDIT-TEST-001",
        )

        db.commit()

        # ---------------------------------------------
        # Verify bill
        # ---------------------------------------------

        assert bill.status == "FINALIZED"
        assert bill.payment_method == "CREDIT"

        # ---------------------------------------------
        # Verify stock
        # ---------------------------------------------

        db.refresh(product)

        assert product.quantity == Decimal("8")

        print(f"Stock after credit sale: {product.quantity} kg")

        # ---------------------------------------------
        # Verify payment record
        # ---------------------------------------------

        payment = (
            db.query(Payment)
            .filter(Payment.bill_id == bill.id)
            .first()
        )

        assert payment is not None
        assert payment.method == "CREDIT"
        assert payment.amount == Decimal("236.00")

        # ---------------------------------------------
        # Verify Khata
        # ---------------------------------------------

        balance = khata_service.get_balance(
            db=db,
            customer_id=customer.id,
        )

        assert balance == Decimal("236.00")

        print(f"Khata balance: ₹{balance}")

        print("\nCredit billing integration test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()