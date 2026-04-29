# Access Tiers and Usage Limits

## Access Tier Configuration

Three access tiers are included by default. Customize their internal config in `src/fastapi_saas_kit/plans/config.py`:

| Feature | Free | Pro | Advanced |
|---------|------|-----|----------|
| Monthly Requests | 100 | 5,000 | Unlimited |
| Team Members | 1 | 10 | 100 |
| Projects | 3 | 25 | Unlimited |
| Storage (MB) | 100 | 5,000 | 50,000 |
| API Access | yes | yes | yes |
| Basic Analytics | yes | yes | yes |
| Advanced Analytics | no | yes | yes |
| Priority Support | no | yes | yes |
| Custom Branding | no | no | yes |
| Export Data | no | yes | yes |
| Webhooks | no | yes | yes |
| SSO | no | no | yes |

The code still uses the `plan` field for compatibility. Public-facing docs describe these values as access tiers.

## Access Tier Hierarchy

```python
from fastapi_saas_kit.plans.config import can_access_plan

can_access_plan("pro", "free")       # True: pro tier >= free tier
can_access_plan("free", "pro")       # False: free tier < pro tier
can_access_plan("free", "free")      # True: equal
```

## Feature Gates

```python
from fastapi_saas_kit.plans.config import has_feature
from fastapi_saas_kit.plans.access import require_feature

if has_feature(user.plan, "advanced_analytics"):
    ...

@router.get("/analytics")
async def analytics(user=Depends(require_feature("advanced_analytics"))):
    ...
```

## Quota Enforcement

```python
from fastapi_saas_kit.plans.quota import check_quota, get_usage_stats

await check_quota(user, "monthly_requests", current_usage=50)
# Raises HTTP 402 if over the configured usage limit

stats = get_usage_stats("pro", {"monthly_requests": 2500, "projects": 10})
```

## Period Reset

Quotas operate on a 30-day rolling window:

```python
from fastapi_saas_kit.plans.quota import should_reset_period

if should_reset_period(user.period_start):
    # Reset usage counters
    ...
```

## Adding Custom Access Tiers

Edit `PLAN_CONFIG` in `plans/config.py`:

```python
PLAN_CONFIG["enterprise"] = {
    "display_name": "Enterprise",
    "price_cents": 0,
    "price_display": "Custom",
    "quotas": {
        "monthly_requests": None,
        "team_members": None,
        "projects": None,
        "storage_mb": 500000,
    },
    "features": {
        "api_access": True,
        "sso": True,
    },
}

VALID_PLANS = set(PLAN_CONFIG.keys())
PLAN_HIERARCHY["enterprise"] = 3
```
