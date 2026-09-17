from decimal import Decimal
from uuid import uuid4

from app.database.connection import SessionLocal
from app.services.khata_service import KhataService


def run_test():
    db = SessionLocal()

    try:
        khata_service = KhataService()

        unique_id = uuid4().hex[:8]

        # Create customer
        customer = khata_service.create_customer(
            db=db,
            name=f"Ravi {unique_id}",
            phone=f"90000{unique_id[:5]}",
        )

        db.commit()
        db.refresh(customer)

        print(f"Customer created: {customer.name}")

        # Add ₹500 credit
        khata_service.add_credit(
            db=db,
            customer_id=customer.id,
            amount=Decimal("500.00"),
            reference="KHATA_TEST",
        )

        db.commit()

        balance = khata_service.get_balance(
            db=db,
            customer_id=customer.id,
        )

        assert balance == Decimal("500.00")

        print(f"After credit: ₹{balance}")

        # Customer pays ₹200
        khata_service.record_payment(
            db=db,
            customer_id=customer.id,
            amount=Decimal("200.00"),
            reference="KHATA_PAYMENT_TEST",
        )

        db.commit()

        balance = khata_service.get_balance(
            db=db,
            customer_id=customer.id,
        )

        assert balance == Decimal("300.00")

        print(f"After payment: ₹{balance}")

        # Try to pay more than outstanding balance
        try:
            khata_service.record_payment(
                db=db,
                customer_id=customer.id,
                amount=Decimal("400.00"),
                reference="INVALID_PAYMENT_TEST",
            )

            raise AssertionError(
                "Expected excessive payment to be rejected."
            )

        except ValueError as error:
            print(f"Excess payment rejected: {error}")

        # Balance must remain ₹300
        balance = khata_service.get_balance(
            db=db,
            customer_id=customer.id,
        )

        assert balance == Decimal("300.00")

        print(f"Final balance: ₹{balance}")
        print("\nKhata test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()