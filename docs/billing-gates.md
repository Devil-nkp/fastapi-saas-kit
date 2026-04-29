# Billing Gates

## Overview

fastapi-saas-kit uses a pluggable `BillingProvider` interface for payment processing. This allows you to integrate any payment provider without changing your application code.

## BillingProvider Interface

```python
class BillingProvider(ABC):
    async def create_order(self, user_id, plan, amount_cents, currency) -> OrderResult: ...
    async def verify_payment(self, order_id, payment_data) -> PaymentResult: ...
    async def handle_webhook(self, payload, signature) -> dict: ...
    async def get_billing_status(self, user_id) -> dict: ...
```

## MockBillingProvider (Development)

All payments succeed immediately. No real money is charged.

```python
from fastapi_saas_kit.billing.adapters.mock import MockBillingProvider
from fastapi_saas_kit.billing.router import configure_billing

configure_billing(MockBillingProvider())
```

## Billing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/billing/create-order` | Create a billing order |
| POST | `/billing/verify-payment` | Verify a completed payment |
| POST | `/billing/webhook` | Handle provider webhooks |
| GET | `/billing/status` | Get user billing status |

## Adding a Real Payment Provider

1. Install your provider's SDK
2. Implement `BillingProvider`
3. Configure at startup

```python
class ProviderBillingProvider(BillingProvider):
    def __init__(self, credential: str):
        self.credential = credential

    async def create_order(self, user_id, plan, amount_cents, currency="USD"):
        provider_order = await self.provider_client.create_checkout(
            plan=plan,
            amount_cents=amount_cents,
            currency=currency,
            metadata={"user_id": user_id},
        )
        return OrderResult(
            order_id=provider_order.id,
            amount_cents=amount_cents,
            checkout_url=provider_order.checkout_url,
        )
    # ... implement other methods
```

## Security Notes

- **Never** commit real payment credentials to your repository
- Use environment variables for all payment credentials
- Always verify webhook signatures
- Log all billing events for audit purposes
