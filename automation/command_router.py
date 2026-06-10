from config import ERROR_KEYWORDS
from automation.actions import execute_pc_action


def get_status_from_message(message: str) -> str:
    message_lower = message.lower()

    for keyword in ERROR_KEYWORDS:
        if keyword in message_lower:
            return "error"

    return "success"


def print_command_log(data: dict):
    print("\n--- Received Command ---")
    print(f"command: {data.get('command')}")
    print(f"gesture: {data.get('gesture')}")
    print(f"text: {data.get('text')}")
    print(f"x: {data.get('x')}, y: {data.get('y')}")


async def handle_command(data: dict) -> dict:
    command = data.get("command")

    if not command:
        return {
            "status": "error",
            "command": None,
            "message": "Missing command",
        }

    print_command_log(data)

    message = execute_pc_action(command, data)
    status = get_status_from_message(message)

    print(f"action: {message}")

    return {
        "status": status,
        "command": command,
        "message": message,
    }