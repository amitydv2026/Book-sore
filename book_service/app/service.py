from bson import ObjectId
from fastapi import HTTPException
from .database import get_books_collection
from .models import BookCreate, BookOut


def _doc_to_book(doc: dict) -> BookOut:
    return BookOut(
        id=str(doc["_id"]),
        title=doc["title"],
        author=doc["author"],
        price=doc["price"],
        stock=doc["stock"],
    )


async def create_book(data: BookCreate) -> BookOut:
    col = get_books_collection()
    result = await col.insert_one(data.model_dump())
    doc = await col.find_one({"_id": result.inserted_id})
    return _doc_to_book(doc)


async def list_books() -> list[BookOut]:
    col = get_books_collection()
    cursor = col.find({})
    docs = await cursor.to_list(length=1000)
    # functional style: map each doc to BookOut
    return list(map(_doc_to_book, docs))


async def get_book(book_id: str) -> BookOut:
    col = get_books_collection()
    try:
        oid = ObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book id")
    doc = await col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Book not found")
    return _doc_to_book(doc)


async def reduce_stock(book_id: str, quantity: int) -> BookOut:
    """Reduce stock atomically; raises 400 if stock is insufficient."""
    col = get_books_collection()
    try:
        oid = ObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book id")

    doc = await col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Book not found")
    if doc["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    updated = await col.find_one_and_update(
        {"_id": oid, "stock": {"$gte": quantity}},
        {"$inc": {"stock": -quantity}},
        return_document=True,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    return _doc_to_book(updated)
