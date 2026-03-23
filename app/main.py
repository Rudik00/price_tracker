from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router
from data.database import init_db
from app.scheduler import (
    startup_parse,
    start_scheduler,
    stop_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # На запуске (startup)
    init_db()

    # Всегда парсим каталог и цены при старте.
    await startup_parse()

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
