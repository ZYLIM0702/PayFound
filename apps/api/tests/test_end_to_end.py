import uuid
from app import paypal

def reserve(client,headers,key=None,product_id='p1',quantity=1):
    return client.post('/api/orders/reserve',headers=headers,json={'product_id':product_id,'quantity':quantity,'idempotency_key':key or uuid.uuid4().hex})

def test_discovery_and_storefront(client):
    assert client.get('/api/health').json()['ok']
    stores=client.get('/api/merchants').json()
    assert len(stores)==4
    products=client.get('/api/products?q=charger').json()
    assert len(products)>=1
    assert all(p['in_stock'] for p in products)
    store=client.get('/api/merchants/northside-electronics').json()
    assert store['rating'] is not None
    assert store['reviews'][0]['demo_review'] is True
    assert len(store['products'])==4

def test_hold_idempotency_and_stock_limit(client,consumer):
    key=uuid.uuid4().hex
    r=reserve(client,consumer,key=key,product_id='p4',quantity=2)
    assert r.status_code==201,r.text
    again=reserve(client,consumer,key=key,product_id='p4',quantity=2)
    assert again.json()['id']==r.json()['id']
    blocked=reserve(client,consumer,product_id='p4',quantity=2)
    assert blocked.status_code==409
    prod=next(p for p in client.get('/api/products?q=mouse').json() if p['id']=='p4')
    assert prod['available_quantity']==1
    canceled=client.post(f"/api/orders/{r.json()['id']}/cancel",headers=consumer)
    assert canceled.status_code==200
    assert next(p for p in client.get('/api/products?q=mouse').json() if p['id']=='p4')['available_quantity']==3

def test_demo_payment_fulfilment_review_and_moderation(client,consumer,merchant,admin):
    response=reserve(client,consumer)
    oid=response.json()['id']
    r=client.post(f'/api/orders/{oid}/mock-pay',headers=consumer)
    assert r.status_code==200,r.text
    assert r.json()['payment_status']=='CAPTURED'
    assert r.json()['payment_mode']=='demo'
    assert client.post(f'/api/orders/{oid}/mock-pay',headers=consumer).status_code==200
    before=client.post('/api/reviews',headers=consumer,json={'order_id':oid,'rating':5,'body':'Perfect'})
    assert before.status_code==403
    for status in ['ACCEPTED','PREPARING','READY','COLLECTED']:
        next_response=client.post(f'/api/orders/{oid}/fulfilment',headers=merchant,json={'status':status})
        assert next_response.status_code==200,next_response.text
    review=client.post('/api/reviews',headers=consumer,json={'order_id':oid,'rating':5,'body':'Worked'})
    assert review.status_code==201,review.text
    assert client.post('/api/reviews',headers=consumer,json={'order_id':oid,'rating':5}).status_code==409
    rid=review.json()['id']
    assert client.patch(f'/api/admin/reviews/{rid}',headers=merchant,json={'visible':False}).status_code==403
    assert client.patch(f'/api/admin/reviews/{rid}',headers=admin,json={'visible':False}).json()['visible'] is False
    storefront=client.get('/api/merchants/northside-electronics').json()
    assert not any(x['id']==rid for x in storefront['reviews'])

def test_role_enforcement(client,consumer,merchant,admin):
    assert client.get('/api/merchant/dashboard',headers=consumer).status_code==403
    assert client.get('/api/admin/overview',headers=merchant).status_code==403
    assert client.get('/api/admin/overview',headers=admin).status_code==200
    assert client.patch('/api/merchant/products/p5/stock',headers=merchant,json={'quantity':8}).status_code==403
    assert client.patch('/api/merchant/products/p1/stock',headers=merchant,json={'quantity':8}).status_code==200
    assert client.patch('/api/merchant/status',headers=merchant,json={'status':'closed'}).json()['status_override']=='closed'
    assert reserve(client,consumer).status_code==409

def test_mock_payment_only_demo_and_paypal_requires_credentials(client,consumer):
    oid=reserve(client,consumer).json()['id']
    assert client.post(f'/api/orders/{oid}/paypal/create',headers=consumer).status_code==503
    assert client.post('/api/paypal/webhook',json={'id':'fake'}).status_code==503
    assert client.get('/api/config').json()['paypal_sandbox_enabled'] is False

def test_agent_no_payments(client,consumer,merchant):
    result=client.post('/api/agents/shop',headers=consumer,json={'message':'USB-C charger'}).json()
    assert result['requires_user_confirmation_for_payment'] is True
    assert len(result['products'])>=1
    assert 'payments' in client.get('/api/agents/tools').json()
    assert client.post('/api/agents/merchant',headers=consumer,json={'message':'low stock'}).status_code==403
    assert len(client.post('/api/agents/merchant',headers=merchant,json={'message':'low stock'}).json()['low_stock'])>=1

