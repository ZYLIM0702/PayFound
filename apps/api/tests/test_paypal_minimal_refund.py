from fastapi import HTTPException
from sqlalchemy import select
from app import paypal
from app.database import SessionLocal
from app.models import Product, ProviderOperation, Refund


def captured_order(client, consumer, monkeypatch):
    async def create(order):
        return {'id': 'MINIMAL-REFUND-ORDER'}

    async def capture(provider_id, order_id):
        return {'id': provider_id, 'status': 'COMPLETED', 'purchase_units': [{'payments': {'captures': [
            {'id': 'MINIMAL-CAPTURE', 'status': 'COMPLETED', 'amount': {'currency_code': 'USD', 'value': '39.99'}}]}}]}

    monkeypatch.setattr(paypal, 'create_order', create)
    monkeypatch.setattr(paypal, 'capture_order', capture)
    made = client.post('/api/orders/reserve', headers=consumer,
        json={'product_id': 'p1', 'idempotency_key': 'minimal-refund-purchase'}).json()
    oid = made['id']
    assert client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).status_code == 200
    assert client.post(f'/api/orders/{oid}/paypal/capture', headers=consumer).json()['payment_status'] == 'CAPTURED'
    return oid


def test_minimal_refund_is_durably_identified_then_verified_and_restocked_once(client, consumer, merchant, monkeypatch):
    oid = captured_order(client, consumer, monkeypatch)
    writes, reads = [], []

    async def refund(capture_id, order_id):
        writes.append((capture_id, order_id))
        return {'id': 'MINIMAL-REFUND', 'status': 'COMPLETED', 'links': []}

    async def get_refund(refund_id):
        reads.append(refund_id)
        with SessionLocal() as db:
            intent = db.scalar(select(Refund).where(Refund.order_id == oid))
            operation = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == oid, ProviderOperation.kind == 'REFUND'))
            assert intent.provider_refund_id == refund_id
            assert operation.provider_id == refund_id and operation.lease_until is None
        return {'id': refund_id, 'status': 'COMPLETED', 'amount': {'currency_code': 'USD', 'value': '39.99'}}

    monkeypatch.setattr(paypal, 'refund_capture', refund)
    monkeypatch.setattr(paypal, 'get_refund', get_refund)
    result = client.post(f'/api/orders/{oid}/refund', headers=merchant)
    assert result.status_code == 200 and result.json()['payment_status'] == 'REFUNDED'
    assert client.post(f'/api/orders/{oid}/refund', headers=merchant).status_code == 200
    assert writes == [('MINIMAL-CAPTURE', oid)] and reads == ['MINIMAL-REFUND']
    with SessionLocal() as db:
        assert db.get(Product, 'p1').quantity == 9


def test_failed_readback_retries_known_refund_get_not_another_refund_write(client, consumer, merchant, monkeypatch):
    oid = captured_order(client, consumer, monkeypatch)
    calls = {'writes': 0, 'reads': 0}

    async def refund(capture_id, order_id):
        calls['writes'] += 1
        return {'id': 'RECOVERABLE-REFUND', 'status': 'COMPLETED'}

    async def get_refund(refund_id):
        calls['reads'] += 1
        if calls['reads'] == 1:
            raise HTTPException(504, 'Synthetic readback timeout')
        return {'id': refund_id, 'status': 'COMPLETED', 'amount': {'currency_code': 'USD', 'value': '39.99'}}

    monkeypatch.setattr(paypal, 'refund_capture', refund)
    monkeypatch.setattr(paypal, 'get_refund', get_refund)
    assert client.post(f'/api/orders/{oid}/refund', headers=merchant).status_code == 504
    assert client.get(f'/api/orders/{oid}', headers=consumer).json()['payment_status'] == 'REFUND_PENDING'
    recovered = client.post(f'/api/orders/{oid}/paypal/reconcile', headers=consumer)
    assert recovered.status_code == 200 and recovered.json()['payment_status'] == 'REFUNDED'
    assert calls == {'writes': 1, 'reads': 2}
