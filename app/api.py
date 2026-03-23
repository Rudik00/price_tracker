from fastapi import APIRouter
from data.database import add_products
from app.models import ProductCreate

router = APIRouter()


@router.post("/product")
def create_product(product: ProductCreate):
    print(product.url, product.name)

    add_products([(product.url, product.name)])

    return {
        "text": "hello"
    }