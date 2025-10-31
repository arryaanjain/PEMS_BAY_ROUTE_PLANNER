from pydantic import BaseModel
from typing import Optional


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ItemRead(ItemCreate):
    id: int

    class Config:
        orm_mode = True
