# 🗄️ VoiceAppoint - Database Architecture (Enterprise-Ready)

> Improved design applying enterprise patterns and best practices for a scalable SaaS

## 📋 Applied Design Principles

### 🎯 **Design Patterns**
- **Multi-Tenant Pattern**: Full isolation per tenant
- **Audit Trail Pattern**: Complete change traceability
- **Soft Delete Pattern**: Referential integrity without data loss
- **Observer Pattern**: Event and notification system
- **Strategy Pattern**: Flexible configurations per business type
- **Template Method Pattern**: Reusable configurations

### 🛡️ **Best Practices**
- **Consistent naming**: snake_case, descriptive names
- **Robust constraints**: FK, UK, CHECK constraints
- **Optimized indexes**: For critical availability queries
- **Audit fields**: created_at, updated_at, created_by, updated_by
- **UUIDs**: For better security and distribution
- **DB validations**: Check constraints and triggers
- **JSON Fields**: For flexible configurations
- **Partitioning**: Ready for scalability

---

## 🏗️ IMPROVED ARCHITECTURE

### 1. 👥 USER MANAGEMENT & AUTHENTICATION

```sql
-- Central system users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    avatar_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    locale VARCHAR(10) DEFAULT 'es',
    timezone VARCHAR(50) DEFAULT 'Europe/Madrid',
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_phone_format CHECK (phone IS NULL OR phone ~ '^\+?[1-9]\d{1,14}$')
);

-- User sessions for JWT blacklist
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

-- Login attempts for security
CREATE TABLE login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 🏢 MULTI-TENANCY & TENANTS

```sql
-- Central tenants (businesses) table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(50) UNIQUE NOT NULL, -- URL-friendly identifier
    name VARCHAR(100) NOT NULL,
    description TEXT,
    business_type VARCHAR(50) NOT NULL, -- 'restaurant', 'clinic', 'salon', etc.
    
    -- Contact info
    email VARCHAR(255),
    phone VARCHAR(20),
    website_url TEXT,
    
    -- Address
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'ES',
    
    -- Business settings
    timezone VARCHAR(50) DEFAULT 'Europe/Madrid',
    locale VARCHAR(10) DEFAULT 'es',
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Configuration
    settings JSONB DEFAULT '{}', -- Flexible settings storage
    features JSONB DEFAULT '{}', -- Feature flags
    
    -- Subscription info
    subscription_status VARCHAR(20) DEFAULT 'trial', -- 'trial', 'active', 'suspended', 'cancelled'
    trial_ends_at TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    CONSTRAINT tenants_slug_format CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
    CONSTRAINT tenants_business_type_valid CHECK (business_type IN ('restaurant', 'clinic', 'salon', 'fitness', 'spa', 'dental', 'veterinary', 'other')),
    CONSTRAINT tenants_subscription_status_valid CHECK (subscription_status IN ('trial', 'active', 'suspended', 'cancelled', 'past_due'))
);

-- User-tenant relation (many-to-many)
CREATE TABLE tenant_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    permissions JSONB DEFAULT '{}',
    is_primary BOOLEAN DEFAULT FALSE, -- Tenant owner
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    UNIQUE(tenant_id, user_id),
    CONSTRAINT tenant_users_role_valid CHECK (role IN ('owner', 'admin', 'manager', 'staff', 'member'))
);
```

### 3. 💳 SUBSCRIPTION & PAYMENT SYSTEM

```sql
-- Subscription plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Limits
    max_services INTEGER DEFAULT 10,
    max_resources INTEGER DEFAULT 5,
    max_appointments_per_month INTEGER DEFAULT 100,
    max_staff_users INTEGER DEFAULT 3,
    
    -- Features
    features JSONB DEFAULT '{}',
    
    -- Stripe
    stripe_price_id_monthly VARCHAR(100),
    stripe_price_id_yearly VARCHAR(100),
    
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Active subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    status VARCHAR(20) NOT NULL, -- 'active', 'cancelled', 'past_due', 'unpaid'
    billing_period VARCHAR(10) NOT NULL, -- 'monthly', 'yearly'
    
    -- Stripe
    stripe_subscription_id VARCHAR(100) UNIQUE,
    stripe_customer_id VARCHAR(100),
    
    -- Billing
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    trial_end TIMESTAMP,
    
    -- Usage tracking
    usage_data JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    CONSTRAINT subscriptions_status_valid CHECK (status IN ('active', 'cancelled', 'past_due', 'unpaid', 'trialing')),
    CONSTRAINT subscriptions_billing_period_valid CHECK (billing_period IN ('monthly', 'yearly'))
);

-- Payment history
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL,
    
    stripe_payment_intent_id VARCHAR(100),
    stripe_charge_id VARCHAR(100),
    
    paid_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT payments_status_valid CHECK (status IN ('pending', 'succeeded', 'failed', 'cancelled', 'refunded'))
);
```

### 4. 🎙️ VAPI CONFIGURATION

```sql
-- Vapi settings per tenant
CREATE TABLE vapi_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Vapi settings
    vapi_phone_number VARCHAR(20),
    vapi_assistant_id VARCHAR(100),
    vapi_voice_id VARCHAR(100),
    
    -- Assistant configuration
    assistant_name VARCHAR(100) DEFAULT 'Booking Assistant',
    assistant_greeting TEXT,
    assistant_instructions TEXT,
    
    -- Language and behavior
    language VARCHAR(10) DEFAULT 'es',
    voice_settings JSONB DEFAULT '{}',
    
    -- Business context for AI
    business_context TEXT, -- Information about the business for the AI
    booking_instructions TEXT, -- Specific booking instructions
    
    -- Webhook settings
    webhook_url TEXT,
    webhook_secret VARCHAR(100),
    
    -- Advanced settings
    max_call_duration_minutes INTEGER DEFAULT 10,
    enable_call_recording BOOLEAN DEFAULT FALSE,
    enable_transcription BOOLEAN DEFAULT TRUE,
    
    -- Configuration
    settings JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    UNIQUE(tenant_id)
);

