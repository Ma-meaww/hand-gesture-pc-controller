# WebSocket Protocol

โปรเจกต์นี้ใช้ WebSocket สำหรับส่งคำสั่งจากแอป Android ไปยังโปรแกรมควบคุมบนคอมพิวเตอร์

## Server URL

เมื่อรันฝั่งคอมพิวเตอร์ด้วยคำสั่ง

```bash
python main.py
```

ระบบจะแสดง URL สำหรับมือถือ เช่น

```text
Use this URL on mobile: ws://192.168.1.42:8765
```

ให้นำ URL นี้ไปใช้ในแอป Android

หมายเหตุ:

- มือถือและคอมพิวเตอร์ต้องอยู่ใน Wi-Fi เดียวกัน
- ห้ามใช้ `localhost` บนมือถือ เพราะ `localhost` หมายถึงเครื่องมือถือเอง
- IP อาจเปลี่ยนได้ตาม Wi-Fi ที่ใช้งาน

---

## JSON Request Format

มือถือส่งคำสั่งมายังคอมพิวเตอร์ในรูปแบบ JSON ดังนี้

```json
{
  "type": "command",
  "command": "PING",
  "gesture": null,
  "x": null,
  "y": null,
  "text": null,
  "timestamp": 123456789
}
```

### Field Description

| Field | Type | Description |
|---|---|---|
| type | string | ประเภทข้อความ ใช้ค่า `"command"` |
| command | string | ชื่อคำสั่งที่ต้องการให้คอมพิวเตอร์ทำ |
| gesture | string/null | ชื่อท่าทางที่ตรวจพบ เช่น `PINCH`, `OPEN_PALM_DOWN` |
| x | number/null | ตำแหน่ง x สำหรับ cursor control ค่า 0.0 - 1.0 |
| y | number/null | ตำแหน่ง y สำหรับ cursor control ค่า 0.0 - 1.0 |
| text | string/null | ข้อความที่ได้จาก Voice-to-Text |
| timestamp | number | เวลาที่มือถือส่งคำสั่ง หน่วย milliseconds |

---

## Supported Commands

| Command | Description |
|---|---|
| `PING` | ใช้ทดสอบการเชื่อมต่อ |
| `SCROLL_DOWN` | เลื่อนหน้าลง |
| `SCROLL_UP` | เลื่อนหน้าขึ้น |
| `CLICK` | คลิกเมาส์ |
| `CONFIRM` | กด Enter เพื่อยืนยัน |
| `INPUT_TEXT` | พิมพ์ข้อความทั่วไป |
| `CURSOR_MOVE` | ขยับเมาส์ตามค่า x, y |
| `OPEN_THAIJO` | เปิดเว็บไซต์ ThaiJO |
| `THAIJO_INPUT_SEARCH` | พิมพ์คำค้นลงช่องค้นหาของ ThaiJO |
| `THAIJO_SUBMIT_SEARCH` | กดค้นหาใน ThaiJO |

---

## Example: Ping

ใช้ทดสอบว่าแอปเชื่อมต่อกับคอมพิวเตอร์ได้หรือไม่

```json
{
  "type": "command",
  "command": "PING",
  "gesture": null,
  "x": null,
  "y": null,
  "text": null,
  "timestamp": 123456789
}
```

Expected response:

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

## Example: Cursor Move

ใช้สำหรับขยับเมาส์ตามตำแหน่งนิ้วมือ

```json
{
  "type": "command",
  "command": "CURSOR_MOVE",
  "gesture": "INDEX_FINGER",
  "x": 0.52,
  "y": 0.34,
  "text": null,
  "timestamp": 123456789
}
```

หมายเหตุ:

- `x = 0.0` คือซ้ายสุดของหน้าจอ
- `x = 1.0` คือขวาสุดของหน้าจอ
- `y = 0.0` คือบนสุดของหน้าจอ
- `y = 1.0` คือล่างสุดของหน้าจอ

---

## Example: Scroll Down

```json
{
  "type": "command",
  "command": "SCROLL_DOWN",
  "gesture": "OPEN_PALM_DOWN",
  "x": null,
  "y": null,
  "text": null,
  "timestamp": 123456789
}
```

---

## Example: Click

```json
{
  "type": "command",
  "command": "CLICK",
  "gesture": "PINCH",
  "x": null,
  "y": null,
  "text": null,
  "timestamp": 123456789
}
```

---

## Example: Open ThaiJO

ต้องเปิด ThaiJO ก่อนใช้งานคำสั่งค้นหา

```json
{
  "type": "command",
  "command": "OPEN_THAIJO",
  "gesture": null,
  "x": null,
  "y": null,
  "text": null,
  "timestamp": 123456789
}
```

---

## Example: ThaiJO Voice Search

หลังจากผู้ใช้พูดคำค้น แอปส่งข้อความที่ได้จาก Voice-to-Text มาด้วยคำสั่งนี้

```json
{
  "type": "command",
  "command": "THAIJO_INPUT_SEARCH",
  "gesture": null,
  "x": null,
  "y": null,
  "text": "machine learning",
  "timestamp": 123456789
}
```

จากนั้นรอผู้ใช้ทำท่า Confirm แล้วส่งคำสั่งค้นหา

```json
{
  "type": "command",
  "command": "THAIJO_SUBMIT_SEARCH",
  "gesture": "PINCH_CONFIRM",
  "x": null,
  "y": null,
  "text": null,
  "timestamp": 123456789
}
```

---

## ACK Response Format

ฝั่งคอมพิวเตอร์จะตอบกลับทุกครั้งในรูปแบบ ACK

```json
{
  "type": "ack",
  "status": "success",
  "command": "PING",
  "message": "pong",
  "latency_ms": 1.4
}
```

### Field Description

| Field | Type | Description |
|---|---|---|
| type | string | ประเภทข้อความ ใช้ค่า `"ack"` |
| status | string | ผลลัพธ์ เช่น `success` หรือ `error` |
| command | string/null | คำสั่งที่ได้รับ |
| message | string | รายละเอียดผลลัพธ์ |
| latency_ms | number/null | เวลาที่ใช้ประมวลผลฝั่งคอม หน่วย milliseconds |

---

## Error Example

กรณีค้นหา ThaiJO โดยยังไม่ได้เปิดเว็บก่อน

```json
{
  "type": "ack",
  "status": "error",
  "command": "THAIJO_INPUT_SEARCH",
  "message": "ThaiJO is not open. Please use OPEN_THAIJO first.",
  "latency_ms": 1.95
}
```

---

## Suggested Gesture Mapping

| Gesture | Command |
|---|---|
| Index finger move | `CURSOR_MOVE` |
| Pinch | `CLICK` |
| Pinch confirm | `CONFIRM` / `THAIJO_SUBMIT_SEARCH` |
| Open palm move down | `SCROLL_DOWN` |
| Open palm move up | `SCROLL_UP` |
| Voice button / voice mode | `THAIJO_INPUT_SEARCH` |
| Start ThaiJO gesture/menu | `OPEN_THAIJO` |

---

## Recommended ThaiJO Flow

ลำดับที่แนะนำสำหรับใช้งาน ThaiJO คือ

1. ส่ง `OPEN_THAIJO`
2. ผู้ใช้พูดคำค้น
3. ส่ง `THAIJO_INPUT_SEARCH` พร้อมข้อความใน field `text`
4. รอผู้ใช้ทำท่า Confirm
5. ส่ง `THAIJO_SUBMIT_SEARCH`
6. ผู้ใช้เลือกบทความเองด้วย cursor, click, scroll

ระบบไม่เปิดผลลัพธ์แรกอัตโนมัติ เพื่อลดโอกาสคลิกผิดและให้ผู้ใช้ควบคุมเอง