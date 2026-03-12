from fastapi import FastAPI
from app.database import init_db
from app.api import router

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


app.include_router(router)


@app.get("/")
def root():
    return {"status": "Price Tracker API running"}