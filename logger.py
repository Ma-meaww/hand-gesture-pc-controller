import csv
import os
from datetime import datetime

LOG_FILE = "event_log.csv"

HEADERS = [
    "timestamp",
    "command",
    "gesture",
    "text",
    "x",
    "y",
    "status",
    "message",
    "latency_ms",
]


def create_log_file_if_needed():
    if os.path.exists(LOG_FILE):
        return

    with open(LOG_FILE, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)


def write_event_log(data: dict, ack: dict):
    create_log_file_if_needed()

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("command"),
        data.get("gesture"),
        data.get("text"),
        data.get("x"),
        data.get("y"),
        ack.get("status"),
        ack.get("message"),
        ack.get("latency_ms"),
    ]

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(row)