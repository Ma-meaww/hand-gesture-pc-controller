# hand-gesture-pc-controller

ฝั่ง Backend สำหรับโปรเจกต์ **ระบบควบคุมคอมพิวเตอร์ด้วยท่าทางมือผ่านสมาร์ตโฟน**

รับคำสั่งจากแอป Flutter บนมือถือผ่าน WebSocket แล้วสั่งงานคอมพิวเตอร์ด้วย PyAutoGUI และ Selenium

> **คู่กับ:** [hand-gesture-frontend](https://github.com/Ma-meaww/hand-gesture-frontend) — แอป Flutter ที่ตรวจจับท่ามือและส่งคำสั่งมายัง server นี้

---

## ภาพรวมระบบ

```
┌─────────────────────────────────────────────────────────────────┐
│                         SMARTPHONE                              │
│                                                                 │
│   Camera  →  MediaPipe   →   Gesture    →  WebSocket Client    │
│              (Flutter)       Detection      (hand-gesture-      │
│                              + Voice STT     frontend)          │
└───────────────────────────────────┬─────────────────────────────┘
                                    │  Wi-Fi (ws://192.168.x.x:8765)
                                    │  JSON commands
┌───────────────────────────────────▼─────────────────────────────┐
│                          THIS REPO                              │
│                                                                 │
│   WebSocket Server  →  Command Router  →  PyAutoGUI             │
│   (server/)                               (mouse, keyboard)     │
│                     →  Selenium           (browser_automation/) │
│                        (ThaiJO search)                          │
│                     →  CSV Logger + Streamlit Dashboard         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Gesture → Command Mapping

| ท่ามือ (Gesture)          | Command ที่ส่งมา       | สิ่งที่คอมทำ               |
|--------------------------|----------------------|--------------------------|
| ชี้นิ้วชี้ + ขยับมือ     | `CURSOR_MOVE`        | เลื่อนเมาส์               |
| Pinch (นิ้วชี้ + นิ้วโป้ง) | `CLICK`              | คลิกซ้าย                  |
| Pinch ค้าง (Confirm)     | `CONFIRM`            | กด Enter                  |
| ฝ่ามือหันลง + เลื่อนลง   | `SCROLL_DOWN`        | Scroll หน้าลง             |
| ฝ่ามือหันขึ้น + เลื่อนขึ้น | `SCROLL_UP`          | Scroll หน้าขึ้น           |
| ปุ่ม Voice บนแอป         | `THAIJO_INPUT_SEARCH` | พิมพ์คำค้นจาก Voice-to-Text |
| เมนู ThaiJO บนแอป        | `OPEN_THAIJO`        | เปิดเว็บ ThaiJO           |

---

## Project Structure

```
hand-gesture-pc-controller/
├── main.py                   # Entry point — รัน WebSocket Server
├── config.py                 # ค่าคงที่: HOST, PORT, ERROR_KEYWORDS
├── dashboard.py              # Streamlit Dashboard
├── PROTOCOL.md               # WebSocket Protocol สำหรับฝั่งมือถือ
├── requirements.txt
│
├── server/
│   └── websocket_server.py   # รับ connection และ dispatch คำสั่ง
│
├── automation/
│   ├── actions.py            # PyAutoGUI: mouse, keyboard, scroll
│   └── browser_automation.py # Selenium: เปิด/ค้นหา ThaiJO
│
├── utils/
│   └── logger.py             # บันทึก event log ลง CSV
│
├── data/
│   └── event_log.csv         # ไฟล์ log (สร้างอัตโนมัติตอน run)
│
└── tests/
    └── test_client.py        # ทดสอบส่ง command แทนมือถือ
```

---

## Requirements

- Windows 11
- Python 3.10+
- Google Chrome (สำหรับ Selenium)
- มือถือและคอมอยู่ Wi-Fi เดียวกัน

---

## Installation

```bash
# สร้างและเปิด virtual environment
python -m venv venv
venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

`requirements.txt`:
```
websockets
pyautogui
pyperclip
selenium
streamlit
pandas
```

---

## Run

**1. รัน WebSocket Server**
```bash
python main.py
```
ระบบจะแสดง URL สำหรับมือถือ:
```
WebSocket Server running at ws://0.0.0.0:8765
Use this URL on mobile: ws://192.168.1.42:8765
```
นำ URL นี้ไปใส่ในแอป Flutter

**2. ทดสอบโดยไม่ต้องใช้มือถือ**
```bash
# เปิด Terminal ใหม่
python tests/test_client.py
```

เมนูที่มี:
```
1. Scroll Down       5. Input Text
2. Scroll Up         6. Cursor Move
3. Click             7. Open ThaiJO
4. Confirm / Enter   8. Search ThaiJO
                     9. Ping Server
```

**3. รัน Dashboard**
```bash
streamlit run dashboard.py
```
ดูได้ที่ `http://localhost:8501` — แสดง latency, success/error count, event log

---

## Supported Commands

| Command                | Description                     |
|------------------------|---------------------------------|
| `PING`                 | ทดสอบการเชื่อมต่อ               |
| `SCROLL_DOWN`          | เลื่อนหน้าลง                   |
| `SCROLL_UP`            | เลื่อนหน้าขึ้น                 |
| `CLICK`                | คลิกเมาส์                      |
| `CONFIRM`              | กด Enter                        |
| `INPUT_TEXT`           | พิมพ์ข้อความ                   |
| `CURSOR_MOVE`          | ขยับเมาส์ด้วยค่า x, y (0.0–1.0) |
| `OPEN_THAIJO`          | เปิดเว็บ ThaiJO                 |
| `THAIJO_INPUT_SEARCH`  | พิมพ์คำค้นใน ThaiJO             |
| `THAIJO_SUBMIT_SEARCH` | กดค้นหาใน ThaiJO               |

โปรโตคอล JSON เต็มอยู่ที่ [PROTOCOL.md](./PROTOCOL.md)

---

## ThaiJO Flow

```
1. OPEN_THAIJO           →  เปิดเว็บ thaijo.org
2. THAIJO_INPUT_SEARCH   →  พิมพ์คำค้น (จาก Voice-to-Text บนมือถือ)
3. THAIJO_SUBMIT_SEARCH  →  กดค้นหา
4. CURSOR_MOVE + CLICK   →  เลือกบทความด้วยตัวเอง
```

> หมายเหตุ: ระบบไม่เปิดผลลัพธ์แรกอัตโนมัติ เพื่อให้ผู้ใช้ควบคุมได้เอง

---

## Troubleshooting

**มือถือเชื่อมต่อไม่ได้**
- ตรวจสอบว่ามือถือกับคอมอยู่ Wi-Fi เดียวกัน
- ใช้ IP ของคอม ไม่ใช่ `localhost`
- อนุญาต Python ใน Windows Firewall

**ThaiJO Search ไม่ทำงาน**
- ต้องส่ง `OPEN_THAIJO` ก่อนเสมอ
- ถ้า Chrome crash ให้ restart server แล้วส่ง `OPEN_THAIJO` ใหม่

**Chrome/Selenium error**
```bash
Ctrl + C
python main.py
```

---

## Related

- [hand-gesture-frontend](https://github.com/Ma-meaww/hand-gesture-frontend) — Flutter app (Android) สำหรับตรวจจับท่ามือและส่ง command
