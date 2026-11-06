
from db import get_connection


class InventoryService:

    def receive_stock(self, product_id, quantity):
        if product_id <= 0:
            raise ValueError("Product ID must be positive")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        connection = get_connection()
        cursor = connection.cursor()

        try:
            # Lock the product row while updating stock.
            cursor.execute(
                """
                SELECT stock_quantity
                FROM products
                WHERE product_id = %s AND is_active = TRUE
                FOR UPDATE
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if product is None:
                raise ValueError("Active product not found")

            # Increase the available stock.
            cursor.execute(
                """
                UPDATE products
                SET stock_quantity = stock_quantity + %s
                WHERE product_id = %s
                """,
                (quantity, product_id)
            )

            # Record the stock received.
            cursor.execute(
                """
                INSERT INTO stock_movements
                    (product_id, movement_type, quantity)
                VALUES (%s, 'IN', %s)
                """,
                (product_id, quantity)
            )

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_stock_movements(self, product_id):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT movement_id, product_id,
                       movement_type, quantity, created_at
                FROM stock_movements
                WHERE product_id = %s
                ORDER BY movement_id DESC
                """,
                (product_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()
    
    def get_low_stock_products(self):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    product_id,
                    name,
                    stock_quantity,
                    reorder_level
                FROM products
                WHERE is_active = TRUE
                  AND stock_quantity <= reorder_level
                ORDER BY stock_quantity ASC
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()
    
    def get_dashboard_summary(self):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*)
                     FROM products
                     WHERE is_active = TRUE),

                    (SELECT COALESCE(SUM(stock_quantity), 0)
                     FROM products
                     WHERE is_active = TRUE),

                    (SELECT COALESCE(
                        SUM(price * stock_quantity), 0)
                     FROM products
                     WHERE is_active = TRUE),

                    (SELECT COUNT(*)
                     FROM orders),

                    (SELECT COUNT(*)
                     FROM orders
                     WHERE status = 'PLACED'),

                    (SELECT COUNT(*)
                     FROM orders
                     WHERE status = 'CANCELLED'),

                    (SELECT COUNT(*)
                     FROM products
                     WHERE is_active = TRUE
                       AND stock_quantity <= reorder_level)
            """)

            result = cursor.fetchone()

            return {
                "total_products": result[0],
                "total_stock": result[1],
                "inventory_value": result[2],
                "total_orders": result[3],
                "placed_orders": result[4],
                "cancelled_orders": result[5],
                "low_stock_products": result[6]
            }

        finally:
            cursor.close()
            connection.close()
