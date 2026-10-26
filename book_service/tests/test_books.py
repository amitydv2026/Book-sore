"""
Unit tests for the Book Service using an in-memory mock for MongoDB.
Run with: pytest
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def make_doc(book_id="6639b1a1b1a1b1a1b1a1b1a1"):
    return {
        "_id": __import__("bson").ObjectId(book_id),
        "title": "Clean Code",
        "author": "Robert Martin",
        "price": 29.99,
        "stock": 10,
    }


@patch("app.service.get_books_collection")
def test_list_books(mock_col_fn):
    col = MagicMock()
    col.find.return_value.to_list = AsyncMock(return_value=[make_doc()])
    mock_col_fn.return_value = col

    resp = client.get("/books/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Clean Code"


@patch("app.service.get_books_collection")
def test_add_book(mock_col_fn):
    doc = make_doc()
    col = MagicMock()
    col.insert_one = AsyncMock(return_value=MagicMock(inserted_id=doc["_id"]))
    col.find_one = AsyncMock(return_value=doc)
    mock_col_fn.return_value = col

    resp = client.post(
        "/books/",
        json={"title": "Clean Code", "author": "Robert Martin", "price": 29.99, "stock": 10},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Clean Code"


@patch("app.service.get_books_collection")
def test_reduce_stock(mock_col_fn):
    doc = make_doc()
    updated_doc = {**doc, "stock": 8}
    col = MagicMock()
    col.find_one = AsyncMock(return_value=doc)
    col.find_one_and_update = AsyncMock(return_value=updated_doc)
    mock_col_fn.return_value = col

    resp = client.patch("/books/6639b1a1b1a1b1a1b1a1b1a1/reduce-stock", json={"quantity": 2})
    assert resp.status_code == 200
    assert resp.json()["stock"] == 8
