import sqlite3
from pathlib import Path

DB_PATH = Path("data/prices.db")


def get_connection():
    # Убедимся, что папка для БД существует (sqlite не создаст директорию автоматически).
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        price REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    conn.commit()
    conn.close()


def add_product(url: str, name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO products (url, name)
        VALUES (?, ?)
        """,
        (url, name)
    )

    conn.commit()

    product_id = cursor.lastrowid

    conn.close()

    return product_id


def add_products(products: list[tuple[str, str]]) -> None:
    """Добавляет несколько товаров в базу за один проход."""

    if not products:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO products (url, name)
        VALUES (?, ?)
        """,
        products,
    )

    conn.commit()
    conn.close()


def add_price(product_id: int, price: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO price_history (product_id, price)
        VALUES (?, ?)
        """,
        (product_id, price)
    )

    conn.commit()
    conn.close()
