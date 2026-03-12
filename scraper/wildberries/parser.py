from .models import Product


def parse_products(soup):
    found = []
    cards = soup.find_all("article", class_="product-card j-card-item j-analitics-item")
    for card in cards:
        id_elem = card.get("id")

        title_elem = card.find("span", class_="product-card__brand")
        title = title_elem.get_text(strip=True) if title_elem else ""

        price = ""
        price_elem = (
            card.find("ins", class_="price__lower-price red-price")
            or card.find("ins", class_="price__lower-price")
        )
        if price_elem:
            price = price_elem.get_text(strip=True)

        img_elem = card.find("img")
        img_link = img_elem["src"] if img_elem else None

        found.append(
            Product(name=title, price=price, id=id_elem, img=img_link)
        )
    return found