-- Vapi call logs
CREATE TABLE vapi_call_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    vapi_call_id VARCHAR(100) NOT NULL,
    
    -- Call details
    caller_phone VARCHAR(20),
    call_duration_seconds INTEGER,
    call_status VARCHAR(20),
    
    -- AI interaction
    transcript TEXT,
    summary TEXT,
    intent_detected VARCHAR(100),
    entities_extracted JSONB,
    
    -- Booking result
    appointment_id UUID REFERENCES appointments(id),
    booking_successful BOOLEAN DEFAULT FALSE,
    booking_error TEXT,
    
    -- Metadata
    call_started_at TIMESTAMP,
    call_ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. 🔔 NOTIFICATION SYSTEM

```sql
-- Notification templates
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id), -- NULL for system templates
    
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'appointment_confirmed', 'appointment_reminder', etc.
    channel VARCHAR(20) NOT NULL, -- 'email', 'sms', 'push', 'webhook'
    
    subject_template TEXT,
    body_template TEXT NOT NULL,
    
    -- Settings
    is_active BOOLEAN DEFAULT TRUE,
    is_system_default BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT notification_templates_type_valid CHECK (type IN (
        'appointment_confirmed', 'appointment_reminder', 'appointment_cancelled',
        'payment_successful', 'payment_failed', 'subscription_expiring',
        'welcome', 'password_reset'
    )),
    CONSTRAINT notification_templates_channel_valid CHECK (channel IN ('email', 'sms', 'push', 'webhook'))
);

-- Notification queue
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    template_id UUID REFERENCES notification_templates(id),
    
    recipient_type VARCHAR(20) NOT NULL, -- 'user', 'client', 'staff'
    recipient_id UUID, -- Could be user_id or client_id
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(20),
    
    channel VARCHAR(20) NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_at TIMESTAMP,
    failure_reason TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT notifications_status_valid CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'cancelled')),
    CONSTRAINT notifications_recipient_type_valid CHECK (recipient_type IN ('user', 'client', 'staff'))
);
```

### 6. 📊 CORE BUSINESS ENTITIES (ENHANCED)

```sql
-- Enhanced services
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    
    -- Timing
    duration_minutes INTEGER NOT NULL,
    buffer_time_minutes INTEGER DEFAULT 5, -- Time between appointments
    
    -- Pricing
    base_price DECIMAL(10,2),
    price_currency VARCHAR(3) DEFAULT 'EUR',
    price_varies BOOLEAN DEFAULT FALSE, -- If price can vary by professional/time
    
    -- Capacity
    max_capacity INTEGER DEFAULT 1, -- Max people per appointment
    min_advance_booking_hours INTEGER DEFAULT 1,
    max_advance_booking_days INTEGER DEFAULT 30,
    
    -- Availability
    available_days JSONB DEFAULT '[1,2,3,4,5]', -- Days of week available
    available_hours JSONB DEFAULT '{"start": "09:00", "end": "18:00"}',
    
    -- Configuration
    requires_confirmation BOOLEAN DEFAULT FALSE,
    allows_cancellation BOOLEAN DEFAULT TRUE,
    cancellation_policy_hours INTEGER DEFAULT 24,
    
    -- Display
    color_hex VARCHAR(7) DEFAULT '#3B82F6',
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    
    -- SEO
    slug VARCHAR(100),
    meta_description TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    UNIQUE(tenant_id, slug),
    CONSTRAINT services_duration_positive CHECK (duration_minutes > 0),
    CONSTRAINT services_price_non_negative CHECK (base_price IS NULL OR base_price >= 0)
);

-- Enhanced resources
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'staff', 'room', 'equipment'
    description TEXT,
    
    -- Staff specific
    staff_user_id UUID REFERENCES users(id), -- If type = 'staff'
    staff_specialties JSONB, -- Array of specialties
    staff_bio TEXT,
    
    -- Contact (for staff)
    email VARCHAR(255),
    phone VARCHAR(20),
    
    -- Availability
    default_schedule JSONB DEFAULT '{}', -- Default weekly schedule
    hourly_rate DECIMAL(10,2), -- If applicable
    
    -- Physical properties (for rooms/equipment)
    capacity INTEGER,
    location VARCHAR(100),
    equipment_features JSONB,
    
    -- Display
    avatar_url TEXT,
    color_hex VARCHAR(7) DEFAULT '#6B7280',
    sort_order INTEGER DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    CONSTRAINT resources_type_valid CHECK (type IN ('staff', 'room', 'equipment', 'vehicle', 'other'))
);

-- Enhanced clients
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Basic info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    
    -- Personal details
    date_of_birth DATE,
    gender VARCHAR(20),
    
    -- Address
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    
    -- Preferences
    preferred_language VARCHAR(10) DEFAULT 'es',
    communication_preferences JSONB DEFAULT '{"email": true, "sms": false}',
    
    -- Medical/Service history
    notes TEXT,
    allergies TEXT,
    medical_conditions TEXT,
    emergency_contact JSONB,
    
    -- Marketing
    marketing_consent BOOLEAN DEFAULT FALSE,
    source VARCHAR(50), -- How they found the business
    
    -- Stats
    total_appointments INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    last_appointment_date TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    CONSTRAINT clients_email_unique_per_tenant UNIQUE(tenant_id, email),
    CONSTRAINT clients_phone_unique_per_tenant UNIQUE(tenant_id, phone),
    CONSTRAINT clients_phone_format CHECK (phone IS NULL OR phone ~ '^\+?[1-9]\d{1,14}$')
);

-- Enhanced appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id),
    client_id UUID NOT NULL REFERENCES clients(id),
    
    -- Timing
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    
    -- Status management
    status VARCHAR(20) DEFAULT 'scheduled',
    status_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_changed_by UUID REFERENCES users(id),
    
    -- Booking details
    booking_method VARCHAR(20) DEFAULT 'online', -- 'online', 'phone', 'vapi', 'walk_in'
    booking_reference VARCHAR(50) UNIQUE,
    
    -- Pricing
    quoted_price DECIMAL(10,2),
    final_price DECIMAL(10,2),
    paid_amount DECIMAL(10,2) DEFAULT 0,
    payment_status VARCHAR(20) DEFAULT 'pending',
    
    -- Communication
    confirmation_sent_at TIMESTAMP,
    reminder_sent_at TIMESTAMP,
    
    -- Notes and details
    client_notes TEXT, -- What the client specified
    staff_notes TEXT, -- Internal notes
    cancellation_reason TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}', -- Flexible data storage
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    CONSTRAINT appointments_status_valid CHECK (status IN (
        'scheduled', 'confirmed', 'in_progress', 'completed', 
        'cancelled', 'no_show', 'rescheduled'
    )),
    CONSTRAINT appointments_payment_status_valid CHECK (payment_status IN (
        'pending', 'paid', 'partially_paid', 'refunded', 'failed'
    )),
    CONSTRAINT appointments_end_after_start CHECK (scheduled_end > scheduled_start)
);
```

