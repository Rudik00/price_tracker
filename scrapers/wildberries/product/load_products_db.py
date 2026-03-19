from app.database import get_connection


def _load_products() -> list[tuple[int, str]]:
    """достаём список товаров из базы данных для проверки цен."""

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM products")
    products = cursor.fetchall()
    conn.close()

    return products
