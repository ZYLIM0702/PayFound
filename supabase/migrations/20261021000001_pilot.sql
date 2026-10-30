-- Generated from the reviewed Alembic revision chain. Do not edit independently.
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 38a40c4d740c

CREATE TABLE audit_events (
    id SERIAL NOT NULL, 
    actor VARCHAR(160) NOT NULL, 
    action VARCHAR(120) NOT NULL, 
    entity_id VARCHAR(100) NOT NULL, 
    details TEXT NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE merchants (
    id VARCHAR(48) NOT NULL, 
    name VARCHAR(130) NOT NULL, 
    slug VARCHAR(150) NOT NULL, 
    description TEXT NOT NULL, 
    category VARCHAR(80) NOT NULL, 
    address VARCHAR(250) NOT NULL, 
    latitude FLOAT NOT NULL, 
    longitude FLOAT NOT NULL, 
    phone VARCHAR(80) NOT NULL, 
    hours VARCHAR(100) NOT NULL, 
    status_override VARCHAR(20) NOT NULL, 
    fulfillment_minutes INTEGER NOT NULL, 
    verified BOOLEAN NOT NULL, 
    logo_emoji VARCHAR(16) NOT NULL, 
    owner_subject VARCHAR(160), 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (slug)
);

CREATE TABLE outbox_jobs (
    id VARCHAR(48) NOT NULL, 
    kind VARCHAR(80) NOT NULL, 
    dedupe_key VARCHAR(200) NOT NULL, 
    payload TEXT NOT NULL, 
    state VARCHAR(20) NOT NULL, 
    attempts INTEGER NOT NULL, 
    available_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    lease_until TIMESTAMP WITHOUT TIME ZONE, 
    lease_token VARCHAR(48), 
    last_error VARCHAR(200), 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (dedupe_key)
);

CREATE INDEX ix_outbox_due ON outbox_jobs (state, available_at);

CREATE TABLE provider_webhooks (
    id VARCHAR(160) NOT NULL, 
    received_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    event_type VARCHAR(120) NOT NULL, 
    payload TEXT NOT NULL, 
    processed_at TIMESTAMP WITHOUT TIME ZONE, 
    verified BOOLEAN NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE agent_runs (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48), 
    principal_key VARCHAR(64) NOT NULL, 
    role VARCHAR(24) NOT NULL, 
    mode VARCHAR(40) NOT NULL, 
    status VARCHAR(40) NOT NULL, 
    tools JSON NOT NULL, 
    product_count INTEGER NOT NULL, 
    latency_ms INTEGER NOT NULL, 
    input_tokens INTEGER NOT NULL, 
    output_tokens INTEGER NOT NULL, 
    estimated_cost_usd FLOAT NOT NULL, 
    reserved_cost_usd FLOAT NOT NULL, 
    usage_estimated BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id)
);

CREATE INDEX ix_agent_runs_created_at ON agent_runs (created_at);

CREATE INDEX ix_agent_runs_merchant_id ON agent_runs (merchant_id);

CREATE TABLE ai_consent_grants (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    purpose VARCHAR(80) NOT NULL, 
    granted BOOLEAN NOT NULL, 
    policy_version INTEGER NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    CONSTRAINT uq_ai_consent_merchant_purpose UNIQUE (merchant_id, purpose)
);

CREATE INDEX ix_ai_consent_grants_merchant_id ON ai_consent_grants (merchant_id);

