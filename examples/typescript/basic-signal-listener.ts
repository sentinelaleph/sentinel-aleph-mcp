import WebSocket from "ws";

const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]"]);

// A wrong or revoked key will not fix itself; every other refusal is retried.
const FATAL_STATUSES = new Set([401, 403]);
const MAX_DELAY_MS = 60_000;

/** The key travels in a header: refuse a plain ws:// URL except locally. */
function checkedUrl(raw: string): string {
  const url = new URL(raw);
  if (url.protocol === "wss:" || (url.protocol === "ws:" && LOCAL_HOSTS.has(url.hostname))) {
    return raw;
  }
  throw new Error(`refusing ${raw}: use wss:// so the API key is not sent in clear text`);
}

/** Retry-After as milliseconds: seconds or an HTTP date; 0 when absent or unreadable. */
function retryAfterMs(header: string | string[] | undefined): number {
  const value = (Array.isArray(header) ? header[0] : header)?.trim();
  if (!value) {
    return 0;
  }
  if (/^\d+$/.test(value)) {
    return Number(value) * 1000;
  }
  const when = Date.parse(value);
  return Number.isNaN(when) ? 0 : Math.max(0, when - Date.now());
}

const wsUrl = checkedUrl(process.env.SENTINEL_MCP_WS_URL ?? "wss://ribqa.com/api/v1/mcp/ws");
const key = process.env.SENTINEL_MCP_KEY;

if (!key) {
  throw new Error("SENTINEL_MCP_KEY is required");
}

let delayMs = 1_000;

function connect(): void {
  let atLeastMs = 0;
  let refused = false;
  const ws = new WebSocket(wsUrl, { headers: { Authorization: `Bearer ${key}` } });

  ws.on("open", () => {
    delayMs = 1_000;
    console.log("connected");
    ws.send(JSON.stringify({
      id: "subscribe-1",
      type: "subscribe",
      symbol: "*"
    }));
  });

  ws.on("message", (raw) => {
    let message: unknown;
    try {
      message = JSON.parse(raw.toString());
    } catch {
      console.warn("skipped a frame that is not JSON");
      return;
    }
    console.log(JSON.stringify(message, null, 2));
  });

  ws.on("unexpected-response", (_req, res) => {
    const status = res.statusCode ?? 0;
    res.resume();
    if (FATAL_STATUSES.has(status)) {
      console.error(`connection refused: HTTP ${status}; check SENTINEL_MCP_KEY`);
      process.exit(1);
    }
    // 429, 5xx and Cloudflare's 52x: wait at least as long as the server asks.
    atLeastMs = retryAfterMs(res.headers["retry-after"]);
    refused = true;
    console.warn(`handshake refused: HTTP ${status}`);
    ws.terminate(); // ends the attempt; "close" schedules the retry
  });

  ws.on("error", (error) => {
    if (!refused) {
      console.error("MCP websocket error", error.message);
    }
  });

  ws.on("close", () => {
    const waitMs = Math.max(delayMs, atLeastMs);
    console.log(`disconnected; reconnecting in ${waitMs / 1000}s`);
    setTimeout(connect, waitMs);
    delayMs = Math.min(delayMs * 2, MAX_DELAY_MS);
  });
}

connect();
