from datetime import datetime

from app.services.pptx_service import PPTXService


def generate_sales_analysis_deck(
    start_date: str,
    end_date: str,
) -> dict:
    """
    Generate a PowerPoint sales analysis deck
    for a specified date range.

    Dates must use YYYY-MM-DD format.
    """

    try:
        start = datetime.strptime(
            start_date,
            "%Y-%m-%d",
        ).date()

        end = datetime.strptime(
            end_date,
            "%Y-%m-%d",
        ).date()

        if start > end:
            return {
                "success": False,
                "error": (
                    "Start date cannot be after "
                    "end date."
                ),
            }

        service = PPTXService()

        result = service.generate_sales_analysis_deck(
            start_date=start,
            end_date=end,
        )

        return result

    except ValueError:
        return {
            "success": False,
            "error": (
                "Invalid date format. "
                "Use YYYY-MM-DD."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }