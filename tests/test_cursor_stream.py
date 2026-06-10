import asyncio
import json
import time

from websockets.asyncio.client import connect

SERVER_URL = "ws://localhost:8765"


def make_cursor_command(x: float, y: float) -> dict:
    return {
        "type": "command",
        "command": "CURSOR_MOVE",
        "gesture": "INDEX_FINGER",
        "x": x,
        "y": y,
        "text": None,
        "timestamp": int(time.time() * 1000),
    }


async def send_cursor_stream():
    async with connect(SERVER_URL) as websocket:
        print("Sending cursor stream...")

        # จำลองนิ้วเลื่อนจากซ้ายไปขวา
        for i in range(20):
            x = 0.1 + (i * 0.04)
            y = 0.5

            command = make_cursor_command(x, y)

            await websocket.send(json.dumps(command, ensure_ascii=False))
            response = await websocket.recv()

            print(response)

            await asyncio.sleep(0.05)

        print("Cursor stream finished")


if __name__ == "__main__":
    asyncio.run(send_cursor_stream())