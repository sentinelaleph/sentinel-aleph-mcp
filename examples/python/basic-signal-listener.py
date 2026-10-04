import asyncio
import json
import os
from urllib.parse import urlparse

import websockets

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def checked_url(url: str) -> str:
    """The key travels in a header: refuse a plain ws:// URL except locally."""
    parsed = urlparse(url)
    if parsed.scheme == "wss" or (parsed.scheme == "ws" and parsed.hostname in LOCAL_HOSTS):
        return url
    raise RuntimeError(f"refusing {url}: use wss:// so the API key is not sent in clear text")


async def listen(ws_url: str, key: str) -> None:
    async with websockets.connect(ws_url, additional_headers={"Authorization": f"Bearer {key}"}) as websocket:
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

    delay = 1
    while True:
        try:
            await listen(ws_url, key)
            delay = 1
        except websockets.InvalidStatus as error:
            # 401 / 403: a wrong or revoked key will not fix itself.
            raise RuntimeError(f"connection refused: HTTP {error.response.status_code}") from error
        except (OSError, websockets.ConnectionClosed) as error:
            print(f"disconnected ({error}); reconnecting in {delay}s")
        await asyncio.sleep(delay)
        delay = min(delay * 2, 60)


if __name__ == "__main__":
    asyncio.run(main())
