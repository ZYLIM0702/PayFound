"""Varied, clearly synthetic order history for the demo shopper (subject `demo-consumer`)."""
from __future__ import annotations
import os
import random
from datetime import timedelta

from sqlalchemy import select

from .models import (Merchant, Order, OrderItem, PickupBooking, PickupSlot, Product, Review, utcnow)

SHOPPER = 'demo-consumer'
# (days ago, status, payment_status, payment_mode, items, review rating or None)
SPECS = [
    (1, 'READY', 'CAPTURED', 'demo', 2, None),
    (2, 'PREPARING', 'CAPTURED', 'paypal_sandbox', 3, None),
    (3, 'ACCEPTED', 'CAPTURED', 'demo', 1, None),
    (4, 'RESERVED', 'CREATED', 'paypal_sandbox', 2, None),
    (6, 'COLLECTED', 'CAPTURED', 'demo', 1, None),
    (9, 'COLLECTED', 'CAPTURED', 'paypal_sandbox', 3, 5),
    (12, 'CANCELLED', 'NOT_STARTED', None, 1, None),
    (15, 'COLLECTED', 'CAPTURED', 'demo', 2, 4),
    (19, 'REFUNDED', 'REFUNDED', 'paypal_sandbox', 1, None),
    (23, 'EXPIRED', 'EXPIRED', None, 2, None),
    (28, 'COLLECTED', 'CAPTURED', 'demo', 3, 3),
    (33, 'COLLECTED', 'CAPTURED', 'paypal_sandbox', 1, None),
    (38, 'CANCELLED', 'NOT_STARTED', None, 2, None),
    (44, 'COLLECTED', 'CAPTURED', 'demo', 2, 5),
    (51, 'REFUNDED', 'REFUNDED', 'demo', 2, None),
    (57, 'COLLECTED', 'CAPTURED', 'demo', 1, 4),
]
REVIEW_TEXT = {
    5: 'Everything was packed and waiting at the counter. (sample review)',
    4: 'Good pickup, short wait at the till. (sample review)',
    3: 'Fine overall, one item was a different brand. (sample review)',
}
OPEN = {'ACCEPTED', 'PREPARING', 'READY'}


def seed_demo_orders(db, force: bool = False) -> int:
    """Create the demo shopper's order history once. Returns the number of orders created."""
    if os.getenv('DEMO_MODE', 'false').lower() != 'true':
        return 0
    if not force and os.getenv('PAYFOUND_TESTING') == '1':
        return 0
    if db.get(Order, 'demo-ord-01'):
        seed_demo_messages(db)
        return 0
    merchants = []
    for m in db.scalars(select(Merchant).order_by(Merchant.id)):
        products = list(db.scalars(select(Product).where(Product.merchant_id == m.id, Product.active.is_(True),
            Product.location_id.is_not(None), Product.price_cents > 0, Product.currency == 'USD').order_by(Product.id)))
        if len(products) >= 3:
            merchants.append((m, products))
    if not merchants:
        return 0
    rng = random.Random(20261023)
    rng.shuffle(merchants)
    now = utcnow()
    seen: set[tuple] = set()
    created = 0
    for n, (days, status, pay, mode, n_items, rating) in enumerate(SPECS, 1):
        merchant, products = merchants[(n - 1) % len(merchants)]
        for _ in range(20):
            picks = rng.sample(products, min(n_items, len(products)))
            lines = [(p, rng.choice([1, 1, 2, 3])) for p in picks]
            sig = (merchant.id, tuple(sorted((p.id, q) for p, q in lines)))
            if sig not in seen:
                seen.add(sig)
                break
        total = sum(p.price_cents * q for p, q in lines)
        created_at = now - timedelta(days=days, hours=rng.randint(0, 9), minutes=rng.randint(0, 59))
        oid = f'demo-ord-{n:02d}'
        paid = pay in ('CAPTURED', 'REFUNDED')
        order = Order(id=oid, merchant_id=merchant.id, location_id=lines[0][0].location_id, product_id=lines[0][0].id,
            quantity=lines[0][1], amount_cents=total, currency='USD', buyer_subject=SHOPPER, buyer_name='Demo shopper',
            status=status, payment_status=pay, payment_mode=mode, idempotency_key=oid,
            paypal_order_id=f'DEMO-SBX-ORDER-{n:02d}' if mode == 'paypal_sandbox' else None,
            paypal_capture_id=f'DEMO-SBX-CAPTURE-{n:02d}' if mode == 'paypal_sandbox' and paid else None,
            paypal_refund_id=f'DEMO-SBX-REFUND-{n:02d}' if mode == 'paypal_sandbox' and pay == 'REFUNDED' else None,
            hold_expires_at=now + timedelta(days=30) if status == 'RESERVED' else created_at + timedelta(minutes=20),
            hold_released=status != 'RESERVED', inventory_committed=paid and status != 'REFUNDED',
            inventory_restocked=status == 'REFUNDED', created_at=created_at, updated_at=created_at)
        db.add(order)
        db.flush()
        for p, q in lines:
            db.add(OrderItem(id=f'{oid}-{p.id}'[:48], order_id=oid, product_id=p.id, product_name=p.name,
                             sku=p.sku, quantity=q, unit_price_cents=p.price_cents))
        if status in OPEN:
            start = (now + timedelta(hours=1 + n)).replace(minute=0, second=0, microsecond=0)
            slot = db.scalar(select(PickupSlot).where(PickupSlot.location_id == order.location_id, PickupSlot.start_at == start))
            if not slot:
                slot = PickupSlot(id=f'demo-slot-{n:02d}', merchant_id=merchant.id, location_id=order.location_id,
                                  start_at=start, end_at=start + timedelta(minutes=30), capacity=5, booked_count=0)
                db.add(slot)
                db.flush()
            slot.booked_count += 1
            db.add(PickupBooking(id=f'demo-book-{n:02d}', order_id=oid, slot_id=slot.id, active=True))
        if rating:
            db.add(Review(id=f'demo-rev-{n:02d}', merchant_id=merchant.id, order_id=oid, buyer_subject=SHOPPER,
                          rating=rating, body=REVIEW_TEXT[rating], created_at=created_at + timedelta(days=1)))
        created += 1
    _seed_wishlist(db, rng, merchants)
    db.flush()
    seed_demo_messages(db)
    return created


