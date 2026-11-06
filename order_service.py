
from decimal import Decimal
from db import get_connection


class OrderService:

    def create_order(self, items):
        """
        items format:
        [(product_id, quantity), (product_id, quantity)]
        """

        if not items:
            raise ValueError("Order must contain at least one item")

        requested = {}

        # Validate and combine duplicate product IDs.
        for product_id, quantity in items:
            if product_id <= 0 or quantity <= 0:
                raise ValueError(
                    "Product IDs and quantities must be positive"
                )

            requested[product_id] = (
                requested.get(product_id, 0) + quantity
            )

        connection = get_connection()
        cursor = connection.cursor()

        try:
            # Lock products in ID order to reduce deadlocks.
            product_ids = sorted(requested)
            placeholders = ", ".join(
                ["%s"] * len(product_ids)
            )

            cursor.execute(
                f"""
                SELECT product_id, name, price, stock_quantity
                FROM products
                WHERE product_id IN ({placeholders})
                  AND is_active = TRUE
                ORDER BY product_id
                FOR UPDATE
                """,
                tuple(product_ids)
            )

            rows = cursor.fetchall()
            products = {row[0]: row for row in rows}

            # Check every requested product before making changes.
            for product_id, quantity in requested.items():
                product = products.get(product_id)

                if product is None:
                    raise ValueError(
                        f"Active product {product_id} not found"
                    )

                available = product[3]

                if quantity > available:
                    raise ValueError(
                        f"Insufficient stock for {product[1]}. "
                        f"Available: {available}, requested: {quantity}"
                    )

            total = Decimal("0.00")

            # Calculate the total using database prices.
            for product_id, quantity in requested.items():
                price = products[product_id][2]
                total += price * quantity

            # Create the order.
            cursor.execute(
                """
                INSERT INTO orders (status, total_amount)
                VALUES ('PLACED', %s)
                """,
                (total,)
            )

            order_id = cursor.lastrowid

            # Save items, reduce stock, and record movements.
            for product_id in product_ids:
                quantity = requested[product_id]
                price = products[product_id][2]

                cursor.execute(
                    """
                    INSERT INTO order_items
                        (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, product_id, quantity, price)
                )

                cursor.execute(
                    """
                    UPDATE products
                    SET stock_quantity = stock_quantity - %s
                    WHERE product_id = %s
                    """,
                    (quantity, product_id)
                )

                cursor.execute(
                    """
                    INSERT INTO stock_movements
                        (product_id, movement_type, quantity)
                    VALUES (%s, 'OUT', %s)
                    """,
                    (product_id, quantity)
                )

            connection.commit()

            return order_id, total

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()
    
    def get_all_orders(self):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT order_id, status, total_amount
                FROM orders
                ORDER BY order_id DESC
            """)

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_order_details(self, order_id):
        if order_id <= 0:
            raise ValueError("Order ID must be positive")

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    oi.product_id,
                    p.name,
                    oi.quantity,
                    oi.unit_price,
                    oi.quantity * oi.unit_price AS subtotal
                FROM order_items oi
                JOIN products p
                    ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
                ORDER BY oi.product_id
            """, (order_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()
    
    def cancel_order(self, order_id):
        if order_id <= 0:
            raise ValueError("Order ID must be positive")

        connection = get_connection()
        cursor = connection.cursor()

        try:
            # Lock the order so it cannot be cancelled twice.
            cursor.execute("""
                SELECT status
                FROM orders
                WHERE order_id = %s
                FOR UPDATE
            """, (order_id,))

            order = cursor.fetchone()

            if order is None:
                raise ValueError("Order not found")

            if order[0] != "PLACED":
                raise ValueError(
                    "Only placed orders can be cancelled"
                )

            # Get the products and quantities in this order.
            cursor.execute("""
                SELECT product_id, quantity
                FROM order_items
                WHERE order_id = %s
                ORDER BY product_id
            """, (order_id,))

            items = cursor.fetchall()

            if not items:
                raise ValueError("No items found for this order")

            # Lock the affected product rows in a consistent order.
            product_ids = [item[0] for item in items]
            placeholders = ", ".join(
                ["%s"] * len(product_ids)
            )

            cursor.execute(
                f"""
                SELECT product_id
                FROM products
                WHERE product_id IN ({placeholders})
                ORDER BY product_id
                FOR UPDATE
                """,
                tuple(product_ids)
            )

            existing_ids = {
                row[0] for row in cursor.fetchall()
            }

            if len(existing_ids) != len(set(product_ids)):
                raise ValueError(
                    "A product from this order no longer exists"
                )

            # Restore stock and record each stock movement.
            for product_id, quantity in items:
                cursor.execute("""
                    UPDATE products
                    SET stock_quantity = stock_quantity + %s
                    WHERE product_id = %s
                """, (quantity, product_id))

                cursor.execute("""
                    INSERT INTO stock_movements
                        (product_id, movement_type, quantity)
                    VALUES (%s, 'IN', %s)
                """, (product_id, quantity))

            # Mark the order as cancelled.
            cursor.execute("""
                UPDATE orders
                SET status = 'CANCELLED'
                WHERE order_id = %s
            """, (order_id,))

            connection.commit()
            return True

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()
