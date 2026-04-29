# Plans and Quotas

## Plan Configuration

Three plans are included by default. Customize in `src/fastapi_saas_kit/plans/config.py`:

| Feature | Free | Pro | Business |
|---------|------|-----|----------|
| Monthly Requests | 100 | 5,000 | Unlimited |
| Team Members | 1 | 10 | 100 |
| Projects | 3 | 25 | Unlimited |
| Storage (MB) | 100 | 5,000 | 50,000 |
| API Access | ✅ | ✅ | ✅ |
| Basic Analytics | ✅ | ✅ | ✅ |
| Advanced Analytics | ❌ | ✅ | ✅ |
| Priority Support | ❌ | ✅ | ✅ |
| Custom Branding | ❌ | ❌ | ✅ |
| Export Data | ❌ | ✅ | ✅ |
| Webhooks | ❌ | ✅ | ✅ |
| SSO | ❌ | ❌ | ✅ |

## Plan Hierarchy

```python
from fastapi_saas_kit.plans.config import can_access_plan

can_access_plan("business", "pro")   # True — business >= pro
can_access_plan("pro", "business")   # False — pro < business
can_access_plan("free", "free")      # True — equal
```

## Feature Gates

```python
from fastapi_saas_kit.plans.config import has_feature
from fastapi_saas_kit.plans.access import require_feature

# Check in code
if has_feature(user.plan, "advanced_analytics"):
    ...

# Use as dependency
@router.get("/analytics")
async def analytics(user = Depends(require_feature("advanced_analytics"))):
    ...
```

## Quota Enforcement

```python
from fastapi_saas_kit.plans.quota import check_quota, get_usage_stats

# Check quota before allowing an action
await check_quota(user, "monthly_requests", current_usage=50)
# Raises HTTP 402 if over limit

# Get usage statistics
stats = get_usage_stats("pro", {"monthly_requests": 2500, "projects": 10})
# Returns: {
#   "monthly_requests": {"used": 2500, "limit": 5000, "remaining": 2500, ...},
#   "projects": {"used": 10, "limit": 25, "remaining": 15, ...},
# }
```

## Period Reset

Quotas operate on a 30-day rolling window:

```python
from fastapi_saas_kit.plans.quota import should_reset_period

if should_reset_period(user.period_start):
    # Reset usage counters
    ...
```

## Adding Custom Plans

Edit `PLAN_CONFIG` in `plans/config.py`:

```python
PLAN_CONFIG["enterprise"] = {
    "display_name": "Enterprise",
    "price_cents": 49900,
    "price_display": "$499/month",
    "quotas": {
        "monthly_requests": None,  # Unlimited
        "team_members": None,
        "projects": None,
        "storage_mb": 500000,
    },
    "features": {
        "api_access": True,
        "sso": True,
        # ... all features enabled
    },
}

# Don't forget to update:
VALID_PLANS = set(PLAN_CONFIG.keys())
PLAN_HIERARCHY["enterprise"] = 3
```
