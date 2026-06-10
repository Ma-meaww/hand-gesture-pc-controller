import os
from datetime import datetime

import pandas as pd

LOG_FILE = "event_log.csv"

CURRENT_COMMANDS = [
    "PING",
    "SCROLL_DOWN",
    "SCROLL_UP",
    "CLICK",
    "CONFIRM",
    "INPUT_TEXT",
    "CURSOR_MOVE",
    "OPEN_THAIJO",
    "THAIJO_INPUT_SEARCH",
    "THAIJO_SUBMIT_SEARCH",
]


def clean_logs():
    if not os.path.exists(LOG_FILE):
        print("event_log.csv not found")
        return

    df = pd.read_csv(LOG_FILE)

    # backup ก่อนล้าง
    backup_name = f"event_log_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(backup_name, index=False, encoding="utf-8-sig")
    print(f"Backup created: {backup_name}")

    # เก็บเฉพาะ command ที่ใช้จริงตอนนี้
    df = df[df["command"].isin(CURRENT_COMMANDS)]

    # แก้ status เก่าที่ message เป็น error แต่เคยถูกบันทึกเป็น success
    error_keywords = [
        "not open",
        "not found",
        "missing",
        "unknown command",
        "invalid session",
        "stale element",
        "message:",
    ]

    def fix_status(row):
        message = str(row.get("message", "")).lower()

        for keyword in error_keywords:
            if keyword in message:
                return "error"

        return row.get("status", "success")

    df["status"] = df.apply(fix_status, axis=1)

    # ลบแถว error เก่าที่เป็น stacktrace ยาว ๆ ออก เพื่อให้ log สะอาด
    df = df[~df["message"].astype(str).str.contains("Stacktrace", case=False, na=False)]

    # เรียงเวลาเก่าไปใหม่ในไฟล์จริง
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp_dt", ascending=True)
    df = df.drop(columns=["timestamp_dt"])

    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

    print("event_log.csv cleaned successfully")
    print(f"Remaining rows: {len(df)}")


if __name__ == "__main__":
    clean_logs()