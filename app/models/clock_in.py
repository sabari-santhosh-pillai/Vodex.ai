from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClockInCreate(BaseModel):
    email: str
    location: str

class ClockInUpdate(BaseModel):
    location: Optional[str] = None

class ClockInResponse(ClockInCreate):
    id: str
    insert_datetime: datetime
