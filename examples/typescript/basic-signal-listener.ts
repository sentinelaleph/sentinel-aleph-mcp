import WebSocket from "ws";

const wsUrl = process.env.SENTINEL_MCP_WS_URL ?? "wss://ribqa.com/api/v1/mcp/ws";
const key = process.env.SENTINEL_MCP_KEY;

if (!key) {
  throw new Error("SENTINEL_MCP_KEY is required");
}

const ws = new WebSocket(wsUrl, { headers: { Authorization: `Bearer ${key}` } });

ws.on("open", () => {
  ws.send(JSON.stringify({
    id: "subscribe-1",
    type: "subscribe",
    symbol: "*"
  }));
});

ws.on("message", (raw) => {
  const message: unknown = JSON.parse(raw.toString());
  console.log(JSON.stringify(message, null, 2));
});

ws.on("error", (error) => {
  console.error("MCP websocket error", error);
});
