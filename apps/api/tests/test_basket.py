from app.database import SessionLocal
from app.demo_orders import seed_demo_basket


def put(client, headers, items):
    return client.put('/api/me/basket', headers=headers, json={'items': items})


def test_basket_starts_empty_and_round_trips(client, consumer):
    assert client.get('/api/me/basket', headers=consumer).json() == {'items': []}
    data = put(client, consumer, [{'product_id': 'p1', 'quantity': 2}, {'product_id': 'p5', 'quantity': 1}]).json()
    assert [(i['product_id'], i['quantity']) for i in data['items']] == [('p1', 2), ('p5', 1)]
    assert data['items'][0]['merchant_id'] and data['items'][0]['location_id']
    assert client.get('/api/me/basket', headers=consumer).json() == data


def test_put_replaces_and_can_empty(client, consumer):
    put(client, consumer, [{'product_id': 'p1', 'quantity': 2}])
    put(client, consumer, [{'product_id': 'p5', 'quantity': 1}])
    assert [i['product_id'] for i in client.get('/api/me/basket', headers=consumer).json()['items']] == ['p5']
    assert put(client, consumer, []).json() == {'items': []}


def test_unknown_products_duplicates_and_caps_are_handled(client, consumer):
    items = [{'product_id': 'nope', 'quantity': 1}, {'product_id': 'p1', 'quantity': 99}, {'product_id': 'p1', 'quantity': 1}]
    data = put(client, consumer, items).json()['items']
    assert [(i['product_id'], i['quantity']) for i in data] == [('p1', 10)]
    many = [{'product_id': pid, 'quantity': 10} for pid in ('p1', 'p2', 'p3', 'p4', 'p5')]
    assert sum(i['quantity'] for i in put(client, consumer, many).json()['items']) <= 30
    assert put(client, consumer, [{'product_id': 'p1', 'quantity': 0}]).status_code == 422


def test_each_user_has_their_own_basket(client, consumer, merchant):
    put(client, consumer, [{'product_id': 'p1', 'quantity': 1}])
    assert client.get('/api/me/basket', headers=merchant).json() == {'items': []}


def test_demo_seed_is_one_time(client, monkeypatch):
    monkeypatch.delenv('PAYFOUND_TESTING', raising=False)
    monkeypatch.setenv('DEMO_MODE', 'true')
    with SessionLocal() as db:
        assert seed_demo_basket(db) >= 1
        db.commit()
        # the shopper empties it; reseeding must not bring it back
        from app.basket import BasketLine
        db.query(BasketLine).delete()
        db.commit()
        assert seed_demo_basket(db) == 0
        assert db.query(BasketLine).count() == 0
