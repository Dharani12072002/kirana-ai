from pathlib import Path
from datetime import datetime
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.database.connection import SessionLocal
from app.models.bill import Bill
from app.models.bill_item import BillItem
from app.models.product import Product
from app.models.customer import Customer


class InvoiceService:

    def generate_invoice_pdf(self, bill_id: int) -> dict:
        """
        Generate a GST invoice PDF for a finalized bill.
        """

        db = SessionLocal()

        try:
            # -----------------------------------------------------
            # 1. Get bill
            # -----------------------------------------------------
            bill = (
                db.query(Bill)
                .filter(Bill.id == bill_id)
                .first()
            )

            if bill is None:
                return {
                    "success": False,
                    "error": f"Bill #{bill_id} not found.",
                }

            # -----------------------------------------------------
            # 2. Only finalized bills can generate invoices
            # -----------------------------------------------------
            if bill.status != "FINALIZED":
                return {
                    "success": False,
                    "error": (
                        f"Bill #{bill_id} is not finalized. "
                        "An invoice can only be generated "
                        "after finalization."
                    ),
                }

            # -----------------------------------------------------
            # 3. Get customer
            # -----------------------------------------------------
            customer = None

            if bill.customer_id is not None:
                customer = (
                    db.query(Customer)
                    .filter(Customer.id == bill.customer_id)
                    .first()
                )

            # -----------------------------------------------------
            # 4. Get bill items
            # -----------------------------------------------------
            items = (
                db.query(BillItem)
                .filter(BillItem.bill_id == bill_id)
                .all()
            )

            if not items:
                return {
                    "success": False,
                    "error": (
                        f"Bill #{bill_id} does not contain "
                        "any items."
                    ),
                }

            # -----------------------------------------------------
            # 5. Output directory
            # -----------------------------------------------------
            output_directory = Path(
                "generated",
                "invoices",
            )

            output_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path = (
                output_directory
                / f"invoice_bill_{bill_id}.pdf"
            )

            # -----------------------------------------------------
            # 6. PDF document
            # -----------------------------------------------------
            document = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=15 * mm,
                leftMargin=15 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm,
            )

            styles = getSampleStyleSheet()

            title_style = styles["Title"]
            heading_style = styles["Heading2"]
            normal_style = styles["Normal"]

            story = []

            # -----------------------------------------------------
            # 7. Header
            # -----------------------------------------------------
            story.append(
                Paragraph(
                    "KIRANAAI",
                    title_style,
                )
            )

            story.append(
                Paragraph(
                    "GST TAX INVOICE",
                    heading_style,
                )
            )

            story.append(Spacer(1, 8))

            # -----------------------------------------------------
            # 8. Invoice information
            # -----------------------------------------------------
            invoice_date = (
                bill.finalized_at
                or bill.created_at
                or datetime.utcnow()
            )

            customer_name = (
                customer.name
                if customer
                else "Walk-in Customer"
            )

            customer_phone = (
                customer.phone
                if customer
                else "N/A"
            )

            invoice_info = [
                [
                    Paragraph(
                        f"<b>Invoice No:</b> {bill.id}",
                        normal_style,
                    ),
                    Paragraph(
                        "<b>Payment:</b> "
                        f"{bill.payment_method or 'N/A'}",
                        normal_style,
                    ),
                ],
                [
                    Paragraph(
                        "<b>Date:</b> "
                        f"{invoice_date.strftime('%d-%m-%Y %H:%M')}",
                        normal_style,
                    ),
                    Paragraph(
                        "<b>Payment Reference:</b> "
                        f"{bill.payment_reference or 'N/A'}",
                        normal_style,
                    ),
                ],
                [
                    Paragraph(
                        f"<b>Customer:</b> {customer_name}",
                        normal_style,
                    ),
                    Paragraph(
                        f"<b>Phone:</b> {customer_phone}",
                        normal_style,
                    ),
                ],
            ]

            invoice_info_table = Table(
                invoice_info,
                colWidths=[90 * mm, 90 * mm],
            )

            invoice_info_table.setStyle(
                TableStyle(
                    [
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            story.append(invoice_info_table)
            story.append(Spacer(1, 8))

            # -----------------------------------------------------
            # 9. Item table
            # -----------------------------------------------------
            table_data = [
                [
                    "Item",
                    "SKU",
                    "Qty",
                    "Rate",
                    "GST",
                    "Taxable",
                    "CGST",
                    "SGST",
                    "Total",
                ]
            ]

            for item in items:

                product = (
                    db.query(Product)
                    .filter(Product.id == item.product_id)
                    .first()
                )

                product_name = (
                    product.name
                    if product
                    else "Unknown Product"
                )

                sku = (
                    product.sku
                    if product
                    else "N/A"
                )

                table_data.append(
                    [
                        product_name,
                        sku,
                        f"{item.quantity}",
                        f"₹{item.unit_price:.2f}",
                        f"{item.gst_rate}%",
                        f"₹{item.taxable_amount:.2f}",
                        f"₹{item.cgst_amount:.2f}",
                        f"₹{item.sgst_amount:.2f}",
                        f"₹{item.total_amount:.2f}",
                    ]
                )

            item_table = Table(
                table_data,
                repeatRows=1,
                colWidths=[
                    30 * mm,
                    22 * mm,
                    13 * mm,
                    18 * mm,
                    13 * mm,
                    22 * mm,
                    18 * mm,
                    18 * mm,
                    22 * mm,
                ],
            )

            item_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.black,
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "ALIGN",
                            (2, 1),
                            (-1, -1),
                            "RIGHT",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                    ]
                )
            )

            story.append(item_table)
            story.append(Spacer(1, 12))
            # -----------------------------------------------------
            # 10. Tax and total summary
            # -----------------------------------------------------

            cgst_value = Decimal(str(bill.cgst or 0))
            sgst_value = Decimal(str(bill.sgst or 0))

            total_tax = cgst_value + sgst_value

            summary_data = [
                [
                    "Subtotal",
                    f"₹{Decimal(str(bill.subtotal or 0)):.2f}",
                ],
                [
                    "CGST",
                    f"₹{cgst_value:.2f}",
                ],
                [
                    "SGST",
                    f"₹{sgst_value:.2f}",
                ],
                [
                    "Total Tax",
                    f"₹{total_tax:.2f}",
                ],
                [
                    "TOTAL",
                    f"₹{Decimal(str(bill.total or 0)):.2f}",
                ],
            ]

            summary_table = Table(
                summary_data,
                colWidths=[
                    130 * mm,
                    40 * mm,
                ],
                hAlign="RIGHT",
            )

            summary_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "ALIGN",
                            (1, 0),
                            (1, -1),
                            "RIGHT",
                        ),
                        (
                            "FONTNAME",
                            (0, -1),
                            (-1, -1),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            9,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            story.append(summary_table)
            story.append(Spacer(1, 15))

            # -----------------------------------------------------
            # 11. Footer
            # -----------------------------------------------------
            story.append(
                Paragraph(
                    "Thank you for shopping with KiranaAI.",
                    normal_style,
                )
            )

            story.append(
                Paragraph(
                    "This invoice was generated from the "
                    "store's finalized billing records.",
                    normal_style,
                )
            )

            # -----------------------------------------------------
            # 12. Build PDF
            # -----------------------------------------------------
            document.build(story)

            return {
                "success": True,
                "bill_id": bill_id,
                "file_path": str(output_path),
                "customer_name": customer_name,
                "total": float(bill.total or 0),
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

        finally:
            db.close()