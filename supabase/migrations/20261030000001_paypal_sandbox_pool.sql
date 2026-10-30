-- Mirror of apps/api Alembic a014paypalpool. NOT applied automatically.
-- Sandbox receiving-account pool: email + display label only. Never passwords or card numbers.
create table if not exists public.paypal_sandbox_accounts (
  id text primary key,
  email text not null unique,
  display_label text not null default '',
  country text not null default 'US',
  account_type text not null default 'BUSINESS',
  assigned_to_subject text,
  assigned_to_merchant_id text unique references public.merchants(id),
  created_at timestamptz not null default now()
);
create table if not exists public.paypal_demo_payments (
  id text primary key,
  merchant_id text not null references public.merchants(id),
  order_id text,
  provider text not null default 'paypal_sandbox',
  stage text not null,
  amount_cents integer not null,
  currency text not null,
  reference text not null,
  demo_seeded boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists ix_paypal_demo_payments_merchant on public.paypal_demo_payments (merchant_id);
alter table public.paypal_sandbox_accounts enable row level security;
alter table public.paypal_demo_payments enable row level security;
-- No policies: server (service role) access only.
