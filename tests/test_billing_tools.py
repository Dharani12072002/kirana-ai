from decimal import Decimal
from uuid import uuid4

from app.database.connection import SessionLocal
from app.models.product import Product
from app.tools.billing_tools import (
    create_bill,
    add_bill_item,
    calculate_bill,
    get_bill,
    update_bill_item,
    remove_bill_item,
    finalize_bill,
)
from app.services.inventory_service import InventoryService


def run_test():
    db = SessionLocal()

    try:
        unique_id = uuid4().hex[:8]

        # Create test product
        product = Product(
            name=f"Tool Test Rice {unique_id}",
            sku=f"TOOL-RICE-{unique_id}",
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

        print(f"Product created: {product.name}")

        # ------------------------------------------------
        # 1. Create bill through TOOL
        # ------------------------------------------------

        result = create_bill()

        assert result["success"] is True

        bill_id = result["bill_id"]

        print(f"Draft bill created: {bill_id}")

        # ------------------------------------------------
        # 2. Add item through TOOL
        # ------------------------------------------------

        result = add_bill_item(
            bill_id=bill_id,
            product_id=product.id,
            quantity=2,
        )

        assert result["success"] is True

        item_id = result["item_id"]

        print(f"Item added: {item_id}")

        # ------------------------------------------------
        # 3. Calculate through TOOL
        # ------------------------------------------------

        result = calculate_bill(
            bill_id=bill_id,
        )

        assert result["success"] is True
        assert result["total"] == 236.0

        print(f"Initial total: ₹{result['total']}")

        # ------------------------------------------------
        # 4. Get current bill through TOOL
        # ------------------------------------------------

        result = get_bill(
            bill_id=bill_id,
        )

        assert result["success"] is True
        assert len(result["items"]) == 1

        print(f"Items in bill: {len(result['items'])}")

        # ------------------------------------------------
        # 5. Update quantity through TOOL
        # ------------------------------------------------

        result = update_bill_item(
            bill_id=bill_id,
            item_id=item_id,
            quantity=3,
        )

        assert result["success"] is True
        assert result["total"] == 354.0

        print(f"Updated total: ₹{result['total']}")

        # ------------------------------------------------
        # 6. Remove item through TOOL
        # ------------------------------------------------

        result = remove_bill_item(
            bill_id=bill_id,
            item_id=item_id,
        )

        assert result["success"] is True
        assert result["total"] == 0.0

        print(f"Total after removal: ₹{result['total']}")

        # ------------------------------------------------
        # 7. Add item again
        # ------------------------------------------------

        result = add_bill_item(
            bill_id=bill_id,
            product_id=product.id,
            quantity=2,
        )

        assert result["success"] is True

        # ------------------------------------------------
        # 8. Finalize through TOOL
        # ------------------------------------------------

        result = finalize_bill(
            bill_id=bill_id,
            payment_method="UPI",
            payment_reference="TOOL-UPI-001",
        )

        assert result["success"] is True
        assert result["status"] == "FINALIZED"
        assert result["payment_method"] == "UPI"
        assert result["total"] == 236.0

        print(f"Finalized bill: {bill_id}")
        print(f"Payment method: {result['payment_method']}")
        print(f"Final total: ₹{result['total']}")

        # ------------------------------------------------
        # 9. Verify stock
        # ------------------------------------------------

        db.refresh(product)

        assert product.quantity == Decimal("8")

        print(f"Final stock: {product.quantity} kg")

        print("\nBilling tool test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()