import sqlite3
from pathlib import Path

DB_PATH = Path("data/prices.db")


def get_connection():
    # Убедимся, что папка для БД существует.
    # sqlite не создаст директорию автоматически.
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

    # Удаляем дубли, оставляя запись с минимальным id для каждого URL.
    cursor.execute(
        """
        DELETE FROM products
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM products
            GROUP BY url
        )
        """
    )

    # Гарантируем уникальность URL на уровне БД.
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_products_url_unique
        ON products (url)
        """
    )

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

    # Отсекаем пустые URL и дубликаты в текущем батче.
    unique_batch: dict[str, str] = {}
    for url, name in products:
        if not url:
            continue
        unique_batch[url] = name

    if not unique_batch:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT OR IGNORE INTO products (url, name)
        VALUES (?, ?)
        """,
        list(unique_batch.items()),
    )

    conn.commit()
    conn.close()


def add_product(url: str, name: str) -> int:
    """Добавляет один товар и возвращает его product_id.

    Если товар с таким URL уже есть, возвращает существующий id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO products (url, name)
        VALUES (?, ?)
        """,
        (url, name),
    )

    cursor.execute(
        """
        SELECT id FROM products
        WHERE url = ?
        LIMIT 1
        """,
        (url,),
    )
    row = cursor.fetchone()

    conn.commit()
    conn.close()

    if row is None:
        raise RuntimeError(
            "Не удалось получить product_id после сохранения товара"
        )

    return int(row["id"])


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


def get_product_by_id(product_id: int) -> dict | None:
    # Получаем цены по product_id
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT price_now, price_max, price_min FROM price_history
        WHERE product_id = ?
        LIMIT 1
        """,
        (product_id,),
        )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return "Товара с таким ID не найден, цены отсутствуют"
    return dict(row)


def get_product_by_url(url: str) -> dict | None:
    # Получаем id по url, а затем цены по id
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM products
        WHERE url = ?
        LIMIT 1
        """,
        (url,),
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return "Такого товара нет в базе данных"

    product_id = int(row["id"])
    cursor.execute(
        """
        SELECT price_now, price_max, price_min FROM price_history
        WHERE product_id = ?
        LIMIT 1
        """,
        (product_id,),
    )
    price_row = cursor.fetchone()
    conn.close()
    if price_row is None:
        return "Товара с таким URL не найден, цены отсутствуют"

    return dict(price_row)