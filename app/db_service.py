import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "prices.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def add_product(url: str, name: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO products (url, name)
        VALUES (?, ?)
        """,
        (url, name)
    )

    conn.commit()
    conn.close()


def add_products(products):

    conn = get_connection()
    cursor = conn.cursor()

    added = 0

    for p in products:

        cursor.execute(
            """
            INSERT OR IGNORE INTO products (url, name)
            VALUES (?, ?)
            """,
            (p.url, p.name)
        )

        if cursor.rowcount > 0:
            added += 1

    conn.commit()
    conn.close()

    print(f"Added {added} new products")