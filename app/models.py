from pydantic import BaseModel


class ProductCreate(BaseModel):
    url: str
    name: str


class ProductResponse(BaseModel):
    id: int
    url: str
    name: str