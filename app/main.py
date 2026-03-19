from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router
from app.database import init_db
from app.scheduler import (
    ensure_products_exist,
    run_price_check_once,
    start_scheduler,
    stop_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # На запуске (startup)
    init_db()

    # Если в базе нет ни одного товара — сначала парсим каталог.
    await ensure_products_exist()

    # Один раз проверяем цены сразу при старте.
    await run_price_check_once()

    # Затем запускаем планировщик для повторных задач.
    start_scheduler()

    yield

    # На остановке (shutdown)
    stop_scheduler()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("/")
def root():
    return {"status": "Price Tracker API running"}