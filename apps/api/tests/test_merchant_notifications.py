from sqlalchemy import select

from app.database import SessionLocal
from app.merchant_notify import MerchantNotification
from app.models import Merchant, MerchantMembership

KEY = 'rsv-key-000001'


def reserve(client, headers, key=KEY, qty=2):
    return client.post('/api/orders/reserve', headers=headers,
                       json={'product_id': 'p1', 'quantity': qty, 'idempotency_key': key, 'buyer_name': 'Ava'})


def add_staff(*subjects, merchant_id='m1', active=True):
    with SessionLocal() as db:
        for i, s in enumerate(subjects):
            db.add(MerchantMembership(id=f'mem-rsv-{merchant_id}-{i}-{s}', merchant_id=merchant_id, subject=s, role='staff', active=active))
        db.commit()


def rows():
    with SessionLocal() as db:
        return list(db.scalars(select(MerchantNotification)))


def test_one_notification_per_active_staff_and_idempotent(client, consumer, merchant):
    add_staff('staff-a', 'staff-b')
    add_staff('staff-gone', active=False)
    r = reserve(client, consumer)
    assert r.status_code == 201, r.text
    got = rows()
    assert sorted(n.recipient_subject for n in got) == ['demo-merchant', 'staff-a', 'staff-b']
    assert all(n.event_type == 'reservation' and 'New reservation: 2 ×' in n.message and 'please prepare' in n.message for n in got)
    assert reserve(client, consumer).status_code in (200, 201)
    assert len(rows()) == 3
    feed = client.get('/api/merchant/notifications', headers=merchant).json()
    assert feed['unread'] == 1 and feed['notifications'][0]['order_id'] == r.json()['id']


def test_read_marks_only_own_row_and_other_merchant_gets_404(client, consumer, merchant):
    with SessionLocal() as db:
        db.add(Merchant(id='m-other', name='Other', slug='other', latitude=1.0, longitude=1.0, owner_subject='other-owner'))
        db.commit()
    add_staff('demo-consumer', merchant_id='m-other')
    reserve(client, consumer)
    nid = client.get('/api/merchant/notifications', headers=merchant).json()['notifications'][0]['id']
    # demo-consumer is staff of ANOTHER merchant: cannot see or mark m1's notification
    assert client.post(f'/api/merchant/notifications/{nid}/read', headers=consumer).status_code == 404
    assert client.get('/api/merchant/notifications?merchant_id=m1', headers=consumer).status_code == 403
    assert client.get('/api/merchant/notifications', headers=consumer).json()['notifications'] == []
    assert client.post(f'/api/merchant/notifications/missing/read', headers=merchant).status_code == 404
    assert client.post(f'/api/merchant/notifications/{nid}/read', headers=merchant).status_code == 200
    assert client.post(f'/api/merchant/notifications/{nid}/read', headers=merchant).status_code == 200
    feed = client.get('/api/merchant/notifications', headers=merchant).json()
    assert feed['unread'] == 0 and feed['notifications'][0]['seen_at']
    assert [n for n in rows() if n.recipient_subject == 'demo-merchant'][0].seen_at is not None
