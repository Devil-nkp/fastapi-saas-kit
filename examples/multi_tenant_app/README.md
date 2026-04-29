# Multi-Tenant App Example

A multi-organization SaaS application using fastapi-saas-kit.

## Run

```bash
cd examples/multi_tenant_app
pip install -e ../../  # Install the kit
python main.py
```

Then visit http://localhost:8001/docs to see the API.

## What This Demonstrates

- Organization-scoped endpoints
- Role-based access control (user, org_admin, main_admin)
- Tenant isolation patterns
- Billing integration with MockBillingProvider
- Feature gates per plan