### 7. 🔗 ENHANCED RELATION TABLES

```sql
-- Services requiring specific resources
CREATE TABLE service_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    
    quantity_required INTEGER DEFAULT 1,
    is_required BOOLEAN DEFAULT TRUE,
    preference_order INTEGER DEFAULT 0, -- For resource selection priority
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(service_id, resource_id),
    CONSTRAINT service_resources_quantity_positive CHECK (quantity_required > 0)
);

-- Resources assigned to specific appointments
CREATE TABLE appointment_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    resource_id UUID NOT NULL REFERENCES resources(id),
    
    allocated_start TIMESTAMP NOT NULL,
    allocated_end TIMESTAMP NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT appointment_resources_end_after_start CHECK (allocated_end > allocated_start)
);

-- Resource work schedules
CREATE TABLE resource_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    
    day_of_week INTEGER NOT NULL, -- 0=Sunday, 1=Monday, etc.
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Effective dates
    effective_from DATE DEFAULT CURRENT_DATE,
    effective_until DATE,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT resource_schedules_day_valid CHECK (day_of_week BETWEEN 0 AND 6),
    CONSTRAINT resource_schedules_end_after_start CHECK (end_time > start_time)
);

-- Schedule blocks and exceptions
CREATE TABLE resource_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    
    block_type VARCHAR(20) NOT NULL, -- 'vacation', 'sick_leave', 'maintenance', 'break'
    reason TEXT,
    
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule JSONB, -- For recurring blocks
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    CONSTRAINT resource_blocks_type_valid CHECK (block_type IN (
        'vacation', 'sick_leave', 'maintenance', 'break', 'training', 'other'
    )),
    CONSTRAINT resource_blocks_end_after_start CHECK (end_datetime > start_datetime)
);
```

### 8. 📈 AUDIT & ANALYTICS

```sql
-- Full audit log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    
    -- What happened
    action VARCHAR(20) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', etc.
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    
    -- Who did it
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),
    
    -- When and where
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    
    -- What changed
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    context JSONB DEFAULT '{}',
    
    CONSTRAINT audit_logs_action_valid CHECK (action IN (
        'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'IMPORT'
    ))
);

-- Business metrics
CREATE TABLE business_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    
    -- Appointment metrics
    appointments_scheduled INTEGER DEFAULT 0,
    appointments_completed INTEGER DEFAULT 0,
    appointments_cancelled INTEGER DEFAULT 0,
    appointments_no_show INTEGER DEFAULT 0,
    
    -- Revenue metrics
    revenue_total DECIMAL(10,2) DEFAULT 0,
    revenue_average_per_appointment DECIMAL(10,2) DEFAULT 0,
    
    -- Client metrics
    new_clients INTEGER DEFAULT 0,
    returning_clients INTEGER DEFAULT 0,
    
    -- Resource utilization
    staff_utilization_percentage DECIMAL(5,2),
    room_utilization_percentage DECIMAL(5,2),
    
    -- Custom metrics
    custom_metrics JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, metric_date, metric_type),
    CONSTRAINT business_metrics_type_valid CHECK (metric_type IN ('daily', 'weekly', 'monthly'))
);
```

---

## 🚀 OPTIMIZED INDEXES

