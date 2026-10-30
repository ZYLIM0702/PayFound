import test from 'node:test';
import assert from 'node:assert/strict';
import { safeNext, invitationSessionFromHash } from './navigation.ts';

test('post-auth navigation stays on the application origin after browser URL normalization', () => {
  for (const input of ['//untrusted.example', '/\n/untrusted.example', '/\t/untrusted.example', '/\r/untrusted.example', '/\\untrusted.example', 'https://untrusted.example', 'javascript:alert(1)', null]) {
    const resolved = new URL(safeNext(input), 'https://payfound.example');
    assert.equal(resolved.origin, 'https://payfound.example');
  }
  assert.equal(safeNext('/orders?status=ready'), '/orders?status=ready');
});

test('only a complete invitation fragment enters the explicit invite-session path', () => {
  assert.deepEqual(invitationSessionFromHash('#type=invite&access_token=test-access&refresh_token=test-refresh'), {
    access_token: 'test-access', refresh_token: 'test-refresh',
  });
  assert.equal(invitationSessionFromHash('#type=invite&access_token=incomplete'), null);
  assert.equal(invitationSessionFromHash('#type=recovery&access_token=test-access&refresh_token=test-refresh'), null);
});
