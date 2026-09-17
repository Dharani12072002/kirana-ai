from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.credit_transaction import CreditTransaction


class CustomerRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        customer_id: int,
    ) -> Customer | None:
        return db.get(Customer, customer_id)

    @staticmethod
    def get_by_phone(
        db: Session,
        phone: str,
    ) -> Customer | None:
        return (
            db.query(Customer)
            .filter(Customer.phone == phone)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> Customer | None:
        return (
            db.query(Customer)
            .filter(Customer.name.ilike(name))
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        name: str,
        phone: str | None = None,
    ) -> Customer:
        customer = Customer(
            name=name,
            phone=phone,
        )

        db.add(customer)
        db.flush()

        return customer

    @staticmethod
    def add_credit_transaction(
        db: Session,
        customer_id: int,
        transaction_type: str,
        amount,
        reference: str | None = None,
    ) -> CreditTransaction:

        transaction = CreditTransaction(
            customer_id=customer_id,
            transaction_type=transaction_type,
            amount=amount,
            reference=reference,
        )

        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def get_credit_transactions(
        db: Session,
        customer_id: int,
    ) -> list[CreditTransaction]:

        return (
            db.query(CreditTransaction)
            .filter(
                CreditTransaction.customer_id == customer_id
            )
            .order_by(CreditTransaction.created_at)
            .all()
        )