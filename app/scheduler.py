import asyncio
import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.database import get_connection
from scrapers.wildberries.catalog.run_browser import run as run_catalog
from scrapers.wildberries.product.start_parser_products import parser_products_main


CATALOG_URL = "https://www.wildberries.ge/catalog/obuv/muzhskaya/kedy-i-krossovki"
CATALOG_SCROLLS = 1
CATALOG_INTERVAL_HOURS = 72
PRICE_INTERVAL_HOURS = 6

scheduler = AsyncIOScheduler()
_catalog_lock: Optional[asyncio.Lock] = None


def _get_lock() -> asyncio.Lock:
    """Возвращает глобальную блокировку, создавая её при необходимости."""

    global _catalog_lock
    if _catalog_lock is None:
        _catalog_lock = asyncio.Lock()
    return _catalog_lock


def _has_products() -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM products LIMIT 1")
    has = cursor.fetchone() is not None
    conn.close()
    return has


async def _do_catalog_parse() -> None:
    """Парсит каталог и сохраняет товары в БД."""

    print("\n\n\n[scheduler] запускаем парсер каталога")
    await asyncio.to_thread(run_catalog, CATALOG_URL, CATALOG_SCROLLS)
    print("[scheduler] парсер каталога завершён")


async def _run_catalog() -> None:
    """Задача планировщика для парсинга каталога."""

    async with _get_lock():
        await _do_catalog_parse()


async def _run_price_check() -> None:
    """Задача планировщика для проверки цен товаров."""

    async with _get_lock():
        if not _has_products():
            print("[scheduler] товаров нет — запускаем парсер каталога перед проверкой")
            await _do_catalog_parse()

        if not _has_products():
            print("[scheduler] после парсинга каталога товары не найдены — пропускаем проверку цен")
            return

        try:
            await parser_products_main()
        except Exception as exc:  # noqa: BLE001
            print(f"[scheduler] ошибка при проверке цен: {exc}")


async def startup_parse() -> None:
    """При старте всегда парсим каталог, затем цены."""

    async with _get_lock():
        await _do_catalog_parse()

        if not _has_products():
            print("[scheduler] товары не найдены — пропускаем проверку цен")
            return

        try:
            await parser_products_main()
        except Exception as exc:  # noqa: BLE001
            print(f"[scheduler] ошибка при проверке цен: {exc}")


def start_scheduler() -> None:
    """Запускает планировщик задач (парсер каталога + проверка цен)."""

    # Парсинг каталога — первый запуск через полный интервал
    # (каталог уже спарсен при старте).
    scheduler.add_job(
        _run_catalog,
        "interval",
        hours=CATALOG_INTERVAL_HOURS,
        id="catalog_parse_job",
        next_run_time=(
            datetime.datetime.now()
            + datetime.timedelta(hours=CATALOG_INTERVAL_HOURS)
        ),
        coalesce=False,
        misfire_grace_time=300,
        max_instances=10,
        replace_existing=True,
    )

    # Проверка цен — первый запуск через полный интервал
    # (цены уже проверены при старте).
    scheduler.add_job(
        _run_price_check,
        "interval",
        hours=PRICE_INTERVAL_HOURS,
        id="price_check_job",
        next_run_time=(
            datetime.datetime.now()
            + datetime.timedelta(hours=PRICE_INTERVAL_HOURS)
        ),
        coalesce=False,
        misfire_grace_time=300,
        max_instances=10,
        replace_existing=True,
    )

    scheduler.start()
    print(
        "[scheduler] запущен "
        f"(парсер каталога каждые {CATALOG_INTERVAL_HOURS} ч; "
        f"проверка цен каждые {PRICE_INTERVAL_HOURS} ч)"
    )


def stop_scheduler() -> None:
    """Останавливает планировщик при завершении работы приложения."""

    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[scheduler] остановлен")
