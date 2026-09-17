from app.services.invoice_service import InvoiceService


service = InvoiceService()

result = service.generate_invoice_pdf(13)

print(result)