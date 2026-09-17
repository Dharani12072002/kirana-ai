from decimal import Decimal

from app.database.connection import SessionLocal
from app.models.product import Product
from app.services.inventory_service import InventoryService
from app.database.connection import SessionLocal

def main():
    db = SessionLocal()

    try:
        product = Product(
            name="Test Rice",
            sku="TEST-RICE-001",
            category="Grocery",
            unit="kg",
            cost_price=Decimal("40.00"),
            selling_price=Decimal("50.00"),
            mrp=Decimal("55.00"),
            quantity=Decimal("0"),
            reorder_level=Decimal("5"),
            gst_rate=Decimal("5.00"),
            hsn_code="1006",
        )

        db.add(product)
        db.flush()

        print(f"Product created: {product.id}")

        # Receive 10 kg
        InventoryService.receive_stock(
            db=db,
            product_id=product.id,
            quantity=Decimal("10"),
            reference="TEST-STOCK-IN",
        )

        db.commit()

        print(f"Stock after receiving: {product.quantity} kg")

        # Sell 4 kg
        InventoryService.remove_stock(
            db=db,
            product_id=product.id,
            quantity=Decimal("4"),
            reference="TEST-SALE-001",
        )

        db.commit()

        print(f"Stock after selling 4 kg: {product.quantity} kg")

        # Try to oversell
        try:
            InventoryService.remove_stock(
                db=db,
                product_id=product.id,
                quantity=Decimal("10"),
                reference="TEST-OVERSALE",
            )

            db.commit()

        except ValueError as error:
            db.rollback()
            print(f"Oversell correctly rejected: {error}")

        print(f"Final stock: {product.quantity} kg")

    finally:
        db.close()


if __name__ == "__main__":
    main()