from uuid import uuid4

from app.tools.khata_tools import (
    create_customer,
    add_credit,
    record_khata_payment,
    get_khata_balance,
)


def run_test():
    unique_id = uuid4().hex[:8]

    # 1. Create customer
    result = create_customer(
        name=f"Tool Ravi {unique_id}",
        phone=f"92222{unique_id[:5]}",
    )

    assert result["success"] is True

    customer_id = result["customer_id"]

    print(f"Customer created: {result['name']}")
    print(f"Customer ID: {customer_id}")

    # 2. Add credit
    result = add_credit(
        customer_id=customer_id,
        amount=500,
        reference="TOOL_KHATA_TEST",
    )

    assert result["success"] is True
    assert result["balance"] == 500.0

    print(f"Credit added: ₹{result['amount']}")
    print(f"Balance: ₹{result['balance']}")

    # 3. Record payment
    result = record_khata_payment(
        customer_id=customer_id,
        amount=200,
        reference="TOOL_PAYMENT_TEST",
    )

    assert result["success"] is True
    assert result["balance"] == 300.0

    print(f"Payment recorded: ₹{result['amount']}")
    print(f"Balance: ₹{result['balance']}")

    # 4. Retrieve balance
    result = get_khata_balance(
        customer_id=customer_id,
    )

    assert result["success"] is True
    assert result["balance"] == 300.0

    print(f"Retrieved balance: ₹{result['balance']}")

    # 5. Invalid excessive payment
    result = record_khata_payment(
        customer_id=customer_id,
        amount=400,
        reference="INVALID_PAYMENT",
    )

    assert result["success"] is False
    assert "exceeds outstanding balance" in result["error"]

    print(f"Excess payment rejected: {result['error']}")

    # 6. Verify balance is unchanged
    result = get_khata_balance(
        customer_id=customer_id,
    )

    assert result["balance"] == 300.0

    print(f"Final balance: ₹{result['balance']}")

    print("\nKhata tool test passed.")


if __name__ == "__main__":
    run_test()