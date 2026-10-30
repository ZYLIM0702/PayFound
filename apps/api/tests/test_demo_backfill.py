"""Demo backfill for m1: extra products + 90 days of history; idempotent, history-only, demo-only."""
import pytest
from sqlalchemy import func, select

from app.database import SessionLocal, engine
from app.demo_backfill import seed_demo_backfill
from app.demo_catalogue import seed_expanded_demo
from app.demo_orders import seed_demo_orders
from app.models import InventoryReservation, Notification, Order, OrderItem, PaymentEvent, Product


@pytest.fixture()
def seeded(client):
    if engine.dialect.name != 'sqlite':
        pytest.skip('Demo backfill is local-only')
    with SessionLocal() as db:
        seed_expanded_demo(db, force=True)
        seed_demo_orders(db, force=True)
        db.commit()
    return client


def _run(force=True):
    with SessionLocal() as db:
        out = seed_demo_backfill(db, force=force)
        db.commit()
    return out


def test_adds_products_and_orders_idempotently(seeded):
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(Order).where(~Order.id.like('bf-%')))
        stock = {p.id: (p.quantity, p.hold_quantity) for p in db.scalars(select(Product).where(~Product.id.like('bf-p-%')))}
    first = _run()
    assert first['products'] >= 30 and 1000 <= first['orders'] <= 2400
    assert _run() == {'products': 0, 'orders': 0}
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Product).where(Product.merchant_id == 'm1', Product.active.is_(True),
            Product.id.like('bf-p-%'))) >= 30
        assert db.scalar(select(func.count()).select_from(Order).where(~Order.id.like('bf-%'))) == before
        assert {p.id: (p.quantity, p.hold_quantity) for p in db.scalars(select(Product).where(~Product.id.like('bf-p-%')))} == stock


def test_orders_are_consistent_and_history_only(seeded):
    _run()
    with SessionLocal() as db:
        orders = list(db.scalars(select(Order).where(Order.id.like('bf-%'))))
        lines = {}
        for it in db.scalars(select(OrderItem).where(OrderItem.order_id.like('bf-%'))):
            lines.setdefault(it.order_id, []).append(it)
        product_ids = set(db.scalars(select(Product.id).where(Product.merchant_id == 'm1')))
        statuses = {o.status for o in orders}
        assert statuses <= {'COLLECTED', 'CANCELLED', 'EXPIRED', 'REFUNDED'} and 'COLLECTED' in statuses and 'REFUNDED' in statuses
        for o in orders:
            assert o.merchant_id == 'm1' and o.currency == 'USD' and o.payment_mode == 'demo'
            assert o.amount_cents == sum(i.quantity * i.unit_price_cents for i in lines[o.id])
            assert all(i.product_id in product_ids and 1 <= i.quantity <= 3 for i in lines[o.id])
            assert o.buyer_subject.startswith('demo-buyer-') and o.buyer_subject != 'demo-consumer'
            assert o.payment_status == {'COLLECTED': 'CAPTURED', 'REFUNDED': 'REFUNDED', 'CANCELLED': 'NOT_STARTED', 'EXPIRED': 'EXPIRED'}[o.status]
            assert o.updated_at >= o.created_at
        assert db.scalar(select(func.count()).select_from(InventoryReservation).where(InventoryReservation.order_id.like('bf-%'))) == 0
        assert db.scalar(select(func.count()).select_from(PaymentEvent).where(PaymentEvent.order_id.like('bf-%'))) == 0


def test_demo_shopper_orders_untouched(seeded):
    def snapshot():
        with SessionLocal() as db:
            return [(o.id, o.status, o.amount_cents, o.updated_at) for o in db.scalars(
                select(Order).where(Order.buyer_subject == 'demo-consumer').order_by(Order.id))]
    before = snapshot()
    assert before
    _run()
    assert snapshot() == before


def test_demo_mode_off_or_testing_creates_nothing(seeded, monkeypatch):
    assert _run(force=False) == {'products': 0, 'orders': 0}
    monkeypatch.setenv('DEMO_MODE', 'false')
    assert _run(force=True) == {'products': 0, 'orders': 0}
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Order).where(Order.id.like('bf-%'))) == 0
