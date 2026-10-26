from pydantic import BaseModel, Field
from typing import Optional


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class BookOut(BaseModel):
    id: str
    title: str
    author: str
    price: float
    stock: int


class StockReduceRequest(BaseModel):
    quantity: int = Field(..., gt=0)