CREATE TABLE connector_connections (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    provider VARCHAR(24) NOT NULL, 
    source_key VARCHAR(500) NOT NULL, 
    store_url VARCHAR(500), 
    shop_domain VARCHAR(255), 
    status VARCHAR(32) NOT NULL, 
    credentials_encrypted TEXT, 
    scopes JSON NOT NULL, 
    capabilities JSON NOT NULL, 
    settings JSON NOT NULL, 
    sync_cursor JSON NOT NULL, 
    generation VARCHAR(48), 
    cycle_started_at TIMESTAMP WITHOUT TIME ZONE, 
    last_synced_at TIMESTAMP WITHOUT TIME ZONE, 
    next_sync_at TIMESTAMP WITHOUT TIME ZONE, 
    last_error VARCHAR(300), 
    lease_token VARCHAR(48), 
    lease_until TIMESTAMP WITHOUT TIME ZONE, 
    state_hash VARCHAR(64), 
    state_expires_at TIMESTAMP WITHOUT TIME ZONE, 
    authorized_at TIMESTAMP WITHOUT TIME ZONE, 
    consent_at TIMESTAMP WITHOUT TIME ZONE, 
    consent_subject VARCHAR(160), 
    published BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    UNIQUE (source_key), 
    UNIQUE (state_hash)
);

CREATE INDEX ix_connector_connections_merchant_id ON connector_connections (merchant_id);

CREATE TABLE merchant_locations (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    name VARCHAR(130) NOT NULL, 
    address VARCHAR(250) NOT NULL, 
    latitude FLOAT NOT NULL, 
    longitude FLOAT NOT NULL, 
    timezone VARCHAR(80) NOT NULL, 
    hours TEXT NOT NULL, 
    special_hours TEXT NOT NULL, 
    operational_status VARCHAR(20) NOT NULL, 
    phone VARCHAR(80) NOT NULL, 
    active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_location_status CHECK (operational_status IN ('auto','open','closed','delayed')), 
    CONSTRAINT ck_location_coordinates CHECK (latitude >= -90 AND latitude <= 90 AND longitude >= -180 AND longitude <= 180), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id)
);

CREATE INDEX ix_merchant_locations_merchant_id ON merchant_locations (merchant_id);

CREATE TABLE merchant_memberships (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    subject VARCHAR(160) NOT NULL, 
    role VARCHAR(20) NOT NULL, 
    active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_membership_role CHECK (role IN ('owner','manager','staff')), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    CONSTRAINT uq_membership_subject UNIQUE (merchant_id, subject)
);

CREATE INDEX ix_merchant_memberships_merchant_id ON merchant_memberships (merchant_id);

CREATE INDEX ix_merchant_memberships_subject ON merchant_memberships (subject);

CREATE TABLE merchant_reports (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    name VARCHAR(160) NOT NULL, 
    state JSON NOT NULL, 
    version INTEGER NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_merchant_report_version CHECK (version > 0), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id)
);

CREATE INDEX ix_merchant_reports_merchant_id ON merchant_reports (merchant_id);

CREATE TABLE staff_invitations (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    email VARCHAR(254), 
    subject VARCHAR(160), 
    role VARCHAR(20) NOT NULL, 
    invited_by VARCHAR(160) NOT NULL, 
    status VARCHAR(20) NOT NULL, 
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_invitation_role CHECK (role IN ('manager','staff')), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id)
);

CREATE INDEX ix_staff_invitations_merchant_id ON staff_invitations (merchant_id);

CREATE TABLE connector_events (
    id VARCHAR(48) NOT NULL, 
    connection_id VARCHAR(48) NOT NULL, 
    delivery_id VARCHAR(160) NOT NULL, 
    topic VARCHAR(100) NOT NULL, 
    body_hash VARCHAR(64) NOT NULL, 
    payload_encrypted TEXT NOT NULL, 
    emitted_at TIMESTAMP WITHOUT TIME ZONE, 
    observed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    processed_at TIMESTAMP WITHOUT TIME ZONE, 
    status VARCHAR(24) NOT NULL, 
    attempts INTEGER NOT NULL, 
    next_attempt_at TIMESTAMP WITHOUT TIME ZONE, 
    error VARCHAR(300), 
    PRIMARY KEY (id), 
    FOREIGN KEY(connection_id) REFERENCES connector_connections (id), 
    UNIQUE (connection_id, delivery_id), 
    UNIQUE (connection_id, topic, body_hash)
);

CREATE INDEX ix_connector_events_connection_id ON connector_events (connection_id);

CREATE INDEX ix_connector_events_pending ON connector_events (status, next_attempt_at);

