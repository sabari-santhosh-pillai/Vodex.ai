from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: date

class ItemUpdate(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    expiry_date: Optional[date] = None

class ItemResponse(ItemCreate):
    id: str
    insert_date: date
