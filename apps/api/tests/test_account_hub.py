from sqlalchemy import select

from app.database import SessionLocal
from app.account_hub import PaymentMethod, ThreadMessage
from app.models import Merchant, Order


def my_order(client, headers):
    r = client.post('/api/orders/reserve', headers=headers, json={'product_id': 'p1', 'quantity': 1, 'idempotency_key': 'hub-key-0001'})
    assert r.status_code == 201, r.text
    return r.json()


def other_merchant_id():
    with SessionLocal() as db:
        other = db.scalar(select(Merchant).where(Merchant.id != 'm1'))
        if not other:
            db.add(Merchant(id='m-hub-other', name='Other Store', owner_subject='someone-else'))
            db.commit()
            return 'm-hub-other'
        return other.id


def test_paypal_sandbox_link_stores_only_masked_label(client, consumer, merchant):
    r = client.post('/api/me/payment-methods/paypal-sandbox', headers=consumer, json={'email': 'Jane.Doe@Example.com'})
    assert r.status_code == 201
    m = r.json()
    assert m['provider'] == 'paypal' and m['status'] == 'sandbox_linked' and m['sandbox'] is True
    assert m['label'] == 'j***@example.com'
    with SessionLocal() as db:
        row = db.get(PaymentMethod, m['id'])
        assert 'jane' not in (row.masked_email + row.status + row.provider).lower()
    # relinking updates the single record
    again = client.post('/api/me/payment-methods/paypal-sandbox', headers=consumer, json={'email': 'x@y.org'}).json()
    assert again['id'] == m['id']
    assert len(client.get('/api/me/payment-methods', headers=consumer).json()['methods']) == 1
    # other users see nothing and cannot remove it
    assert client.get('/api/me/payment-methods', headers=merchant).json()['methods'] == []
    assert client.delete(f"/api/me/payment-methods/{m['id']}", headers=merchant).status_code == 404
    assert client.delete(f"/api/me/payment-methods/{m['id']}", headers=consumer).status_code == 200
    assert client.get('/api/me/payment-methods', headers=consumer).json()['methods'] == []


def test_payment_method_rejects_secrets_and_bad_email(client, consumer):
    url = '/api/me/payment-methods/paypal-sandbox'
    for extra in ({'card_number': '4111111111111111'}, {'password': 'hunter2'}, {'token': 'abc'}):
        assert client.post(url, headers=consumer, json={'email': 'a@b.com', **extra}).status_code == 422
    assert client.post(url, headers=consumer, json={'email': 'not-an-email'}).status_code == 422
    assert client.get('/api/me/payment-methods', headers=consumer).json()['methods'] == []


def test_message_thread_ownership_and_sanitising(client, consumer, merchant):
    order = my_order(client, consumer)
    r = client.post('/api/me/messages/start', headers=consumer, json={'merchant_id': order['merchant_id'], 'order_id': order['id'], 'body': 'Hello <script>alert(1)</script>there'})
    assert r.status_code == 201, r.text
    thread = r.json()
    assert thread['created'] and thread['last_message']['body'] == 'Hello alert(1)there'
    # start again reuses the same thread
    assert client.post('/api/me/messages/start', headers=consumer, json={'merchant_id': order['merchant_id'], 'order_id': order['id']}).json()['id'] == thread['id']
    assert len(client.get('/api/me/messages', headers=consumer).json()['threads']) == 1
    assert client.get('/api/me/messages', headers={'x-demo-role': 'admin'}).json()['threads'] == []
    assert client.post(f"/api/me/messages/{thread['id']}", headers=consumer, json={'body': 'second'}).status_code == 201
    detail = client.get(f"/api/me/messages/{thread['id']}", headers=consumer).json()
    assert [m['sender'] for m in detail['messages']] == ['buyer', 'buyer'] and detail['viewer'] == 'buyer'
    # empty after sanitising, and too long
    assert client.post(f"/api/me/messages/{thread['id']}", headers=consumer, json={'body': '<b></b>  '}).status_code == 422
    assert client.post(f"/api/me/messages/{thread['id']}", headers=consumer, json={'body': 'x' * 1001}).status_code == 422
    assert client.post(f"/api/me/messages/{thread['id']}", headers=consumer, json={'body': 'x' * 1000}).status_code == 201
    # another order that is not yours / wrong merchant
    assert client.post('/api/me/messages/start', headers=merchant, json={'merchant_id': order['merchant_id'], 'order_id': order['id']}).status_code == 404
    assert client.post('/api/me/messages/start', headers=consumer, json={'merchant_id': 'nope'}).status_code == 404


