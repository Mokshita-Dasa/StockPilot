from inventory_service import InventoryService
from decimal import Decimal, InvalidOperation
from product_service import ProductService
from order_service import OrderService
import logging

def get_positive_int(prompt):
    value = int(input(prompt))

    if value <= 0:
        raise ValueError("Please enter a number greater than zero.")

    return value


def get_non_negative_int(prompt):
    value = int(input(prompt))

    if value < 0:
        raise ValueError("Please enter zero or a positive number.")

    return value

logging.basicConfig(
    filename="stockpilot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main(service=None, inventory=None, orders=None):
    logger.info("StockPilot application started")

    if service is None:
        service = ProductService()

    if inventory is None:
        inventory = InventoryService()

    if orders is None:
        orders = OrderService()
    while True:
        print("\n===== STOCKPILOT =====")
        print("1. Add Product")
        print("2. View All Products")
        print("3. Search Product")
        print("4. Update Product Price")
        print("5. Deactivate Product")
        print("6. Receive Stock")
        print("7. View Stock Movements")
        print("8. Exit")
        print("9. Create Order")
        print("10. View All Orders")
        print("11. View Order Details")
        print("12. Cancel Order")
        print("13. View Low-Stock Products")
        print("14. View Dashboard")

        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                name = input("Product name: ").strip()

                if not name:
                    raise ValueError("Product name cannot be empty.")

                price = Decimal(input("Product price: "))

                quantity = get_non_negative_int(
                    "Initial stock quantity: "
                )

                reorder_level = get_non_negative_int(
                    "Reorder level: "
                )

                product_id = service.add_product(
                    name, price, quantity, reorder_level
                )

                logger.info("Product added successfully. Product ID: %s", product_id)

                print(f"Product added successfully! ID: {product_id}")

            elif choice == "2":
                products = service.get_all_products()

                if not products:
                    print("No active products found.")
                else:
                    for product in products:
                        print(
                            f"ID: {product['product_id']} | "
                            f"Name: {product['name']} | "
                            f"Price: {product['price']} | "
                            f"Stock: {product['stock_quantity']}"
                        )

            elif choice == "3":
                product_id = get_positive_int("Enter product ID: ")
                product = service.search_product(product_id)

                if product:
                    logger.info("Product searched successfully. Product ID: %s", product_id)
                    print("Product found:")
                    print(product)
                else:
                    print("Active product not found.")

            elif choice == "4":
                product_id = get_positive_int("Enter product ID: ")
                new_price = Decimal(input("Enter new price: "))

                success = service.update_product_price(product_id, new_price)

                if success:
                    logger.info("Product price updated. Product ID: %s", product_id)
                    print("Product price updated successfully!")
                else:
                    print("Active product not found.")

            elif choice == "5":
                product_id = get_positive_int("Enter product ID: ")
                confirm = input(
                    "Deactivate this product? (yes/no): "
                ).strip().lower()

                if confirm == "yes":
                    if service.deactivate_product(product_id):
                        logger.info("Product deactivated. Product ID: %s", product_id)
                        print("Product deactivated successfully!")
                    else:
                        print("Active product not found.")
                else:
                    print("Deactivation cancelled.")
            
            elif choice == "6":
                product_id = get_positive_int("Enter product ID: ")
                quantity = get_positive_int("Quantity received: ")

                inventory.receive_stock(product_id, quantity)
                logger.info(
                    "Stock received successfully. Product ID: %s, Quantity: %s",
                    product_id,
                    quantity
                )

                print("Stock received successfully!")

            elif choice == "7":
                product_id = get_positive_int("Enter product ID: ")
                movements = inventory.get_stock_movements(product_id)

                if movements:
                    logger.info(
                        "Stock movements viewed. Product ID: %s",
                        product_id
                    )

                    for movement in movements:
                        print(movement)
                else:
                    print("No stock movements found.")
            
            elif choice == "9":
                items = []

                count = get_positive_int(
                    "How many different products? "
                )

                if count <= 0:
                    raise ValueError(
                        "Enter at least one product"
                    )

                for i in range(count):
                    print(f"\nProduct {i + 1}")

                    product_id = get_positive_int(
                        "Enter product ID: "
                    )

                    quantity = get_positive_int(
                        "Enter quantity: "
                    )
                    items.append((product_id, quantity))

                order_id, total = orders.create_order(items)

                logger.info(
                    "Order created successfully. Order ID: %s, Total: %s",
                    order_id,
                    total
                )

                print("\nOrder placed successfully!")
                print("Order ID:", order_id)
                print("Order Total:", total)

            elif choice == "10":
                all_orders = orders.get_all_orders()

                if not all_orders:
                    print("No orders found.")
                else:
                    logger.info("All order history viewed. Total orders: %s", len(all_orders))

                    print("\n--- Order History ---")

                    for order in all_orders:
                        print(
                            f"Order ID: {order[0]} | "
                            f"Status: {order[1]} | "
                            f"Total: {order[2]}"
                        )

            elif choice == "11":
                order_id = get_positive_int("Enter order ID: ")

                details = orders.get_order_details(order_id)

                if not details:
                    print("No items found for this order.")
                else:
                    logger.info(
                        "Order details viewed. Order ID: %s",
                        order_id
                    )

                    print(f"\n--- Details for Order {order_id} ---")

                    for item in details:
                        print(
                            f"Product ID: {item[0]} | "
                            f"Name: {item[1]} | "
                            f"Quantity: {item[2]} | "
                            f"Unit Price: {item[3]} | "
                            f"Subtotal: {item[4]}"
                        )

            elif choice == "12":
                order_id = get_positive_int("Enter the order ID to cancel: ")

                cancelled = orders.cancel_order(order_id)

                if cancelled:
                    logger.info("Order cancelled successfully. Order ID: %s", order_id)

                    print("\nOrder cancelled successfully!")
                    print("Product stock has been restored.")
            
            elif choice == "13":
                low_stock = inventory.get_low_stock_products()

                logger.info(
                    "Low-stock report viewed. Products found: %s",
                    len(low_stock)
                )

                if not low_stock:
                    print("\nAll products have sufficient stock.")
                else:
                    print("\n--- Low-Stock Alerts ---")

                    for product in low_stock:
                        print(
                            f"Product ID: {product[0]} | "
                            f"Name: {product[1]} | "
                            f"Stock: {product[2]} | "
                            f"Reorder Level: {product[3]}"
                        )
            elif choice == "14":
                summary = inventory.get_dashboard_summary()
                logger.info("StockPilot dashboard viewed")
                print("\n================================")
                print("       STOCKPILOT DASHBOARD")
                print("================================")

                print(
                    "Total Active Products:",
                    summary["total_products"]
                )

                print(
                    "Total Stock Units:",
                    summary["total_stock"]
                )

                print(
                    "Total Inventory Value: ₹",
                    summary["inventory_value"]
                )

                print(
                    "Total Orders:",
                    summary["total_orders"]
                )

                print(
                    "Placed Orders:",
                    summary["placed_orders"]
                )

                print(
                    "Cancelled Orders:",
                    summary["cancelled_orders"]
                )

                print(
                    "Low-Stock Products:",
                    summary["low_stock_products"]
                )

                print("================================")

            elif choice == "8":
                logger.info("StockPilot application closed")
                print("Thank you for using StockPilot!")
                break

            
            else:
                raise ValueError("Invalid choice. Please enter a number from 1 to 14.")

        except (ValueError, InvalidOperation) as error:
            logger.warning("Invalid input or value: %s", error)
            print("Invalid input:", error)

        except Exception as error:
            logger.exception("An unexpected error occurred")
            print("Something went wrong. Please try again.")
            print("Error details:", error)

if __name__ == "__main__":
    main()
