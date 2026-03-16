from .parser import parse_price
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def run(url: str) -> float | None:

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(url)

        page.wait_for_timeout(2000)

        html = page.content()

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    price = parse_price(soup)

    return price
