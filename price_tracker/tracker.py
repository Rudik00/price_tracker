from app.database import get_connection, add_price
from scrapers.wildberries.product.browser import run


def check_prices():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, url FROM products")

    products = cursor.fetchall()

    conn.close()

    print(f"Found {len(products)} products to check")

    for product in products:

        product_id = product["id"]
        url = product["url"]

        try:
            price = run(url)

            if price is None:
                print(f"Price not found for {url}")
                continue

            add_price(product_id, price)

            print(f"Saved price {price} for product {product_id}")

        except Exception as e:
            print(f"Error checking {url}: {e}")