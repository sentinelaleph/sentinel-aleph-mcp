# Signal Lifecycle

`received` -> `validated` -> `risk_checked` -> `paper_submitted` -> `paper_closed` -> `audited`

Signals may also end as:

- `rejected_stale`
- `rejected_expired`
- `rejected_confidence`
- `rejected_duplicate`
- `rejected_symbol`
- `rejected_route`
- `rejected_malformed`
- `rejected_risk`
- `rejected_mode`

## State Notes

- `received`: raw payload was observed and stored with timestamp and source.
- `validated`: payload passed age, expiry, confidence, duplicate, symbol, and TP/SL checks.
- `risk_checked`: local account and portfolio rules passed.
- `paper_submitted`: a paper intent was emitted with an idempotency key.
- `paper_closed`: simulated lifecycle has a terminal outcome.
- `audited`: all inputs, decisions, and outcomes are persisted.

Every terminal rejection should include a reason code and enough context for later review.
