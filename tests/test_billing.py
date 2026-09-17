from decimal import Decimal
from uuid import uuid4

from app.database.connection import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.services.inventory_service import InventoryService
from app.services.billing_service import BillingService


def run_test():
    db = SessionLocal()

    try:
        unique_id = uuid4().hex[:8]

        # Create product
        product = Product(
            name=f"Edit Test Rice {unique_id}",
            sku=f"EDIT-RICE-{unique_id}",
            category="Groceries",
            unit="kg",
            cost_price=Decimal("80.00"),
            selling_price=Decimal("100.00"),
            mrp=Decimal("110.00"),
            quantity=Decimal("0"),
            reorder_level=Decimal("2"),
            gst_rate=Decimal("18.00"),
            hsn_code="1006",
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        # Receive 10 kg
        InventoryService.receive_stock(
            db=db,
            product_id=product.id,
            quantity=Decimal("10"),
            reference="EDIT_BILL_TEST",
        )
        db.commit()

        billing_service = BillingService()

        # Create draft
        bill = billing_service.create_draft(db=db)

        # Add 2 kg
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

        assert bill.total == Decimal("236.00")

        print("Initial bill: 2 kg")
        print(f"Initial total: ₹{bill.total}")

        # ------------------------------------------------
        # Change 2 kg → 3 kg
        # ------------------------------------------------

        bill = billing_service.update_item_quantity(
            db=db,
            bill_id=bill.id,
            item_id=item.id,
            quantity=Decimal("3"),
        )

        db.commit()

        assert bill.total == Decimal("354.00")

        # Stock must still be 10 kg
        db.refresh(product)

        assert product.quantity == Decimal("10")

        print("Quantity updated: 2 kg → 3 kg")
        print(f"Updated total: ₹{bill.total}")
        print(f"Stock after editing: {product.quantity} kg")

        # ------------------------------------------------
        # Remove item
        # ------------------------------------------------

        bill = billing_service.remove_item(
            db=db,
            bill_id=bill.id,
            item_id=item.id,
        )

        db.commit()

        assert bill.total == Decimal("0.00")

        # Stock must STILL be 10 kg
        db.refresh(product)

        assert product.quantity == Decimal("10")

        print("Item removed successfully.")
        print(f"Total after removing item: ₹{bill.total}")
        print(f"Stock after removing item: {product.quantity} kg")

        print("\nBill editing test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()