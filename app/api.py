from fastapi import APIRouter
from data.database import add_products
from app.models import ProductCreate

router = APIRouter()


@router.post("/product")
def create_product(product: ProductCreate):

    product_id = add_products(product.url, product.name)

    return {
        "id": product_id,
        "url": product.url,
        "name": product.name
    }