from .parser import parse_products
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from .sorting import uniqueness_check
from app.database import add_products


def _parser(soup) -> list:
    for _ in range(3):
        found = parse_products(soup)

        if len(found) != 0:
            return found
        
    raise RuntimeError("Не удалось получить результат, после парсера пусто")


def run(url: str, scrolls: int = 1) -> None:
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
            print(f"Прокрутили страницу {n+1} раз из {scrolls}")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        found = _parser(soup=soup)
        
        products.extend(found)
        print(f"найдено {len(found)} товаров (итого {len(products)})")

        page.wait_for_timeout(5000)
        browser.close()

        products = uniqueness_check(products)

        # Сохраняем весь список продуктов в базе данных
        # (add_products ожидает список (url, name)).
        add_products([(p.url, p.name) for p in products])

    return
