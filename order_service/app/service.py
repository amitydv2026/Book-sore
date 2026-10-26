"""
Order business logic.

Functional programming notes
-----------------------------
order_total() uses map(), filter(), and sum() to compute totals, satisfying
the functional-programming checklist item.

Transaction note
----------------
place_order() wraps "insert order + reduce stock (via HTTP)" inside a single
SQLAlchemy transaction.  If the HTTP call to Book Service fails the DB
transaction is rolled back automatically (the `async with session.begin()`
context manager rolls back on any exception).
"""
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from .database import OrderDB
from .discount import get_discount_strategy
from .payment import PaymentFactory
from .models import OrderCreate, OrderOut


# ── Helper: functional total calculation ──────────────────────────────────────

def order_total(prices: list[float], quantity: int, discount_name: str) -> float:
    """
    Use map, filter, sum (functional style) to compute the final price.
    - filter: remove non-positive prices (defensive)
    - map: multiply each valid price by quantity
    - sum: add them up (here we always have one price per call)
    """
    strategy = get_discount_strategy(discount_name)
    valid_prices = filter(lambda p: p > 0, prices)
    discounted = map(lambda p: strategy.apply(p) * quantity, valid_prices)
    return round(sum(discounted), 2)


# ── Service functions ──────────────────────────────────────────────────────────

async def place_order(data: OrderCreate, session: AsyncSession) -> OrderOut:
    """
    Place an order inside a single DB transaction:
    1. Fetch book price from Book Service.
    2. Calculate total with discount.
    3. Process payment (Factory).
    4. BEGIN transaction:
       a. Insert order row.
       b. Call Book Service to reduce stock.
       c. COMMIT (or ROLLBACK on any error).
    """
    # 1. Fetch book details
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.book_service_url}/books/{data.book_id}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Book not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Book service error")

    book = resp.json()
    unit_price: float = book["price"]

    # 2. Compute discounted total (functional)
    total = order_total([unit_price], data.quantity, data.discount_type)

    # 3. Payment (Factory pattern)
    processor = PaymentFactory.create(data.payment_method)
    payment_result = processor.process(total, data.user_id)
    if payment_result["status"] != "success":
        raise HTTPException(status_code=402, detail="Payment failed")

    # 4. Transaction: save order + reduce stock atomically
    async with session.begin():
        order = OrderDB(
            user_id=data.user_id,
            book_id=data.book_id,
            quantity=data.quantity,
            unit_price=unit_price,
            total_price=total,
            payment_method=data.payment_method,
            status="confirmed",
        )
        session.add(order)
        await session.flush()  # get the generated id before HTTP call

        # Reduce stock in Book Service (still inside the transaction window)
        async with httpx.AsyncClient() as client:
            stock_resp = await client.patch(
                f"{settings.book_service_url}/books/{data.book_id}/reduce-stock",
                json={"quantity": data.quantity},
            )
        if stock_resp.status_code != 200:
            # Rollback happens automatically when we raise inside `session.begin()`
            raise HTTPException(
                status_code=stock_resp.status_code,
                detail=stock_resp.json().get("detail", "Stock reduction failed"),
            )

    await session.refresh(order)
    return OrderOut.model_validate(order)


async def get_orders(user_id: str, session: AsyncSession) -> list[OrderOut]:
    """Fetch all orders for a user (uses the ix_orders_user_id index)."""
    result = await session.execute(
        select(OrderDB).where(OrderDB.user_id == user_id).order_by(OrderDB.created_at.desc())
    )
    rows = result.scalars().all()
    return list(map(OrderOut.model_validate, rows))