def test_refund_demo(client,consumer,merchant):
    oid=reserve(client,consumer,product_id='p4').json()['id']
    client.post(f'/api/orders/{oid}/mock-pay',headers=consumer)
    r=client.post(f'/api/orders/{oid}/refund',headers=merchant)
    assert r.status_code==200,r.text
    assert r.json()['payment_status']=='REFUNDED'
    assert r.json()['status']=='CANCELLED'
    assert client.post(f'/api/orders/{oid}/fulfilment',headers=merchant,json={'status':'ACCEPTED'}).status_code==409

def test_paypal_api_contract_with_provider_stub(client,consumer,monkeypatch):
    # Contract test: simulated provider responses. NOT an actual PayPal sandbox payment.
    import app.paypal as module
    monkeypatch.setenv('PAYPAL_CLIENT_ID','sandbox-example')
    monkeypatch.setenv('PAYPAL_CLIENT_SECRET','example-not-real')
    oid=reserve(client,consumer,product_id='p1').json()['id']
    async def mock_create(order):
        assert order.amount_cents==3999
        assert order.currency=='USD'
        return {'id':'SYNTHETIC-PAYPAL-ORDER-1'}
    async def mock_capture(provider_id,order_id):
        assert provider_id=='SYNTHETIC-PAYPAL-ORDER-1'
        return {'id':provider_id,'status':'COMPLETED','purchase_units':[{'payments':{'captures':[{'id':'SYNTHETIC-CAPTURE-1','status':'COMPLETED','amount':{'currency_code':'USD','value':'39.99'}}]}}]}
    monkeypatch.setattr(module,'create_order',mock_create)
    monkeypatch.setattr(module,'capture_order',mock_capture)
    made=client.post(f'/api/orders/{oid}/paypal/create',headers=consumer)
    assert made.status_code==200,made.text
    assert made.json()['id']=='SYNTHETIC-PAYPAL-ORDER-1'
    result=client.post(f'/api/orders/{oid}/paypal/capture',headers=consumer)
    assert result.status_code==200,result.text
    assert result.json()['payment_status']=='CAPTURED'
    assert result.json()['payment_mode']=='paypal_sandbox'
    assert client.post(f'/api/orders/{oid}/paypal/capture',headers=consumer).json()['payment_status']=='CAPTURED'

def test_reservation_key_reuse_different_item_rejected(client,consumer):
    key=uuid.uuid4().hex
    first=reserve(client,consumer,key=key,product_id='p1')
    assert first.status_code==201
    conflict=reserve(client,consumer,key=key,product_id='p2')
    assert conflict.status_code==409
    assert client.get(f"/api/orders/{first.json()['id']}",headers=consumer).json()['product_id']=='p1'


def test_closed_merchant_cannot_reserve_and_admin_checks(client,consumer,merchant):
    changed=client.patch('/api/merchant/status',headers=merchant,json={'status':'closed'})
    assert changed.status_code==200
    assert client.get('/api/merchants/northside-electronics').json()['is_open'] is False
    assert reserve(client,consumer,product_id='p1').status_code==409
    client.patch('/api/merchant/status',headers=merchant,json={'status':'open'})
    assert reserve(client,consumer,product_id='p1').status_code==201


def test_paypal_wrong_amount_enters_reconciliation_without_faking_capture(client,consumer,monkeypatch):
    import app.paypal as module
    order=reserve(client,consumer,product_id='p1').json()
    oid=order['id']
    async def create(_):return {'id':'TEST-ORDER-WRONG-AMOUNT'}
    async def capture(_provider_id,_order_id):return {'id':'TEST-ORDER-WRONG-AMOUNT','status':'COMPLETED','purchase_units':[{'payments':{'captures':[{'id':'TEST-CAPTURE','status':'COMPLETED','amount':{'currency_code':'USD','value':'0.01'}}]}}]}
    monkeypatch.setattr(module,'create_order',create)
    monkeypatch.setattr(module,'capture_order',capture)
    assert client.post(f'/api/orders/{oid}/paypal/create',headers=consumer).status_code==200
    result=client.post(f'/api/orders/{oid}/paypal/capture',headers=consumer)
    assert result.status_code==409
    later=client.get(f'/api/orders/{oid}',headers=consumer).json()
    assert later['payment_status']=='RECONCILIATION_REQUIRED'
    assert later['status']=='RESERVED'
