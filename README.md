# Price Tracker

Сервис для отслеживания цен товаров Wildberries.

## Коротко

- FastAPI API для добавления товара и получения цен.
- Парсинг каталога и карточек товаров через Playwright.
- SQLite для хранения товаров и истории цен.
- Планировщик:
  - каталог каждые 72 часа,
  - цены каждые 6 часов.
- Логи пишутся в `logs/app.log`.

## Быстрый старт

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
uvicorn app.main:app --reload
```

После запуска:
- API: `http://127.0.0.1:8000`
- Документация: `http://127.0.0.1:8000/docs`

## API

- `POST /product` — добавить товар по `url` и `name`.
- `GET /get_price_id?product_id=1` — получить цену по id.
- `GET /get_price_url?url=...` — получить цену по URL.

Ограничение URL в `POST /product`:
- только `http/https`,
- только домены Wildberries.
