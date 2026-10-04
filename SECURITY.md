# Security

## Reporting a vulnerability

Email **support@ribqa.com** with the details: what you found, how to reproduce it, and what it affects. Please do not open a public issue for a vulnerability.

The same contact is published at [ribqa.com/.well-known/security.txt](https://ribqa.com/.well-known/security.txt).

## Scope

- This repository: the docs and the example clients.
- The MCP server at `https://ribqa.com/api/v1/mcp` and its events channel at `wss://ribqa.com/api/v1/mcp/ws`.

## API keys

- Keys are created on the [account page](https://ribqa.com/account) and shown once. Revoke a key there if it leaks.
- The examples read the key from the `SENTINEL_MCP_KEY` environment variable. Never commit a key; `.env` is in `.gitignore`.
- Send keys only over TLS (`https://`, `wss://`). The examples refuse a plain `ws://` URL except for `localhost`.
