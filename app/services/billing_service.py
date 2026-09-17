from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.product import Product
from app.repositories.billing_repository import BillingRepository
from app.services.inventory_service import InventoryService
from app.models.payment import Payment
from app.services.khata_service import KhataService

class BillingService:

    def __init__(self):
        self.billing_repository = BillingRepository()

    def create_draft(
        self,
        db: Session,
        customer_id: int | None = None,
        idempotency_key: str | None = None,
    ) -> Bill:

        return self.billing_repository.create_bill(
            db=db,
            customer_id=customer_id,
            idempotency_key=idempotency_key,
        )

    def add_item(
        self,
        db: Session,
        bill_id: int,
        product_id: int,
        quantity: Decimal,
    ):

        bill = self.billing_repository.get_bill(
            db=db,
            bill_id=bill_id,
        )

        if bill is None:
            raise ValueError("Bill not found.")

        if bill.status != "DRAFT":
            raise ValueError("Only draft bills can be modified.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        product = db.get(Product, product_id)

        if product is None:
            raise ValueError("Product not found.")

        if product.quantity < quantity:
            raise ValueError(
                f"Insufficient stock. "
                f"Available: {product.quantity} {product.unit}."
            )

        unit_price = Decimal(str(product.selling_price))
        cost_price = Decimal(str(product.cost_price))
        gst_rate = Decimal(str(product.gst_rate))

        taxable_amount = (
            unit_price * quantity
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        gst_amount = (
            taxable_amount * gst_rate / Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        cgst_amount = (
            gst_amount / Decimal("2")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        sgst_amount = (
            gst_amount - cgst_amount
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        total_amount = taxable_amount + gst_amount

        return self.billing_repository.add_item(
            db=db,
            bill_id=bill_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            cost_price=cost_price,
            gst_rate=gst_rate,
            hsn_code=product.hsn_code,
            taxable_amount=taxable_amount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            total_amount=total_amount,
        )

    def calculate_bill(self, db, bill_id):
        bill = self.billing_repository.get_bill(db, bill_id)

        if bill is None:
            raise ValueError("Bill not found.")

        if bill.status != "DRAFT":
            raise ValueError("Only draft bills can be calculated.")

        items = self.billing_repository.get_bill_items(db, bill_id)

        subtotal = Decimal("0.00")
        cgst = Decimal("0.00")
        sgst = Decimal("0.00")

        for item in items:
            subtotal += Decimal(str(item.taxable_amount))
            cgst += Decimal(str(item.cgst_amount))
            sgst += Decimal(str(item.sgst_amount))

        total = subtotal + cgst + sgst

        return self.billing_repository.update_bill_totals(
            db=db,
            bill_id=bill_id,
            subtotal=subtotal,
            cgst=cgst,
            sgst=sgst,
            total=total,
        )

    def finalize_bill(
        self,
        db: Session,
        bill_id: int,
        payment_method: str,
        payment_reference: str | None = None,
    ) -> Bill:

        bill = self.billing_repository.get_bill(db, bill_id)

        if bill is None:
            raise ValueError("Bill not found.")

        if bill.status != "DRAFT":
            raise ValueError("Only draft bills can be finalized.")

        items = self.billing_repository.get_bill_items(db, bill_id)

        if not items:
            raise ValueError("Cannot finalize an empty bill.")

        payment_method = payment_method.upper().strip()

        allowed_methods = {"CASH", "UPI", "CARD", "CREDIT"}

        if payment_method not in allowed_methods:
            raise ValueError(
                "Invalid payment method. "
                "Use CASH, UPI, CARD, or CREDIT."
            )

        # CREDIT requires a customer
        if payment_method == "CREDIT" and bill.customer_id is None:
            raise ValueError(
                "Customer is required for credit billing."
            )

        # Recalculate totals before finalization
        bill = self.calculate_bill(db, bill_id)

        # Deduct stock and create SALE transactions
        for item in items:
            InventoryService.remove_stock(
                db=db,
                product_id=item.product_id,
                quantity=Decimal(str(item.quantity)),
                reference=f"BILL-{bill_id}",
            )

        # Record payment
        payment = Payment(
            bill_id=bill_id,
            method=payment_method,
            amount=Decimal(str(bill.total)),
            reference=payment_reference,
        )

        db.add(payment)

        # If this is a credit sale, add the amount to Khata
        if payment_method == "CREDIT":
            khata_service = KhataService()

            khata_service.add_credit(
                db=db,
                customer_id=bill.customer_id,
                amount=Decimal(str(bill.total)),
                reference=f"BILL-{bill_id}",
            )

        # Mark bill as finalized
        bill = self.billing_repository.finalize_bill(
            db=db,
            bill_id=bill_id,
            payment_method=payment_method,
            payment_reference=payment_reference,
        )

        return bill
    
    def update_item_quantity(
        self,
        db: Session,
        bill_id: int,
        item_id: int,
        quantity,
    ):
        bill = self.billing_repository.get_bill(db, bill_id)

        if bill is None:
            raise ValueError("Bill not found.")

        if bill.status != "DRAFT":
            raise ValueError("Only draft bills can be modified.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        item = self.billing_repository.get_bill_item(
            db=db,
            bill_id=bill_id,
            item_id=item_id,
        )

        if item is None:
            raise ValueError("Bill item not found.")

        product = db.get(Product, item.product_id)

        if product is None:
            raise ValueError("Product not found.")

        if product.quantity < quantity:
            raise ValueError(
                f"Insufficient stock. Available: "
                f"{product.quantity} {product.unit}."
            )

        # Recalculate the item using authoritative product data
        unit_price = Decimal(str(product.selling_price))
        cost_price = Decimal(str(product.cost_price))
        gst_rate = Decimal(str(product.gst_rate))

        taxable_amount = (
            unit_price * quantity
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        gst_amount = (
            taxable_amount * gst_rate / Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        cgst_amount = (
            gst_amount / Decimal("2")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        sgst_amount = (
            gst_amount - cgst_amount
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        total_amount = taxable_amount + gst_amount

        item.quantity = quantity
        item.unit_price = unit_price
        item.cost_price = cost_price
        item.gst_rate = gst_rate
        item.hsn_code = product.hsn_code
        item.taxable_amount = taxable_amount
        item.cgst_amount = cgst_amount
        item.sgst_amount = sgst_amount
        item.total_amount = total_amount

        db.flush()

        return self.calculate_bill(db, bill_id)

    def remove_item(
        self,
        db: Session,
        bill_id: int,
        item_id: int,
    ):
        bill = self.billing_repository.get_bill(db, bill_id)

        if bill is None:
            raise ValueError("Bill not found.")

        if bill.status != "DRAFT":
            raise ValueError("Only draft bills can be modified.")

        item = self.billing_repository.get_bill_item(
            db=db,
            bill_id=bill_id,
            item_id=item_id,
        )

        if item is None:
            raise ValueError("Bill item not found.")

        self.billing_repository.delete_bill_item(
            db=db,
            item_id=item_id,
        )

        return self.calculate_bill(db, bill_id)