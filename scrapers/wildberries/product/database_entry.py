import asyncio

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from app.database import add_price, update_price
from .browser import _fetch_html_with_browser
from .parser import _parse_price_from_html


def _parser_price(html) -> float:
    for _ in range(3):
        price_now = _parse_price_from_html(html)

        if price_now:
            return price_now


async def check_price(product: dict, browser) -> None:
    """Получить страницу товара, проанализировать цену и сохранить ее в базе данных."""

    product_id = product["id"]
    url = product["url"]

    price_min = product.get("price_min")
    price_max = product.get("price_max")

    try:
        html = await _fetch_html_with_browser(browser, url)
        price_now = _parser_price(html)

        # проверка на None — если не удалось найти цену, не сохраняем запись в базу данных, но и не падаем.
        if price_now is None:
            print(f"Price not found for {url}")
            return

        if price_min is None and price_max is None:
            price_min = price_now
            price_max = price_now
            await asyncio.to_thread(add_price, product_id, price_now, price_max, price_min)
            return

        else:
            price_min = min(price_min, price_now)
            price_max = max(price_max, price_now)

        # Синхронная запись в sqlite выполняем в потоке, чтобы не блокировать event loop.
        await asyncio.to_thread(update_price, product_id, price_now, price_max, price_min)

    except PlaywrightTimeoutError:
        print(f"Timeout while loading {url}")

    except Exception as e:
        print(f"Error checking {url}: {e}")
