from fastapi import APIRouter
from data.database import add_product, get_product_by_id, get_product_by_url
from app.models import ProductCreate

router = APIRouter()


@router.post("/product")
def create_product(product: ProductCreate):

    product_id = add_product(product.url, product.name)

    return {
        "product_id": product_id
    }


@router.get("/get_price_id")
def get_price_id(product_id: int | None = None):
    # если есть product_id, то получаем цены по нему
    if product_id:
        product = get_product_by_id(product_id)
        if isinstance(product, dict):
            return {
                "price_now": product.get("price_now"),
                "price_max": product.get("price_max"),
                "price_min": product.get("price_min"),
            }
        elif isinstance(product, str):
            return {"error": f"{product}"}
    # если нет возвращаем ошибку
    else:
        return {"error": "Пожалуйста, укажите product_id"}


@router.get("/get_price_url")
def get_price_url(url: str | None = None):
    # если есть url, то получаем id по url а затем цены по id
    if url:
        product = get_product_by_url(url)
        if isinstance(product, dict):
            return {
                "price_now": product.get("price_now"),
                "price_max": product.get("price_max"),
                "price_min": product.get("price_min"),
            }
        elif isinstance(product, str):
            return {"error": f"{product}"}

    # если нет возвращаем ошибку
    else:
        return {"error": "Пожалуйста, укажите URL товара"}