```sql
-- ====================
-- MAIN INDEXES
-- ====================

-- Users - Authentication
CREATE INDEX idx_users_email_active ON users(email) WHERE is_active = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_users_phone_active ON users(phone) WHERE is_active = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token_jti ON user_sessions(token_jti);

-- Tenants - Multi-tenancy
CREATE INDEX idx_tenants_slug ON tenants(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_tenant_users_tenant_id ON tenant_users(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tenant_users_user_id ON tenant_users(user_id) WHERE deleted_at IS NULL;

-- Core Business - Availability Queries (CRITICAL)
CREATE INDEX idx_appointments_tenant_date ON appointments(tenant_id, scheduled_start) WHERE deleted_at IS NULL;
CREATE INDEX idx_appointments_service_date ON appointments(service_id, scheduled_start) WHERE deleted_at IS NULL;
CREATE INDEX idx_appointments_status_date ON appointments(status, scheduled_start) WHERE deleted_at IS NULL;

-- Resource allocation - Critical performance
CREATE INDEX idx_appointment_resources_resource_time ON appointment_resources(resource_id, allocated_start, allocated_end);
CREATE INDEX idx_resource_blocks_resource_time ON resource_blocks(resource_id, start_datetime, end_datetime) WHERE deleted_at IS NULL;

-- Client lookup
CREATE INDEX idx_clients_tenant_email ON clients(tenant_id, email) WHERE deleted_at IS NULL;
CREATE INDEX idx_clients_tenant_phone ON clients(tenant_id, phone) WHERE deleted_at IS NULL;
CREATE INDEX idx_clients_tenant_name ON clients(tenant_id, first_name, last_name) WHERE deleted_at IS NULL;

-- Services and Resources
CREATE INDEX idx_services_tenant_active ON services(tenant_id) WHERE is_active = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_resources_tenant_active ON resources(tenant_id) WHERE is_active = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_resources_type_tenant ON resources(tenant_id, type) WHERE is_active = TRUE AND deleted_at IS NULL;

-- Subscriptions and Payments
CREATE INDEX idx_subscriptions_tenant_status ON subscriptions(tenant_id, status);
CREATE INDEX idx_payments_subscription_status ON payments(subscription_id, status);

-- Notifications
CREATE INDEX idx_notifications_status_created ON notifications(status, created_at);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_type, recipient_id);

-- Audit and Analytics
CREATE INDEX idx_audit_logs_tenant_timestamp ON audit_logs(tenant_id, timestamp);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_business_metrics_tenant_date ON business_metrics(tenant_id, metric_date);

-- ====================
-- SPECIALIZED COMPOSITE INDEXES
-- ====================

-- Availability lookup (THE MOST CRITICAL)
CREATE INDEX idx_availability_lookup ON appointments(
    tenant_id, service_id, scheduled_start, scheduled_end, status
) WHERE status NOT IN ('cancelled', 'no_show') AND deleted_at IS NULL;

-- Resource availability lookup
CREATE INDEX idx_resource_availability ON appointment_resources(
    resource_id, allocated_start, allocated_end
);

-- Client appointment history
CREATE INDEX idx_client_appointments ON appointments(
    client_id, scheduled_start DESC
) WHERE deleted_at IS NULL;

-- Staff schedule lookup
CREATE INDEX idx_staff_schedule ON resource_schedules(
    resource_id, day_of_week, start_time, end_time
) WHERE is_active = TRUE;
```

---

## 🔐 CONSTRAINTS & VALIDATIONS

```sql
-- ====================
-- BUSINESS LOGIC CONSTRAINTS
-- ====================

-- Prevent double booking of resources
CREATE UNIQUE INDEX idx_unique_resource_booking ON appointment_resources(
    resource_id, 
    allocated_start
) WHERE allocated_start IS NOT NULL;

-- Ensure appointment times are business hours
ALTER TABLE appointments ADD CONSTRAINT appointments_business_hours 
CHECK (
    EXTRACT(HOUR FROM scheduled_start) >= 6 AND 
    EXTRACT(HOUR FROM scheduled_end) <= 23
);

-- Prevent scheduling in the past
ALTER TABLE appointments ADD CONSTRAINT appointments_future_only 
CHECK (scheduled_start > CURRENT_TIMESTAMP - INTERVAL '1 hour');

-- Ensure resource blocks don't overlap (simplified uniqueness on start)
CREATE UNIQUE INDEX idx_unique_resource_blocks ON resource_blocks(
    resource_id,
    start_datetime
) WHERE deleted_at IS NULL;

-- Subscription business rules
ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_period_valid
CHECK (current_period_end > current_period_start);

-- Payment amount validation
ALTER TABLE payments ADD CONSTRAINT payments_amount_positive
CHECK (amount > 0);

-- ====================
-- DATA INTEGRITY TRIGGERS
-- ====================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all main tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Audit trigger for sensitive operations
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        tenant_id, action, table_name, record_id, 
        user_id, old_values, new_values, timestamp
    ) VALUES (
        COALESCE(NEW.tenant_id, OLD.tenant_id),
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        CURRENT_USER::UUID, -- Assuming user context is set
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
        CURRENT_TIMESTAMP
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Apply audit triggers to critical tables
CREATE TRIGGER audit_appointments AFTER INSERT OR UPDATE OR DELETE ON appointments
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
    
CREATE TRIGGER audit_payments AFTER INSERT OR UPDATE OR DELETE ON payments
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

---

## 🔄 VIEWS FOR COMMON QUERIES

```sql
-- ====================
-- PERFORMANCE VIEWS
-- ====================

-- View for resource availability
CREATE VIEW resource_availability AS
SELECT 
    r.id,
    r.tenant_id,
    r.name,
    r.type,
    rs.day_of_week,
    rs.start_time,
    rs.end_time,
    CASE 
        WHEN rb.id IS NOT NULL THEN false
        ELSE true
    END as is_available
FROM resources r
LEFT JOIN resource_schedules rs ON r.id = rs.resource_id AND rs.is_active = true
LEFT JOIN resource_blocks rb ON r.id = rb.resource_id 
    AND rb.deleted_at IS NULL
    AND CURRENT_TIMESTAMP BETWEEN rb.start_datetime AND rb.end_datetime
WHERE r.is_active = true AND r.deleted_at IS NULL;

-- View for appointment statistics
CREATE VIEW appointment_stats AS
SELECT 
    a.tenant_id,
    a.service_id,
    s.name as service_name,
    DATE(a.scheduled_start) as appointment_date,
    COUNT(*) as total_appointments,
    COUNT(*) FILTER (WHERE a.status = 'completed') as completed_appointments,
    COUNT(*) FILTER (WHERE a.status = 'cancelled') as cancelled_appointments,
    COUNT(*) FILTER (WHERE a.status = 'no_show') as no_show_appointments,
    SUM(a.final_price) FILTER (WHERE a.status = 'completed') as revenue,
    AVG(a.final_price) FILTER (WHERE a.status = 'completed') as avg_price
FROM appointments a
JOIN services s ON a.service_id = s.id
WHERE a.deleted_at IS NULL
GROUP BY a.tenant_id, a.service_id, s.name, DATE(a.scheduled_start);

