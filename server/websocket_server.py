import asyncio
import json
import time

from websockets.asyncio.server import serve

from automation.command_router import handle_command
from utils.logger import write_event_log
from utils.network import get_local_ip


def create_ack(result: dict, start_time: float) -> dict:
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "type": "ack",
        "status": result.get("status"),
        "command": result.get("command"),
        "message": result.get("message"),
        "latency_ms": latency_ms,
    }


def create_error_ack(
    message: str,
    command: str | None = None,
    start_time: float | None = None,
) -> dict:
    latency_ms = None

    if start_time is not None:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "type": "ack",
        "status": "error",
        "command": command,
        "message": message,
        "latency_ms": latency_ms,
    }


async def websocket_handler(websocket):
    print("Client connected")

    async for message in websocket:
        start_time = time.perf_counter()
        data = {}

        try:
            data = json.loads(message)
            if not isinstance(data, dict):
                ack = create_error_ack(
                    message="Invalid message format: JSON must be an object",
                    start_time=start_time,
                )
            else:
                result = await handle_command(data)
                ack = create_ack(result, start_time)

        except json.JSONDecodeError:
            ack = create_error_ack(
                message="Invalid JSON",
                start_time=start_time,
            )

        except Exception as error:
            command = data.get("command") if isinstance(data, dict) else None
            ack = create_error_ack(
                message=str(error),
                command=command,
                start_time=start_time,
            )

        write_event_log(data, ack)
        await websocket.send(json.dumps(ack, ensure_ascii=False))


async def start_server(host: str, port: int):
    local_ip = get_local_ip()

    print(f"WebSocket Server running at ws://{host}:{port}")
    print(f"Use this URL on mobile: ws://{local_ip}:{port}")

    async with serve(websocket_handler, host, port):
        await asyncio.Future()