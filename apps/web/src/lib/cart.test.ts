import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCart, groupByStore, storeCount, readPending } from './basket.ts';

test('parseCart accepts the old shape and the new one with store ids', () => {
  const out = parseCart(JSON.stringify([{ product_id: 'a', quantity: 2 }, { product_id: 'b', quantity: 99, merchant_id: 'm1', location_id: 'l1' }]));
  assert.deepEqual(out, [{ product_id: 'a', quantity: 2 }, { product_id: 'b', quantity: 10, merchant_id: 'm1', location_id: 'l1' }]);
});

test('parseCart drops bad lines, duplicates and caps total units at 30', () => {
  assert.deepEqual(parseCart('nope'), []);
  assert.deepEqual(parseCart(null), []);
  const lines = [{ product_id: 'a', quantity: 0 }, { product_id: 'a', quantity: 1.5 }, { product_id: 7, quantity: 1 }, { product_id: 'a', quantity: 1 }, { product_id: 'a', quantity: 2 }];
  assert.deepEqual(parseCart(JSON.stringify(lines)), [{ product_id: 'a', quantity: 1 }]);
  const many = Array.from({ length: 5 }, (_, i) => ({ product_id: `p${i}`, quantity: 10 }));
  assert.equal(parseCart(JSON.stringify(many)).length, 3);
});

test('groupByStore groups by store then branch and keeps order', () => {
  const l = (id: string, m: string, loc: string, currency = 'USD') => ({ id, product: { merchant_id: m, location_id: loc, currency } });
  const groups = groupByStore([l('1', 'A', 'x'), l('2', 'B', 'y', 'EUR'), l('3', 'A', 'x'), l('4', 'A', 'z'), { id: '5', product: undefined }]);
  assert.deepEqual(groups.map(g => [g.key, g.lines.length, g.currency]), [['A:x', 2, 'USD'], ['B:y', 1, 'EUR'], ['A:z', 1, 'USD'], ['unknown', 1, '']]);
});

test('storeCount and readPending', () => {
  assert.equal(storeCount([{ merchant_id: 'a' }, { merchant_id: 'a' }, {}, { merchant_id: 'b' }]), 2);
  assert.deepEqual(readPending('[{"id":"1","store":"S"},{"id":2}]'), [{ id: '1', store: 'S' }]);
  assert.deepEqual(readPending('x'), []);
});
