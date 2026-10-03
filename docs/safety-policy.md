# Safety Policy

Minimum safe policy:

- `MIN_CONFIDENCE >= 0.80`
- `MAX_SIGNAL_AGE_SECONDS <= 1800`
- paper mode before live mode
- daily loss cap
- max open positions
- symbol cooldown
- idempotency key per signal action

## Required Rejections

- reject expired signals
- reject stale signals
- reject duplicate signal ids
- reject malformed entries, take-profit levels, or stop-loss values
- reject unsupported symbols, venues, or routes
- reject signals below local confidence policy
- reject actions that would exceed local risk limits

## Execution Boundary

Sentinel signals are not execution commands. This kit supports read-only listeners and paper-first bot patterns. Any live trading path requires explicit future Sentinel policy support, local operator approval, and separate execution controls owned by the agent operator.
