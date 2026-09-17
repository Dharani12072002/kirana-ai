from datetime import date

from app.services.pptx_service import PPTXService


service = PPTXService()

result = service.generate_sales_analysis_deck(
    start_date=date(2026, 9, 17),
    end_date=date(2026, 9, 17),
)

print(result)