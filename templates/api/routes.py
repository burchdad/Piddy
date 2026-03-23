"""
FastAPI REST API Template
=========================
Clone this folder and customize for a new API endpoint.

Usage:
    cp -r templates/api/ src/my_api/
    # Edit routes, models, and config as needed
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/template", tags=["template"])


# --- Models ---

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


# --- In-memory store (replace with database) ---

_items: dict[int, dict] = {}
_next_id = 1


# --- Routes ---

@router.get("/items", response_model=list[ItemResponse])
async def list_items():
    return [ItemResponse(id=k, **v) for k, v in _items.items()]


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(id=item_id, **_items[item_id])


@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    global _next_id
    _items[_next_id] = item.model_dump()
    result = ItemResponse(id=_next_id, **_items[_next_id])
    _next_id += 1
    logger.info(f"Created item: {result.name}")
    return result


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
