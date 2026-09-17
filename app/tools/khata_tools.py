from app.database.connection import SessionLocal
from app.services.khata_service import KhataService
from app.database.connection import SessionLocal
from app.models.customer import Customer

def create_customer(
    name: str,
    phone: str | None = None,
) -> dict:
    """
    Create a customer for the store's Khata ledger.
    """

    db = SessionLocal()

    try:
        khata_service = KhataService()

        customer = khata_service.create_customer(
            db=db,
            name=name,
            phone=phone,
        )

        db.commit()

        return {
            "success": True,
            "customer_id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "message": f"Customer {customer.name} created.",
        }

    except ValueError as error:
        db.rollback()

        return {
            "success": False,
            "error": str(error),
        }

    except Exception as error:
        db.rollback()

        return {
            "success": False,
            "error": "Unable to create customer.",
            "details": str(error),
        }

    finally:
        db.close()


def add_credit(
    customer_id: int,
    amount: float,
    reference: str | None = None,
) -> dict:
    """
    Add a credit transaction to a customer's Khata.
    """

    db = SessionLocal()

    try:
        khata_service = KhataService()

        transaction = khata_service.add_credit(
            db=db,
            customer_id=customer_id,
            amount=amount,
            reference=reference,
        )

        db.commit()

        balance = khata_service.get_balance(
            db=db,
            customer_id=customer_id,
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "transaction_id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "amount": float(transaction.amount),
            "balance": float(balance),
            "message": (
                f"₹{transaction.amount} added to Khata. "
                f"Outstanding balance: ₹{balance}."
            ),
        }

    except ValueError as error:
        db.rollback()

        return {
            "success": False,
            "error": str(error),
        }

    except Exception as error:
        db.rollback()

        return {
            "success": False,
            "error": "Unable to add credit.",
            "details": str(error),
        }

    finally:
        db.close()


def record_khata_payment(
    customer_id: int,
    amount: float,
    reference: str | None = None,
) -> dict:
    """
    Record a payment against a customer's outstanding Khata balance.
    """

    db = SessionLocal()

    try:
        khata_service = KhataService()

        transaction = khata_service.record_payment(
            db=db,
            customer_id=customer_id,
            amount=amount,
            reference=reference,
        )

        db.commit()

        balance = khata_service.get_balance(
            db=db,
            customer_id=customer_id,
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "transaction_id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "amount": float(transaction.amount),
            "balance": float(balance),
            "message": (
                f"Payment of ₹{transaction.amount} recorded. "
                f"Outstanding balance: ₹{balance}."
            ),
        }

    except ValueError as error:
        db.rollback()

        return {
            "success": False,
            "error": str(error),
        }

    except Exception as error:
        db.rollback()

        return {
            "success": False,
            "error": "Unable to record Khata payment.",
            "details": str(error),
        }

    finally:
        db.close()


def get_khata_balance(
    customer_id: int,
) -> dict:
    """
    Get the current outstanding Khata balance.
    """

    db = SessionLocal()

    try:
        khata_service = KhataService()

        balance = khata_service.get_balance(
            db=db,
            customer_id=customer_id,
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "balance": float(balance),
            "message": f"Outstanding balance: ₹{balance}.",
        }

    except ValueError as error:
        return {
            "success": False,
            "error": str(error),
        }

    except Exception as error:
        return {
            "success": False,
            "error": "Unable to retrieve Khata balance.",
            "details": str(error),
        }

    finally:
        db.close()

def find_customer(query: str) -> dict:
    """
    Find customers by name or phone number.
    """
    db = SessionLocal()

    try:
        query = query.strip()

        if not query:
            return {
                "success": False,
                "error": "Customer name or phone number is required.",
            }

        customers = (
            db.query(Customer)
            .filter(
                (Customer.name.ilike(f"%{query}%"))
                | (Customer.phone.ilike(f"%{query}%"))
            )
            .all()
        )

        return {
            "success": True,
            "customers": [
                {
                    "id": customer.id,
                    "name": customer.name,
                    "phone": customer.phone,
                }
                for customer in customers
            ],
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    finally:
        db.close()