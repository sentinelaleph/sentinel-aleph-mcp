# Bot Guidelines

## Recommended Architecture

1. Signal Intake
2. Validation Gate
3. Risk Gate
4. Paper Execution Adapter
5. Audit Ledger

## Do

- store every received signal id
- record the received timestamp and raw payload hash
- create idempotency keys before simulated execution
- enforce max signal age
- enforce confidence floors
- enforce cooldowns
- start in paper mode
- keep an audit record for accepted and rejected signals

## Do Not

- do not average down automatically
- do not trade expired signals
- do not trade the same signal twice
- do not convert a signal directly into a market order
- do not bypass Sentinel key, tier, add-on, or usage policy
- do not present live execution as enabled by this public kit

## Minimal Decision Flow

1. Receive a signal from `signal.subscribe` or `signal.history`.
2. Reject stale, expired, malformed, duplicate, unsupported, or low-confidence payloads.
3. Apply local risk policy for open positions, daily loss, cooldown, route, and mode.
4. Emit a paper intent with an idempotency key.
5. Persist the decision and outcome in an audit ledger.
