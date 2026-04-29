"""
Mock provider adapter for development and testing.
"""

import uuid

import structlog

from ..interfaces import BillingProvider, OrderResult, PaymentResult

logger = structlog.get_logger("saas_kit.billing.mock")

_mock_orders: dict[str, dict] = {}


class MockBillingProvider(BillingProvider):
    """Mock provider that simulates access flows.

    All access requests succeed immediately. Useful for local development,
    integration testing, and demo environments.
    """

    async def create_order(
        self,
        user_id: str,
        plan: str,
        amount_cents: int,
        currency: str = "USD",
    ) -> OrderResult:
        """Create a mock request that can be immediately verified."""
        order_id = f"mock_order_{uuid.uuid4().hex[:12]}"

        _mock_orders[order_id] = {
            "user_id": user_id,
            "plan": plan,
            "amount_cents": amount_cents,
            "currency": currency,
            "status": "created",
        }

        logger.info("mock_order_created", order_id=order_id, plan=plan, amount=amount_cents)

        return OrderResult(
            order_id=order_id,
            amount_cents=amount_cents,
            currency=currency,
            status="created",
            checkout_url=f"/billing/mock-checkout/{order_id}",
            metadata={"provider": "mock", "plan": plan},
        )

    async def verify_payment(
        self,
        order_id: str,
        payment_data: dict,
    ) -> PaymentResult:
        """Verify a mock provider event."""
        order = _mock_orders.get(order_id)
        if not order:
            return PaymentResult(
                payment_id=f"mock_pay_{uuid.uuid4().hex[:12]}",
                order_id=order_id,
                status="failed",
                plan="free",
                message="Order not found.",
            )

        payment_id = f"mock_pay_{uuid.uuid4().hex[:12]}"
        order["status"] = "verified"

        logger.info("mock_provider_event_verified", order_id=order_id, payment_id=payment_id, plan=order["plan"])

        return PaymentResult(
            payment_id=payment_id,
            order_id=order_id,
            status="verified",
            plan=order["plan"],
            message=f"Mock provider event for {order['plan'].title()} tier verified successfully.",
        )

    async def handle_webhook(
        self,
        payload: dict,
        signature: str,
    ) -> dict:
        """Handle a mock webhook."""
        logger.info("mock_webhook_received", event_type=payload.get("event_type", "unknown"))
        return {"status": "processed", "provider": "mock"}

    async def get_billing_status(self, user_id: str) -> dict:
        """Get mock access status for a user."""
        user_orders = {oid: order for oid, order in _mock_orders.items() if order.get("user_id") == user_id}

        return {
            "provider": "mock",
            "user_id": user_id,
            "orders": [
                {
                    "order_id": oid,
                    "plan": order["plan"],
                    "status": order["status"],
                    "amount_cents": order["amount_cents"],
                }
                for oid, order in user_orders.items()
            ],
        }
