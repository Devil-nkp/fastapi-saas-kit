"""
External provider stub for access-gate integrations.

This stub shows the structure for wiring a provider SDK behind the
stable BillingProvider interface. It does not contain working provider
code or credentials.
"""

import structlog

from ..interfaces import BillingProvider, OrderResult, PaymentResult

logger = structlog.get_logger("saas_kit.billing.stripe")


class StripeBillingStub(BillingProvider):
    """Stub provider adapter.

    The class name is kept for compatibility with the existing import path.
    Replace the placeholder implementations with provider SDK calls.
    """

    async def create_order(
        self,
        user_id: str,
        plan: str,
        amount_cents: int,
        currency: str = "USD",
    ) -> OrderResult:
        """Create an external provider request."""
        raise NotImplementedError(
            "Provider integration not configured. "
            "Install the provider SDK and implement this method. "
            "See docs/billing-gates.md for guidance."
        )

    async def verify_payment(
        self,
        order_id: str,
        payment_data: dict,
    ) -> PaymentResult:
        """Verify provider callback data."""
        raise NotImplementedError("Provider verification not configured.")

    async def handle_webhook(
        self,
        payload: dict,
        signature: str,
    ) -> dict:
        """Handle provider webhook events."""
        raise NotImplementedError("Provider webhook handling not configured.")

    async def get_billing_status(self, user_id: str) -> dict:
        """Get access status from the provider."""
        raise NotImplementedError("Provider status lookup not configured.")
