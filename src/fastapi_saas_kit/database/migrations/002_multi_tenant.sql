-- ============================================================
-- fastapi-saas-kit - Multi-Tenant Extensions
-- Additional tables for org-level management and audit.
-- ============================================================

-- ── Organization Access Log (Audit Trail) ───────────────────
CREATE TABLE IF NOT EXISTS organization_access_log (
    id BIGSERIAL PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL
        CHECK (action IN (
            'member_added',
            'member_removed',
            'member_role_changed',
            'settings_updated',
            'plan_changed',
            'admin_login'
        )),
    entity_type TEXT,
    entity_id UUID,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Quota Tracking ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS quota_usage (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    quota_type TEXT NOT NULL
        CHECK (quota_type IN ('monthly_requests', 'team_members', 'projects', 'storage_mb')),
    used INT NOT NULL DEFAULT 0,
    limit_value INT NOT NULL,
    period_start TIMESTAMPTZ DEFAULT NOW(),
    period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ─────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_access_log_org ON organization_access_log(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_access_log_user ON organization_access_log(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quota_user ON quota_usage(user_id, quota_type);
CREATE INDEX IF NOT EXISTS idx_quota_org ON quota_usage(organization_id, quota_type);
