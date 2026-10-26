"""
Strategy pattern for discounts.

SOLID notes
-----------
- Single Responsibility : each class has one job (apply its discount).
- Open/Closed           : add a new discount by subclassing, not editing.
- Liskov Substitution   : any DiscountStrategy can replace another.
- Interface Segregation : the ABC exposes only what callers need.
- Dependency Inversion  : service depends on the DiscountStrategy ABC,
                          not on concrete classes.
"""
from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """Abstract base class for all discount strategies."""

    @abstractmethod
    def apply(self, price: float) -> float:
        """Return the discounted price."""


class NoDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price


class TenPercentDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return round(price * 0.90, 2)


def get_discount_strategy(name: str) -> DiscountStrategy:
    """Simple factory helper that maps a name to a strategy."""
    strategies: dict[str, DiscountStrategy] = {
        "none": NoDiscount(),
        "ten_percent": TenPercentDiscount(),
    }
    return strategies.get(name, NoDiscount())
