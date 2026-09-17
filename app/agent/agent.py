import json

from groq import Groq

from app.config.settings import settings
from app.agent.tools import execute_tool


class KiranaAgent:
    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )
        self.messages = []
        self.pending_confirmation = None
        self.active_bill_id = None

        self.model = settings.GROQ_MODEL

        self.tools = [
    {
        "type": "function",
        "function": {
            "name": "find_customer",
            "description": (
                "Find customers in the supermarket customer "
                "database by customer name or phone number."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Customer name or phone number "
                            "to search for."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Search supermarket products by product name "
                "or SKU. Use this when the shopkeeper refers "
                "to a product by name instead of product ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Product name or SKU to search for."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock",
            "description": (
                "Get the current stock quantity of a specific "
                "product."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "Database ID of the product.",
                    }
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_low_stock",
            "description": (
                "Get all products whose current stock is at "
                "or below their reorder level."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "receive_stock",
            "description": (
                "Record incoming stock for a product. Use this "
                "when the shopkeeper says that stock has been "
                "received."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "Database ID of the product.",
                    },
                    "quantity": {
                        "type": "number",
                        "description": (
                            "Quantity of stock received."
                        ),
                    },
                    "reference": {
                        "type": "string",
                        "description": (
                            "Optional reference such as supplier "
                            "invoice number."
                        ),
                    },
                },
                "required": [
                    "product_id",
                    "quantity",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_product",
            "description": (
                "Add a new product to the supermarket product "
                "catalog."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Product name.",
                    },
                    "sku": {
                        "type": "string",
                        "description": "Unique product SKU.",
                    },
                    "unit": {
                        "type": "string",
                        "description": (
                            "Selling unit such as kg, litre, "
                            "piece, or packet."
                        ),
                    },
                    "cost_price": {
                        "type": "number",
                        "description": "Purchase/cost price.",
                    },
                    "selling_price": {
                        "type": "number",
                        "description": "Selling price.",
                    },
                    "gst_rate": {
                        "type": "number",
                        "description": "GST percentage.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional product category.",
                    },
                    "mrp": {
                        "type": "number",
                        "description": "Optional maximum retail price.",
                    },
                    "reorder_level": {
                        "type": "number",
                        "description": (
                            "Stock level at which the product "
                            "should be considered low stock."
                        ),
                    },
                    "hsn_code": {
                        "type": "string",
                        "description": "Optional HSN code.",
                    },
                },
                "required": [
                    "name",
                    "sku",
                    "unit",
                    "cost_price",
                    "selling_price",
                    "gst_rate",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_bill",
            "description": (
                "Create a new draft supermarket bill. Use this when "
                "the shopkeeper wants to start a new bill. A customer "
                "ID can be provided when the bill is for a specific "
                "customer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": ["integer", "null"],
                        "description": (
                            "Optional database ID of the customer. "
                            "Use null when creating a bill without a customer."
                        ),
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_bill_item",
            "description": (
                "Add a product and quantity to an existing draft bill. "
                "Use search_products first when the shopkeeper gives "
                "a product name instead of a product ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {
                        "type": "integer",
                        "description": "ID of the draft bill.",
                    },
                    "product_id": {
                        "type": "integer",
                        "description": "Database ID of the product.",
                    },
                    "quantity": {
                        "type": "number",
                        "description": "Quantity to add to the bill.",
                    },
                },
                "required": [
                    "bill_id",
                    "product_id",
                    "quantity",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_bill",
            "description": (
                "Calculate the subtotal, CGST, SGST, and total of "
                "a draft bill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {
                        "type": "integer",
                        "description": "ID of the bill.",
                    }
                },
                "required": ["bill_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bill",
            "description": (
                "Get the current details and items of a bill. "
                "Use this when the shopkeeper asks to see, show, "
                "or check the bill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {
                        "type": "integer",
                        "description": "ID of the bill.",
                    }
                },
                "required": ["bill_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_bill_item",
            "description": (
                "Change the quantity of an existing item in a "
                "draft bill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {
                        "type": "integer",
                        "description": "ID of the bill.",
                    },
                    "item_id": {
                        "type": "integer",
                        "description": "ID of the bill item.",
                    },
                    "quantity": {
                        "type": "number",
                        "description": "New quantity for the item.",
                    },
                },
                "required": [
                    "bill_id",
                    "item_id",
                    "quantity",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_bill_item",
            "description": (
                "Remove an item from a draft bill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {
                        "type": "integer",
                        "description": "ID of the bill.",
                    },
                    "item_id": {
                        "type": "integer",
                        "description": "ID of the bill item.",
                    },
                },
                "required": [
                    "bill_id",
                    "item_id",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finalize_bill",
            "description": (
                "Finalize a draft bill after the shopkeeper has "
                "confirmed the bill. Finalization records the sale "
                "and deducts stock. If the payment method is not "
                "provided, the billing layer may resolve it from "
                "the stored default payment preference. "
                "Do not call this merely because the shopkeeper "
                "asks to create or edit a bill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {
                        "type": "integer",
                        "description": "ID of the draft bill.",
                    },
                    "payment_method": {
                        "type": ["string", "null"],
                        "enum": [
                            "CASH",
                            "UPI",
                            "CARD",
                            "CREDIT",
                            None,
                        ],
                        "description": (
                            "Payment method. Use CASH, UPI, CARD, "
                            "or CREDIT when explicitly specified "
                            "or when a stored default payment "
                            "preference exists. Use null when no "
                            "payment method is known."
                        ),
                    },
                    "payment_reference": {
                        "type": "string",
                        "description": (
                            "Optional payment reference, such as "
                            "a UPI transaction reference."
                        ),
                    },
                },
                "required": [
                    "bill_id",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_customer",
            "description": (
                "Create a new customer for the store. "
                "Use this when the shopkeeper wants to add a new "
                "customer to the customer database."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Customer name.",
                    },
                    "phone": {
                        "type": ["string", "null"],
                        "description": (
                            "Customer phone number, if available."
                        ),
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_credit",
            "description": (
                "Add a credit/udhaar amount to a customer's Khata. "
                "Use this when a customer purchases on credit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Database ID of the customer.",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Credit amount in INR.",
                    },
                    "reference": {
                        "type": ["string", "null"],
                        "description": "Optional reference or note.",
                    },
                },
                "required": [
                    "customer_id",
                    "amount",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_khata_payment",
            "description": (
                "Record a payment made by a customer toward their "
                "existing Khata balance."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Database ID of the customer.",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Payment amount in INR.",
                    },
                    "reference": {
                        "type": ["string", "null"],
                        "description": "Optional payment reference or note.",
                    },
                },
                "required": [
                    "customer_id",
                    "amount",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_khata_balance",
            "description": (
                "Get the current outstanding Khata balance for a customer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Database ID of the customer.",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_sales_report",
            "description": (
                "Get the store's sales report for a specific date. "
                "Use this when the shopkeeper asks about today's sales, "
                "sales for a particular date, total sales, tax collected, "
                "payment-method totals, bill count, or top-selling products. "
                "Only finalized bills are included."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": ["string", "null"],
                        "description": (
                            "Optional date in YYYY-MM-DD format. "
                            "Use null for today's sales."
                        ),
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_invoice_pdf",
            "description": (
                "Generate a GST tax invoice PDF for a finalized bill. "
                "Use this when the shopkeeper asks for a bill or invoice "
                "as a PDF. The bill must already be finalized."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {
                        "type": "integer",
                        "description": (
                            "Database ID of the finalized bill "
                            "for which the invoice should be generated."
                        ),
                    }
                },
                "required": ["bill_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_sales_analysis_deck",
            "description": (
                "Generate a PowerPoint sales analysis deck for a date range. "
                "Use this when the shopkeeper asks for a sales analysis, "
                "sales report presentation, weekly sales deck, or business "
                "analysis PowerPoint. The deck contains finalized sales, "
                "daily sales trend, payment breakdown, top products, "
                "product details, and business summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": (
                            "Start date in YYYY-MM-DD format."
                        ),
                    },
                    "end_date": {
                        "type": "string",
                        "description": (
                            "End date in YYYY-MM-DD format."
                        ),
                    },
                },
                "required": [
                    "start_date",
                    "end_date",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_preference",
            "description": (
                "Save or update a persistent store-owner preference. "
                "Use this when the shopkeeper explicitly asks you to "
                "remember a standing preference such as default payment "
                "method, preferred product brand, shop name, or GSTIN."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": (
                            "A short stable key for the preference, "
                            "for example default_payment_method."
                        ),
                    },
                    "value": {
                        "type": "string",
                        "description": (
                            "The preference value to remember."
                        ),
                    },
                },
                "required": [
                    "key",
                    "value",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_preference",
            "description": (
                "Retrieve one persistent store-owner preference "
                "from the database."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": (
                            "The preference key to retrieve."
                        ),
                    },
                },
                "required": [
                    "key",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_preferences",
            "description": (
                "Retrieve all persistent store-owner preferences "
                "from the database. Use this when you need the "
                "owner's standing preferences to answer or perform "
                "an operation."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
        self.system_prompt = """
You are KiranaAI, an AI assistant for an Indian kirana/supermarket owner.

Understand natural-language requests and use tools.

Be concise, practical, and use simple shopkeeper-friendly English.

Never invent database information.

For billing:
- Bills are drafts.
- Adding/editing items must not reduce stock.
- Stock is reduced only when finalized.
- Use database prices/GST/product information.
- Do not finalize without a clear payment method.
- Do not finalize merely because creating or editing a bill.

For analytics:
- Use get_daily_sales_report for sales questions.
- Only finalized bills count as sales.
- Do not calculate sales from conversation history.
- Use the database report as the source of truth.

For sales analysis:
- Use generate_sales_analysis_deck for PowerPoint sales analysis requests.
- Use finalized database sales only.
- Do not invent sales figures or business insights.
- For "today", use today's date for both start_date and end_date.

For persistent preferences:
- Use set_preference when the shopkeeper explicitly asks you to remember a standing preference.
- Use get_preference or get_all_preferences when a stored preference is relevant.
- Preferences are persistent database data and survive /new chat and application restarts.
- Do not claim to remember a preference unless it was successfully saved.
- Do not invent preferences that are not stored in the database.
- Before finalizing a bill, if the shopkeeper has not explicitly specified a payment method, check the stored preference for "default_payment_method".
- If a default payment method exists, use it.
- If no default payment method exists and payment method is required, ask the shopkeeper.
- An explicitly specified payment method always takes precedence over the stored default.

For billing payment method:
- When the shopkeeper asks to finalize a bill and does NOT explicitly provide a payment method, you MUST call get_preference with key "default_payment_method" before asking the shopkeeper for a payment method.
- If get_preference returns a stored value, use that value as the payment_method for finalize_bill.
- Only ask the shopkeeper for the payment method if no default_payment_method is stored.
- If the shopkeeper explicitly says CASH, UPI, CARD, or CREDIT, use that explicit method and do not use the stored default.
- Never invent a payment method.
"""

    def run(self, user_message: str) -> str:

        answer = user_message.strip().lower()

        # ---------------------------------------------------------
        # 1. Handle a pending bill-finalization confirmation
        # ---------------------------------------------------------
        if self.pending_confirmation is not None:

            if answer in {"yes", "y", "confirm", "confirmed"}:

                pending = self.pending_confirmation

                # Consume confirmation BEFORE executing transaction
                # so the same confirmation cannot be reused.
                self.pending_confirmation = None

                result = execute_tool(
                    pending["tool_name"],
                    pending["arguments"],
                )

                if not result.get("success"):
                    return (
                        "❌ I could not finalize the bill: "
                        + result.get("error", "Unknown error.")
                    )

                # Finalized bill is no longer the active draft.
                self.active_bill_id = None

                return (
                    f"✅ Bill #{pending['arguments']['bill_id']} "
                    f"has been finalized successfully."
                )

            if answer in {"no", "n", "cancel", "cancelled"}:

                self.pending_confirmation = None

                return "Okay. I did not finalize the bill."

            return (
                "Please confirm the bill finalization with "
                "Yes or No."
            )

        # ---------------------------------------------------------
        # 2. Prevent standalone "Yes" from reaching the LLM
        # ---------------------------------------------------------
        if answer in {"yes", "y", "confirm", "confirmed"}:
            return "There is no pending bill confirmation."

        # ---------------------------------------------------------
        # 3. Add normal user message to conversation history
        # ---------------------------------------------------------
        self.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        max_iterations = 5

        # ---------------------------------------------------------
        # 4. Agent tool-calling loop
        # ---------------------------------------------------------
        for _ in range(max_iterations):

            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # -----------------------------------------------------
            # No tool call → final LLM response
            # -----------------------------------------------------
            if not assistant_message.tool_calls:

                final_text = assistant_message.content or ""

                self.messages.append(
                    {
                        "role": "assistant",
                        "content": final_text,
                    }
                )

                return final_text

            # -----------------------------------------------------
            # Store assistant's tool-call message
            # -----------------------------------------------------
            self.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in assistant_message.tool_calls
                    ],
                }
            )

            # -----------------------------------------------------
            # Execute requested tools
            # -----------------------------------------------------
            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                # -------------------------------------------------
                # Safe JSON parsing
                # -------------------------------------------------
                try:
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                except (json.JSONDecodeError, TypeError):

                    error_message = (
                        "Invalid tool arguments. "
                        "Please retry the request."
                    )

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(
                                {
                                    "success": False,
                                    "error": error_message,
                                }
                            ),
                        }
                    )

                    continue

                # =================================================
                # ACTIVE BILL GUARD
                # =================================================
                bill_tools = {
                    "add_bill_item",
                    "calculate_bill",
                    "get_bill",
                    "update_bill_item",
                    "remove_bill_item",
                    "finalize_bill",
                }

                if (
                    tool_name in bill_tools
                    and self.active_bill_id is None
                ):

                    message = (
                        "There is no active bill. "
                        "Please create a bill first, for example: "
                        "'Create a bill for Ravi'."
                    )

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(
                                {
                                    "success": False,
                                    "error": message,
                                }
                            ),
                        }
                    )

                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": message,
                        }
                    )

                    return message

                # =================================================
                # CONSEQUENTIAL ACTION GUARD
                #
                # Finalizing a bill requires explicit confirmation.
                # =================================================
                if tool_name == "finalize_bill":

                    bill_id = arguments.get("bill_id")

                    if bill_id is None:
                        return (
                            "❌ Bill ID is required before "
                            "finalization."
                        )

                    # ---------------------------------------------
                    # Ensure the requested bill is the active bill
                    # ---------------------------------------------
                    if (
                        self.active_bill_id is not None
                        and bill_id != self.active_bill_id
                    ):
                        return (
                            f"❌ Bill #{bill_id} is not the active bill. "
                            f"The active bill is "
                            f"#{self.active_bill_id}."
                        )

                    # ---------------------------------------------
                    # Recalculate authoritative bill totals
                    # ---------------------------------------------
                    calculate_result = execute_tool(
                        "calculate_bill",
                        {
                            "bill_id": bill_id,
                        },
                    )

                    if not calculate_result.get("success"):
                        return (
                            "❌ I could not calculate the bill "
                            "before finalization."
                        )

                    # ---------------------------------------------
                    # Retrieve updated bill
                    # ---------------------------------------------
                    bill_result = execute_tool(
                        "get_bill",
                        {
                            "bill_id": bill_id,
                        },
                    )

                    if not bill_result.get("success"):
                        return (
                            "❌ I could not verify the bill before "
                            "finalization."
                        )

                    # get_bill currently returns bill fields at
                    # the top level, but this also supports a
                    # nested "bill" structure.
                    bill = bill_result.get("bill")

                    if bill is None:
                        bill = bill_result

                    total = bill.get(
                        "total",
                        "unknown",
                    )

                    payment_method = arguments.get(
                        "payment_method",
                        "unknown",
                    )

                    items = bill.get(
                        "items",
                        [],
                    )

                    # ---------------------------------------------
                    # Build stock-impact summary
                    # ---------------------------------------------
                    stock_lines = []

                    for item in items:

                        product_name = item.get(
                            "product_name",
                            item.get(
                                "name",
                                "Unknown product",
                            ),
                        )

                        quantity = item.get(
                            "quantity",
                            0,
                        )

                        unit = item.get(
                            "unit",
                            "",
                        )

                        stock_lines.append(
                            f"- {product_name}: "
                            f"{quantity} {unit}"
                        )

                    stock_summary = ""

                    if stock_lines:
                        stock_summary = (
                            "\n\nStock to be deducted:\n"
                            + "\n".join(stock_lines)
                        )

                    # ---------------------------------------------
                    # Store pending transaction
                    # ---------------------------------------------
                    self.pending_confirmation = {
                        "tool_name": tool_name,
                        "arguments": arguments,
                    }

                    # ---------------------------------------------
                    # Ask for explicit confirmation
                    # ---------------------------------------------
                    return (
                        f"Bill #{bill_id} is ready to finalize.\n\n"
                        f"Total: ₹{total}\n"
                        f"Payment: {payment_method}"
                        f"{stock_summary}\n\n"
                        "Finalizing will record the payment "
                        "and reduce stock.\n"
                        "Do you want to finalize this bill?\n"
                        "Please reply Yes or No."
                    )

                # =================================================
                # NORMAL TOOL EXECUTION
                # =================================================
                result = execute_tool(
                    tool_name,
                    arguments,
                )

                # -------------------------------------------------
                # Store newly created bill as active bill
                # -------------------------------------------------
                if (
                    tool_name == "create_bill"
                    and result.get("success")
                    and result.get("bill_id")
                ):
                    self.active_bill_id = result["bill_id"]

                # =================================================
                # CUSTOMER AMBIGUITY GUARD
                #
                # Never let the LLM randomly choose between
                # multiple matching customers.
                # =================================================
                if (
                    tool_name == "find_customer"
                    and result.get("success")
                    and len(
                        result.get("customers", [])
                    ) > 1
                ):

                    customers = result["customers"]

                    options = []

                    for customer in customers:

                        options.append(
                            f"{customer['id']}. "
                            f"{customer['name']} - "
                            f"Phone: "
                            f"{customer.get('phone') or 'N/A'}"
                        )

                    clarification = (
                        "I found multiple matching customers:\n\n"
                        + "\n".join(options)
                        + "\n\n"
                        "Please tell me the customer ID, "
                        "phone number, or another detail to "
                        "identify the correct customer."
                    )

                    # Store tool result so the next turn has
                    # complete conversation history.
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result),
                        }
                    )

                    # Store clarification as assistant response.
                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": clarification,
                        }
                    )

                    return clarification

                # -------------------------------------------------
                # Store normal tool result
                # -------------------------------------------------
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        # ---------------------------------------------------------
        # 5. Safety fallback if agent exceeds iterations
        # ---------------------------------------------------------
        return (
            "I could not complete the request right now. "
            "Please try again."
        )