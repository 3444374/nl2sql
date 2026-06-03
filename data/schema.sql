DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    city TEXT NOT NULL,
    level TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO customers VALUES
    (1, 'Acme Retail', 'Shanghai', 'gold'),
    (2, 'Northwind Mart', 'Beijing', 'silver'),
    (3, 'Future Shop', 'Shanghai', 'silver'),
    (4, 'Blue Ocean', 'Shenzhen', 'gold'),
    (5, 'Metro Direct', 'Beijing', 'bronze');

INSERT INTO products VALUES
    (1, 'Laptop Pro', 'computer', 7200.0),
    (2, 'Office Chair', 'furniture', 860.0),
    (3, 'Monitor 27', 'computer', 1680.0),
    (4, 'Standing Desk', 'furniture', 2300.0),
    (5, 'Wireless Mouse', 'computer', 160.0);

INSERT INTO orders VALUES
    (101, 1, '2025-01-15', 'paid'),
    (102, 1, '2025-02-18', 'paid'),
    (103, 2, '2025-03-05', 'cancelled'),
    (104, 3, '2025-03-21', 'paid'),
    (105, 4, '2025-04-03', 'paid'),
    (106, 5, '2025-04-12', 'paid'),
    (107, 2, '2025-05-20', 'paid');

INSERT INTO order_items VALUES
    (1001, 101, 1, 2, 7100.0),
    (1002, 101, 5, 10, 150.0),
    (1003, 102, 3, 4, 1600.0),
    (1004, 103, 2, 5, 820.0),
    (1005, 104, 4, 2, 2200.0),
    (1006, 105, 1, 1, 7200.0),
    (1007, 105, 3, 2, 1680.0),
    (1008, 106, 2, 3, 860.0),
    (1009, 107, 5, 20, 155.0),
    (1010, 107, 3, 1, 1650.0);
