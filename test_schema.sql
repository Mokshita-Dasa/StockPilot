
CREATE DATABASE IF NOT EXISTS stockpilot_test_db;

USE stockpilot_test_db;

-- 1. SUPPLIERS TABLE
CREATE TABLE suppliers (
    supplier_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    PRIMARY KEY (supplier_id)
) ENGINE=InnoDB;

-- 2. PRODUCTS TABLE
CREATE TABLE products (
    product_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 5,
    supplier_id INT DEFAULT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (product_id),
    KEY supplier_id (supplier_id),
    CONSTRAINT products_ibfk_1
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers (supplier_id)
        ON DELETE SET NULL,
    CONSTRAINT products_chk_1 CHECK (price >= 0),
    CONSTRAINT products_chk_2 CHECK (stock_quantity >= 0),
    CONSTRAINT products_chk_3 CHECK (reorder_level >= 0)
) ENGINE=InnoDB;

-- 3. ORDERS TABLE
CREATE TABLE orders (
    order_id INT NOT NULL AUTO_INCREMENT,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('PLACED','CANCELLED')
        NOT NULL DEFAULT 'PLACED',
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (order_id),
    CONSTRAINT orders_chk_1 CHECK (total_amount >= 0)
) ENGINE=InnoDB;

-- 4. ORDER ITEMS TABLE
CREATE TABLE order_items (
    order_item_id INT NOT NULL AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_item_id),
    UNIQUE KEY order_id (order_id, product_id),
    KEY product_id (product_id),
    CONSTRAINT order_items_ibfk_1
        FOREIGN KEY (order_id)
        REFERENCES orders (order_id),
    CONSTRAINT order_items_ibfk_2
        FOREIGN KEY (product_id)
        REFERENCES products (product_id),
    CONSTRAINT order_items_chk_1 CHECK (quantity > 0),
    CONSTRAINT order_items_chk_2 CHECK (unit_price >= 0)
) ENGINE=InnoDB;

-- 5. STOCK MOVEMENTS TABLE
CREATE TABLE stock_movements (
    movement_id INT NOT NULL AUTO_INCREMENT,
    product_id INT NOT NULL,
    movement_type ENUM('IN','OUT','RETURN') NOT NULL,
    quantity INT NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (movement_id),
    KEY product_id (product_id),
    CONSTRAINT stock_movements_ibfk_1
        FOREIGN KEY (product_id)
        REFERENCES products (product_id),
    CONSTRAINT stock_movements_chk_1 CHECK (quantity > 0)
) ENGINE=InnoDB;
