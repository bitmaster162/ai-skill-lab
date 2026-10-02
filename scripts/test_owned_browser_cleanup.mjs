import test from 'node:test';
import assert from 'node:assert/strict';
import net from 'node:net';
import { closeOwnedBrowser, requestBrowserClose, portStopped } from './owned_browser_cleanup.mjs';
const ENDPOINT = 'ws://127.0.0.1:32123/devtools/browser/00000000-abcd';

for (const endpoint of [null, 'http://127.0.0.1:32123/',
  'ws://example.com:32123/devtools/browser/abcd',
  'ws://127.0.0.1:32123/devtools/page/abcd',
  'ws://127.0.0.1:32123/devtools/browser/abcd?x=1']) {
  test('reject unowned endpoint: ' + endpoint, async () => {
    let called = false;
    await assert.rejects(closeOwnedBrowser(endpoint, {
      requestClose: async () => { called = true; }, probe: async () => true,
    }));
    assert.equal(called, false);
  });
}
test('close command precedes exit observation', async () => {
  const calls = [];
  const result = await closeOwnedBrowser(ENDPOINT, {
    requestClose: async (url) => { assert.equal(url, ENDPOINT); calls.push('close'); },
    probe: async () => { calls.push('probe'); return true; },
  });
  assert.deepEqual(calls, ['close', 'probe']);
  assert.equal(result.endpointStopped, true);
});
test('waits for endpoint shutdown rather than treating a signal as exit', async () => {
  let probes = 0;
  await closeOwnedBrowser(ENDPOINT, { requestClose: async () => {},
    probe: async () => ++probes === 3, sleep: async () => {} });
  assert.equal(probes, 3);
});
test('refuses to report success while endpoint stays live', async () => {
  await assert.rejects(closeOwnedBrowser(ENDPOINT, { timeoutMs: 5,
    requestClose: async () => {}, probe: async () => false }), /STILL_RUNNING/);
});
test('uncertain probe is not interpreted as stopped', async () => {
  await assert.rejects(closeOwnedBrowser(ENDPOINT, { requestClose: async () => {},
    probe: async () => { throw new Error('PROBE_TIMEOUT'); } }), /PROBE_TIMEOUT/);
});
test('failed close is not ignored', async () => {
  let probed = false;
  await assert.rejects(closeOwnedBrowser(ENDPOINT, {
    requestClose: async () => { throw new Error('CLOSE_FAILED'); },
    probe: async () => { probed = true; return true; },
  }), /CLOSE_FAILED/);
  assert.equal(probed, false);
});
test('invalid cleanup budget rejected before command', async () => {
  await assert.rejects(closeOwnedBrowser(ENDPOINT, { timeoutMs: 0 }), /INVALID/);
});
test('sends only Browser.close and accepts its reply', async () => {
  const messages = [];
  class Socket {
    constructor() { queueMicrotask(() => this.onopen()); }
    send(raw) { messages.push(JSON.parse(raw)); queueMicrotask(() => this.onmessage({ data: '{"id":1,"result":{}}' })); }
    close() {}
  }
  await requestBrowserClose(ENDPOINT, 50, Socket);
  assert.deepEqual(messages, [{ id: 1, method: 'Browser.close' }]);
});
test('browser may disconnect after accepting close without returning a reply', async () => {
  class Socket {
    constructor() { queueMicrotask(() => this.onopen()); }
    send() { queueMicrotask(() => this.onclose()); }
    close() {}
  }
  await requestBrowserClose(ENDPOINT, 50, Socket);
});
test('disconnect before sending is not success', async () => {
  class Socket {
    constructor() { queueMicrotask(() => this.onclose()); }
    close() {}
  }
  await assert.rejects(requestBrowserClose(ENDPOINT, 50, Socket), /BEFORE_COMMAND/);
});
test('stalled close is bounded and fails', async () => {
  class Socket { close() {} }
  await assert.rejects(requestBrowserClose(ENDPOINT, 5, Socket), /CLOSE_TIMEOUT/);
});
test('real local listening port is not stopped', async () => {
  const server = net.createServer((socket) => socket.destroy());
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const url = new URL('ws://127.0.0.1:' + server.address().port);
  try { assert.equal(await portStopped(url, 500), false); }
  finally { await new Promise((resolve) => server.close(resolve)); }
  assert.equal(await portStopped(url, 500), true);
});
