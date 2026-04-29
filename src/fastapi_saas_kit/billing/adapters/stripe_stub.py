"""
Stripe billing stub — starting point for Stripe integration.

This is a stub implementation that shows the structure for a
real Stripe integration. It does NOT contain working Stripe code.
You must install the `stripe` package and add your own API keys
to make this work.

Install:
    pip install stripe

Configure:
    BILLING_PROVIDER=stripe
    # Add your Stripe keys to .env (not tracked in git)
"""

import structlog

from ..interfaces import BillingProvider, OrderResult, PaymentResult

logger = structlog.get_logger("saas_kit.billing.stripe")


class StripeBillingStub(BillingProvider):
    """Stub Stripe billing provider.

    This is a starting point for integrating Stripe Checkout.
    Replace the placeholder implementations with actual Stripe
    API calls using the stripe Python package.

    See: https://stripe.com/docs/payments/checkout
    """

    async def create_order(
        self,
        user_id: str,
        plan: str,
        amount_cents: int,
        currency: str = "USD",
    ) -> OrderResult:
        """Create a Stripe Checkout session.

        TODO: Implement with:
            import stripe
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[...],
                mode="subscription" or "payment",
                success_url="...",
                cancel_url="...",
            )
        """
        raise NotImplementedError(
            "Stripe integration not configured. "
            "Install the stripe package and implement this method. "
            "See docs/billing-gates.md for guidance."
        )

    async def verify_payment(
        self,
        order_id: str,
        payment_data: dict,
    ) -> PaymentResult:
        """Verify a Stripe payment.

        TODO: Implement with:
            session = stripe.checkout.Session.retrieve(order_id)
            if session.payment_status == "paid":
                return PaymentResult(status="verified", ...)
        """
        raise NotImplementedError("Stripe payment verification not configured.")

    async def handle_webhook(
        self,
        payload: dict,
        signature: str,
    ) -> dict:
        """Handle Stripe webhook events.

        TODO: Implement with:
            import stripe
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            # Handle event types like checkout.session.completed
        """
        raise NotImplementedError("Stripe webhook handling not configured.")

    async def get_billing_status(self, user_id: str) -> dict:
        """Get billing status from Stripe.

        TODO: Implement by querying Stripe Customer and Subscription objects.
        """
        raise NotImplementedError("Stripe billing status not configured.")
