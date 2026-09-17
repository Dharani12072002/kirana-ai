from app.services.invoice_service import InvoiceService


def generate_invoice_pdf(bill_id: int) -> dict:
    """
    Generate a GST invoice PDF for a finalized bill.
    """

    try:
        service = InvoiceService()

        result = service.generate_invoice_pdf(
            bill_id=bill_id
        )

        return result

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }