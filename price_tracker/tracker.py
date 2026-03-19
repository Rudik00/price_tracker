import asyncio

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from rich.progress import Progress
from app.database import add_price, get_connection
from scrapers.wildberries.product.browser import _fetch_html_with_browser
from scrapers.wildberries.product.parser import _parse_price_from_html


def _load_products():
    """Вспомогательная функция для синхронной загрузки товаров из базы данных."""

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM products")
    products = cursor.fetchall()
    conn.close()

    return products


async def check_price(product: dict, browser) -> None:
    """Получить страницу товара, проанализировать цену и сохранить ее в базе данных."""

    product_id = product["id"]
    url = product["url"]

    try:
        html = await _fetch_html_with_browser(browser, url)
        price = _parse_price_from_html(html)

        if price is None:
            print(f"Price not found for {url}")
            return

        # Синхронная запись в sqlite выполняем в потоке, чтобы не блокировать event loop.
        await asyncio.to_thread(add_price, product_id, price)

        print(f"Saved price {price} for product {product_id}")

    except PlaywrightTimeoutError:
        print(f"Timeout while loading {url}")

    except Exception as e:
        print(f"Error checking {url}: {e}")


async def main() -> None:
    """Точка входа: загрузка продуктов и одновременное выполнение всех проверок."""

    products = await asyncio.to_thread(_load_products)

    print(f"Found {len(products)} products to check")

    # Ограничьте количество одновременно работающих сайтов
    semaphore = asyncio.Semaphore(10)

    with Progress() as progress:
        task = progress.add_task("Checking prices", total=len(products))

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)

            async def guarded_check(product):
                async with semaphore:
                    await check_price(product, browser)
                    progress.update(task, advance=1)

            # Создаем задачи
            tasks = [guarded_check(p) for p in products]

            await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