CREATE TABLE connector_locations (
    id VARCHAR(48) NOT NULL, 
    connection_id VARCHAR(48) NOT NULL, 
    source_location_id VARCHAR(160) NOT NULL, 
    name VARCHAR(180) NOT NULL, 
    kind VARCHAR(24) NOT NULL, 
    active BOOLEAN NOT NULL, 
    location_id VARCHAR(48), 
    mapping_confirmed BOOLEAN NOT NULL, 
    seen_generation VARCHAR(48), 
    PRIMARY KEY (id), 
    FOREIGN KEY(connection_id) REFERENCES connector_connections (id), 
    FOREIGN KEY(location_id) REFERENCES merchant_locations (id), 
    UNIQUE (connection_id, source_location_id)
);

CREATE INDEX ix_connector_locations_connection_id ON connector_locations (connection_id);

CREATE TABLE connector_sync_runs (
    id VARCHAR(48) NOT NULL, 
    connection_id VARCHAR(48) NOT NULL, 
    status VARCHAR(24) NOT NULL, 
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    finished_at TIMESTAMP WITHOUT TIME ZONE, 
    summary JSON NOT NULL, 
    error VARCHAR(300), 
    PRIMARY KEY (id), 
    FOREIGN KEY(connection_id) REFERENCES connector_connections (id)
);

CREATE INDEX ix_connector_sync_runs_connection_id ON connector_sync_runs (connection_id);

