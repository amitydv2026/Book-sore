# Book Store — Python FastAPI Microservices

Two FastAPI services: **Book Service** (MongoDB) and **Order Service** (PostgreSQL).

## Quick Start

```bash
docker compose up --build
```

| Service        | URL                        |
|----------------|----------------------------|
| Book Service   | http://localhost:8000/docs |
| Order Service  | http://localhost:8001/docs |

---

## Project Layout

```
Book Store/
├── book_service/
│   ├── app/
│   │   ├── config.py      # settings (pydantic-settings)
│   │   ├── database.py    # Motor async MongoDB client
│   │   ├── models.py      # Pydantic request/response models
│   │   ├── service.py     # business logic
│   │   ├── routes.py      # FastAPI router
│   │   └── main.py        # app entry point
│   ├── tests/
│   │   └── test_books.py
│   ├── Dockerfile
│   ├── Makefile
│   └── pyproject.toml
│
├── order_service/
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py    # SQLAlchemy async + ORM model + index
│   │   ├── models.py
│   │   ├── discount.py    # Strategy pattern (ABC)
│   │   ├── payment.py     # Factory pattern
│   │   ├── service.py     # business logic + transaction
│   │   ├── routes.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_orders.py
│   ├── Dockerfile
│   ├── Makefile
│   └── pyproject.toml
│
├── docker-compose.yml
├── Jenkinsfile
├── Makefile
├── README.md
└── task.txt
```

---

## API Endpoints

### Book Service (port 8000)

| Method | Path                              | Description           |
|--------|-----------------------------------|-----------------------|
| POST   | `/books/`                         | Add a book            |
| GET    | `/books/`                         | List all books        |
| GET    | `/books/{id}`                     | Get one book          |
| PATCH  | `/books/{id}/reduce-stock`        | Reduce stock          |

### Order Service (port 8001)

| Method | Path                | Description                |
|--------|---------------------|----------------------------|
| POST   | `/orders/`          | Place an order             |
| GET    | `/orders/{user_id}` | Get orders for a user      |

---

## Design Patterns

### Strategy — Discounts (`order_service/app/discount.py`)

```
DiscountStrategy (ABC)
├── NoDiscount
└── TenPercentDiscount
```

Pass `"discount_type": "ten_percent"` in the order payload to get 10 % off.

### Factory — Payments (`order_service/app/payment.py`)

```
PaymentFactory.create("upi")  → UPIPayment
PaymentFactory.create("card") → CardPayment
```

---

## Functional Programming

`order_service/app/service.py → order_total()` uses:

```python
valid_prices = filter(lambda p: p > 0, prices)
discounted   = map(lambda p: strategy.apply(p) * quantity, valid_prices)
total        = sum(discounted)
```

---

## Transaction

`place_order()` in `order_service/app/service.py` wraps the DB insert **and** the
HTTP call to reduce stock inside `async with session.begin()`.  If the stock
call fails, SQLAlchemy rolls back the order row automatically.

---

## Query Optimisation — Index & EXPLAIN

The `orders` table has an index on `user_id` (created in `database.py`):

```sql
CREATE INDEX ix_orders_user_id ON orders (user_id);
```

### EXPLAIN results (run inside the PostgreSQL container)

```sql
-- connect: docker compose exec postgres psql -U postgres orderdb

-- Seed 10,000 rows first:
-- INSERT INTO orders ... FROM generate_series(1, 10000);

-- BEFORE index (drop it temporarily to test):
DROP INDEX ix_orders_user_id;
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 'user_1';
-- → Seq Scan on orders  (cost=0.00..142.99 rows=8 width=584)
--   actual time=0.026..2.696 rows=99 loops=1
--   Execution Time: 2.755 ms

-- AFTER index:
CREATE INDEX ix_orders_user_id ON orders (user_id);
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 'user_1';
-- → Bitmap Heap Scan on orders  (cost=5.05..128.46 rows=99 width=62)
--   actual time=0.141..0.252 rows=99 loops=1
--   Execution Time: 0.384 ms
```

**Time difference: 2.755 ms → 0.384 ms — 7× faster on 10,000 rows.**  
Without the index PostgreSQL did a Seq Scan and read all 10,001 rows, discarding 9,902.  
With the index it used a Bitmap Index Scan and jumped straight to the 99 matching rows.  
On millions of rows the gap grows to 100× or more (Seq Scan is O(n), Index Scan is O(log n)).

---

## Jenkins Pipeline (3 steps)

1. **Install** — `pip install -e ".[dev]"` for both services (parallel)  
2. **Test** — `pytest tests/ -v` for both services (parallel)  
3. **Build** — `docker build` for both images (parallel)

---

## Skill Checklist

| Skill                | How it is covered |
|----------------------|--------------------------------------------------|
| Functional Programming | `map`, `filter`, `sum` in `order_total()` |
| SOLID                | ABC `DiscountStrategy`; separate files per layer |
| Design Patterns      | Strategy (discounts) + Factory (payments) |
| Microservices        | Order Service calls Book Service via HTTP |
| Transactions         | `session.begin()` wraps order + stock reduction |
| Query Optimisation   | Index on `user_id`, EXPLAIN results above |
| NoSQL                | MongoDB (Motor async) for Book Service |
| Docker               | Dockerfile per service + docker-compose.yml |
| Jenkins              | 3-stage Jenkinsfile |
| Build Tools          | `pyproject.toml` + `Makefile` per service |

---

## Resume Lines

- Built 2 Python FastAPI microservices (PostgreSQL and MongoDB) deployed with Docker Compose.  
- Used a database transaction to keep orders and stock consistent.  
- Added an index to speed up order history queries, checked with EXPLAIN.  
- Applied Strategy and Factory patterns with SOLID principles.  
- Created a Jenkins pipeline for automatic tests and Docker builds.  
- Collected client demo feedback and improved the project.
