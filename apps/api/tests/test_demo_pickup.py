"""Demo pickup schedule: busy, capacity-safe, idempotent, demo-only."""
from datetime import timedelta

import pytest
from sqlalchemy import func, select

from app.database import SessionLocal, engine
from app.demo_catalogue import seed_expanded_demo
from app.demo_pickup import seed_demo_pickup
from app.models import MerchantLocation, Order, PickupBooking, PickupSlot, utcnow


@pytest.fixture()
def seeded(client):
    if engine.dialect.name != 'sqlite':
        pytest.skip('Demo pickup fixture is local-only')
    with SessionLocal() as db:
        seed_expanded_demo(db, force=True)
        db.commit()
        seed_demo_pickup(db, force=True)
        db.commit()
    return client


def test_every_branch_has_a_week_of_slots(seeded):
    with SessionLocal() as db:
        branches = list(db.scalars(select(MerchantLocation.id).where(MerchantLocation.active.is_(True))))
        assert len(branches) >= 40
        now = utcnow()
        for loc in branches:
            days = {s.start_at.date() for s in db.scalars(select(PickupSlot).where(PickupSlot.location_id == loc))
                    if now - timedelta(days=2) < s.start_at < now + timedelta(days=9)}
            assert len(days) >= 7, loc
        assert db.get(MerchantLocation, 'loc-m1-b2') and db.get(MerchantLocation, 'loc-m1-b3')


def test_capacities_respected_and_pattern_varied(seeded):
    with SessionLocal() as db:
        slots = list(db.scalars(select(PickupSlot).where(PickupSlot.id.like('dp-%'))))
        assert len(slots) > 3000
        assert all(0 <= s.booked_count <= s.capacity for s in slots)
        assert any(s.booked_count == s.capacity for s in slots)
        assert any(s.booked_count == 0 for s in slots)
        fresh = [s.capacity for s in slots if s.location_id == 'loc-m14']
        hardware = [s.capacity for s in slots if s.location_id == 'loc-m2']
        assert sum(fresh) / len(fresh) > sum(hardware) / len(hardware)


def test_idempotent_and_orders_linked(seeded):
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(PickupSlot))
        orders = db.scalar(select(func.count()).select_from(Order))
        assert seed_demo_pickup(db, force=True) == 0
        assert db.scalar(select(func.count()).select_from(PickupSlot)) == before
        assert db.scalar(select(func.count()).select_from(Order)) == orders
        linked = list(db.scalars(select(PickupBooking).where(PickupBooking.id.like('demo-pkb-%'))))
        assert len(linked) >= 20
        for b in linked:
            slot = db.get(PickupSlot, b.slot_id)
            assert slot.booked_count >= 1 and db.get(Order, b.order_id).location_id == slot.location_id


def test_nothing_seeded_when_demo_mode_off(client, monkeypatch):
    monkeypatch.setenv('DEMO_MODE', 'false')
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(PickupSlot))
        assert seed_demo_pickup(db, force=True) == 0
        assert db.scalar(select(func.count()).select_from(PickupSlot)) == before
