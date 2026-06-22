from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_all
from router_logic import get_routing_rules
from routers.chat import router as chat_router
from routers.providers import router as providers_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_all()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(providers_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/router")
def get_router():
    return get_routing_rules()
