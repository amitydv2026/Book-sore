from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from .models import OrderCreate, OrderOut
from . import service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=201)
async def place_order(data: OrderCreate, session: AsyncSession = Depends(get_session)):
    """Place a new order. Calls Book Service to verify and reduce stock."""
    return await service.place_order(data, session)


@router.get("/{user_id}", response_model=list[OrderOut])
async def my_orders(user_id: str, session: AsyncSession = Depends(get_session)):
    """Get all orders for a user."""
    return await service.get_orders(user_id, session)