-- View for tenant dashboard
CREATE VIEW tenant_dashboard AS
SELECT 
    t.id as tenant_id,
    t.name as business_name,
    t.subscription_status,
    COUNT(DISTINCT s.id) as total_services,
    COUNT(DISTINCT r.id) as total_resources,
    COUNT(DISTINCT c.id) as total_clients,
    COUNT(DISTINCT a.id) FILTER (WHERE a.scheduled_start >= CURRENT_DATE) as upcoming_appointments,
    COUNT(DISTINCT a.id) FILTER (WHERE DATE(a.scheduled_start) = CURRENT_DATE) as today_appointments,
    sub.plan_id,
    sp.name as plan_name,
    sub.current_period_end as subscription_expires
FROM tenants t
LEFT JOIN services s ON t.id = s.tenant_id AND s.deleted_at IS NULL
LEFT JOIN resources r ON t.id = r.tenant_id AND r.deleted_at IS NULL
LEFT JOIN clients c ON t.id = c.tenant_id AND c.deleted_at IS NULL
LEFT JOIN appointments a ON t.id = a.tenant_id AND a.deleted_at IS NULL
LEFT JOIN subscriptions sub ON t.id = sub.tenant_id AND sub.status = 'active'
LEFT JOIN subscription_plans sp ON sub.plan_id = sp.id
WHERE t.deleted_at IS NULL
GROUP BY t.id, t.name, t.subscription_status, sub.plan_id, sp.name, sub.current_period_end;
```

---

## 📊 SAMPLE DATA

```sql
-- ====================
-- SEED DATA
-- ====================

-- Default subscription plans
INSERT INTO subscription_plans (name, description, price_monthly, price_yearly, max_services, max_resources, max_appointments_per_month, max_staff_users) VALUES
('Starter', 'Perfect for small businesses', 29.99, 299.99, 5, 3, 100, 2),
('Professional', 'For growing businesses', 59.99, 599.99, 15, 10, 500, 5),
('Enterprise', 'For large operations', 99.99, 999.99, -1, -1, -1, -1);

-- System notification templates
INSERT INTO notification_templates (name, type, channel, subject_template, body_template, is_system_default) VALUES
('Appointment Confirmation Email', 'appointment_confirmed', 'email', 'Appointment Confirmed - {{service_name}}', 'Your appointment for {{service_name}} has been confirmed for {{appointment_date}} at {{appointment_time}}.', true),
('Appointment Reminder SMS', 'appointment_reminder', 'sms', NULL, 'Reminder: You have an appointment tomorrow at {{appointment_time}} for {{service_name}}. {{business_name}}', true),
('Payment Successful', 'payment_successful', 'email', 'Payment Confirmed', 'Your payment of {{amount}} has been processed successfully.', true);

-- Example tenant (Salon)
INSERT INTO tenants (id, slug, name, business_type, email, phone, timezone) VALUES
('01234567-89ab-cdef-0123-456789abcdef', 'bella-hair-salon', 'Bella Hair Salon', 'salon', 'info@bellahair.com', '+34612345678', 'Europe/Madrid');

-- Example services for the salon
INSERT INTO services (tenant_id, name, description, duration_minutes, base_price, category) VALUES
('01234567-89ab-cdef-0123-456789abcdef', 'Haircut', 'Custom cut with wash', 45, 25.00, 'Haircuts'),
('01234567-89ab-cdef-0123-456789abcdef', 'Full Color', 'Full color from roots to ends', 120, 65.00, 'Color'),
('01234567-89ab-cdef-0123-456789abcdef', 'Manicure', 'Complete manicure with polish', 60, 20.00, 'Nails');

-- Example resources
INSERT INTO resources (tenant_id, name, type, description) VALUES
('01234567-89ab-cdef-0123-456789abcdef', 'María García', 'staff', 'Senior stylist specialized in cuts and color'),
('01234567-89ab-cdef-0123-456789abcdef', 'Main Chair', 'room', 'Primary workstation with mirror and wash unit'),
('01234567-89ab-cdef-0123-456789abcdef', 'Manicure Table', 'equipment', 'Specialized table for manicure services');
```

---

## 🎯 NEXT STEPS

### 1. **Incremental Implementation**
```bash
# Phase 1: Core Authentication & Multi-tenancy
- users, tenants, tenant_users tables
- Basic auth endpoints
- Tenant isolation middleware

# Phase 2: Business Logic
- services, resources, clients tables
- Appointment system
- Basic availability logic

# Phase 3: External Integrations
- vapi_configurations, vapi_call_logs
- Stripe subscriptions & payments
- Notification system

