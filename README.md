# Sentinel Aleph MCP Agent Kit

Sentinel Aleph publishes crypto trading signals and the public ledger that
scores them. Agents reach them through an MCP server. A signal is a decision
input, not an instruction: the server places no orders, simulated or live.

## Endpoint

- MCP remote (Streamable HTTP, JSON-RPC 2.0, protocol `2025-06-18`):
  `POST https://ribqa.com/api/v1/mcp`
- Auth: `Authorization: Bearer <API key>` on `tools/call`. `initialize`,
  `ping` and `tools/list` need no key. Keys are created on
  https://ribqa.com/account and shown once.
- Tool list, schemas, limits and error codes: https://ribqa.com/mcp

Claude Code:

```bash
claude mcp add --transport http sentinel-aleph https://ribqa.com/api/v1/mcp \
  --header "Authorization: Bearer $SENTINEL_MCP_KEY"
```

## Events channel (push)

MCP over HTTP has no push. New signals, BTC regime vetoes and BTC chart read
changes arrive on a separate WebSocket, `wss://ribqa.com/api/v1/mcp/ws`, with
the same `Authorization: Bearer` header. Send
`{"id":"1","type":"subscribe","symbol":"*"}` (or a pair such as `BTCUSDT`);
events arrive as `{"id":"event","result":{"type":"signal"|"signal.veto"|"market.btc_chart_read","symbol":..,"data":..}}`.
`examples/` holds a Python and a TypeScript listener.

## Boundary

Sentinel Aleph does not provide financial advice, managed trading or assured
outcomes. Agents and their operators own every execution and risk decision.
`docs/` describes agent-side validation and risk practice.

## License

MIT, see [LICENSE](LICENSE). The license covers this kit (docs and examples); the Sentinel Aleph service and its data are governed by the terms at https://ribqa.com.
