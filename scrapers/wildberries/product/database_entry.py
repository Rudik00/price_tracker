import asyncio

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from app.database import add_price
from .browser import _fetch_html_with_browser
from .parser import _parse_price_from_html


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

    except PlaywrightTimeoutError:
        print(f"Timeout while loading {url}")

    except Exception as e:
        print(f"Error checking {url}: {e}")
