from decimal import Decimal

from app.database.connection import SessionLocal
from app.models.product import Product
from app.services.inventory_service import InventoryService


def receive_stock(
    product_id: int,
    quantity: float,
    reference: str | None = None,
) -> dict:
    """
    Receive stock for an existing product.
    """

    db = SessionLocal()

    try:
        product = db.get(Product, product_id)

        if product is None:
            return {
                "success": False,
                "error": "Product not found.",
            }

        updated_product = InventoryService.receive_stock(
            db=db,
            product_id=product_id,
            quantity=Decimal(str(quantity)),
            reference=reference,
        )

        db.commit()

        return {
            "success": True,
            "product_id": updated_product.id,
            "product_name": updated_product.name,
            "quantity_received": quantity,
            "current_stock": float(updated_product.quantity),
            "unit": updated_product.unit,
        }

    except ValueError as error:
        db.rollback()

        return {
            "success": False,
            "error": str(error),
        }

    except Exception:
        db.rollback()

        return {
            "success": False,
            "error": "Unable to receive stock.",
        }

    finally:
        db.close()


def get_stock(product_id: int) -> dict:
    """
    Get the current stock level of a product.
    """

    db = SessionLocal()

    try:
        product = db.get(Product, product_id)

        if product is None:
            return {
                "success": False,
                "error": "Product not found.",
            }

        return {
            "success": True,
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": float(product.quantity),
            "unit": product.unit,
            "reorder_level": float(product.reorder_level),
            "low_stock": product.quantity <= product.reorder_level,
        }

    finally:
        db.close()

def get_low_stock() -> dict:
    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.quantity <= Product.reorder_level)
            .all()
        )

        return {
            "success": True,
            "count": len(products),
            "products": [
                {
                    "product_id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "current_stock": float(product.quantity),
                    "reorder_level": float(product.reorder_level),
                    "unit": product.unit,
                }
                for product in products
            ],
        }

    finally:
        db.close()

def search_products(query: str) -> dict:
    """
    Search products by name or SKU.
    """

    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(
                (Product.name.ilike(f"%{query}%"))
                | (Product.sku.ilike(f"%{query}%"))
            )
            .all()
        )

        return {
            "success": True,
            "query": query,
            "count": len(products),
            "products": [
                {
                    "product_id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "unit": product.unit,
                    "current_stock": float(product.quantity),
                    "selling_price": float(product.selling_price),
                    "gst_rate": float(product.gst_rate),
                }
                for product in products
            ],
        }

    finally:
        db.close()

def add_product(
    name: str,
    sku: str,
    unit: str,
    cost_price: float,
    selling_price: float,
    gst_rate: float,
    category: str | None = None,
    mrp: float | None = None,
    reorder_level: float = 0,
    hsn_code: str | None = None,
) -> dict:
    """
    Add a new product to the store inventory.
    """

    db = SessionLocal()

    try:
        existing = (
            db.query(Product)
            .filter(
                (Product.sku == sku)
                | (Product.name.ilike(name))
            )
            .first()
        )

        if existing:
            return {
                "success": False,
                "error": "A product with this name or SKU already exists.",
                "existing_product_id": existing.id,
            }

        product = Product(
            name=name,
            sku=sku,
            category=category,
            unit=unit,
            cost_price=Decimal(str(cost_price)),
            selling_price=Decimal(str(selling_price)),
            mrp=Decimal(str(mrp)) if mrp is not None else None,
            quantity=Decimal("0"),
            reorder_level=Decimal(str(reorder_level)),
            gst_rate=Decimal(str(gst_rate)),
            hsn_code=hsn_code,
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return {
            "success": True,
            "product_id": product.id,
            "name": product.name,
            "sku": product.sku,
            "unit": product.unit,
            "selling_price": float(product.selling_price),
            "gst_rate": float(product.gst_rate),
            "current_stock": float(product.quantity),
        }

    except Exception as error:
        db.rollback()

        return {
            "success": False,
            "error": str(error),
        }

    finally:
        db.close()