from pydantic import BaseModel
from pydantic import field_validator
import re
from urllib.parse import urlparse


class ProductCreate(BaseModel):
    url: str
    name: str

    @field_validator("url")
    @classmethod
    def validate_wildberries_url(cls, value: str) -> str:
        value = value.strip()
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL должен быть валидным http/https адресом")

        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]

        is_wildberries = re.fullmatch(
            r"(?:[a-z0-9-]+\.)*wildberries\.[a-z.]+",
            host,
        ) is not None

        if not is_wildberries:
            raise ValueError("Разрешены только ссылки Wildberries")

        return value


class ProductResponse(BaseModel):
    id: int
    url: str
    name: str
