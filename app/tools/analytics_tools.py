from datetime import datetime

from app.services.analytics_service import AnalyticsService


def get_daily_sales_report(date=None) -> dict:
    """
    Get the store's sales report for a given date.

    If no date is provided, today's sales are returned.
    """

    try:
        target_date = None

        if date:
            target_date = datetime.strptime(
                date,
                "%Y-%m-%d",
            ).date()

        service = AnalyticsService()

        result = service.get_daily_sales_report(
            target_date=target_date,
        )

        return result

    except ValueError:
        return {
            "success": False,
            "error": (
                "Invalid date format. "
                "Please use YYYY-MM-DD."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }