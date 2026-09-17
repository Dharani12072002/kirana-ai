from app.database.connection import SessionLocal
from app.services.billing_service import BillingService
from app.models.product import Product
from app.services.preference_service import PreferenceService


def create_bill(customer_id: int | None = None) -> dict:
    """
    Create a new draft bill.

    Args:
        customer_id: Optional customer ID. Required when the bill
                     may later be finalized as CREDIT.
    """

    db = SessionLocal()

    try:
        billing_service = BillingService()

        bill = billing_service.create_draft(
            db=db,
            customer_id=customer_id,
        )

        db.commit()

        return {
            "success": True,
            "bill_id": bill.id,
            "customer_id": bill.customer_id,
            "status": bill.status,
            "message": f"Draft bill {bill.id} created.",
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
            "error": "Unable to create bill.",
            "details": str(error),
        }

    finally:
        db.close()

def add_bill_item(
    bill_id: int,
    product_id: int,
    quantity: float,
) -> dict:
    """
    Add a product to an existing draft bill.

    Stock is only checked here.
    Stock is NOT deducted until the bill is finalized.
    """

    db = SessionLocal()

    try:
        billing_service = BillingService()

        item = billing_service.add_item(
            db=db,
            bill_id=bill_id,
            product_id=product_id,
            quantity=quantity,
        )

        db.commit()

        return {
            "success": True,
            "bill_id": bill_id,
            "item_id": item.id,
            "product_id": item.product_id,
            "quantity": float(item.quantity),
            "unit_price": float(item.unit_price),
            "gst_rate": float(item.gst_rate),
            "total_amount": float(item.total_amount),
            "message": (
                f"Added {item.quantity} units of product "
                f"{item.product_id} to bill {bill_id}."
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
            "error": "Unable to add item to bill.",
            "details": str(error),
        }

    finally:
        db.close()

def calculate_bill(bill_id: int) -> dict:
    """
    Calculate the current totals of a draft bill.

    The billing service is the source of truth for
    subtotal, CGST, SGST, and total.
    """

    db = SessionLocal()

    try:
        billing_service = BillingService()

        bill = billing_service.calculate_bill(
            db=db,
            bill_id=bill_id,
        )

        db.commit()

        return {
            "success": True,
            "bill_id": bill.id,
            "status": bill.status,
            "subtotal": float(bill.subtotal),
            "cgst": float(bill.cgst),
            "sgst": float(bill.sgst),
            "total": float(bill.total),
            "message": (
                f"Bill {bill.id} total is ₹{bill.total}."
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
            "error": "Unable to calculate bill.",
            "details": str(error),
        }

    finally:
        db.close()

def update_bill_item(
    bill_id: int,
    item_id: int,
    quantity: float,
) -> dict:
    """
    Change the quantity of an item in a draft bill.
    """

    db = SessionLocal()

    try:
        billing_service = BillingService()

        bill = billing_service.update_item_quantity(
            db=db,
            bill_id=bill_id,
            item_id=item_id,
            quantity=quantity,
        )

        db.commit()

        return {
            "success": True,
            "bill_id": bill.id,
            "item_id": item_id,
            "quantity": quantity,
            "subtotal": float(bill.subtotal),
            "cgst": float(bill.cgst),
            "sgst": float(bill.sgst),
            "total": float(bill.total),
            "message": (
                f"Updated item {item_id} in bill {bill_id}. "
                f"New total is ₹{bill.total}."
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
            "error": "Unable to update bill item.",
            "details": str(error),
        }

    finally:
        db.close()

def remove_bill_item(
    bill_id: int,
    item_id: int,
) -> dict:
    """
    Remove an item from a draft bill.
    """

    db = SessionLocal()

    try:
        billing_service = BillingService()

        bill = billing_service.remove_item(
            db=db,
            bill_id=bill_id,
            item_id=item_id,
        )

        db.commit()

        return {
            "success": True,
            "bill_id": bill.id,
            "removed_item_id": item_id,
            "subtotal": float(bill.subtotal),
            "cgst": float(bill.cgst),
            "sgst": float(bill.sgst),
            "total": float(bill.total),
            "message": (
                f"Removed item {item_id} from bill {bill_id}. "
                f"New total is ₹{bill.total}."
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
            "error": "Unable to remove bill item.",
            "details": str(error),
        }

    finally:
        db.close()

def get_bill(bill_id: int) -> dict:
    """
    Retrieve the current state of a bill and its items.
    """

    db = SessionLocal()

    try:
        billing_service = BillingService()

        bill = billing_service.billing_repository.get_bill(
            db=db,
            bill_id=bill_id,
        )

        if bill is None:
            return {
                "success": False,
                "error": "Bill not found.",
            }

        items = (
            billing_service.billing_repository.get_bill_items(
                db=db,
                bill_id=bill_id,
            )
        )

        bill_items = []

        for item in items:

            product = db.get(
                Product,
                item.product_id,
            )

            bill_items.append(
                {
                    "item_id": item.id,
                    "product_id": item.product_id,
                    "product_name": (
                        product.name
                        if product
                        else "Unknown product"
                    ),
                    "unit": (
                        product.unit
                        if product
                        else ""
                    ),
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "gst_rate": float(item.gst_rate),
                    "taxable_amount": float(
                        item.taxable_amount
                    ),
                    "cgst_amount": float(
                        item.cgst_amount
                    ),
                    "sgst_amount": float(
                        item.sgst_amount
                    ),
                    "total_amount": float(
                        item.total_amount
                    ),
                }
            )

        return {
            "success": True,
            "bill_id": bill.id,
            "customer_id": bill.customer_id,
            "status": bill.status,
            "items": bill_items,
            "subtotal": float(bill.subtotal),
            "cgst": float(bill.cgst),
            "sgst": float(bill.sgst),
            "total": float(bill.total),
        }

    except Exception as error:
        return {
            "success": False,
            "error": "Unable to retrieve bill.",
            "details": str(error),
        }

    finally:
        db.close()

def finalize_bill(
    bill_id: int,
    payment_method: str | None = None,
    payment_reference: str | None = None,
) -> dict:
    """
    Finalize a draft bill.

    If payment_method is not explicitly provided, use the
    persistent default payment method configured by the
    store owner.
    """

    # Resolve payment method from persistent preference
    # when the agent does not provide one explicitly.
    if payment_method is None:
        preference_service = PreferenceService()

        preference_result = preference_service.get_preference(
            key="default_payment_method"
        )

        if not preference_result.get("success"):
            return {
                "success": False,
                "error": (
                    "No payment method was provided and no "
                    "default payment method is configured."
                ),
            }

        payment_method = preference_result["value"]

    # Normalize the payment method.
    payment_method = payment_method.strip().upper()

    # Validate the resolved payment method.
    allowed_methods = {
        "CASH",
        "UPI",
        "CARD",
        "CREDIT",
    }

    if payment_method not in allowed_methods:
        return {
            "success": False,
            "error": (
                f"Invalid payment method '{payment_method}'. "
                "Allowed methods are CASH, UPI, CARD, or CREDIT."
            ),
        }

    # Create database session.
    db = SessionLocal()

    try:
        service = BillingService()

        bill = service.finalize_bill(
            db=db,
            bill_id=bill_id,
            payment_method=payment_method,
            payment_reference=payment_reference,
        )

        # BillingService returns a Bill SQLAlchemy object.
        db.commit()

        return {
            "success": True,
            "bill_id": bill.id,
            "status": bill.status,
            "payment_method": bill.payment_method,
            "payment_reference": bill.payment_reference,
            "subtotal": float(bill.subtotal or 0),
            "cgst": float(bill.cgst or 0),
            "sgst": float(bill.sgst or 0),
            "total": float(bill.total or 0),
            "message": (
                f"Bill #{bill.id} finalized successfully "
                f"using {bill.payment_method}."
            ),
        }

    except Exception as error:
        db.rollback()

        return {
            "success": False,
            "error": str(error),
        }

    finally:
        db.close()