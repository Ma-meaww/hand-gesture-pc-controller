# hand-gesture-pc-controller

ฝั่ง Backend สำหรับโปรเจกต์ **ระบบควบคุมคอมพิวเตอร์ด้วยท่าทางมือผ่านสมาร์ตโฟน**

รับคำสั่งจากแอป Flutter บนมือถือผ่าน WebSocket แล้วสั่งงานคอมพิวเตอร์ด้วย PyAutoGUI และ Selenium

> **คู่กับ:** [hand-gesture-frontend](https://github.com/Ma-meaww/hand-gesture-frontend) — แอป Flutter ที่ตรวจจับท่ามือและส่งคำสั่งมายัง server นี้

---

## ภาพรวมระบบ

```
┌─────────────────────────────────────────────────────────────┐
│                      SMARTPHONE                             │
│                                                             │
│  Camera → MediaPipe → Gesture Classifier → WebSocket Client │
│           (Flutter)   + Voice STT          (frontend repo)  │
└───────────────────────────────┬─────────────────────────────┘
                                │  Wi-Fi  ws://192.168.x.x:8765
                                │  JSON command
┌───────────────────────────────▼─────────────────────────────┐
│                    THIS REPO (Python)                        │
│                                                             │
│  server/websocket_server.py                                 │
│       │                                                     │
│       ├─→ automation/actions.py        (PyAutoGUI)          │
│       │      mouse move, click, scroll, keyboard            │
│       │                                                     │
│       ├─→ automation/browser_automation.py  (Selenium)      │
│       │      เปิด / ค้นหา ThaiJO                           │
│       │                                                     │
│       ├─→ automation/command_router.py                      │
│       │      dispatch command → ไปเรียก action ที่ถูกต้อง   │
│       │                                                     │
│       └─→ utils/logger.py  →  logs/event_log.csv           │
│                                                             │
│  dashboard.py  (Streamlit — ดู log + latency)               │
└─────────────────────────────────────────────────────────────┘
```

---

## Gesture → Command Mapping

| ท่ามือ (Gesture)               | Command ที่ส่งมา        | สิ่งที่คอมทำ              |
|-------------------------------|------------------------|--------------------------|
| ชี้นิ้วชี้ + ขยับมือ          | `CURSOR_MOVE`          | เลื่อนเมาส์              |
| Pinch (นิ้วชี้ + นิ้วโป้ง)    | `CLICK`                | คลิกซ้าย                 |
| Pinch ค้าง (Confirm)          | `CONFIRM`              | กด Enter                 |
| ฝ่ามือหันลง + เลื่อนลง        | `SCROLL_DOWN`          | Scroll หน้าลง            |
| ฝ่ามือหันขึ้น + เลื่อนขึ้น    | `SCROLL_UP`            | Scroll หน้าขึ้น          |
| ปุ่ม Voice บนแอป              | `THAIJO_INPUT_SEARCH`  | พิมพ์คำค้นจาก Voice STT  |
| เมนู ThaiJO บนแอป             | `OPEN_THAIJO`          | เปิดเว็บ ThaiJO          |

---

## Project Structure

```
hand-gesture-pc-controller/
├── main.py                          # Entry point — รัน WebSocket Server
├── config.py                        # HOST, PORT, ERROR_KEYWORDS
├── dashboard.py                     # Streamlit Dashboard
├── PROTOCOL.md                      # WebSocket Protocol สำหรับฝั่งมือถือ
├── requirements.txt
│
├── server/
│   ├── __init__.py
│   └── websocket_server.py          # รับ connection, parse JSON, dispatch
│
├── automation/
│   ├── __init__.py
│   ├── actions.py                   # PyAutoGUI: move, click, scroll, keyboard
│   ├── browser_automation.py        # Selenium: เปิด/ค้นหา ThaiJO
│   └── command_router.py            # Map command string → function call
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                    # บันทึก event log
│   └── network.py                   # ดึง local IP สำหรับแสดงใน console
│
├── data/
│   └── evaluation_template.csv      # Template สำหรับประเมินผล
│
├── logs/
│   └── event_log.csv                # ไฟล์ log (สร้างอัตโนมัติตอน run)
│
├── tests/
│   ├── test_client.py               # ทดสอบส่ง command แทนมือถือ
│   └── test_cursor_stream.py        # ทดสอบ cursor move แบบ stream
│
└── tools/
    ├── analyze_evaluation.py        # วิเคราะห์ผล evaluation
    ├── clean_logs.py                # ล้าง log เก่า
    └── generate_test_template.py    # สร้าง evaluation template
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
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
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

**2. ทดสอบโดยไม่ต้องใช้มือถือ**
```bash
python tests/test_client.py
```
เมนูที่มี:
```
1. Scroll Down        6. Cursor Move
2. Scroll Up          7. Open ThaiJO
3. Click              8. Search ThaiJO
4. Confirm / Enter    9. Ping Server
5. Input Text
```

**3. ทดสอบ cursor stream (continuous move)**
```bash
python tests/test_cursor_stream.py
```

**4. รัน Dashboard**
```bash
streamlit run dashboard.py
# เปิด http://localhost:8501
```

---

## Supported Commands

| Command                | Description                       |
|------------------------|-----------------------------------|
| `PING`                 | ทดสอบการเชื่อมต่อ                 |
| `SCROLL_DOWN`          | เลื่อนหน้าลง                     |
| `SCROLL_UP`            | เลื่อนหน้าขึ้น                   |
| `CLICK`                | คลิกเมาส์                        |
| `CONFIRM`              | กด Enter                          |
| `INPUT_TEXT`           | พิมพ์ข้อความ                     |
| `CURSOR_MOVE`          | ขยับเมาส์ด้วยค่า x, y (0.0–1.0)  |
| `OPEN_THAIJO`          | เปิดเว็บ ThaiJO                   |
| `THAIJO_INPUT_SEARCH`  | พิมพ์คำค้นใน ThaiJO               |
| `THAIJO_SUBMIT_SEARCH` | กดค้นหาใน ThaiJO                 |

โปรโตคอล JSON เต็มดูได้ที่ [PROTOCOL.md](./PROTOCOL.md)

---

## ThaiJO Flow

```
1. OPEN_THAIJO           →  เปิดเว็บ thaijo.org
2. THAIJO_INPUT_SEARCH   →  พิมพ์คำค้น (จาก Voice STT บนมือถือ)
3. THAIJO_SUBMIT_SEARCH  →  กดค้นหา
4. CURSOR_MOVE + CLICK   →  เลือกบทความด้วยตัวเอง
```

> ระบบไม่เปิดผลลัพธ์แรกอัตโนมัติ เพื่อให้ผู้ใช้ควบคุมได้เอง

---

## Tools

| Script                             | ใช้ทำอะไร                             |
|------------------------------------|--------------------------------------|
| `tools/analyze_evaluation.py`      | วิเคราะห์ผลการประเมินจาก CSV         |
| `tools/clean_logs.py`              | ลบ log เก่าออกจาก `logs/`            |
| `tools/generate_test_template.py`  | สร้าง `data/evaluation_template.csv` |

---

## Troubleshooting

**มือถือเชื่อมต่อไม่ได้**
- มือถือกับคอมต้องอยู่ Wi-Fi เดียวกัน
- ใช้ IP ของคอม ไม่ใช่ `localhost`
- อนุญาต Python ใน Windows Firewall

**ThaiJO Search ไม่ทำงาน**
- ต้องส่ง `OPEN_THAIJO` ก่อนเสมอ

**Chrome/Selenium error**
```bash
Ctrl + C && python main.py
```

---

## Related

- [hand-gesture-frontend](https://github.com/Ma-meaww/hand-gesture-frontend) — Flutter app สำหรับตรวจจับท่ามือและส่ง command
testgithub