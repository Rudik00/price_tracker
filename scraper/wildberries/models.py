from dataclasses import dataclass

@dataclass
class Product:
    id: str | None = None
    name: str = ""
    price: str = ""
    img: str | None = None
