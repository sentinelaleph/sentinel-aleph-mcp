from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import websockets
from websockets.exceptions import ConnectionClosed, InvalidHandshake, InvalidMessage, InvalidStatus

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}

# A wrong or revoked key will not fix itself; every other refusal is retried.
FATAL_STATUSES = {401, 403}
MAX_DELAY = 60


def checked_url(url: str) -> str:
    """The key travels in a header: refuse a plain ws:// URL except locally."""
    parsed = urlparse(url)
    if parsed.scheme == "wss" or (parsed.scheme == "ws" and parsed.hostname in LOCAL_HOSTS):
        return url
    raise RuntimeError(f"refusing {url}: use wss:// so the API key is not sent in clear text")


def retry_after_seconds(value: str | None) -> float:
    """Retry-After as seconds: a number of seconds or an HTTP date; 0 when absent or unreadable."""
    if not value:
        return 0
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return 0
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


class Backoff:
    """Exponential delay, 1 s doubling to MAX_DELAY, reset after a successful open."""

    def __init__(self) -> None:
        self.delay = 1

    def reset(self) -> None:
        self.delay = 1

    def next(self, at_least: float = 0) -> float:
        wait = max(self.delay, at_least)
        self.delay = min(self.delay * 2, MAX_DELAY)
        return wait


async def listen(ws_url: str, key: str, backoff: Backoff) -> None:
    async with websockets.connect(ws_url, additional_headers={"Authorization": f"Bearer {key}"}) as websocket:
        backoff.reset()
        print("connected")
        await websocket.send(json.dumps({
            "id": "subscribe-1",
            "type": "subscribe",
            "symbol": "*",
        }))

        async for raw in websocket:
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                print("skipped a frame that is not JSON")
                continue
            print(json.dumps(message, indent=2))


async def main() -> None:
    ws_url = checked_url(os.getenv("SENTINEL_MCP_WS_URL", "wss://ribqa.com/api/v1/mcp/ws"))
    key = os.getenv("SENTINEL_MCP_KEY")

    if not key:
        raise RuntimeError("SENTINEL_MCP_KEY is required")

    backoff = Backoff()
    while True:
        at_least = 0.0
        try:
            await listen(ws_url, key, backoff)
            reason = "connection closed"
        except InvalidStatus as error:
            status = error.response.status_code
            if status in FATAL_STATUSES:
                raise SystemExit(f"connection refused: HTTP {status}; check SENTINEL_MCP_KEY") from error
            # 429, 5xx and Cloudflare's 52x: wait at least as long as the server asks.
            at_least = retry_after_seconds(error.response.headers.get("Retry-After"))
            reason = f"handshake refused: HTTP {status}"
        except (InvalidHandshake, InvalidMessage) as error:
            reason = f"handshake failed ({error})"
        except (OSError, ConnectionClosed) as error:
            reason = f"disconnected ({error})"
        wait = backoff.next(at_least)
        print(f"{reason}; reconnecting in {wait:g}s")
        await asyncio.sleep(wait)


if __name__ == "__main__":
    asyncio.run(main())
