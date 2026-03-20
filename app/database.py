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
        price_now REAL,
        price_max REAL,
        price_min REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    conn.commit()
    conn.close()


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


def get_price_stats(product_id: int) -> dict | None:
    """Возвращает min/max цены из price_history для product_id."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            MIN(price_now) AS price_min,
            MAX(price_now) AS price_max,
            COUNT(*) AS count_rows
        FROM price_history
        WHERE product_id = ?
        """,
        (product_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None or row["count_rows"] == 0:
        return None

    return {
        "price_min": row["price_min"],
        "price_max": row["price_max"],
    }


def add_price(
        product_id: int,
        price_now: float,
        price_max: float,
        price_min: float,
        ) -> None:
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO price_history (product_id, price_now, price_max, price_min)
        VALUES (?, ?, ?, ?)
        """,
        (product_id, price_now, price_max, price_min)
    )

    conn.commit()
    conn.close()


def update_price(
        product_id: int,
        price_now: float,
        price_max: float,
        price_min: float,
) -> None:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE price_history
        SET price_now = ?, price_max = ?, price_min = ?
        WHERE product_id = ?
        """,
        (price_now, price_max, price_min, product_id)
    )

    conn.commit()
    conn.close()