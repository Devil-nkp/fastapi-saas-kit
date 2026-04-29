"""
Billing router — endpoints for order creation, payment verification, and status.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..auth.dependencies import get_current_user
from ..auth.models import CurrentUser
from ..plans.config import PLAN_CONFIG, is_valid_plan
from .adapters.mock import MockBillingProvider
from .interfaces import BillingProvider

logger = structlog.get_logger("saas_kit.billing")
router = APIRouter(prefix="/billing", tags=["Billing"])

# Module-level billing provider instance
_billing_provider: BillingProvider | None = None


def configure_billing(provider: BillingProvider) -> None:
    """Configure the global billing provider."""
    global _billing_provider
    _billing_provider = provider
    logger.info("billing_provider_configured", provider=type(provider).__name__)


def get_billing_provider() -> BillingProvider:
    """Get the configured billing provider, defaulting to MockBillingProvider."""
    if _billing_provider is None:
        return MockBillingProvider()
    return _billing_provider


class CreateOrderRequest(BaseModel):
    plan: str


class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_data: dict = {}


@router.post("/create-order")
async def create_order(
    req: CreateOrderRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Create a billing order for a plan purchase."""
    if not is_valid_plan(req.plan) or req.plan == "free":
        raise HTTPException(status_code=400, detail="Invalid plan. Choose 'pro' or 'business'.")

    plan_config = PLAN_CONFIG.get(req.plan)
    if not plan_config:
        raise HTTPException(status_code=400, detail="Plan configuration not found.")

    provider = get_billing_provider()
    order = await provider.create_order(
        user_id=user.id,
        plan=req.plan,
        amount_cents=plan_config["price_cents"],
    )
    return order.model_dump()


@router.post("/verify-payment")
async def verify_payment(
    req: VerifyPaymentRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Verify a payment after the user completes checkout."""
    provider = get_billing_provider()
    result = await provider.verify_payment(
        order_id=req.order_id,
        payment_data=req.payment_data,
    )
    return result.model_dump()


@router.post("/webhook")
async def billing_webhook(request: Request):
    """Handle incoming billing provider webhook events."""
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.") from exc

    signature = request.headers.get("x-webhook-signature", "")

    provider = get_billing_provider()
    result = await provider.handle_webhook(payload, signature)
    return result


@router.get("/status")
async def billing_status(
    user: CurrentUser = Depends(get_current_user),
):
    """Get current billing status for the authenticated user."""
    provider = get_billing_provider()
    status = await provider.get_billing_status(user.id)
    return status
