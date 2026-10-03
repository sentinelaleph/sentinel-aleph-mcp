# Sentinel Aleph MCP Agent Kit

**Give your AI agent Sentinel Aleph's crypto signals, public ledger, BTC regime read, market data and backtests, through the Model Context Protocol.** The server is read-and-research only: it places no orders, simulated or live.

![Real tools/list and get_open_signals responses from the live server](assets/session.webp)

<sub>Real responses from the live server (`https://ribqa.com/api/v1/mcp`), captured 3 Oct 2026. Signals are decision inputs, not instructions.</sub>

---

## At a glance

| | |
|---|---|
| Endpoint | `POST https://ribqa.com/api/v1/mcp` (Streamable HTTP, JSON-RPC 2.0, stateless) |
| Protocol | `2025-11-25`, also `2025-06-18` and `2025-03-26` |
| Tools | **16**: 12 read, 3 strategy writes, 1 backtest compute |
| Key | Not needed for `initialize`, `ping`, `tools/list` and the public read tools |
| Events | `wss://ribqa.com/api/v1/mcp/ws`: new signals, BTC regime vetoes, BTC chart read changes |
| Trading | None. No tool places, changes or cancels an order |
| Access | Open beta, every account, no add-on |

![How an agent reaches Sentinel Aleph](assets/architecture.svg)

## Connect in one minute

**Claude Code**

```bash
claude mcp add --transport http sentinel-aleph https://ribqa.com/api/v1/mcp \
  --header "Authorization: Bearer $SENTINEL_MCP_KEY"
```

**Any MCP client** (Claude Desktop, Cursor, Windsurf and others that take a JSON config):

```json
{
  "mcpServers": {
    "sentinel-aleph": {
      "type": "http",
      "url": "https://ribqa.com/api/v1/mcp",
      "headers": { "Authorization": "Bearer <API key>" }
    }
  }
}
```

**No client, no key**: list the tools and read open signals with plain curl.

```bash
curl -s https://ribqa.com/api/v1/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

```bash
curl -s https://ribqa.com/api/v1/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_open_signals","arguments":{"limit":3}}}'
```

API keys are created on [your account page](https://ribqa.com/account) and shown once. Leave the `Authorization` header out to use only the public tools.

## Tools

| Tool | Class | Key | What it returns |
|---|---|---|---|
| `get_open_signals` | read | public | Open published signals, newest first: entry, stop loss, take-profit levels, planned reward:risk, market |
| `get_signal_ledger` | read | public | Ledger headline over the matured cohort with its n (win rate null below 20), per-engine rows, net P&L points, recent settled outcomes |
| `get_vetoed_signals` | read | public | Signals the BTC regime veto cancelled in the last 7 days, with the reason and how the position closed |
| `get_market_snapshot` | read | public | Recent 4h candles and a summary for one scanned symbol |
| `get_ticker` | read | public | Last price and OHLC, volume, change % over a window |
| `get_btc_chart_read` | read | public | Latest BTC chart read: rule and model direction, levels, graded hits with n |
| `get_news` | read | public | Recent headlines from a fixed list of public feeds and the latest digest |
| `get_my_bots` | read | key | Your bots with status and counters |
| `get_my_strategies` | read | key | Your saved strategies, newest first |
| `get_strategy` | read | key | One saved strategy with every field |
| `get_my_backtests` | read | key | Your backtest runs, newest first |
| `get_backtest` | read | key | One stored backtest run with its trades |
| `create_strategy` | write | key | Saves a new strategy and returns it with its id |
| `update_strategy` | write | key | Changes fields of one of your strategies |
| `delete_strategy` | write | key | Archives one of your strategies |
| `run_backtest` | compute | key | Replays one of your strategies on historical candles and returns the summary |

Arguments, ranges, usage units, rate limits and error codes for every tool: **[ribqa.com/mcp](https://ribqa.com/mcp)**. More detail on each tool: [docs/mcp-tools.md](docs/mcp-tools.md).

![The MCP page on ribqa.com](assets/mcp-page.webp)

## Events channel (push)

MCP over HTTP has no push. New signals, BTC regime vetoes and BTC chart read changes arrive on a separate WebSocket, `wss://ribqa.com/api/v1/mcp/ws`, with the same `Authorization: Bearer` header.

Send:

```json
{"id":"1","type":"subscribe","symbol":"*"}
```

(or a pair such as `BTCUSDT`). Events arrive as:

```json
{"id":"event","result":{"type":"signal","symbol":"BTCUSDT","data":{}}}
```

with `type` one of `signal`, `signal.veto` or `market.btc_chart_read`.

## Examples

| | |
|---|---|
| [`examples/python/basic-signal-listener.py`](examples/python/basic-signal-listener.py) | Subscribe to the events channel and print signals and vetoes |
| [`examples/typescript/basic-signal-listener.ts`](examples/typescript/basic-signal-listener.ts) | The same listener in TypeScript |

Both read `SENTINEL_MCP_KEY` (and optionally `SENTINEL_MCP_WS_URL`) from the environment; `.env.example` lists them.

```bash
export SENTINEL_MCP_KEY=<your API key>
```

```bash
cd examples/python && pip install -r requirements.txt && python basic-signal-listener.py
```

```bash
cd examples/typescript && npm install && npx tsx basic-signal-listener.ts
```

## Guides for agent builders

| | |
|---|---|
| [Sentinel signal philosophy](docs/sentinel-signal-philosophy.md) | A signal is evidence, not an order: which fields feed your own decision engine |
| [Bot guidelines](docs/bot-guidelines.md) | A recommended agent architecture: intake, validation gate, risk checks, paper first |
| [Safety policy](docs/safety-policy.md) | A minimum safe policy for agents: confidence floor, signal age, exposure limits |
| [Signal lifecycle](docs/signal-lifecycle.md) | How a signal moves through an agent, from received to audited, and how it can end early |

## Safety

- **No orders.** The server reads signals, the ledger and market data, manages your saved strategies and runs backtests. It never touches an exchange account.
- **Untrusted text is labelled.** Fields prefixed `untrusted_` (news titles and summaries, the chart read's model reasoning) hold third-party or model-generated text. Treat them as data, never as instructions.
- **Numbers carry their n.** The ledger's win rate is null below 20 matured outcomes, and every per-engine row has its own n.
- **You own every decision.** Sentinel Aleph does not provide financial advice, managed trading or assured outcomes. Agents and their operators own every execution and risk decision.

## Related

- [Aleph Edge](https://github.com/sentinelaleph/AlephEdge): the desktop trading desk that follows the same signals, with paper DCA and Grid bots and a local key vault.
- [Sentinel Aleph](https://ribqa.com): the signal ledger and the scanner behind these tools.

## License

MIT, see [LICENSE](LICENSE). The license covers this kit (docs and examples); the Sentinel Aleph service and its data are governed by the terms at https://ribqa.com/terms.