# Phase 4: Analytics & Optimization
- audit_logs, business_metrics
- Performance monitoring
- Advanced features
```

### 2. **Migrations Strategy**
```sql
-- Create migrations in order:
-- 001_create_users_and_auth.sql
-- 002_create_tenants_and_multitenancy.sql
-- 003_create_subscriptions_and_payments.sql
-- 004_create_services_and_resources.sql
-- 005_create_appointments_system.sql
-- 006_create_vapi_integration.sql
-- 007_create_notifications.sql
-- 008_create_audit_and_analytics.sql
-- 009_create_indexes_and_constraints.sql
-- 010_create_views_and_functions.sql
```

### 3. **Testing Strategy**
```sql
-- Unit tests for each constraint
-- Integration tests for availability logic
-- Performance tests for booking queries
-- Load tests for concurrent booking scenarios
-- Data integrity tests
```

---
##  Table Confirmation

###  Main Tables Covered

####  Authentication & Users
- USERS – Central system users table
- USER_SESSIONS – JWT session management
- TENANT_USERS – Many-to-many user–tenant relationship

####  Multi-Tenancy
- TENANTS – Businesses / companies (core entity)
- VAPI_CONFIGURATIONS – Vapi configuration per tenant

####  Core Business
- SERVICES – Services offered by each business
- RESOURCES – Business resources (staff, rooms, equipment)
- CLIENTS – Clients of each business
- APPOINTMENTS – Appointments / bookings

####  Relationships & Scheduling
- SERVICE_RESOURCES – Resources each service requires
- APPOINTMENT_RESOURCES – Resources assigned to specific appointments
- RESOURCE_SCHEDULES – Base resource schedules
- RESOURCE_BLOCKS – Temporary exceptions / blocks

####  Billing
- SUBSCRIPTION_PLANS – Subscription plans
- SUBSCRIPTIONS – Active subscriptions
- PAYMENTS – Payment history

####  Vapi Integration
- VAPI_CALL_LOGS – Vapi call logs

####  Analytics & Audit
- BUSINESS_METRICS – Business metrics
- AUDIT_LOGS – Full system audit
- NOTIFICATIONS – Notification system
---
---

## 🔗 MAIN RELATIONSHIPS

### **1. Multi-Tenancy (System Core)**
```
USERS ←─→ TENANT_USERS ←─→ TENANTS
```
- A user can belong to multiple tenants
- A tenant can have multiple users with different roles

### **2. Subscriptions & Payments**
```
TENANTS → SUBSCRIPTIONS → PAYMENTS
SUBSCRIPTIONS → SUBSCRIPTION_PLANS
```
- Each tenant has an active subscription
- Each subscription generates multiple payments

### **3. Core Business Logic**
```
TENANTS → SERVICES ←─→ SERVICE_RESOURCES ←─→ RESOURCES
TENANTS → CLIENTS
TENANTS → APPOINTMENTS
```
- Services require specific resources (N:M)
- Appointments assign specific resources via APPOINTMENT_RESOURCES

### **4. Scheduling & Availability**
```
RESOURCES → RESOURCE_SCHEDULES (regular schedules)
RESOURCES → RESOURCE_BLOCKS (exceptions/blocks)
APPOINTMENTS → APPOINTMENT_RESOURCES (allocations)
```

### **5. Vapi Integration**
```
TENANTS → VAPI_CONFIGURATIONS (1:1)
TENANTS → VAPI_CALL_LOGS → APPOINTMENTS
```

### **6. Notifications**
```
TENANTS → NOTIFICATION_TEMPLATES → NOTIFICATIONS
```

### **7. Audit & Analytics**
```
ALL_TABLES → AUDIT_LOGS (automatic triggers)
TENANTS → BUSINESS_METRICS (aggregated metrics)
```

---

## 📚 DETAILED ANALYSIS OF TABLES AND RELATIONSHIPS

> **Comprehensive explanation of the purpose of each table and how it integrates into the system ecosystem**

---

## 🔐 **AUTHENTICATION AND SECURITY SYSTEM**

### **1. USERS - Central User Table**
**🎯 Purpose:**
- Stores all system users (business owners, employees, administrators)
- Manages authentication credentials and basic profiles
- Serves as the central identification point throughout the system

**🔗 Relationships and Why:**
- **→ TENANT_USERS (1:N):** A user can work in multiple businesses with different roles
- **→ USER_SESSIONS (1:N):** To manage multiple active sessions (mobile, web, tablet)
- **→ RESOURCES (1:N):** When the user is staff, linked as a human resource
- **→ All tables (audit):** To track who performed each action

**💡 Use Cases:**
- A stylist can work at 3 different salons with different roles
- An admin can manage multiple clinics from one account
- An owner can have several businesses in different locations

### **2. USER_SESSIONS - Session Management**
**🎯 Purpose:**
- Implements JWT blacklist for advanced security
- Allows invalidating specific sessions without affecting others
- Tracks devices and locations for anomaly detection

**🔗 Relationships and Why:**
- **← USERS (N:1):** Each session belongs to a specific user
- **Standalone:** Not related to other tables for simplicity

**💡 Use Cases:**
- Log out only on mobile when a device is lost
- Detect suspicious access from unusual locations
- Limit the number of active devices per user

### **3. LOGIN_ATTEMPTS - Security and Auditing**
**🎯 Purpose:**
- Prevents brute force attacks
- Audits access attempts for compliance
- Enables automatic IP blocking

**🔗 Relationships and Why:**
- **Standalone:** Deliberately unrelated to capture failed attempts
- **Email reference:** To link with users without a formal FK

**💡 Use Cases:**
- Block IP after 5 failed attempts
- Alert user about unauthorized access attempts
- Generate security reports for audits

---

## 🏢 **MULTI-TENANCY AND BUSINESS MANAGEMENT**

### **4. TENANTS - System Core**
**🎯 Purpose:**
- Represents each business/organization in the system
- Provides complete data isolation between businesses
- Centralizes business configuration and metadata

**🔗 Relationships and Why:**
- **← TENANT_USERS (1:N):** To manage who has access to the business
- **→ ALL business tables:** Data isolation and ownership
- **→ SUBSCRIPTIONS (1:N):** Each business has its own billing
- **→ VAPI_CONFIGURATIONS (1:1):** Unique voice assistant configuration

**💡 Use Cases:**
- A dental clinic with 3 doctors and 2 receptionists
- A salon chain with centralized configuration
- A spa offering multiple services with different resources

### **5. TENANT_USERS - Roles and Permissions**
**🎯 Purpose:**
- Implements granular role system per business
- Allows users to have different access levels
- Facilitates team and organizational hierarchy management

**🔗 Relationships and Why:**
- **← USERS (N:1):** Multiple assignments per user
- **← TENANTS (N:1):** Multiple users per business
- **Junction Table:** Resolves many-to-many relationship with extra metadata

**💡 Use Cases:**
- Dr. Garcia is 'owner' in Clinic A and 'staff' in Clinic B
- Receptionist can view appointments but not modify prices
- Manager can manage schedules but not access billing

---

## 💳 **SUBSCRIPTION AND PAYMENT SYSTEM (SaaS)**

### **6. SUBSCRIPTION_PLANS - Business Models**
**🎯 Purpose:**
- Defines the different service levels offered
- Sets limits and features per plan
- Enables scalable revenue model

**🔗 Relationships and Why:**
- **→ SUBSCRIPTIONS (1:N):** Multiple businesses can have the same plan
- **Standalone:** Does not depend on tenant-specific data

**💡 Use Cases:**
- Starter Plan: 5 services, 100 appointments/month, €29.99
- Enterprise Plan: Unlimited services, unlimited appointments, €99.99
- Seasonal Plan: Special pricing for seasonal businesses

### **7. SUBSCRIPTIONS - Billing Status**
**🎯 Purpose:**
- Tracks the current status of each subscription
- Manages billing periods and renewals
- Integrates with Stripe for automated payments

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** Each business has an active subscription
- **← SUBSCRIPTION_PLANS (N:1):** To get plan features
- **→ PAYMENTS (1:N):** Associated payment history

**💡 Use Cases:**
- Business pays monthly, auto-renewal
- Mid-cycle plan change with proration
- Suspension for non-payment with grace period

### **8. PAYMENTS - Financial History**
**🎯 Purpose:**
- Records all financial transactions
- Provides traceability for accounting reconciliation
- Facilitates fiscal and revenue reporting

**🔗 Relationships and Why:**
- **← SUBSCRIPTIONS (N:1):** Each payment is linked to a subscription
- **← TENANTS (N:1):** For client-based reporting
- **Stripe Integration:** For payment gateway sync

**💡 Use Cases:**
- Generate automatic monthly invoices
- Track failed payments for automatic retry
- Revenue reports by period and segment

---

## 🎙️ **VAPI INTEGRATION (VOICE ASSISTANT)**

### **9. VAPI_CONFIGURATIONS - Assistant Personalization**
**🎯 Purpose:**
- Configures unique voice assistant behavior per business
- Allows customizing the phone customer experience
- Manages integration with Vapi API

**🔗 Relationships and Why:**
- **← TENANTS (1:1):** Each business has its unique configuration
- **→ VAPI_CALL_LOGS (1:N):** Call logs using this configuration

**💡 Use Cases:**
- Salon: "Hello, this is Bella Hair, how can I help you?"
- Clinic: "Health Clinic, tell me your symptom and I'll assign a specialist"
- Restaurant: "Welcome to Casa Mario, for how many people?"

### **10. VAPI_CALL_LOGS - Business Intelligence**
**🎯 Purpose:**
- Records all phone interactions
- Provides insights on call patterns
- Connects conversations with business outcomes

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** To segregate logs by business
- **← VAPI_CONFIGURATIONS (N:1):** Configuration used in the call
- **→ APPOINTMENTS (N:1):** If the call resulted in an appointment

**💡 Use Cases:**
- "85% of Monday calls result in appointments"
- "Calls over 3 minutes have higher conversion"
- "Most effective phrases for closing phone sales"

---

## 📊 **CORE BUSINESS ENTITIES**

### **11. SERVICES - Service Catalog**
**🎯 Purpose:**
- Defines what each business offers to clients
- Sets prices, duration, and resource requirements
- Enables flexible configuration by industry type

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** Each service belongs to a specific business
- **↔ RESOURCES (N:M):** Services require specific resources
- **→ APPOINTMENTS (1:N):** Appointments are based on concrete services

**💡 Use Cases:**
- "Haircut": 45 min, €25, requires stylist + chair
- "Cardiology consult": 30 min, €60, requires cardiologist + office
- "Table for 4": 120 min, €0, requires specific table

### **12. RESOURCES - Business Assets**
**🎯 Purpose:**
- Represents limiting elements (people, spaces, equipment)
- Enables capacity and utilization optimization
- Facilitates schedule and availability management

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** Resources belong to specific businesses
- **← USERS (N:1):** If staff, links to system user
- **↔ SERVICES (N:M):** Defines which resources each service requires
- **→ APPOINTMENT_RESOURCES (1:N):** Specific assignments
- **→ RESOURCE_SCHEDULES (1:N):** Availability schedules
- **→ RESOURCE_BLOCKS (1:N):** Exceptions and blocks

**💡 Use Cases:**
- Dr. Garcia (staff): 9am-5pm schedule, cardiology specialist
- Operating room (room): Capacity 1, requires sterilization
- X-ray machine (equipment): Maintenance every 6 months

### **13. CLIENTS - Customer Base**
**🎯 Purpose:**
- Centralizes client information per business
- Enables personalized marketing and follow-up
- Maintains medical/service history for continuity

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** Clients are business-specific
- **→ APPOINTMENTS (1:N):** Client's appointment history

**💡 Use Cases:**
- VIP client with 50+ appointments, automatic discounts
- Medical history for treatment follow-up
- Communication preferences (email vs SMS)

### **14. APPOINTMENTS - Core Transactions**
**🎯 Purpose:**
- Represents the system's main transaction
- Connects clients, services, resources, and time
- Generates revenue and utilization metrics

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** Business isolation
- **← SERVICES (N:1):** Which service is being provided
- **← CLIENTS (N:1):** Who is receiving the service
- **→ APPOINTMENT_RESOURCES (1:N):** Which specific resources are used
- **← VAPI_CALL_LOGS (1:N):** If originated by phone call

**💡 Use Cases:**
- Appointment scheduled online with automatic confirmation
- Emergency appointment that adjusts other resource schedules
- Recurring appointment (physiotherapy) with same therapist

---

## 🔗 **RELATIONSHIP AND CONFIGURATION TABLES**

### **15. SERVICE_RESOURCES - Service Requirements**
**🎯 Purpose:**
- Defines which specific resources each service needs
- Allows flexible resource assignment
- Enables automatic availability calculation

**🔗 Relationships and Why:**
- **Junction Table:** Resolves N:M relationship between SERVICES and RESOURCES
- **Additional metadata:** Quantity required, preferences, optionality

**💡 Use Cases:**
- "Hair coloring" requires: 1 colorist + 1 chair + 1 washbasin
- "Minor surgery" requires: 1 surgeon + 1 nurse + 1 operating room
- "Romantic dinner" requires: 1 terrace table (preferred) OR 1 indoor table

### **16. APPOINTMENT_RESOURCES - Specific Assignments**
**🎯 Purpose:**
- Records which specific resources were used in each appointment
- Enables detailed utilization and billing tracking
- Facilitates efficiency analysis per resource

**🔗 Relationships and Why:**
- **← APPOINTMENTS (N:1):** Each assignment belongs to an appointment
- **← RESOURCES (N:1):** Specific assigned resource
- **Temporal:** Includes specific usage times

**💡 Use Cases:**
- Dr. Garcia attended patient from 10:30 to 11:15 (not the full 30 min scheduled)
- X-ray room used 15 extra minutes due to complications
- Table assigned released early, available for walk-ins

### **17. RESOURCE_SCHEDULES - Base Schedules**
**🎯 Purpose:**
- Defines regular work/availability schedules
- Enables automatic calculation of available slots
- Allows different schedules per day of the week

**🔗 Relationships and Why:**
- **← RESOURCES (N:1):** Each resource has its own schedule
- **Temporal:** With effective dates for scheduled changes

**💡 Use Cases:**
- Dr. Garcia: Mon-Fri 9am-5pm, Sat 9am-1pm
- Salon: Opens 10am on weekdays, 9am on Saturdays
- X-ray machine: Only available when technician is present (Mon-Fri)

### **18. RESOURCE_BLOCKS - Exceptions and Blocks**
**🎯 Purpose:**
- Manages exceptions to regular schedules
- Enables vacation and maintenance planning
- Allows temporary blocks for emergencies

**🔗 Relationships and Why:**
- **← RESOURCES (N:1):** Specific blocks per resource
- **Soft Delete:** To maintain change history
- **Recurrence:** For patterns like "closed every Sunday"

**💡 Use Cases:**
- Dr. Garcia on vacation from Aug 15-29
- Machine in preventive maintenance every first Monday of the month
- Room blocked for fumigation Friday afternoon

---

## 🔔 **NOTIFICATION SYSTEM**

### **19. NOTIFICATION_TEMPLATES - Standardized Communication**
**🎯 Purpose:**
- Standardizes communications with clients and staff
- Allows business-specific customization while maintaining consistency
- Facilitates compliance with communication regulations

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** Business-specific templates (nullable for system templates)
- **→ NOTIFICATIONS (1:N):** Basis for specific notifications

**💡 Use Cases:**
- System template: "Your appointment is confirmed for {{date}}"
- Clinic template: "Remember to fast for 12h before your test"
- Spa template: "Arrive 15 min early to relax in the waiting room"

### **20. NOTIFICATIONS - Communication Queue**
**🎯 Purpose:**
- Manages actual sending of communications
- Provides delivery traceability
- Enables automatic retry on failures

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** For segregation and reporting
- **← NOTIFICATION_TEMPLATES (N:1):** Template used as base
- **Multi-recipient:** Can target users, clients, or staff

**💡 Use Cases:**
- Reminder SMS sent 24h before appointment
- Confirmation email sent immediately after booking
- Push notification to staff when client arrives

---

## 📈 **AUDIT AND ANALYTICS**

### **21. AUDIT_LOGS - Complete Traceability**
**🎯 Purpose:**
- Meets compliance and audit requirements
- Facilitates debugging and issue resolution
- Provides transparency for enterprise clients

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** To segregate logs by business
- **← USERS (N:1):** Who performed the action
- **Universal:** Conceptually relates to all tables
- **Automatic triggers:** Captures changes without manual intervention

**💡 Use Cases:**
- "Who canceled Mr. Garcia's appointment on Tuesday?"
- "When was the manicure service price changed?"
- "Access audit for ISO 27001 certification"

### **22. BUSINESS_METRICS - Business Intelligence**
**🎯 Purpose:**
- Provides aggregated insights on performance
- Enables data-driven decision making
- Optimizes operations and resources

**🔗 Relationships and Why:**
- **← TENANTS (N:1):** Business-specific metrics
- **Aggregation:** Data calculated from multiple transactional tables
- **Temporal:** Metrics by period for trend analysis

**💡 Use Cases:**
- "Dr. Garcia's utilization dropped 15% this month"
- "Manicure revenue increased 30% after price hike"
- "Monday is the day with most no-shows, send extra reminders"

---

## 🎯 **KEY INTERACTION PATTERNS**

### **🔄 Phone Booking Flow (Vapi)**
```
1. VAPI_CONFIGURATIONS → Configures assistant behavior
2. VAPI_CALL_LOGS → Records the conversation
3. CLIENTS → Identifies or creates client
4. SERVICES → Identifies requested service
5. RESOURCES → Checks availability via RESOURCE_SCHEDULES/BLOCKS
6. APPOINTMENTS → Creates the appointment
7. APPOINTMENT_RESOURCES → Assigns specific resources
8. NOTIFICATIONS → Sends automatic confirmation
```

### **📊 Availability Flow**
```
1. SERVICES → Defines duration and required resources
2. SERVICE_RESOURCES → Lists needed resources
3. RESOURCE_SCHEDULES → Base available schedules
4. RESOURCE_BLOCKS → Subtracts exceptions/blocks
5. APPOINTMENTS + APPOINTMENT_RESOURCES → Subtracts occupied slots
6. Result = Available slots for booking
```

### **💰 SaaS Billing Flow**
```
1. SUBSCRIPTION_PLANS → Defines limits and price
2. SUBSCRIPTIONS → Current business status
3. BUSINESS_METRICS → Monitors usage vs limits
4. PAYMENTS → Processes automatic billing
5. Automatic upgrade/downgrade based on usage
```

### **🔐 Multi-tenant Authentication Flow**
```
1. USERS → Validates credentials
2. USER_SESSIONS → Creates/validates JWT token
3. TENANT_USERS → Determines accessible businesses
4. Tenant context → Filters all subsequent data
5. AUDIT_LOGS → Records access and actions
```

---
