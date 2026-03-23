from .models import Product


def uniqueness_check(
    products: list[Product],
) -> list[Product]:
    unique = []
    seen = set()
    for p in products:
        key = (p.url)
        if key not in seen:
            seen.add(key)
            unique.append(p)

    print(f"Сохранено {len(unique)} уникальных товаров")
    return unique
