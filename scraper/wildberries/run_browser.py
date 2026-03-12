from .models import Product
from .parser import parse_products
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def run(url: str, scrolls: int = 1) -> list[Product]:
    products = []

    with sync_playwright() as p:
        # для отладки можно запускать с headless=False, slow_mo=100
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # открать для отладки
        # page.set_viewport_size({"width": 1280, "height": 800})

        page.goto(url)

        for n in range(scrolls):
            page.wait_for_timeout(5000)
            page.mouse.wheel(0, 1000)
            print(f"Прокрутили страницу {n+1} раз")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        found = parse_products(soup)

        products.extend(found)
        print(f"найдено {len(found)} товаров (итого {len(products)})")

        page.wait_for_timeout(5000)
        browser.close()
    return products
