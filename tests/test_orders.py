import pytest

import order_service
import product_service

from order_service import OrderService
from product_service import ProductService
from db import get_test_connection


@pytest.fixture
def setup_services(monkeypatch):
    monkeypatch.setattr(
        order_service,
        "get_connection",
        get_test_connection
    )

    monkeypatch.setattr(
        product_service,
        "get_connection",
        get_test_connection
    )

    return OrderService(), ProductService()


def create_order_product(product_service):
    return product_service.add_product(
        "Order Test Product",
        200.00,
        20,
        5
    )


def get_product_stock(product_id):
    connection = get_test_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT stock_quantity
            FROM products
            WHERE product_id = %s
            """,
            (product_id,)
        )

        return cursor.fetchone()[0]

    finally:
        cursor.close()
        connection.close()


def test_create_order(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    order_id, total = orders.create_order([
        (product_id, 2)
    ])

    assert order_id > 0
    assert total == 400.00


def test_order_reduces_stock(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    orders.create_order([
        (product_id, 5)
    ])

    stock = get_product_stock(product_id)

    assert stock == 15


def test_get_order_details(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    order_id, total = orders.create_order([
        (product_id, 3)
    ])

    details = orders.get_order_details(order_id)

    assert len(details) == 1
    assert details[0][0] == product_id
    assert details[0][1] == "Order Test Product"
    assert details[0][2] == 3
    assert details[0][3] == 200.00


def test_cancel_order_restores_stock(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    initial_stock = get_product_stock(product_id)

    order_id, total = orders.create_order([
        (product_id, 4)
    ])

    orders.cancel_order(order_id)

    final_stock = get_product_stock(product_id)

    assert final_stock == initial_stock


def test_cancel_order_twice(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    order_id, total = orders.create_order([
        (product_id, 2)
    ])

    orders.cancel_order(order_id)

    with pytest.raises(ValueError):
        orders.cancel_order(order_id)


def test_insufficient_stock(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    with pytest.raises(ValueError):
        orders.create_order([
            (product_id, 100)
        ])

    assert get_product_stock(product_id) == 20
def test_empty_order(setup_services):
    orders, products = setup_services

    with pytest.raises(ValueError):
        orders.create_order([])


def test_invalid_product_id(setup_services):
    orders, products = setup_services

    with pytest.raises(ValueError):
        orders.create_order([
            (999999, 2)
        ])


def test_invalid_order_quantity(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    with pytest.raises(ValueError):
        orders.create_order([
            (product_id, 0)
        ])
def test_duplicate_product_ids(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    order_id, total = orders.create_order([
        (product_id, 2),
        (product_id, 3)
    ])

    details = orders.get_order_details(order_id)

    assert total == 1000.00
    assert len(details) == 1
    assert details[0][2] == 5
    assert get_product_stock(product_id) == 15
def test_get_all_orders(setup_services):
    orders, products = setup_services

    product_id = create_order_product(products)

    order_id, total = orders.create_order([
        (product_id, 2)
    ])

    all_orders = orders.get_all_orders()

    matching_orders = [
        order for order in all_orders
        if order[0] == order_id
    ]

    assert len(matching_orders) == 1
    assert matching_orders[0][1] == "PLACED"
    assert matching_orders[0][2] == total