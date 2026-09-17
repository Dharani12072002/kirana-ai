from datetime import datetime, timedelta

from sqlalchemy import func

from app.models.bill import Bill
from app.models.bill_item import BillItem
from app.models.product import Product


class AnalyticsRepository:

    def get_daily_sales(self, db, target_date=None):
        """
        Return sales summary for a specific date.

        Only FINALIZED bills are included.
        """

        if target_date is None:
            target_date = datetime.now().date()

        start_datetime = datetime.combine(
            target_date,
            datetime.min.time(),
        )

        end_datetime = start_datetime + timedelta(days=1)

        # ---------------------------------------------------------
        # Overall sales summary
        # ---------------------------------------------------------
        summary = (
            db.query(
                func.count(Bill.id).label("bill_count"),
                func.coalesce(
                    func.sum(Bill.subtotal),
                    0,
                ).label("subtotal"),
                func.coalesce(
                    func.sum(Bill.cgst),
                    0,
                ).label("cgst"),
                func.coalesce(
                    func.sum(Bill.sgst),
                    0,
                ).label("sgst"),
                func.coalesce(
                    func.sum(Bill.total),
                    0,
                ).label("total"),
            )
            .filter(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start_datetime,
                Bill.finalized_at < end_datetime,
            )
            .first()
        )

        # ---------------------------------------------------------
        # Sales grouped by payment method
        # ---------------------------------------------------------
        payment_rows = (
            db.query(
                Bill.payment_method,
                func.coalesce(
                    func.sum(Bill.total),
                    0,
                ).label("amount"),
            )
            .filter(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start_datetime,
                Bill.finalized_at < end_datetime,
            )
            .group_by(Bill.payment_method)
            .all()
        )

        payment_summary = {
            "CASH": 0,
            "UPI": 0,
            "CARD": 0,
            "CREDIT": 0,
        }

        for row in payment_rows:
            if row.payment_method:
                payment_summary[row.payment_method] = float(
                    row.amount or 0
                )

        # ---------------------------------------------------------
        # Top-selling products
        # ---------------------------------------------------------
        top_products = (
            db.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.unit.label("unit"),
                func.sum(BillItem.quantity).label("quantity_sold"),
                func.sum(BillItem.total_amount).label(
                    "sales_amount"
                ),
            )
            .join(
                BillItem,
                BillItem.product_id == Product.id,
            )
            .join(
                Bill,
                Bill.id == BillItem.bill_id,
            )
            .filter(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start_datetime,
                Bill.finalized_at < end_datetime,
            )
            .group_by(
                Product.id,
                Product.name,
                Product.unit,
            )
            .order_by(
                func.sum(BillItem.quantity).desc()
            )
            .limit(5)
            .all()
        )

        products = []

        for row in top_products:
            products.append(
                {
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "unit": row.unit,
                    "quantity_sold": float(
                        row.quantity_sold or 0
                    ),
                    "sales_amount": float(
                        row.sales_amount or 0
                    ),
                }
            )

        return {
            "date": target_date.isoformat(),
            "bill_count": int(summary.bill_count or 0),
            "subtotal": float(summary.subtotal or 0),
            "cgst": float(summary.cgst or 0),
            "sgst": float(summary.sgst or 0),
            "tax_collected": float(
                (summary.cgst or 0) + (summary.sgst or 0)
            ),
            "total_sales": float(summary.total or 0),
            "payment_methods": payment_summary,
            "top_products": products,
        }

    def get_sales_analysis_data(self, db, start_date, end_date):
        """
        Get sales analysis data between two dates.

        Only finalized bills are included.
        """

        start_datetime = datetime.combine(
            start_date,
            datetime.min.time(),
        )

        end_datetime = datetime.combine(
            end_date,
            datetime.max.time(),
        )

        # ---------------------------------------------------------
        # 1. Sales by date
        # ---------------------------------------------------------
        daily_sales_rows = (
            db.query(
                func.date(Bill.finalized_at).label("sale_date"),
                func.count(Bill.id).label("bill_count"),
                func.coalesce(
                    func.sum(Bill.total),
                    0,
                ).label("sales"),
            )
            .filter(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start_datetime,
                Bill.finalized_at <= end_datetime,
            )
            .group_by(
                func.date(Bill.finalized_at)
            )
            .order_by(
                func.date(Bill.finalized_at)
            )
            .all()
        )

        daily_sales = []

        for row in daily_sales_rows:
            daily_sales.append(
                {
                    "date": str(row.sale_date),
                    "bill_count": int(row.bill_count or 0),
                    "sales": float(row.sales or 0),
                }
            )

        # ---------------------------------------------------------
        # 2. Payment method breakdown
        # ---------------------------------------------------------
        payment_rows = (
            db.query(
                Bill.payment_method,
                func.coalesce(
                    func.sum(Bill.total),
                    0,
                ).label("amount"),
            )
            .filter(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start_datetime,
                Bill.finalized_at <= end_datetime,
            )
            .group_by(
                Bill.payment_method
            )
            .all()
        )

        payment_methods = {}

        for row in payment_rows:
            payment_methods[row.payment_method or "UNKNOWN"] = float(
                row.amount or 0
            )

        # ---------------------------------------------------------
        # 3. Top-selling products
        # ---------------------------------------------------------
        product_rows = (
            db.query(
                Product.name.label("product_name"),
                Product.unit.label("unit"),
                func.sum(
                    BillItem.quantity
                ).label("quantity_sold"),
                func.sum(
                    BillItem.total_amount
                ).label("sales_amount"),
            )
            .join(
                BillItem,
                BillItem.product_id == Product.id,
            )
            .join(
                Bill,
                Bill.id == BillItem.bill_id,
            )
            .filter(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start_datetime,
                Bill.finalized_at <= end_datetime,
            )
            .group_by(
                Product.id,
                Product.name,
                Product.unit,
            )
            .order_by(
                func.sum(
                    BillItem.quantity
                ).desc()
            )
            .limit(10)
            .all()
        )

        top_products = []

        for row in product_rows:
            top_products.append(
                {
                    "product_name": row.product_name,
                    "unit": row.unit,
                    "quantity_sold": float(
                        row.quantity_sold or 0
                    ),
                    "sales_amount": float(
                        row.sales_amount or 0
                    ),
                }
            )

        # ---------------------------------------------------------
        # 4. Overall summary
        # ---------------------------------------------------------
        summary = (
            db.query(
                func.count(Bill.id).label("bill_count"),
                func.coalesce(
                    func.sum(Bill.subtotal),
                    0,
                ).label("subtotal"),
                func.coalesce(
                    func.sum(Bill.cgst),
                    0,
                ).label("cgst"),
                func.coalesce(
                    func.sum(Bill.sgst),
                    0,
                ).label("sgst"),
                func.coalesce(
                    func.sum(Bill.total),
                    0,
                ).label("total_sales"),
            )
            .filter(
                Bill.status == "FINALIZED",
                Bill.finalized_at >= start_datetime,
                Bill.finalized_at <= end_datetime,
            )
            .first()
        )

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),

            "summary": {
                "bill_count": int(
                    summary.bill_count or 0
                ),
                "subtotal": float(
                    summary.subtotal or 0
                ),
                "cgst": float(
                    summary.cgst or 0
                ),
                "sgst": float(
                    summary.sgst or 0
                ),
                "tax_collected": float(
                    (summary.cgst or 0)
                    + (summary.sgst or 0)
                ),
                "total_sales": float(
                    summary.total_sales or 0
                ),
            },

            "daily_sales": daily_sales,

            "payment_methods": payment_methods,

            "top_products": top_products,
        }