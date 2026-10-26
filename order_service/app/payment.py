"""
Factory pattern for payment processors.
"""
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Abstract payment processor."""

    @abstractmethod
    def process(self, amount: float, user_id: str) -> dict:
        """Process a payment and return a result dict."""


class UPIPayment(PaymentProcessor):
    def process(self, amount: float, user_id: str) -> dict:
        # In production this would call a UPI gateway SDK.
        return {"method": "upi", "status": "success", "amount": amount, "user": user_id}


class CardPayment(PaymentProcessor):
    def process(self, amount: float, user_id: str) -> dict:
        # In production this would call a card gateway SDK.
        return {"method": "card", "status": "success", "amount": amount, "user": user_id}


class PaymentFactory:
    """Factory that creates the right PaymentProcessor."""

    @staticmethod
    def create(method: str) -> PaymentProcessor:
        if method == "card":
            return CardPayment()
        return UPIPayment()
