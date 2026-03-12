from fastapi import APIRouter
from app.database import add_product
from app.models import ProductCreate

router = APIRouter()


@router.post("/product")
def create_product(product: ProductCreate):

    product_id = add_product(product.url, product.name)

    return {
        "id": product_id,
        "url": product.url,
        "name": product.name
    }