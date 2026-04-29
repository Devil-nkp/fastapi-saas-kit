# Architecture

## System Overview

fastapi-saas-kit uses an adapter-based architecture for a production-ready FastAPI backend foundation. Authentication, access control, provider adapters, caching, and database access are separated behind clear interfaces so you can replace infrastructure without rewriting route logic.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WEB["Web Frontend"]
        API_CLIENT["API Client"]
    end

    subgraph "API Layer"
        FASTAPI["FastAPI App"]
        MW_CORS["CORS Middleware"]
        MW_SEC["Security Headers"]
        MW_ERR["Error Handler"]
        MW_RL["Rate Limiter"]
    end

    subgraph "Auth Layer"
        AUTH_DEP["Auth Dependencies"]
        AUTH_IF["AuthProvider Interface"]
        MOCK_AUTH["MockAuthProvider"]
        JWT_UTIL["JWT Utilities"]
    end

    subgraph "Access Layer"
        RBAC["Role-Based Access Control"]
        TIERS["Access Tier Configuration"]
        QUOTAS["Quota Enforcement"]
        TENANCY["Multi-Tenant Service"]
    end

    subgraph "Provider Adapter Layer"
        ACCESS_IF["BillingProvider Interface"]
        MOCK_ACCESS["MockBillingProvider"]
        PROVIDER_STUB["Provider Stub"]
    end

    subgraph "Infrastructure Layer"
        CACHE_IF["CacheProvider Interface"]
        MEM_CACHE["InMemoryCacheProvider"]
        DB_POOL["Database Pool"]
        MIGRATIONS["Migration Runner"]
        PG["PostgreSQL"]
    end

    WEB --> FASTAPI
    API_CLIENT --> FASTAPI
    FASTAPI --> MW_CORS --> MW_SEC --> MW_ERR
    FASTAPI --> MW_RL
    FASTAPI --> AUTH_DEP
    AUTH_DEP --> AUTH_IF
    AUTH_IF --> MOCK_AUTH
    AUTH_IF --> JWT_UTIL
    AUTH_DEP --> RBAC
    RBAC --> TIERS
    RBAC --> QUOTAS
    FASTAPI --> TENANCY
    TENANCY --> DB_POOL
    FASTAPI --> ACCESS_IF
    ACCESS_IF --> MOCK_ACCESS
    ACCESS_IF --> PROVIDER_STUB
    DB_POOL --> MIGRATIONS
    MIGRATIONS --> PG
    CACHE_IF --> MEM_CACHE
```

## Key Design Principles

### 1. Adapter Pattern

External services are accessed through abstract interfaces:

| Interface | Purpose | Included Adapters |
|-----------|---------|-------------------|
| `AuthProvider` | Authentication and identity | `MockAuthProvider` |
| `BillingProvider` | Access events and entitlement adapter | `MockBillingProvider`, provider stub |
| `CacheProvider` | Data caching | `InMemoryCacheProvider` |

`BillingProvider` remains the stable code interface name. Public usage can treat it as a provider adapter for access gates, entitlements, and external event handling.

### 2. Dependency Injection

FastAPI dependency injection is used for:

- Authentication: `get_current_user` resolves the user from the request
- Authorization: `require_role()` and `require_plan()` gate access
- Rate limiting: `rate_limit_ip()` and `rate_limit_user()` enforce request limits

### 3. Tenant Isolation

All data access is scoped by `organization_id`:

- Users can only access their own organization's data
- Org admins can manage their organization only
- Main admins have cross-tenant access

### 4. Configuration

All settings use Pydantic's `BaseSettings` with environment variable loading:

- Type-safe configuration
- Validation during application initialization
- `.env` file support for development

## Module Structure

```text
src/fastapi_saas_kit/
|-- app.py              # App factory
|-- config.py           # Pydantic settings
|-- auth/               # Authentication and RBAC
|-- tenancy/            # Multi-tenant organizations
|-- plans/              # Access tier config and quotas
|-- billing/            # Provider adapter interface and routes
|-- cache/              # Caching layer
|-- middleware/         # Rate limiting, security, errors
|-- database/           # Connection pool and migrations
`-- health/             # Health check endpoints
```
