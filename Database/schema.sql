-- ============================================================
-- TicketVault — Complete Supabase Schema
-- Run this entire file in Supabase SQL Editor
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- CITIES
CREATE TABLE cities (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name      TEXT NOT NULL UNIQUE,
  slug      TEXT NOT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- USERS
CREATE TABLE users (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_id   TEXT NOT NULL UNIQUE,
  name       TEXT NOT NULL,
  email      TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- EVENTS
CREATE TABLE events (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  venue      TEXT NOT NULL,
  city_id    UUID NOT NULL REFERENCES cities(id) ON DELETE RESTRICT,
  date       TIMESTAMPTZ NOT NULL,
  image_url  TEXT,
  source     TEXT DEFAULT 'manual',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_event UNIQUE (name, city_id, date)
);

CREATE INDEX idx_events_city ON events(city_id);
CREATE INDEX idx_events_date ON events(date);

-- TICKET STATUS ENUM
CREATE TYPE ticket_status AS ENUM (
  'available',
  'locked',
  'pending_confirmation',
  'sold',
  'cancelled'
);

-- TICKETS
CREATE TABLE tickets (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id       UUID NOT NULL REFERENCES events(id) ON DELETE RESTRICT,
  seller_id      UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  city_id        UUID NOT NULL REFERENCES cities(id) ON DELETE RESTRICT,
  price          NUMERIC(10,2) NOT NULL CHECK (price > 0),
  original_price NUMERIC(10,2) NOT NULL CHECK (original_price > 0),
  listing_fee    NUMERIC(10,2) GENERATED ALWAYS AS (ROUND(price * 0.20, 2)) STORED,
  status         ticket_status NOT NULL DEFAULT 'available',
  locked_by      UUID REFERENCES users(id),
  lock_expiry    TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tickets_event  ON tickets(event_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_city   ON tickets(city_id);
CREATE INDEX idx_tickets_seller ON tickets(seller_id);

-- TICKET QRs
CREATE TABLE ticket_qrs (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id    UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  qr_image_url TEXT NOT NULL,
  qr_data      TEXT NOT NULL,
  fingerprint  TEXT NOT NULL UNIQUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_qr_fingerprint ON ticket_qrs(fingerprint);

-- ORDER ENUMS
CREATE TYPE payment_status AS ENUM (
  'pending', 'paid', 'failed', 'refunded'
);

CREATE TYPE confirmation_status AS ENUM (
  'pending', 'confirmed', 'auto_confirmed', 'disputed'
);

-- ORDERS
CREATE TABLE orders (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id              UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  total_price           NUMERIC(10,2) NOT NULL CHECK (total_price > 0),
  payment_status        payment_status NOT NULL DEFAULT 'pending',
  stripe_payment_intent TEXT,
  confirmation_status   confirmation_status NOT NULL DEFAULT 'pending',
  confirmation_deadline TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_buyer  ON orders(buyer_id);
CREATE INDEX idx_orders_status ON orders(payment_status, confirmation_status);

-- ORDER ITEMS
CREATE TABLE order_items (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id  UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE RESTRICT,
  UNIQUE (ticket_id)
);

-- ROW LEVEL SECURITY
ALTER TABLE users       ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_qrs  ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders      ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

-- Public read policies (for SSR home page using anon key)
CREATE POLICY "Public can read events" ON events FOR SELECT USING (true);
CREATE POLICY "Public can read cities" ON cities FOR SELECT USING (true);
