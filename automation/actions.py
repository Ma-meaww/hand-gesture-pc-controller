import time
import pyautogui
import pyperclip

from automation.browser_automation import (
    open_thaijo,
    input_thaijo_search,
    submit_thaijo_search,
    close_browser,
)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

SCROLL_AMOUNT = 40

COMMAND_COOLDOWN = {
    "CLICK": 0.6,
    "CONFIRM": 0.6,
    "SCROLL_DOWN": 0.25,
    "SCROLL_UP": 0.25,
    "THAIJO_SUBMIT_SEARCH": 0.8,
    "OPEN_THAIJO": 1.0,
    "CLOSE_BROWSER": 0.8,
}

last_command_time = {}

CURSOR_SMOOTHING_FACTOR = 0.28
CURSOR_DEAD_ZONE_PX = 10
CURSOR_MIN_INTERVAL_SEC = 0.015

last_cursor_x = None
last_cursor_y = None
last_cursor_move_time = 0.0


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(value, max_value))

def is_on_cooldown(command: str) -> bool:
    cooldown = COMMAND_COOLDOWN.get(command)

    if cooldown is None:
        return False

    now = time.perf_counter()
    last_time = last_command_time.get(command, 0)

    if now - last_time < cooldown:
        return True

    last_command_time[command] = now
    return False

def input_text(text: str) -> str:
    if not text:
        return "No text to input"

    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")

    return f"Input text: {text}"


def clamp_pixel(value: float, max_value: int) -> int:
    return max(0, min(int(round(value)), max_value - 1))


def reset_cursor_state() -> str:
    global last_cursor_x, last_cursor_y, last_cursor_move_time

    last_cursor_x = None
    last_cursor_y = None
    last_cursor_move_time = 0.0

    return "Cursor state reset"


def move_cursor(x: float, y: float) -> str:
    global last_cursor_x, last_cursor_y, last_cursor_move_time

    now = time.perf_counter()

    if now - last_cursor_move_time < CURSOR_MIN_INTERVAL_SEC:
        return "Cursor move ignored, interval too short"

    last_cursor_move_time = now

    x = clamp(float(x))
    y = clamp(float(y))

    screen_width, screen_height = pyautogui.size()

    target_x = clamp_pixel(x * (screen_width - 1), screen_width)
    target_y = clamp_pixel(y * (screen_height - 1), screen_height)

    if last_cursor_x is None or last_cursor_y is None:
        current_x, current_y = pyautogui.position()
        last_cursor_x = clamp_pixel(current_x, screen_width)
        last_cursor_y = clamp_pixel(current_y, screen_height)

    diff_x = target_x - last_cursor_x
    diff_y = target_y - last_cursor_y

    if abs(diff_x) < CURSOR_DEAD_ZONE_PX and abs(diff_y) < CURSOR_DEAD_ZONE_PX:
        return f"Cursor not moved, movement too small ({target_x}, {target_y})"

    smooth_x = clamp_pixel(
        last_cursor_x + diff_x * CURSOR_SMOOTHING_FACTOR,
        screen_width,
    )
    smooth_y = clamp_pixel(
        last_cursor_y + diff_y * CURSOR_SMOOTHING_FACTOR,
        screen_height,
    )

    pyautogui.moveTo(smooth_x, smooth_y, duration=0)

    last_cursor_x = smooth_x
    last_cursor_y = smooth_y

    return f"Moved cursor to ({smooth_x}, {smooth_y}) target=({target_x}, {target_y})"

def success(message: str) -> dict:
    return {
        "status": "success",
        "message": message,
    }

def error(message: str) -> dict:
    return {
        "status": "error",
        "message": message,
    }

def browser_result(message: str) -> dict:
    error_keywords = (
        "not open",
        "not found",
        "no keyword",
        "browser is not open",
    )

    message_lower = message.lower()

    for keyword in error_keywords:
        if keyword in message_lower:
            return error(message)

    return success(message)

def execute_pc_action(command: str, data: dict) -> dict:
    if is_on_cooldown(command):
        return success(f"Ignored {command}, cooldown active")
    
    if command == "PING":
        return success("pong")

    if command == "SCROLL_DOWN":
        pyautogui.scroll(-SCROLL_AMOUNT)
        return success(f"Scrolled down {SCROLL_AMOUNT}")

    if command == "SCROLL_UP":
        pyautogui.scroll(SCROLL_AMOUNT)
        return success(f"Scrolled up {SCROLL_AMOUNT}")

    if command == "CLICK":
        pyautogui.click()
        return success("Clicked")

    if command == "CONFIRM":
        pyautogui.press("enter")
        return success("Pressed Enter")

    if command == "INPUT_TEXT":
        text = data.get("text", "")

        if not text:
            return error("No text to input")

        return success(input_text(text))

    if command == "CURSOR_MOVE":
        x = data.get("x")
        y = data.get("y")

        if x is None or y is None:
            return error("Missing x or y")

        try:
            return success(move_cursor(float(x), float(y)))
        except (TypeError, ValueError):
            return error("Invalid x or y")
        
    if command == "CURSOR_RESET":
        return success(reset_cursor_state())

    if command == "OPEN_THAIJO":
        return browser_result(open_thaijo())

    if command == "THAIJO_INPUT_SEARCH":
        return browser_result(input_thaijo_search(data.get("text", "")))

    if command == "THAIJO_SUBMIT_SEARCH":
        return browser_result(submit_thaijo_search())

    if command == "CLOSE_BROWSER":
        return browser_result(close_browser())

    return error(f"Unknown command: {command}")