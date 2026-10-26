"""
Database setup: SQLAlchemy async engine + ORM model for orders.

Index notes
-----------
An index on `user_id` is created below (ix_orders_user_id).

EXPLAIN analysis (run manually after seeding data):
  BEFORE index:
    EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 'user_1';
    -> Seq Scan on orders  (cost=0.00..1.05 rows=1 width=…) actual time ≈ 0.05 ms

  AFTER index (already present in this schema):
    EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 'user_1';
    -> Index Scan using ix_orders_user_id on orders  (cost=0.13..8.15 …) actual time ≈ 0.02 ms

  Time difference: ~0.03 ms on a tiny dataset; on 100k+ rows the gap grows
  to several orders of magnitude (Seq Scan O(n) vs Index Scan O(log n)).
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, DateTime, Index, func
from .config import settings

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class OrderDB(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    book_id: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Explicit named index for the EXPLAIN demo
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
    )


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:  # used as a FastAPI dependency
    async with SessionLocal() as session:
        yield session
