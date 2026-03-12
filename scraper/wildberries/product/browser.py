from parser import parse_products
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def run(url: str) -> list:

    with sync_playwright() as p:
        # для отладки можно запускать с headless=False, slow_mo=100
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # открать для отладки
        # page.set_viewport_size({"width": 1280, "height": 800})

        page.goto(url)

        page.wait_for_timeout(2000)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        found = parse_products(soup)

        browser.close()

    return found
