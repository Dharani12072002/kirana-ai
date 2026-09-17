from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.stock_transaction import StockTransaction
from app.repositories.product_repository import ProductRepository


class InventoryService:

    @staticmethod
    def receive_stock(
        db: Session,
        product_id: int,
        quantity: Decimal,
        reference: str | None = None,
    ):
        if quantity <= 0:
            raise ValueError("Received quantity must be greater than zero.")

        product = ProductRepository.get_by_id(db, product_id)

        if product is None:
            raise ValueError("Product not found.")

        product = ProductRepository.increase_stock(
            db=db,
            product_id=product_id,
            quantity=quantity,
        )

        transaction = StockTransaction(
            product_id=product_id,
            transaction_type="STOCK_IN",
            quantity=quantity,
            reference=reference,
        )

        db.add(transaction)
        db.flush()

        return product

    @staticmethod
    def remove_stock(
        db: Session,
        product_id: int,
        quantity: Decimal,
        reference: str | None = None,
    ):
        if quantity <= 0:
            raise ValueError("Removed quantity must be greater than zero.")

        product = ProductRepository.get_by_id(db, product_id)

        if product is None:
            raise ValueError("Product not found.")

        product = ProductRepository.decrease_stock(
            db=db,
            product_id=product_id,
            quantity=quantity,
        )

        transaction = StockTransaction(
            product_id=product_id,
            transaction_type="SALE",
            quantity=-quantity,
            reference=reference,
        )

        db.add(transaction)
        db.flush()

        return product