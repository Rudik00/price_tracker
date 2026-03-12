import requests


API_URL = "http://127.0.0.1:8000/product"


def add_product(url: str, name: str):

    data = {
        "url": url,
        "name": name
    }

    response = requests.post(API_URL, json=data)

    if response.status_code == 200:
        print("Product added:", response.json())
    else:
        print("Error:", response.text)


if __name__ == "__main__":
    add_product(
        "https://www.wildberries.ge/catalog/123456",
        "Test sneakers"
    )