CREATE TABLE pickup_slots (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    location_id VARCHAR(48) NOT NULL, 
    start_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    end_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    capacity INTEGER NOT NULL, 
    booked_count INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_pickup_capacity CHECK (capacity > 0 AND booked_count >= 0 AND booked_count <= capacity), 
    CONSTRAINT ck_pickup_window CHECK (end_at > start_at), 
    FOREIGN KEY(location_id) REFERENCES merchant_locations (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    CONSTRAINT uq_location_pickup_window UNIQUE (location_id, start_at, end_at)
);

CREATE INDEX ix_pickup_slots_location_id ON pickup_slots (location_id);

CREATE INDEX ix_pickup_slots_merchant_id ON pickup_slots (merchant_id);

CREATE INDEX ix_pickup_slots_start_at ON pickup_slots (start_at);

CREATE TABLE products (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    location_id VARCHAR(48), 
    name VARCHAR(180) NOT NULL, 
    description TEXT NOT NULL, 
    category VARCHAR(90) NOT NULL, 
    sku VARCHAR(90) NOT NULL, 
    price_cents INTEGER NOT NULL, 
    currency VARCHAR(3) NOT NULL, 
    quantity INTEGER NOT NULL, 
    hold_quantity INTEGER NOT NULL, 
    stock_updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    image_emoji VARCHAR(16) NOT NULL, 
    active BOOLEAN NOT NULL, 
    inventory_source VARCHAR(60) NOT NULL, 
    source_product_id VARCHAR(180), 
    source_version VARCHAR(100), 
    source_updated_at TIMESTAMP WITHOUT TIME ZONE, 
    source_observed_at TIMESTAMP WITHOUT TIME ZONE, 
    source_metadata TEXT NOT NULL, 
    availability_state VARCHAR(40) NOT NULL, 
    supports_reservation BOOLEAN NOT NULL, 
    synthetic BOOLEAN NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_product_price CHECK (price_cents > 0), 
    CONSTRAINT ck_product_stock CHECK (quantity >= 0 AND hold_quantity >= 0 AND hold_quantity <= quantity), 
    FOREIGN KEY(location_id) REFERENCES merchant_locations (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    CONSTRAINT uq_location_sku UNIQUE (merchant_id, location_id, sku)
);

CREATE INDEX ix_products_category_name ON products (category, name);

CREATE INDEX ix_products_location_id ON products (location_id);

CREATE INDEX ix_products_merchant_id ON products (merchant_id);

CREATE TABLE connector_offers (
    id VARCHAR(48) NOT NULL, 
    connection_id VARCHAR(48) NOT NULL, 
    source_location_id VARCHAR(160) NOT NULL, 
    source_product_id VARCHAR(160) NOT NULL, 
    source_variant_id VARCHAR(160) NOT NULL, 
    sku VARCHAR(90) NOT NULL, 
    product_id VARCHAR(48), 
    snapshot JSON NOT NULL, 
    source_catalog_at TIMESTAMP WITHOUT TIME ZONE, 
    source_inventory_at TIMESTAMP WITHOUT TIME ZONE, 
    observed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    seen_generation VARCHAR(48), 
    blocked_reason VARCHAR(160), 
    deleted BOOLEAN NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(connection_id) REFERENCES connector_connections (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    UNIQUE (connection_id, source_location_id, source_variant_id)
);

CREATE INDEX ix_connector_offers_connection_id ON connector_offers (connection_id);

CREATE INDEX ix_connector_offers_product_id ON connector_offers (product_id);

CREATE TABLE orders (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    location_id VARCHAR(48), 
    product_id VARCHAR(48) NOT NULL, 
    quantity INTEGER NOT NULL, 
    amount_cents INTEGER NOT NULL, 
    currency VARCHAR(3) NOT NULL, 
    buyer_subject VARCHAR(160) NOT NULL, 
    buyer_name VARCHAR(130) NOT NULL, 
    status VARCHAR(32) NOT NULL, 
    payment_status VARCHAR(40) NOT NULL, 
    payment_mode VARCHAR(32), 
    paypal_order_id VARCHAR(80), 
    paypal_capture_id VARCHAR(80), 
    paypal_refund_id VARCHAR(80), 
    hold_expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    hold_released BOOLEAN NOT NULL, 
    inventory_committed BOOLEAN NOT NULL, 
    inventory_restocked BOOLEAN NOT NULL, 
    confirmation_status VARCHAR(32) NOT NULL, 
    confirmed_by VARCHAR(160), 
    confirmed_at TIMESTAMP WITHOUT TIME ZONE, 
    expected_payee_id VARCHAR(160), 
    version INTEGER NOT NULL, 
    idempotency_key VARCHAR(100) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_order_amount CHECK (quantity > 0 AND amount_cents > 0), 
    FOREIGN KEY(location_id) REFERENCES merchant_locations (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    CONSTRAINT uq_buyer_order_idem UNIQUE (buyer_subject, idempotency_key), 
    UNIQUE (paypal_capture_id), 
    UNIQUE (paypal_order_id), 
    UNIQUE (paypal_refund_id)
);

CREATE INDEX ix_order_expiry ON orders (payment_status, hold_expires_at);

CREATE INDEX ix_orders_location_id ON orders (location_id);

CREATE INDEX ix_orders_merchant_id ON orders (merchant_id);

CREATE TABLE fulfilment_proofs (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    state VARCHAR(32) NOT NULL, 
    actor VARCHAR(160) NOT NULL, 
    proof VARCHAR(500) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    CONSTRAINT uq_fulfilment_proof UNIQUE (order_id, state)
);

CREATE INDEX ix_fulfilment_proofs_order_id ON fulfilment_proofs (order_id);

CREATE TABLE inventory_reservations (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    product_id VARCHAR(48) NOT NULL, 
    quantity INTEGER NOT NULL, 
    state VARCHAR(32) NOT NULL, 
    source VARCHAR(60) NOT NULL, 
    proof_id VARCHAR(180), 
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_reservation_state CHECK (state IN ('PENDING_CONFIRMATION','HELD','CONSUMED','RELEASED')), 
    CONSTRAINT ck_reservation_quantity CHECK (quantity > 0), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    CONSTRAINT uq_reservation_item UNIQUE (order_id, product_id)
);

CREATE INDEX ix_inventory_reservations_order_id ON inventory_reservations (order_id);

CREATE INDEX ix_inventory_reservations_product_id ON inventory_reservations (product_id);

CREATE TABLE order_items (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    product_id VARCHAR(48) NOT NULL, 
    product_name VARCHAR(180) NOT NULL, 
    sku VARCHAR(90) NOT NULL, 
    quantity INTEGER NOT NULL, 
    unit_price_cents INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_order_item_money CHECK (quantity > 0 AND unit_price_cents > 0), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    CONSTRAINT uq_order_item UNIQUE (order_id, product_id)
);

CREATE INDEX ix_order_items_order_id ON order_items (order_id);

CREATE INDEX ix_order_items_product_id ON order_items (product_id);

CREATE TABLE payment_attempts (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    provider VARCHAR(32) NOT NULL, 
    amount_cents INTEGER NOT NULL, 
    currency VARCHAR(3) NOT NULL, 
    expected_payee_id VARCHAR(160), 
    provider_order_id VARCHAR(80), 
    capture_id VARCHAR(80), 
    state VARCHAR(40) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_attempt_amount CHECK (amount_cents > 0), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    UNIQUE (capture_id), 
    UNIQUE (order_id), 
    UNIQUE (provider_order_id)
);

CREATE TABLE payment_events (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    event_type VARCHAR(80) NOT NULL, 
    dedupe_key VARCHAR(200) NOT NULL, 
    details TEXT NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    UNIQUE (dedupe_key)
);

CREATE INDEX ix_payment_events_order_id ON payment_events (order_id);

CREATE TABLE pickup_bookings (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    slot_id VARCHAR(48) NOT NULL, 
    active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    FOREIGN KEY(slot_id) REFERENCES pickup_slots (id), 
    UNIQUE (order_id)
);

CREATE INDEX ix_pickup_bookings_slot_id ON pickup_bookings (slot_id);

CREATE TABLE provider_operations (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    kind VARCHAR(20) NOT NULL, 
    request_id VARCHAR(80) NOT NULL, 
    state VARCHAR(32) NOT NULL, 
    lease_until TIMESTAMP WITHOUT TIME ZONE, 
    attempts INTEGER NOT NULL, 
    provider_id VARCHAR(160), 
    last_error VARCHAR(200), 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    CONSTRAINT uq_order_provider_operation UNIQUE (order_id, kind), 
    UNIQUE (request_id)
);

CREATE INDEX ix_provider_operations_order_id ON provider_operations (order_id);

CREATE TABLE refunds (
    id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    capture_id VARCHAR(80), 
    provider_refund_id VARCHAR(80), 
    amount_cents INTEGER NOT NULL, 
    currency VARCHAR(3) NOT NULL, 
    state VARCHAR(32) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_refund_amount CHECK (amount_cents > 0), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    UNIQUE (order_id), 
    UNIQUE (provider_refund_id)
);

CREATE TABLE reviews (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    buyer_subject VARCHAR(160) NOT NULL, 
    rating INTEGER NOT NULL, 
    body VARCHAR(1500) NOT NULL, 
    visible BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    UNIQUE (order_id)
);

CREATE INDEX ix_reviews_merchant_id ON reviews (merchant_id);

INSERT INTO alembic_version (version_num) VALUES ('38a40c4d740c') RETURNING alembic_version.version_num;

-- Running upgrade 38a40c4d740c -> a001canonical

CREATE TABLE canonical_products (
    id VARCHAR(48) NOT NULL, 
    gtin VARCHAR(14) NOT NULL, 
    name VARCHAR(180) NOT NULL, 
    brand VARCHAR(100) NOT NULL, 
    category VARCHAR(90) NOT NULL, 
    attributes TEXT NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (gtin)
);

ALTER TABLE products ADD COLUMN canonical_product_id VARCHAR(48);

ALTER TABLE products ADD COLUMN image_url VARCHAR(2000);

ALTER TABLE products ADD CONSTRAINT fk_product_canonical FOREIGN KEY(canonical_product_id) REFERENCES canonical_products (id);

CREATE INDEX ix_products_canonical_product_id ON products (canonical_product_id);

UPDATE alembic_version SET version_num='a001canonical' WHERE alembic_version.version_num = '38a40c4d740c';

-- Running upgrade a001canonical -> a002private

ALTER TABLE public."agent_runs" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."agent_runs" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."agent_runs" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."ai_consent_grants" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."ai_consent_grants" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."ai_consent_grants" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."audit_events" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."audit_events" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."audit_events" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."canonical_products" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."canonical_products" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."canonical_products" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."connector_connections" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."connector_connections" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."connector_connections" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."connector_events" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."connector_events" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."connector_events" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."connector_locations" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."connector_locations" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."connector_locations" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."connector_offers" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."connector_offers" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."connector_offers" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."connector_sync_runs" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."connector_sync_runs" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."connector_sync_runs" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."fulfilment_proofs" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."fulfilment_proofs" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."fulfilment_proofs" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."inventory_reservations" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."inventory_reservations" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."inventory_reservations" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."merchant_locations" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."merchant_locations" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."merchant_locations" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."merchant_memberships" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."merchant_memberships" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."merchant_memberships" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."merchant_reports" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."merchant_reports" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."merchant_reports" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."merchants" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."merchants" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."merchants" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."order_items" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."order_items" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."order_items" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."orders" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."orders" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."orders" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."outbox_jobs" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."outbox_jobs" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."outbox_jobs" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."payment_attempts" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."payment_attempts" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."payment_attempts" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."payment_events" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."payment_events" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."payment_events" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."pickup_bookings" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."pickup_bookings" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."pickup_bookings" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."pickup_slots" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."pickup_slots" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."pickup_slots" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."products" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."products" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."products" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."provider_operations" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."provider_operations" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."provider_operations" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."provider_webhooks" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."provider_webhooks" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."provider_webhooks" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."refunds" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."refunds" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."refunds" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."reviews" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."reviews" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."reviews" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."staff_invitations" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."staff_invitations" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."staff_invitations" FROM authenticated;
                END IF;
            END $$;

ALTER TABLE public."alembic_version" ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE public."alembic_version" FROM anon;
                END IF;
            END $$;

DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE public."alembic_version" FROM authenticated;
                END IF;
            END $$;

UPDATE alembic_version SET version_num='a002private' WHERE alembic_version.version_num = 'a001canonical';

-- Running upgrade a002private -> a003indexes

CREATE INDEX ix_orders_product_id ON orders (product_id);

CREATE INDEX ix_connector_locations_location_id ON connector_locations (location_id);

UPDATE alembic_version SET version_num='a003indexes' WHERE alembic_version.version_num = 'a002private';

-- Running upgrade a003indexes -> a004notifications

CREATE TABLE notifications (
    id VARCHAR(48) NOT NULL, 
    merchant_id VARCHAR(48) NOT NULL, 
    order_id VARCHAR(48) NOT NULL, 
    audience VARCHAR(20) NOT NULL, 
    buyer_subject VARCHAR(160), 
    event_type VARCHAR(80) NOT NULL, 
    message VARCHAR(300) NOT NULL, 
    seen_at TIMESTAMP WITHOUT TIME ZONE, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_notification_effect UNIQUE (order_id, event_type, audience), 
    FOREIGN KEY(merchant_id) REFERENCES merchants (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id)
);

CREATE INDEX ix_notifications_merchant_id ON notifications (merchant_id);

CREATE INDEX ix_notifications_order_id ON notifications (order_id);

CREATE INDEX ix_notifications_buyer_subject ON notifications (buyer_subject);

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON TABLE public.notifications FROM anon,authenticated; END IF; END $$;

UPDATE alembic_version SET version_num='a004notifications' WHERE alembic_version.version_num = 'a003indexes';

-- Running upgrade a004notifications -> a005sku

ALTER TABLE products DROP CONSTRAINT uq_location_sku;

CREATE UNIQUE INDEX uq_manual_location_sku ON products (merchant_id, location_id, sku) WHERE inventory_source IN ('manual','merchant_manual','synthetic_local');

UPDATE alembic_version SET version_num='a005sku' WHERE alembic_version.version_num = 'a004notifications';

COMMIT;

