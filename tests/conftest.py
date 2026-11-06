import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
import pytest
from db import get_test_connection


@pytest.fixture(autouse=True)
def clean_test_database():
    connection = get_test_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM stock_movements")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM suppliers")

        connection.commit()

    finally:
        cursor.close()
        connection.close()