from app.tools.inventory_tools import (
    add_product,
    get_stock,
    receive_stock,
    search_products,
    get_low_stock,
)


def main():
    print("=== Testing add_product ===")

    result = add_product(   
        name="Aashirvaad Rice",
        sku="RICE-AASH-001",
        unit="kg",
        cost_price=580,
        selling_price=650,
        gst_rate=5,
        category="Grocery",
        mrp=700,
        reorder_level=10,
        hsn_code="1006",
    )

    print(result)

    print("=== Testing search_products ===")

    result = search_products("rice")
    print(result)

    print("\n=== Testing get_stock ===")

    result = get_stock(1)
    print(result)

    print("\n=== Testing receive_stock ===")

    result = receive_stock(
        product_id=1,
        quantity=5,
        reference="TOOL-TEST-001",
    )

    print(result)

    print("\n=== Checking stock again ===")

    result = get_stock(1)
    print(result)

    print("\n=== Testing get_low_stock ===")
    print(get_low_stock())


if __name__ == "__main__":
    main()