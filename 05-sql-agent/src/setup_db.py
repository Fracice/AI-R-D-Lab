
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sales.db"


def setup_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.executescript("""
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS customers;

            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL
            );

            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0)
            );

            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );

            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price REAL NOT NULL CHECK (unit_price >= 0),
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
        """)

        customers = [
            (1, "Alice Rossi", "Italy", "Milan"),
            (2, "Marco Bianchi", "Italy", "Rome"),
            (3, "Sofia Garcia", "Spain", "Madrid"),
            (4, "James Smith", "USA", "New York"),
            (5, "Emma Wilson", "UK", "London"),
        ]

        products = [
            (1, "Laptop", "Electronics", 1200.00),
            (2, "Smartphone", "Electronics", 800.00),
            (3, "Headphones", "Accessories", 150.00),
            (4, "Keyboard", "Accessories", 80.00),
            (5, "Monitor", "Electronics", 300.00),
        ]

        orders = [
            (1, 1, "2026-01-10", "completed"),
            (2, 2, "2026-01-15", "completed"),
            (3, 1, "2026-02-03", "completed"),
            (4, 3, "2026-02-20", "pending"),
            (5, 4, "2026-03-05", "completed"),
            (6, 5, "2026-03-18", "cancelled"),
            (7, 2, "2026-04-02", "completed"),
            (8, 3, "2026-04-12", "completed"),
        ]

        order_items = [
            (1, 1, 1, 1, 1200.00),
            (2, 1, 3, 2, 150.00),
            (3, 2, 2, 1, 800.00),
            (4, 2, 4, 2, 80.00),
            (5, 3, 5, 2, 300.00),
            (6, 3, 3, 1, 150.00),
            (7, 4, 2, 1, 800.00),
            (8, 5, 1, 1, 1200.00),
            (9, 5, 5, 2, 300.00),
            (10, 6, 3, 1, 150.00),
            (11, 7, 2, 2, 800.00),
            (12, 8, 4, 3, 80.00),
            (13, 8, 3, 1, 150.00),
        ]

        cursor.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?)", customers
        )
        cursor.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?)", products
        )
        cursor.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?)", orders
        )
        cursor.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", order_items
        )

        conn.commit()

    print(f"Database created at: {DB_PATH}")
    print(f"Customers: {len(customers)}")
    print(f"Products: {len(products)}")
    print(f"Orders: {len(orders)}")
    print(f"Order items: {len(order_items)}")


if __name__ == "__main__":
    setup_database()
