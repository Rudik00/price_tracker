from fastapi import APIRouter
from data.database import add_product
from app.models import ProductCreate

router = APIRouter()


@router.post("/product")
def create_product(product: ProductCreate):
    print(product.url, product.name)

    product_id = add_product(product.url, product.name)

    return {
        "product_id": product_id
    }
