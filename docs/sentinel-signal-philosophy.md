# Sentinel Signal Philosophy

A Sentinel signal is evidence. It is not an order.

Each consumer must treat `direction`, `confidence`, `entry`, `take_profit`, `stop_loss`, `expires_at`, and evidence fields as inputs to a separate local decision engine.

Required local checks:

- reject expired signals
- reject stale signals
- reject duplicate signal ids
- reject unsupported symbols or venues
- reject malformed TP/SL geometry
- reject signals below local confidence policy
- reject signals while account mode is not paper or explicitly approved live

The safest integration is paper-first. Live execution must be guarded by local risk controls, operator approval, and future Sentinel live-execution policy.

Sentinel market data should be consumed through Sentinel MCP/API outputs. Do not bypass Sentinel policy by calling exchanges directly for data that Sentinel already provides.
