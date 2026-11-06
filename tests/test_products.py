from decimal import Decimal

import product_service
from product_service import ProductService
from db import get_test_connection


def test_add_product(monkeypatch):

    monkeypatch.setattr(
        product_service,
        "get_connection",
        get_test_connection
    )

    service = ProductService()

    product_id = service.add_product(
        "Pytest Keyboard",
        Decimal("1500.00"),
        10,
        3
    )

    connection = get_test_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT name, price, stock_quantity, reorder_level
            FROM products
            WHERE product_id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        # Consume any remaining results
        cursor.fetchall()

        assert product is not None
        assert product["name"] == "Pytest Keyboard"
        assert product["price"] == Decimal("1500.00")
        assert product["stock_quantity"] == 10
        assert product["reorder_level"] == 3

    finally:
        cursor.close()
        connection.close()
def test_search_product(monkeypatch):
    monkeypatch.setattr(
        product_service, "get_connection", get_test_connection
    )

    service = ProductService()

    product_id = service.add_product(
        "Search Test Product", Decimal("500.00"), 5, 2
    )

    product = service.search_product(product_id)

    assert product is not None
    assert product["product_id"] == product_id
    assert product["name"] == "Search Test Product"


def test_update_product_price(monkeypatch):
    monkeypatch.setattr(
        product_service, "get_connection", get_test_connection
    )

    service = ProductService()

    product_id = service.add_product(
        "Update Test Product", Decimal("500.00"), 5, 2
    )

    result = service.update_product_price(
        product_id, Decimal("750.00")
    )

    product = service.search_product(product_id)

    assert result is True
    assert product["price"] == Decimal("750.00")


def test_deactivate_product(monkeypatch):
    monkeypatch.setattr(
        product_service, "get_connection", get_test_connection
    )

    service = ProductService()

    product_id = service.add_product(
        "Deactivate Test Product", Decimal("300.00"), 5, 2
    )

    result = service.deactivate_product(product_id)

    product = service.search_product(product_id)

    assert result is True
    assert product is None


def test_update_invalid_product(monkeypatch):
    monkeypatch.setattr(
        product_service, "get_connection", get_test_connection
    )

    service = ProductService()

    result = service.update_product_price(
        999999, Decimal("750.00")
    )

    assert result is False


def test_deactivate_invalid_product(monkeypatch):
    monkeypatch.setattr(
        product_service, "get_connection", get_test_connection
    )

    service = ProductService()

    result = service.deactivate_product(999999)

    assert result is False