def seed_demo_messages(db) -> None:
    """Two realistic conversations for the demo shopper about their collections. Idempotent; demo data only."""
    from .account_hub import MessageThread, ThreadMessage
    now = utcnow()
    specs = [
        ('demo-thr-1', 'demo-ord-01', 'buyer', 'Hi, I am collecting my order around 5pm. Will it be ready?', timedelta(hours=6)),
        ('demo-thr-1', 'demo-ord-01', 'merchant', 'Hi! Yes, it is packed and waiting at the front counter. Just give the name on the order.', timedelta(hours=5, minutes=40)),
        ('demo-thr-1', 'demo-ord-01', 'buyer', 'Great, thank you. Do you have a bag for the cables?', timedelta(hours=5, minutes=35)),
        ('demo-thr-1', 'demo-ord-01', 'merchant', 'We do, one free bag per order. See you soon.', timedelta(hours=5, minutes=30)),
        ('demo-thr-2', 'demo-ord-02', 'buyer', 'Hi, the hammer I reserved is the 16oz. Could I swap it for the 20oz?', timedelta(hours=27)),
        ('demo-thr-2', 'demo-ord-02', 'merchant', 'Sure, the 20oz is in stock at this branch. I will set it aside. The difference is $3.50, paid at pickup.', timedelta(hours=26, minutes=30)),
        ('demo-thr-2', 'demo-ord-02', 'buyer', 'Perfect, I will pick it up tomorrow morning. Thanks!', timedelta(hours=26)),
    ]
    for tid, oid, side, text, ago in specs:
        order = db.get(Order, oid)
        if not order:
            continue
        thread = db.get(MessageThread, tid)
        if not thread:
            thread = MessageThread(id=tid, buyer_subject=SHOPPER, merchant_id=order.merchant_id, order_id=oid,
                                   subject=f'Order {oid[-8:]}', created_at=now - ago, updated_at=now - ago)
            db.add(thread)
            db.flush()
        mid = f'{tid}-{side}-{int(ago.total_seconds())}'
        if db.get(ThreadMessage, mid):
            continue
        db.add(ThreadMessage(id=mid, thread_id=tid, sender_role=side,
                             sender_subject=SHOPPER if side == 'buyer' else f'merchant:{order.merchant_id}', body=text, created_at=now - ago))
        thread.updated_at = max(thread.updated_at, now - ago)
    db.flush()
    seed_demo_enquiries(db)


