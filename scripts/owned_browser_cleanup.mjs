import net from 'node:net';

// A private CDP browser endpoint identifies this test's browser, not all Chrome.
function validateEndpoint(value) {
  const url = new URL(value);
  if (url.protocol !== 'ws:' || url.hostname !== '127.0.0.1' || !url.port
      || url.username || url.password || url.search || url.hash
      || !/^\/devtools\/browser\/[a-f0-9-]+$/i.test(url.pathname)) {
    throw new Error('OWNED_BROWSER_ENDPOINT_REQUIRED');
  }
  return url;
}

export function requestBrowserClose(url, timeoutMs, Socket = WebSocket) {
  return new Promise((resolve, reject) => {
    let sent = false;
    let finished = false;
    const socket = new Socket(url);
    const finish = (error) => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      try { socket.close(); } catch {}
      if (error) reject(error); else resolve();
    };
    const timer = setTimeout(() => finish(new Error('BROWSER_CLOSE_TIMEOUT')), timeoutMs);
    socket.onopen = () => {
      sent = true;
      try { socket.send(JSON.stringify({ id: 1, method: 'Browser.close' })); }
      catch (error) { finish(error); }
    };
    socket.onmessage = ({ data }) => {
      try {
        const result = JSON.parse(String(data));
        if (result.id === 1) finish(result.error ? new Error(JSON.stringify(result.error)) : null);
      } catch (error) { finish(error); }
    };
    socket.onclose = () => finish(sent ? null : new Error('BROWSER_CLOSED_BEFORE_COMMAND'));
    socket.onerror = () => finish(new Error('BROWSER_CLOSE_CONNECTION_FAILED'));
  });
}

export function portStopped(url, timeoutMs) {
  return new Promise((resolve, reject) => {
    const socket = net.createConnection({ host: url.hostname, port: Number(url.port) });
    const finish = (error, stopped) => {
      socket.destroy();
      if (error) reject(error); else resolve(stopped);
    };
    socket.once('connect', () => finish(null, false));
    socket.once('error', (error) => {
      if (error.code === 'ECONNREFUSED') finish(null, true);
      else finish(error);
    });
    socket.setTimeout(timeoutMs, () => finish(new Error('BROWSER_EXIT_PROBE_TIMEOUT')));
  });
}

export async function closeOwnedBrowser(endpoint, {
  timeoutMs = 5000, requestClose = requestBrowserClose, probe = portStopped,
  sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
} = {}) {
  const url = validateEndpoint(endpoint);
  if (!Number.isInteger(timeoutMs) || timeoutMs <= 0) throw new Error('INVALID_CLEANUP_TIMEOUT');
  await requestClose(url.href, timeoutMs);
  const deadline = Date.now() + timeoutMs;
  do {
    if (await probe(url, Math.min(500, Math.max(1, deadline - Date.now())))) {
      return { command: 'Browser.close', endpointStopped: true };
    }
    await sleep(50);
  } while (Date.now() < deadline);
  throw new Error('BROWSER_ENDPOINT_STILL_RUNNING');
}
