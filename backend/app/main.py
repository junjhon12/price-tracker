import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from app.db import (
    get_db,
    init_db,
    insert_item,
    insert_price_point,
    update_item_meta,
    get_all_items,
    get_item_by_id,
    get_price_history,
    get_all_item_ids,
)
from app.scraper import scrape_product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Price Tracker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AddItemRequest(BaseModel):
    url: HttpUrl


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/items", status_code=201)
async def add_item(body: AddItemRequest):
    url = str(body.url)
    result = await scrape_product(url)

    async with get_db() as db:
        item_id = await insert_item(db, url, result.title, result.image_url)
        await insert_price_point(db, item_id, result.price, result.error)

    return {
        "id": item_id,
        "url": url,
        "title": result.title,
        "image_url": result.image_url,
        "price": result.price,
        "error": result.error,
    }


@app.get("/items")
async def list_items():
    async with get_db() as db:
        return await get_all_items(db)


@app.get("/items/{item_id}/history")
async def item_history(item_id: int):
    async with get_db() as db:
        item = await get_item_by_id(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        history = await get_price_history(db, item_id)
    return {"item": item, "history": history}


@app.post("/items/{item_id}/refresh")
async def refresh_item(item_id: int):
    async with get_db() as db:
        item = await get_item_by_id(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        url = item["url"]

    result = await scrape_product(url)

    async with get_db() as db:
        await update_item_meta(db, item_id, result.title, result.image_url)
        await insert_price_point(db, item_id, result.price, result.error)

    return {
        "id": item_id,
        "price": result.price,
        "error": result.error,
    }


@app.post("/refresh-all")
async def refresh_all():
    async with get_db() as db:
        item_ids = await get_all_item_ids(db)

    results = []
    for item_id in item_ids:
        async with get_db() as db:
            item = await get_item_by_id(db, item_id)
        if not item:
            continue
        result = await scrape_product(item["url"])
        async with get_db() as db:
            await update_item_meta(db, item_id, result.title, result.image_url)
            await insert_price_point(db, item_id, result.price, result.error)
        results.append({"id": item_id, "price": result.price, "error": result.error})

    return results
