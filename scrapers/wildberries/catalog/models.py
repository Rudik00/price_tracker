from dataclasses import dataclass

@dataclass
class Product:
    url: str | None = None
    name: str = ""
    price: str = ""