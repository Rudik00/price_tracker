import re


def parse_products(soup) -> str:
    price = ""
    price_elem = (
        soup.find("ins", class_="mo-typography mo-typography_variant_title2 mo-typography_variable-weight_title2 mo-typography_variable mo-typography_color_danger priceBlockFinalPrice--iToZR")
        or soup.find("ins", class_="mo-typography mo-typography_variant_title2 mo-typography_variable-weight_title2 mo-typography_variable mo-typography_color_primary priceBlockFinalPrice--iToZR")
    )
    if price_elem:
        price = price_elem.get_text(strip=True)
        price = float(re.sub(r'[^\d,\.]', '', price).replace(',', '.'))

    print(f"Parsed price: {price}")

    return price