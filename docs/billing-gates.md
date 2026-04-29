# Access Gates and Provider Adapters

## Overview

fastapi-saas-kit includes a pluggable provider adapter interface for access gates, entitlement checks, and external event handling. The current code-level interface is named `BillingProvider` for compatibility, but you can use it as a generic access provider adapter.

## Provider Adapter Interface

```python
class BillingProvider(ABC):
    async def create_order(self, user_id, plan, amount_cents, currency) -> OrderResult: ...
    async def verify_payment(self, order_id, payment_data) -> PaymentResult: ...
    async def handle_webhook(self, payload, signature) -> dict: ...
    async def get_billing_status(self, user_id) -> dict: ...
```

## Mock Provider for Development

The included `MockBillingProvider` returns deterministic development responses and does not require external credentials.

```python
from fastapi_saas_kit.billing.adapters.mock import MockBillingProvider
from fastapi_saas_kit.billing.router import configure_billing

configure_billing(MockBillingProvider())
```

## Access Gate Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/billing/create-order` | Create an access request through the configured adapter |
| POST | `/billing/verify-payment` | Verify an external provider event |
| POST | `/billing/webhook` | Handle provider webhooks |
| GET | `/billing/status` | Get user access status |

Endpoint paths remain stable for compatibility. New applications can wrap or rename routes at the application boundary if they prefer access-focused route names.

## Adding a Provider Adapter

1. Install the provider SDK if needed
2. Implement `BillingProvider`
3. Configure the provider during application initialization

```python
class ProviderAccessAdapter(BillingProvider):
    def __init__(self, credential: str):
        self.credential = credential

    async def create_order(self, user_id, plan, amount_cents, currency="USD"):
        provider_result = await self.provider_client.create_access_request(
            tier=plan,
            metadata={"user_id": user_id},
        )
        return OrderResult(
            order_id=provider_result.id,
            amount_cents=amount_cents,
            checkout_url=provider_result.redirect_url,
        )
```

## Security Notes

- Never commit real provider credentials to your repository
- Use environment variables for all provider credentials
- Always verify webhook signatures
- Log provider events for auditability