# Pre-purchase enquiries for the demo business's stores. Each one is its own thread, so each chat stays separate.
DEMO_ENQUIRIES = [
    ('demo-enq-1', 'm1', 'Mei Lin', 'Stock question', [
        ('buyer', 'Do you have the USB-C cable 2m in stock today?', 26),
        ('merchant', 'Yes, we have 6 at the front counter. Reserve online and collect whenever suits you.', 25)]),
    ('demo-enq-2', 'm1', 'Sam Okafor', 'Opening hours', [
        ('buyer', 'Are you open on public holidays?', 9),
        ('merchant', 'We are open 10 to 6 on public holidays. Closed Christmas Day.', 8)]),
    ('demo-enq-3', 'm11', 'Priya Nair', 'Pet food', [
        ('buyer', 'Do you carry the grain-free salmon kibble for adult cats?', 4),
        ('buyer', 'Also, is there a discount for bulk bags?', 4),
        ('merchant', 'We do stock it, 4 bags left. Bulk bags over 10kg get 5% off at the counter.', 3)]),
    ('demo-enq-4', 'm12', 'Tom Reyes', 'Tent availability', [
        ('buyer', 'Can I check if the 3-person tent is available for pickup this weekend?', 50),
        ('merchant', 'Yes, one left in green. I can hold it until Saturday noon if you reserve it.', 48)]),
    ('demo-enq-5', 'm14', 'Hannah Lee', 'Gluten-free options', [
        ('buyer', 'Which of your loaves are gluten free?', 2)]),
    ('demo-enq-6', 'm16', 'Jordan Blake', 'Custom cake', [
        ('buyer', 'Can you do a 2-tier birthday cake with a 48 hour notice?', 30),
        ('merchant', 'Yes, 48 hours works. Tell us the flavour and the pickup time and we will confirm the price.', 28)]),
]


def seed_demo_enquiries(db) -> int:
    """Pre-sale enquiries for the demo business's stores. Idempotent; demo data only. Returns threads created."""
    from .account_hub import MessageThread, ThreadMessage
    created = 0
    now = utcnow()
    for tid, merchant_id, buyer_name, subject, turns in DEMO_ENQUIRIES:
        if db.get(MessageThread, tid) or not db.get(Merchant, merchant_id):
            continue
        first = now - timedelta(hours=turns[0][2])
        thread = MessageThread(id=tid, buyer_subject=f'demo-enquirer-{tid[-1]}', merchant_id=merchant_id, order_id=None,
                               subject=subject, buyer_name=buyer_name, created_at=first, updated_at=first)
        db.add(thread)
        db.flush()
        for index, (side, text, hours_ago) in enumerate(turns):
            at = now - timedelta(hours=hours_ago)
            db.add(ThreadMessage(id=f'{tid}-{index}-{side}', thread_id=tid, sender_role=side,
                                 sender_subject=f'demo-enquirer-{tid[-1]}' if side == 'buyer' else f'merchant:{merchant_id}', body=text, created_at=at))
            thread.updated_at = max(thread.updated_at, at)
        created += 1
    db.flush()
    return created


def _seed_wishlist(db, rng, merchants) -> None:
    from .account import WishlistItem
    pool = [p for _, products in merchants for p in products]
    for i, p in enumerate(rng.sample(pool, min(5, len(pool)))):
        wid = f'demo-wish-{i + 1}'
        if db.get(WishlistItem, wid):
            continue
        # i=0 saved dearer than today (price dropped), i=1 saved while out of stock (back in stock), others unchanged.
        saved_price = int(p.price_cents * 1.18) if i == 0 else p.price_cents
        db.add(WishlistItem(id=wid, owner_subject=SHOPPER, product_id=p.id, saved_price_cents=saved_price,
                            saved_in_stock=i != 1, created_at=utcnow() - timedelta(days=3 + i * 5)))


def seed_demo_basket(db) -> int:
    """Give the demo shopper a small starting basket, once. A basket the shopper later empties stays empty."""
    if os.getenv('DEMO_MODE', 'false').lower() != 'true' or os.getenv('PAYFOUND_TESTING') == '1':
        return 0
    from .basket import BasketLine
    from .commerce import audit
    from .models import Audit
    marker = 'demo_basket_seeded'
    if db.scalar(select(Audit.id).where(Audit.action == marker).limit(1)):
        return 0
    audit(db, SHOPPER, marker)
    if db.scalar(select(BasketLine.product_id).where(BasketLine.owner_subject == SHOPPER).limit(1)):
        return 0
    store = db.scalar(select(Merchant).where(Merchant.id == 'm1'))
    picks = list(db.scalars(select(Product).where(Product.merchant_id == (store.id if store else 'm1'), Product.active.is_(True),
        Product.quantity - Product.hold_quantity >= 3, Product.price_cents > 0).order_by(Product.id).limit(3)))
    for position, product in enumerate(picks):
        db.add(BasketLine(owner_subject=SHOPPER, product_id=product.id, quantity=2 if position == 0 else 1, position=position))
    return len(picks)
