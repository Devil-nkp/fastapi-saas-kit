"""
Billing interfaces — abstract base class for pluggable billing providers.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class OrderResult(BaseModel):
    """Result of creating a billing order."""

    order_id: str
    amount_cents: int
    currency: str = "USD"
    status: str = "created"
    checkout_url: str | None = None
    metadata: dict = {}


class PaymentResult(BaseModel):
    """Result of verifying a payment."""

    payment_id: str
    order_id: str
    status: str  # verified, failed, pending
    plan: str
    message: str = ""


class BillingProvider(ABC):
    """Abstract interface for billing/payment providers.

    Implement this interface to integrate your preferred payment
    processor (Stripe, Paddle, LemonSqueezy, etc.).

    The boilerplate ships with a MockBillingProvider for development
    and a StripeStubProvider as a starting point for Stripe integration.

    Example:
        class StripeBillingProvider(BillingProvider):
            async def create_order(self, user_id, plan, amount_cents):
                session = stripe.checkout.Session.create(...)
                return OrderResult(order_id=session.id, ...)

            async def verify_payment(self, order_id, payment_data):
                # Verify webhook signature and payment status
                return PaymentResult(...)
    """

    @abstractmethod
    async def create_order(
        self,
        user_id: str,
        plan: str,
        amount_cents: int,
        currency: str = "USD",
    ) -> OrderResult:
        """Create a new billing order for a plan purchase.

        Args:
            user_id: The purchasing user's ID.
            plan: The plan being purchased.
            amount_cents: Amount in cents.
            currency: Currency code.

        Returns:
            OrderResult with order details.
        """
        ...

    @abstractmethod
    async def verify_payment(
        self,
        order_id: str,
        payment_data: dict,
    ) -> PaymentResult:
        """Verify a payment after the user completes checkout.

        Args:
            order_id: The order ID from create_order.
            payment_data: Provider-specific payment verification data.

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
        """Handle an incoming webhook from the payment provider.

        Args:
            payload: The webhook payload.
            signature: The webhook signature for verification.

        Returns:
            Processing result.
        """
        ...

    @abstractmethod
    async def get_billing_status(self, user_id: str) -> dict:
        """Get the current billing status for a user.

        Args:
            user_id: The user's ID.

        Returns:
            Dict with billing status details.
        """
        ...