def test_merchant_reply_only_for_members(client, consumer, merchant):
    order = my_order(client, consumer)
    t = client.post('/api/me/messages/start', headers=consumer, json={'merchant_id': order['merchant_id'], 'order_id': order['id'], 'body': 'Is it ready?'}).json()
    # staff of that merchant may read and reply
    assert client.get(f"/api/me/messages/{t['id']}", headers=merchant).json()['viewer'] == 'merchant'
    reply = client.post(f"/api/me/messages/{t['id']}", headers=merchant, json={'body': 'Yes, ready.'})
    assert reply.status_code == 201 and reply.json()['sender'] == 'merchant'
    # a thread with a different store is invisible to demo merchant (member of m1 only)
    other = other_merchant_id()
    t2 = client.post('/api/me/messages/start', headers=consumer, json={'merchant_id': other, 'body': 'Hi'}).json()
    assert client.get(f"/api/me/messages/{t2['id']}", headers=merchant).status_code == 404
    assert client.post(f"/api/me/messages/{t2['id']}", headers=merchant, json={'body': 'sneaky'}).status_code == 404
    with SessionLocal() as db:
        assert db.scalar(select(ThreadMessage).where(ThreadMessage.thread_id == t2['id'], ThreadMessage.sender_role == 'merchant')) is None
    assert client.get('/api/me/messages/missing', headers=consumer).status_code == 404


def test_message_rate_limit(client, consumer):
    t = client.post('/api/me/messages/start', headers=consumer, json={'merchant_id': 'm1'}).json()
    codes = [client.post(f"/api/me/messages/{t['id']}", headers=consumer, json={'body': f'm{i}'}).status_code for i in range(22)]
    assert codes[:20] == [201] * 20 and 429 in codes[20:]


def test_support_ticket_owner_only_and_sanitised(client, consumer, merchant):
    r = client.post('/api/me/support-tickets', headers=consumer, json={'topic': 'refunds', 'subject': ' Where is <i>my</i> refund? ', 'message': 'It has been a week.'})
    assert r.status_code == 201
    ticket = r.json()
    assert ticket['subject'] == 'Where is my refund?' and ticket['status'] == 'open' and ticket['topic'] == 'refunds'
    assert client.post('/api/me/support-tickets', headers=consumer, json={'topic': 'weird', 'subject': 's', 'message': 'm'}).json()['topic'] == 'other'
    assert client.post('/api/me/support-tickets', headers=consumer, json={'subject': 'x' * 121, 'message': 'm'}).status_code == 422
    assert client.post('/api/me/support-tickets', headers=consumer, json={'subject': 's', 'message': 'm' * 2001}).status_code == 422
    assert client.post('/api/me/support-tickets', headers=consumer, json={'subject': 's', 'message': 'm', 'order_id': 'demo-ord-01'}).status_code == 404
    mine = client.get('/api/me/support-tickets', headers=consumer).json()['tickets']
    assert len(mine) == 2
    assert client.get('/api/me/support-tickets', headers=merchant).json()['tickets'] == []


def test_demo_messages_seed_is_idempotent(client):
    from app.demo_orders import SHOPPER, seed_demo_orders, seed_demo_messages
    with SessionLocal() as db:
        seed_demo_orders(db, force=True)
        db.commit()
        seed_demo_messages(db)
        seed_demo_messages(db)
        db.commit()
    headers = {'x-demo-role': 'consumer'}
    threads = client.get('/api/me/messages', headers=headers).json()['threads']
    assert len(threads) == 2
    with SessionLocal() as db:
        assert db.scalar(select(Order.id).where(Order.id == 'demo-ord-01')) and SHOPPER == 'demo-consumer'
