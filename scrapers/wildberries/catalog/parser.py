from models import Product
import re


def parse_products(soup):
    # url, name, price
    found = []
    cards = soup.find_all("article", class_="product-card j-card-item j-analitics-item")
    for card in cards:
        url_elem = card.find("a", class_="product-card__link j-card-link j-open-full-product-card")
        url = url_elem["href"] if url_elem else None

        title_elem = card.find("span", class_="product-card__brand")
        title = title_elem.get_text(strip=True) if title_elem else ""

        price = ""
        price_elem = (
            card.find("ins", class_="price__lower-price red-price")
            or card.find("ins", class_="price__lower-price")
        )
        if price_elem:
            price = price_elem.get_text(strip=True)
            price = float(re.sub(r'[^\d,\.]', '', price).replace(',', '.'))
            
        found.append(
            Product(url=url, name=title, price=price)
        )
    return found
