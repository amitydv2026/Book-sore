from fastapi import APIRouter
from .models import BookCreate, BookOut, StockReduceRequest
from . import service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookOut, status_code=201)
async def add_book(data: BookCreate):
    """Add a new book to the catalogue."""
    return await service.create_book(data)


@router.get("/", response_model=list[BookOut])
async def list_books():
    """Return all books."""
    return await service.list_books()


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: str):
    """Return a single book by its id."""
    return await service.get_book(book_id)


@router.patch("/{book_id}/reduce-stock", response_model=BookOut)
async def reduce_stock(book_id: str, body: StockReduceRequest):
    """Reduce the stock of a book by the given quantity."""
    return await service.reduce_stock(book_id, body.quantity)
