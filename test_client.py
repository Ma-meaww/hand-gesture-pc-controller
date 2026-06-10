import asyncio
import json
import time

from websockets.asyncio.client import connect

SERVER_URL = "ws://localhost:8765"


def now_ms() -> int:
    return int(time.time() * 1000)


def make_command(command: str, gesture=None, text=None, x=None, y=None) -> dict:
    return {
        "type": "command",
        "command": command,
        "gesture": gesture,
        "x": x,
        "y": y,
        "text": text,
        "timestamp": now_ms(),
    }


async def send_command(command: dict, delay: int = 0):
    if delay > 0:
        print(f"\nCommand will be sent in {delay} seconds...")

        for i in range(delay, 0, -1):
            print(f"{i}...")
            await asyncio.sleep(1)

    async with connect(SERVER_URL) as websocket:
        await websocket.send(json.dumps(command, ensure_ascii=False))
        response = await websocket.recv()

    print("\nResponse from server:")
    print(response)
    print()


async def thaijo_search_flow():
    keyword = input("Enter ThaiJO keyword: ")

    await send_command(make_command("THAIJO_INPUT_SEARCH", text=keyword))

    submit = input("Submit search? y/n: ").strip().lower()

    if submit == "y":
        await send_command(make_command("THAIJO_SUBMIT_SEARCH", gesture="PINCH_CONFIRM"))
    else:
        print("Search was not submitted\n")


def build_command(choice: str) -> dict | None:
    if choice == "1":
        return make_command("SCROLL_DOWN", gesture="OPEN_PALM_DOWN")

    if choice == "2":
        return make_command("SCROLL_UP", gesture="OPEN_PALM_UP")

    if choice == "3":
        return make_command("CLICK", gesture="PINCH")

    if choice == "4":
        return make_command("CONFIRM", gesture="PINCH_CONFIRM")

    if choice == "5":
        text = input("Enter text: ")
        return make_command("INPUT_TEXT", text=text)

    if choice == "6":
        x = float(input("Enter x 0.0 - 1.0: "))
        y = float(input("Enter y 0.0 - 1.0: "))
        return make_command("CURSOR_MOVE", gesture="INDEX_FINGER", x=x, y=y)

    if choice == "7":
        return make_command("OPEN_THAIJO")

    if choice == "9":
        return make_command("PING")

    return None


async def main():
    while True:
        print("===== Test Command Menu =====")
        print("1. Scroll Down")
        print("2. Scroll Up")
        print("3. Click")
        print("4. Confirm / Enter")
        print("5. Input Text")
        print("6. Cursor Move")
        print("7. Open ThaiJO")
        print("8. Search ThaiJO")
        print("9. Ping Server")
        print("q. Quit")

        choice = input("Select command: ").strip().lower()

        if choice == "q":
            print("Exit test client")
            break

        if choice == "8":
            await thaijo_search_flow()
            continue

        command = build_command(choice)

        if command is None:
            print("Invalid choice\n")
            continue

        delay = 3 if command["command"] in ["INPUT_TEXT", "CLICK", "CONFIRM"] else 0
        await send_command(command, delay=delay)


if __name__ == "__main__":
    asyncio.run(main())