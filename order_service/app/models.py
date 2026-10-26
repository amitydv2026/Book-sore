from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


# ── Request / Response models ──────────────────────────────────────────────────

class OrderCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    book_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    payment_method: Literal["upi", "card"] = "upi"
    discount_type: Literal["none", "ten_percent"] = "none"


class OrderOut(BaseModel):
    id: int
    user_id: str
    book_id: str
    quantity: int
    unit_price: float
    total_price: float
    payment_method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
