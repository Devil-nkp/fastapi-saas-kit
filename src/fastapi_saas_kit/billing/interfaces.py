"""
Provider adapter interfaces for access gates and external events.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class OrderResult(BaseModel):
    """Result of creating a provider access request."""

    order_id: str
    amount_cents: int
    currency: str = "USD"
    status: str = "created"
    checkout_url: str | None = None
    metadata: dict = {}


class PaymentResult(BaseModel):
    """Result of verifying a provider event."""

    payment_id: str
    order_id: str
    status: str  # verified, failed, pending
    plan: str
    message: str = ""


class BillingProvider(ABC):
    """Abstract interface for provider adapters.

    Implement this interface to integrate your preferred external
    access or entitlement provider. The class name is kept stable for
    compatibility with existing code.
    """

    @abstractmethod
    async def create_order(
        self,
        user_id: str,
        plan: str,
        amount_cents: int,
        currency: str = "USD",
    ) -> OrderResult:
        """Create a new access request through the provider adapter.

        Args:
            user_id: The user's ID.
            plan: The requested access tier.
            amount_cents: Optional amount field used by some adapters.
            currency: Currency code for adapters that need it.

        Returns:
            OrderResult with provider request details.
        """
        ...

    @abstractmethod
    async def verify_payment(
        self,
        order_id: str,
        payment_data: dict,
    ) -> PaymentResult:
        """Verify provider callback data.

        Args:
            order_id: The order ID from create_order.
            payment_data: Provider-specific verification data.

        Returns:
            PaymentResult with verification status.
        """
        ...

    @abstractmethod
    async def handle_webhook(
        self,
        payload: dict,
        signature: str,
    ) -> dict:
        """Handle an incoming webhook from the provider.

        Args:
            payload: The webhook payload.
            signature: The webhook signature for verification.

        Returns:
            Processing result.
        """
        ...

    @abstractmethod
    async def get_billing_status(self, user_id: str) -> dict:
        """Get the current access status for a user.

        Args:
            user_id: The user's ID.

        Returns:
            Dict with access status details.
        """
        ...
