import asyncio
import json
import time

import pyautogui
import pyperclip
from websockets.asyncio.server import serve

HOST = "localhost"
PORT = 8765

# เลื่อนเมาส์ไปมุมซ้ายบนสุดเพื่อหยุดฉุกเฉินได้
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def execute_pc_action(command: str, data: dict) -> str:
    """
    แปลง command ที่รับจากมือถือ/Client
    ให้เป็นการควบคุมคอมด้วย PyAutoGUI
    """

    if command == "SCROLL_DOWN":
        pyautogui.scroll(-5)
        return "Scrolled down"

    if command == "SCROLL_UP":
        pyautogui.scroll(5)
        return "Scrolled up"

    if command == "CLICK":
        pyautogui.click()
        return "Clicked"

    if command == "CONFIRM":
        pyautogui.press("enter")
        return "Pressed Enter"

    if command == "INPUT_TEXT":
        text = data.get("text", "")

        if not text:
            return "No text to input"

        # ใช้ copy-paste เพื่อรองรับทั้งภาษาไทยและอังกฤษ
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")

        return f"Input text: {text}"

    if command == "CURSOR_MOVE":
        x = data.get("x")
        y = data.get("y")

        if x is None or y is None:
            return "Missing x or y"

        screen_width, screen_height = pyautogui.size()

        # x, y จากมือถือเป็นค่า 0.0 - 1.0
        target_x = int(float(x) * screen_width)
        target_y = int(float(y) * screen_height)

        pyautogui.moveTo(target_x, target_y, duration=0.05)

        return f"Moved cursor to ({target_x}, {target_y})"

    return f"Unknown command: {command}"


async def handle_command(data: dict) -> dict:
    command = data.get("command")
    gesture = data.get("gesture")
    text = data.get("text")
    x = data.get("x")
    y = data.get("y")

    print("\n--- Received Command ---")
    print(f"command: {command}")
    print(f"gesture: {gesture}")
    print(f"text: {text}")
    print(f"x: {x}, y: {y}")

    if not command:
        return {
            "status": "error",
            "command": None,
            "message": "Missing command"
        }

    action_message = execute_pc_action(command, data)

    print(f"action: {action_message}")

    return {
        "status": "success",
        "command": command,
        "message": action_message
    }


async def websocket_handler(websocket):
    print("Client connected")

    async for message in websocket:
        start_time = time.perf_counter()

        try:
            data = json.loads(message)
            result = await handle_command(data)

            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            ack = {
                "type": "ack",
                "status": result["status"],
                "command": result["command"],
                "message": result["message"],
                "latency_ms": latency_ms
            }

        except json.JSONDecodeError:
            ack = {
                "type": "ack",
                "status": "error",
                "command": None,
                "message": "Invalid JSON",
                "latency_ms": None
            }

        except Exception as e:
            ack = {
                "type": "ack",
                "status": "error",
                "command": None,
                "message": str(e),
                "latency_ms": None
            }

        await websocket.send(json.dumps(ack, ensure_ascii=False))


async def main():
    print(f"WebSocket Server running at ws://{HOST}:{PORT}")

    async with serve(websocket_handler, HOST, PORT):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())