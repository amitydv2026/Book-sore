"""
Unit tests for Order Service logic (no real DB or HTTP calls).
"""
import pytest
from app.service import order_total
from app.discount import NoDiscount, TenPercentDiscount, get_discount_strategy
from app.payment import PaymentFactory, UPIPayment, CardPayment


# ── discount tests ──────────────────────────────────────────────────────────

def test_no_discount():
    s = NoDiscount()
    assert s.apply(100.0) == 100.0


def test_ten_percent_discount():
    s = TenPercentDiscount()
    assert s.apply(100.0) == 90.0


def test_get_discount_strategy_none():
    s = get_discount_strategy("none")
    assert isinstance(s, NoDiscount)


def test_get_discount_strategy_ten_percent():
    s = get_discount_strategy("ten_percent")
    assert isinstance(s, TenPercentDiscount)


# ── payment factory tests ───────────────────────────────────────────────────

def test_factory_upi():
    p = PaymentFactory.create("upi")
    assert isinstance(p, UPIPayment)
    result = p.process(50.0, "user_1")
    assert result["method"] == "upi"
    assert result["status"] == "success"


def test_factory_card():
    p = PaymentFactory.create("card")
    assert isinstance(p, CardPayment)
    result = p.process(50.0, "user_1")
    assert result["method"] == "card"


# ── functional total calculation ────────────────────────────────────────────

def test_order_total_no_discount():
    total = order_total([29.99], 2, "none")
    assert total == pytest.approx(59.98, rel=1e-3)


def test_order_total_ten_percent():
    total = order_total([100.0], 1, "ten_percent")
    assert total == pytest.approx(90.0, rel=1e-3)


def test_order_total_filters_nonpositive():
    # negative/zero prices should be filtered out
    total = order_total([0.0, -5.0, 10.0], 2, "none")
    assert total == pytest.approx(20.0, rel=1e-3)
