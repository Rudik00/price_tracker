import re


def parse_price(soup) -> float | None:

    price_elem = (
        soup.find(
            "ins",
            class_="mo-typography mo-typography_variant_title2 mo-typography_variable-weight_title2 mo-typography_variable mo-typography_color_danger priceBlockFinalPrice--iToZR"
        )
        or soup.find(
            "ins",
            class_="mo-typography mo-typography_variant_title2 mo-typography_variable-weight_title2 mo-typography_variable mo-typography_color_primary priceBlockFinalPrice--iToZR"
        )
    )

    if not price_elem:
        return None

    price_text = price_elem.get_text(strip=True)

    price = float(
        re.sub(r"[^\d,\.]", "", price_text).replace(",", ".")
    )

    return price
