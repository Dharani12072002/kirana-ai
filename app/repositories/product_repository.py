from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Product | None:
        return db.get(Product, product_id)

    @staticmethod
    def get_by_sku(db: Session, sku: str) -> Product | None:
        statement = select(Product).where(Product.sku == sku)
        return db.scalar(statement)

    @staticmethod
    def get_by_name(db: Session, name: str) -> Product | None:
        statement = select(Product).where(Product.name == name)
        return db.scalar(statement)

    @staticmethod
    def create(
        db: Session,
        *,
        name: str,
        sku: str,
        unit: str,
        cost_price: Decimal,
        selling_price: Decimal,
        gst_rate: Decimal,
        category: str | None = None,
        mrp: Decimal | None = None,
        reorder_level: Decimal = Decimal("0"),
        hsn_code: str | None = None,
    ) -> Product:

        product = Product(
            name=name,
            sku=sku,
            category=category,
            unit=unit,
            cost_price=cost_price,
            selling_price=selling_price,
            mrp=mrp,
            quantity=Decimal("0"),
            reorder_level=reorder_level,
            gst_rate=gst_rate,
            hsn_code=hsn_code,
        )

        db.add(product)
        db.flush()

        return product

    @staticmethod
    def increase_stock(
        db: Session,
        product_id: int,
        quantity: Decimal,
    ) -> Product:
        if quantity <= 0:
            raise ValueError("Stock quantity must be greater than zero.")

        product = db.get(Product, product_id)

        if product is None:
            raise ValueError("Product not found.")

        product.quantity += quantity
        db.flush()

        return product

    @staticmethod
    def decrease_stock(
        db: Session,
        product_id: int,
        quantity: Decimal,
    ) -> Product:
        if quantity <= 0:
            raise ValueError("Stock quantity must be greater than zero.")

        statement = (
            update(Product)
            .where(
                Product.id == product_id,
                Product.quantity >= quantity,
            )
            .values(quantity=Product.quantity - quantity)
        )

        result = db.execute(statement)

        if result.rowcount == 0:
            product = db.get(Product, product_id)

            if product is None:
                raise ValueError("Product not found.")

            raise ValueError(
                f"Insufficient stock. Available: {product.quantity}"
            )

        db.flush()

        product = db.get(Product, product_id)
        return product