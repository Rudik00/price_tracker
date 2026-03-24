import logging

from .models import Product


logger = logging.getLogger(__name__)


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

    logger.info("Сохранено %s уникальных товаров", len(unique))
    return unique
