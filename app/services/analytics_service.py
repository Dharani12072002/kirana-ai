from datetime import datetime

from app.database.connection import SessionLocal
from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:

    def __init__(self):
        self.analytics_repository = AnalyticsRepository()

    def get_daily_sales_report(self, target_date=None):
        """
        Get the sales report for a specific date.

        If no date is provided, today's date is used.
        """

        db = SessionLocal()

        try:
            if target_date is None:
                target_date = datetime.now().date()

            report = self.analytics_repository.get_daily_sales(
                db=db,
                target_date=target_date,
            )

            return {
                "success": True,
                "report": report,
            }

        except Exception as error:
            db.rollback()

            return {
                "success": False,
                "error": str(error),
            }

        finally:
            db.close()

    def get_sales_analysis_data(
        self,
        start_date,
        end_date,
    ):
        """
        Get sales analysis data for a date range.
        """

        db = SessionLocal()

        try:
            result = self.analytics_repository.get_sales_analysis_data(
                db=db,
                start_date=start_date,
                end_date=end_date,
            )

            return {
                "success": True,
                "data": result,
            }

        except Exception as error:
            db.rollback()

            return {
                "success": False,
                "error": str(error),
            }

        finally:
            db.close()