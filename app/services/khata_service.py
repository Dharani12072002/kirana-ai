from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository


class KhataService:

    def __init__(self):
        self.customer_repository = CustomerRepository()

    def create_customer(
        self,
        db: Session,
        name: str,
        phone: str | None = None,
    ) -> Customer:

        name = name.strip()

        if not name:
            raise ValueError("Customer name is required.")

        if phone:
            existing_customer = (
                self.customer_repository.get_by_phone(
                    db=db,
                    phone=phone,
                )
            )

            if existing_customer:
                raise ValueError(
                    "A customer with this phone number already exists."
                )

        return self.customer_repository.create(
            db=db,
            name=name,
            phone=phone,
        )

    def add_credit(
        self,
        db: Session,
        customer_id: int,
        amount,
        reference: str | None = None,
    ):

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError("Credit amount must be greater than zero.")

        customer = self.customer_repository.get_by_id(
            db=db,
            customer_id=customer_id,
        )

        if customer is None:
            raise ValueError("Customer not found.")

        transaction = (
            self.customer_repository.add_credit_transaction(
                db=db,
                customer_id=customer_id,
                transaction_type="CREDIT",
                amount=amount,
                reference=reference,
            )
        )

        return transaction

    def record_payment(
        self,
        db: Session,
        customer_id: int,
        amount,
        reference: str | None = None,
    ):

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero."
            )

        customer = self.customer_repository.get_by_id(
            db=db,
            customer_id=customer_id,
        )

        if customer is None:
            raise ValueError("Customer not found.")

        balance = self.get_balance(
            db=db,
            customer_id=customer_id,
        )

        if amount > balance:
            raise ValueError(
                f"Payment exceeds outstanding balance of ₹{balance}."
            )

        transaction = (
            self.customer_repository.add_credit_transaction(
                db=db,
                customer_id=customer_id,
                transaction_type="PAYMENT",
                amount=amount,
                reference=reference,
            )
        )

        return transaction

    def get_balance(
        self,
        db: Session,
        customer_id: int,
    ) -> Decimal:

        customer = self.customer_repository.get_by_id(
            db=db,
            customer_id=customer_id,
        )

        if customer is None:
            raise ValueError("Customer not found.")

        transactions = (
            self.customer_repository.get_credit_transactions(
                db=db,
                customer_id=customer_id,
            )
        )

        balance = Decimal("0.00")

        for transaction in transactions:
            amount = Decimal(str(transaction.amount))

            if transaction.transaction_type == "CREDIT":
                balance += amount

            elif transaction.transaction_type == "PAYMENT":
                balance -= amount

        return balance.quantize(Decimal("0.01"))