import json

from app.tools.khata_tools import find_customer
from app.tools.inventory_tools import (
    search_products,
    get_stock,
    get_low_stock,
    receive_stock,
    add_product,
)
from app.tools.billing_tools import (
    create_bill,
    add_bill_item,
    calculate_bill,
    update_bill_item,
    remove_bill_item,
    get_bill,
    finalize_bill,
)
from app.tools.khata_tools import (
    find_customer,
    create_customer,
    add_credit,
    record_khata_payment,
    get_khata_balance,
)
from app.tools.analytics_tools import get_daily_sales_report
from app.tools.invoice_tools import generate_invoice_pdf
from app.tools.pptx_tools import generate_sales_analysis_deck

from app.tools.preference_tools import (
    set_preference,
    get_preference,
    get_all_preferences,
)

# ---------------------------------------------------------
# 1. Tell Gemini what tool is available
# ---------------------------------------------------------

FIND_CUSTOMER_TOOL = {
    "type": "function",
    "name": "find_customer",
    "description": (
        "Find customers in the supermarket customer database "
        "by customer name or phone number. Use this when the "
        "shopkeeper refers to a customer but does not provide "
        "the customer ID."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Customer name or phone number to search for."
                ),
            }
        },
        "required": ["query"],
    },
}


# ---------------------------------------------------------
# 2. Map Gemini's tool name to our real Python function
# ---------------------------------------------------------

AVAILABLE_TOOLS = {

    # -----------------------------
    # Customer / Khata
    # -----------------------------
    "find_customer": find_customer,
    "create_customer": create_customer,
    "add_credit": add_credit,
    "record_khata_payment": record_khata_payment,
    "get_khata_balance": get_khata_balance,

    # -----------------------------
    # Inventory
    # -----------------------------
    "search_products": search_products,
    "get_stock": get_stock,
    "get_low_stock": get_low_stock,
    "receive_stock": receive_stock,
    "add_product": add_product,

    # -----------------------------
    # Billing
    # -----------------------------
    "create_bill": create_bill,
    "add_bill_item": add_bill_item,
    "calculate_bill": calculate_bill,
    "update_bill_item": update_bill_item,
    "remove_bill_item": remove_bill_item,
    "get_bill": get_bill,
    "finalize_bill": finalize_bill,

    # -----------------------------
    # Analytics
    # -----------------------------
    "get_daily_sales_report": get_daily_sales_report,

    # -----------------------------
    # Documents
    # -----------------------------
    "generate_invoice_pdf": generate_invoice_pdf,
    "generate_sales_analysis_deck": generate_sales_analysis_deck,

    # -----------------------------
    # Persistent preferences
    # -----------------------------
    "set_preference": set_preference,
    "get_preference": get_preference,
    "get_all_preferences": get_all_preferences,
}

def execute_tool(tool_name: str, arguments: dict) -> dict:
    """
    Execute a tool requested by Gemini.
    """

    tool = AVAILABLE_TOOLS.get(tool_name)

    if tool is None:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
        }

    try:
        return tool(**arguments)

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }