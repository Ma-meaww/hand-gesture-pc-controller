# PC Controller Backend

โปรแกรมฝั่งคอมพิวเตอร์สำหรับรับคำสั่งจากแอป Android ผ่าน WebSocket แล้วควบคุมคอมพิวเตอร์ด้วย Python, PyAutoGUI และ Selenium

ระบบนี้เป็นส่วน Backend + Automation ของโปรเจกต์ระบบควบคุมคอมพิวเตอร์ด้วยท่าทางมือผ่านสมาร์ตโฟน

---

## Features

- รับคำสั่งจากมือถือผ่าน WebSocket
- ส่ง ACK กลับไปยังมือถือ
- วัดค่า latency เบื้องต้น
- ควบคุมเมาส์และคีย์บอร์ดด้วย PyAutoGUI
- รองรับ Cursor Move, Click, Confirm, Scroll
- เปิดเว็บไซต์ ThaiJO
- ค้นหาข้อมูลใน ThaiJO ด้วย Selenium
- บันทึก Event Log เป็นไฟล์ CSV
- แสดง Dashboard ด้วย Streamlit

---

## Project Structure

```text
pc_controller/
  main.py
  actions.py
  browser_automation.py
  logger.py
  dashboard.py
  test_client.py
  PROTOCOL.md
  README.md
  requirements.txt
  event_log.csv
```

### File Description

| File | Description |
|---|---|
| `main.py` | WebSocket Server หลัก |
| `actions.py` | รวมคำสั่งควบคุมคอมพิวเตอร์ |
| `browser_automation.py` | ควบคุมเว็บไซต์ ThaiJO ด้วย Selenium |
| `logger.py` | บันทึก log ลงไฟล์ CSV |
| `dashboard.py` | Dashboard สำหรับดู log และ latency |
| `test_client.py` | ตัวทดสอบส่ง command แทนมือถือ |
| `PROTOCOL.md` | เอกสารรูปแบบ JSON สำหรับให้ฝั่งมือถือใช้ |
| `requirements.txt` | รายชื่อ library ที่ต้องติดตั้ง |

---

## Requirements

- Windows 11
- Python 3.10 ขึ้นไป
- Google Chrome
- มือถือและคอมต้องอยู่ Wi-Fi เดียวกัน ถ้าจะทดสอบกับมือถือจริง

---

## Installation

สร้าง virtual environment

```bash
python -m venv venv
```

เปิดใช้งาน virtual environment

```bash
venv\Scripts\activate
```

ติดตั้ง library

```bash
pip install -r requirements.txt
```

---

## requirements.txt

ไฟล์ `requirements.txt` ควรมีรายการประมาณนี้

```txt
websockets
pyautogui
pyperclip
selenium
streamlit
pandas
```

---

## Run WebSocket Server

รัน server ฝั่งคอมพิวเตอร์

```bash
python main.py
```

ตัวอย่างผลลัพธ์

```text
WebSocket Server running at ws://0.0.0.0:8765
Use this URL on mobile: ws://192.168.1.42:8765
```

URL ที่ขึ้นหลังคำว่า `Use this URL on mobile` คือ URL ที่แอป Android ต้องใช้เชื่อมต่อ

---

## Run Test Client

ใช้ทดสอบระบบโดยไม่ต้องรอแอปมือถือ

เปิด Terminal อีกหน้าต่าง แล้วรัน

```bash
python test_client.py
```

เมนูทดสอบที่มีตอนนี้

```text
1. Scroll Down
2. Scroll Up
3. Click
4. Confirm / Enter
5. Input Text
6. Cursor Move
7. Open ThaiJO
8. Search ThaiJO
9. Ping Server
q. Quit
```

---

## Run Dashboard

เปิด Dashboard ด้วย Streamlit

```bash
streamlit run dashboard.py
```

Dashboard ใช้สำหรับดูข้อมูล เช่น

- จำนวน command ทั้งหมด
- จำนวน success / error
- command ล่าสุด
- latency เฉลี่ย
- กราฟ latency
- ตาราง event log ล่าสุด

---

## Basic Test Flow

### 1. ทดสอบ WebSocket

รัน `main.py`

```bash
python main.py
```

จากนั้นรัน `test_client.py`

```bash
python test_client.py
```

เลือกเมนู

```text
9. Ping Server
```

ถ้าสำเร็จจะได้ response ประมาณนี้

```json
{
  "type": "ack",
  "status": "success",
  "command": "PING",
  "message": "pong",
  "latency_ms": 1.4
}
```

---

### 2. ทดสอบ ThaiJO Search

เลือกเมนู

```text
7. Open ThaiJO
```

จากนั้นเลือก

```text
8. Search ThaiJO
```

ใส่คำค้น เช่น

```text
machine learning
```

ระบบจะใส่คำค้นลงช่องค้นหา แล้วถามว่าจะ submit หรือไม่

```text
Submit search? y/n:
```

ถ้าตอบ `y` ระบบจะกดค้นหา

---

## Supported Commands

| Command | Description |
|---|---|
| `PING` | ทดสอบการเชื่อมต่อ |
| `SCROLL_DOWN` | เลื่อนหน้าลง |
| `SCROLL_UP` | เลื่อนหน้าขึ้น |
| `CLICK` | คลิกเมาส์ |
| `CONFIRM` | กด Enter |
| `INPUT_TEXT` | พิมพ์ข้อความ |
| `CURSOR_MOVE` | ขยับเมาส์ด้วยค่า x, y |
| `OPEN_THAIJO` | เปิดเว็บไซต์ ThaiJO |
| `THAIJO_INPUT_SEARCH` | ใส่คำค้นในช่องค้นหา ThaiJO |
| `THAIJO_SUBMIT_SEARCH` | กดค้นหาใน ThaiJO |

---

## Notes for Mobile Integration

ฝั่งมือถือให้ดูรายละเอียดในไฟล์

```text
PROTOCOL.md
```

มือถือจะต้องส่ง JSON ผ่าน WebSocket มาที่ URL ของคอม เช่น

```text
ws://192.168.1.42:8765
```

ห้ามใช้

```text
ws://localhost:8765
```

เพราะ `localhost` บนมือถือหมายถึงตัวมือถือเอง ไม่ใช่คอมพิวเตอร์

---

## Common Problems

### 1. มือถือเชื่อมต่อไม่ได้

ให้ตรวจสอบว่า

- มือถือกับคอมอยู่ Wi-Fi เดียวกัน
- ใช้ IP ของคอม ไม่ใช่ `localhost`
- Windows Firewall อนุญาต Python แล้ว

---

### 2. ThaiJO Search ใช้ไม่ได้

ให้เปิด ThaiJO ก่อนด้วยคำสั่ง

```text
OPEN_THAIJO
```

จากนั้นค่อยใช้

```text
THAIJO_INPUT_SEARCH
THAIJO_SUBMIT_SEARCH
```

ถ้าใช้คำสั่งค้นหาก่อนเปิดเว็บ ระบบจะตอบกลับว่า

```text
ThaiJO is not open. Please use OPEN_THAIJO first.
```

---

### 3. Chrome/Selenium Error

ถ้า Chrome ถูกปิดหรือ Selenium session พัง ระบบจะสร้าง driver ใหม่เมื่อเปิด ThaiJO อีกครั้ง

ถ้ายังมีปัญหา ให้หยุด server แล้วรันใหม่

```bash
Ctrl + C
python main.py
```

---

## Current Status

Backend + Automation Status: Ready for mobile integration testing

สิ่งที่ทำได้แล้ว

- WebSocket Server
- Command ACK
- Latency Log
- PyAutoGUI Control
- Cursor Move
- ThaiJO Search
- CSV Event Log
- Streamlit Dashboard
- Protocol Documentation
