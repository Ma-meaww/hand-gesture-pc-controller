from config import ERROR_KEYWORDS
from automation.actions import execute_pc_action

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

    result = execute_pc_action(command, data)
    print(f"action: {result.get('message')}")

    return {
        "status": result.get("status", "success"),
        "command": command,
        "message": result.get("message", ""),
    }