import inventory_service
from inventory_service import InventoryService
from product_service import ProductService
from db import get_test_connection


def setup_test_database(monkeypatch):
    monkeypatch.setattr(
        inventory_service,
        "get_connection",
        get_test_connection
    )

    monkeypatch.setattr(
        "product_service.get_connection",
        get_test_connection
    )


def create_test_product():
    product_service = ProductService()

    return product_service.add_product(
        "Inventory Test Product",
        200.00,
        5,
        3
    )


def test_receive_stock(monkeypatch):
    setup_test_database(monkeypatch)

    service = InventoryService()
    product_id = create_test_product()

    result = service.receive_stock(product_id, 10)

    connection = get_test_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT stock_quantity FROM products WHERE product_id = %s",
            (product_id,)
        )

        stock = cursor.fetchone()

        assert result is True
        assert stock[0] == 15

    finally:
        cursor.close()
        connection.close()


def test_stock_movement_record(monkeypatch):
    setup_test_database(monkeypatch)

    service = InventoryService()
    product_id = create_test_product()

    service.receive_stock(product_id, 8)

    movements = service.get_stock_movements(product_id)

    assert len(movements) == 2
    assert movements[0]["movement_type"] == "IN"
    assert movements[0]["quantity"] == 8


def test_low_stock_products(monkeypatch):
    setup_test_database(monkeypatch)

    service = InventoryService()
    product_id = create_test_product()

    connection = get_test_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = 2, reorder_level = 3
            WHERE product_id = %s
            """,
            (product_id,)
        )
        connection.commit()

    finally:
        cursor.close()
        connection.close()

    low_stock = service.get_low_stock_products()

    product_ids = [product[0] for product in low_stock]

    assert product_id in product_ids
def test_dashboard_summary(monkeypatch):
    setup_test_database(monkeypatch)

    service = InventoryService()

    # Create a product for the dashboard
    create_test_product()

    summary = service.get_dashboard_summary()

    expected_keys = [
        "total_products",
        "total_stock",
        "inventory_value",
        "total_orders",
        "placed_orders",
        "cancelled_orders",
        "low_stock_products"
    ]

    for key in expected_keys:
        assert key in summary
        assert summary[key] is not None

    assert summary["total_products"] >= 1
    assert summary["total_stock"] >= 0
    assert summary["inventory_value"] >= 0
    assert summary["total_orders"] >= 0
    assert summary["placed_orders"] >= 0
    assert summary["cancelled_orders"] >= 0
    assert summary["low_stock_products"] >= 0