from decimal import Decimal
from db import get_connection


class ProductService:

    def add_product(
        self, name, price, quantity, reorder_level=5, supplier_id=None
    ):
        name = name.strip()
        price = Decimal(str(price))

        if not name:
            raise ValueError("Product name is required")

        if not price.is_finite() or price < 0:
            raise ValueError("Price must be non-negative")

        if price.as_tuple().exponent < -2:
            raise ValueError("Price can have at most 2 decimal places")

        if quantity < 0 or reorder_level < 0:
            raise ValueError("Stock and reorder level cannot be negative")

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO products
                    (name, price, stock_quantity,
                     reorder_level, supplier_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, price, quantity, reorder_level, supplier_id)
            )

            product_id = cursor.lastrowid

            if quantity > 0:
                cursor.execute(
                    """
                    INSERT INTO stock_movements
                        (product_id, movement_type, quantity)
                    VALUES (%s, 'IN', %s)
                    """,
                    (product_id, quantity)
                )

            connection.commit()
            return product_id

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_all_products(self):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT product_id, name, price,
                       stock_quantity, reorder_level, supplier_id
                FROM products
                WHERE is_active = TRUE
                ORDER BY product_id
                """
            )
            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def search_product(self, product_id):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT product_id, name, price,
                       stock_quantity, reorder_level, supplier_id
                FROM products
                WHERE product_id = %s AND is_active = TRUE
                """,
                (product_id,)
            )
            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def update_product_price(self, product_id, new_price):
        new_price = Decimal(str(new_price))

        if not new_price.is_finite() or new_price < 0:
            raise ValueError("Price must be non-negative")

        if new_price.as_tuple().exponent < -2:
            raise ValueError("Price can have at most 2 decimal places")

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE products
                SET price = %s
                WHERE product_id = %s AND is_active = TRUE
                """,
                (new_price, product_id)
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return False

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def deactivate_product(self, product_id):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                UPDATE products
                SET is_active = FALSE
                WHERE product_id = %s AND is_active = TRUE
                """,
                (product_id,)
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return False

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()