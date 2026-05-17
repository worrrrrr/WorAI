"""
KRIT Inference Engine V3.0 - With Tools
เพิ่มความสามารถเรียกฟังก์ชันภายนอกเหมือน Claude
"""
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable

class ToolRegistry:
    """คลัง Tools ที่ KRIT เรียกใช้ได้"""
    def __init__(self):
        self.tools = {}

    def register(self, name: str, description: str, parameters: Dict):
        """ลงทะเบียน Tool ใหม่"""
        def decorator(func: Callable):
            self.tools[name] = {
                "function": func,
                "description": description,
                "parameters": parameters
            }
            return func
        return decorator

    def get_schema(self) -> List[Dict]:
        """ส่ง schema ให้ AI รู้ว่ามี Tools อะไรบ้าง"""
        return [
            {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for name, tool in self.tools.items()
        ]

    def execute(self, name: str, arguments: Dict):
        """รัน Tool ที่ AI เรียก"""
        if name not in self.tools:
            return {"error": f"Tool {name} not found"}
        try:
            return self.tools[name]["function"](**arguments)
        except Exception as e:
            return {"error": str(e)}

# สร้าง Registry กลาง
tools = ToolRegistry()

# ===== ตัวอย่าง Tools ที่ KRIT ใช้ได้ =====

@tools.register(
    name="check_calendar",
    description="ตรวจสอบตารางเวลาวันนี้ว่ามีประชุมกี่โมง",
    parameters={
        "type": "object",
        "properties": {
            "date": {"type": "string", "description": "วันที่ รูปแบบ YYYY-MM-DD"}
        },
        "required": ["date"]
    }
)
def check_calendar(date: str) -> Dict:
    # ต่อ Google Calendar API จริงตรงนี้
    return {
        "events": [
            {"time": "10:00", "title": "ประชุมทีม"},
            {"time": "14:00", "title": "คุยลูกค้า"}
        ],
        "free_slots": ["11:00-13:00", "15:00-17:00"]
    }

@tools.register(
    name="send_line_notify",
    description="ส่งข้อความแจ้งเตือนเข้า Line",
    parameters={
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "ข้อความที่ต้องการส่ง"}
        },
        "required": ["message"]
    }
)
def send_line_notify(message: str) -> Dict:
    # ต่อ Line Notify API จริงตรงนี้
    print(f"[LINE] {message}")
    return {"status": "sent", "message": message}

@tools.register(
    name="create_task",
    description="สร้าง Task ใหม่ในระบบ",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "assignee": {"type": "string"},
            "due_date": {"type": "string"}
        },
        "required": ["title"]
    }
)
def create_task(title: str, assignee: str = "me", due_date: str = "") -> Dict:
    # ต่อ Notion/Asana API จริงตรงนี้
    return {
        "task_id": "TASK-001",
        "title": title,
        "assignee": assignee,
        "status": "created"
    }

@tools.register(
    name="search_knowledge",
    description="ค้นหาความรู้จากคลังแสง KRIT",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "คำค้น"}
        },
        "required": ["query"]
    }
)
def search_knowledge(query: str) -> Dict:
    # ต่อ Vector DB จริงตรงนี้
    return {
        "results": [
            {"title": "Atomic Habits สรุป", "insight": "ทำให้น้อยแต่ทำทุกวัน"},
            {"title": "วิธีเลิกผัดวัน", "insight": "กฎ 2 นาที"}
        ]
    }

class KritEngineV3:
    """KRIT V3.0 + Tools"""

    def __init__(self, tool_registry: ToolRegistry):
        self.name = "KRIT"
        self.version = "3.0"
        self.tools = tool_registry
        self.greeting = "สวัสดีครับ ผม KRIT V3 พร้อมคิดและลงมือทำ"

        # กฎ 3 ข้อเหมือนเดิม
        self.rules = {
            "focus": "บังคับเลือกทำทีละอย่าง",
            "control": "เช็คว่าคุมได้หรือไม่",
            "belief": "ตรวจสอบความเชื่อ"
        }

    def think_and_act(self, user_input: str) -> Dict:
        """
        ขั้นตอน: คิด -> ตัดสินใจใช้ Tool -> ตอบ
        Returns: {reply, tool_calls, state}
        """
        # 1. วิเคราะห์ว่าต้องใช้ Tool ไหม
        tool_calls = []

        if "ตาราง" in user_input or "ว่าง" in user_input:
            # เรียก Tool เช็คปฏิทิน
            result = self.tools.execute("check_calendar", {
                "date": datetime.now().strftime("%Y-%m-%d")
            })
            tool_calls.append({"tool": "check_calendar", "result": result})

            reply = f"ตรวจสอบตารางแล้ว วันนี้คุณว่างช่วง {', '.join(result['free_slots'])} ครับ แนะนำใช้ช่วงนี้ทำ {user_input}"

        elif "สร้างงาน" in user_input or "จด" in user_input:
            # เรียก Tool สร้าง Task
            result = self.tools.execute("create_task", {
                "title": user_input,
                "assignee": "คุณ"
            })
            tool_calls.append({"tool": "create_task", "result": result})

            reply = f"สร้าง Task เรียบร้อยครับ: {result['title']} รหัส {result['task_id']}"

        elif "หาความรู้" in user_input or "สรุป" in user_input:
            # เรียก Tool ค้นหา
            result = self.tools.execute("search_knowledge", {
                "query": user_input
            })
            tool_calls.append({"tool": "search_knowledge", "result": result})

            insights = "\n".join([f"- {r['insight']}" for r in result['results']])
            reply = f"ค้นหามาให้แล้วครับ:\n{insights}\n\nAction แนะนำ: เลือก 1 ข้อมาใช้วันนี้"

        else:
            # ไม่ใช้ Tool ตอบแบบเดิม
            reply = "รับทราบครับ คุณต้องการให้ผมช่วยเรื่องอะไรเป็นพิเศษ สามารถสั่งให้ผมเช็คตาราง, สร้างงาน, หรือหาความรู้ได้"

        return {
            "reply": reply,
            "tool_calls": tool_calls,
            "state": {"last_input": user_input}
        }

# ใช้งาน
def krit_with_tools(user_text: str) -> Dict:
    engine = KritEngineV3(tools)
    return engine.think_and_act(user_text)

if __name__ == "__main__":
    print("=== KRIT V3.0 With Tools ===")
    print("Tools ที่มี:", [t["name"] for t in tools.get_schema()])

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == 'exit':
            break

        res = krit_with_tools(user_input)
        print(f"\nKRIT: {res['reply']}")
        if res['tool_calls']:
            print(f"[Tools Used]: {res['tool_calls']}")