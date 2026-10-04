import WebSocket from "ws";

const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]"]);

/** The key travels in a header: refuse a plain ws:// URL except locally. */
function checkedUrl(raw: string): string {
  const url = new URL(raw);
  if (url.protocol === "wss:" || (url.protocol === "ws:" && LOCAL_HOSTS.has(url.hostname))) {
    return raw;
  }
  throw new Error(`refusing ${raw}: use wss:// so the API key is not sent in clear text`);
}

const wsUrl = checkedUrl(process.env.SENTINEL_MCP_WS_URL ?? "wss://ribqa.com/api/v1/mcp/ws");
const key = process.env.SENTINEL_MCP_KEY;

if (!key) {
  throw new Error("SENTINEL_MCP_KEY is required");
}

let delayMs = 1_000;

function connect(): void {
  const ws = new WebSocket(wsUrl, { headers: { Authorization: `Bearer ${key}` } });

  ws.on("open", () => {
    delayMs = 1_000;
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
    // 401 / 403: a wrong or revoked key will not fix itself.
    console.error(`connection refused: HTTP ${res.statusCode}`);
    process.exit(1);
  });

  ws.on("error", (error) => {
    console.error("MCP websocket error", error.message);
  });

  ws.on("close", () => {
    console.log(`disconnected; reconnecting in ${delayMs / 1000}s`);
    setTimeout(connect, delayMs);
    delayMs = Math.min(delayMs * 2, 60_000);
  });
}

connect();
