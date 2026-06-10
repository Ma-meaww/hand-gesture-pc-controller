import asyncio
import json
import time
import socket

from websockets.asyncio.server import serve

from actions import execute_pc_action
from logger import write_event_log

HOST = "0.0.0.0"
PORT = 8765


def get_status_from_message(message: str) -> str:
    error_keywords = [
        "not open",
        "not found",
        "missing",
        "unknown command",
        "no text",
        "no keyword",
        "invalid",
    ]

    message_lower = message.lower()

    for keyword in error_keywords:
        if keyword in message_lower:
            return "error"

    return "success"

async def handle_command(data: dict) -> dict:
    command = data.get("command")

    if not command:
        return {
            "status": "error",
            "command": None,
            "message": "Missing command",
        }

    print("\n--- Received Command ---")
    print(f"command: {command}")
    print(f"gesture: {data.get('gesture')}")
    print(f"text: {data.get('text')}")
    print(f"x: {data.get('x')}, y: {data.get('y')}")

    message = execute_pc_action(command, data)
    status = get_status_from_message(message)

    print(f"action: {message}")

    return {
        "status": status,
        "command": command,
        "message": message,
    }


def create_ack(result: dict, start_time: float) -> dict:
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "type": "ack",
        "status": result.get("status"),
        "command": result.get("command"),
        "message": result.get("message"),
        "latency_ms": latency_ms,
    }


async def websocket_handler(websocket):
    print("Client connected")

    async for message in websocket:
        start_time = time.perf_counter()
        data = {}

        try:
            data = json.loads(message)
            result = await handle_command(data)
            ack = create_ack(result, start_time)

        except json.JSONDecodeError:
            ack = {
                "type": "ack",
                "status": "error",
                "command": None,
                "message": "Invalid JSON",
                "latency_ms": None,
            }

        except Exception as error:
            ack = {
                "type": "ack",
                "status": "error",
                "command": data.get("command"),
                "message": str(error),
                "latency_ms": None,
            }

        write_event_log(data, ack)
        await websocket.send(json.dumps(ack, ensure_ascii=False))


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to detect IP"

async def main():
    local_ip = get_local_ip()

    print(f"WebSocket Server running at ws://{HOST}:{PORT}")
    print(f"Use this URL on mobile: ws://{local_ip}:{PORT}")

    async with serve(websocket_handler, HOST, PORT):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")