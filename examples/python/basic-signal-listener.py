import asyncio
import json
import os
import websockets


async def main() -> None:
    ws_url = os.getenv("SENTINEL_MCP_WS_URL", "wss://ribqa.com/api/v1/mcp/ws")
    key = os.getenv("SENTINEL_MCP_KEY")

    if not key:
        raise RuntimeError("SENTINEL_MCP_KEY is required")

    async with websockets.connect(ws_url, additional_headers={"Authorization": f"Bearer {key}"}) as websocket:
        await websocket.send(json.dumps({
            "id": "subscribe-1",
            "type": "subscribe",
            "symbol": "*",
        }))

        async for raw in websocket:
            message = json.loads(raw)
            print(json.dumps(message, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
