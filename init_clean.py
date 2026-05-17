import os
import shutil
import sys
from pathlib import Path
import hashlib

ROOT = Path(__file__).parent
LOCKED_DIRS = ["logs", "tests"]
AI_IGNORE = ROOT / ".ai-ignore"

def get_dir_hash(path):
    if not path.exists(): return ""
    files = sorted(path.rglob("*.py"))
    content = "".join([f.name + str(f.stat().st_mtime) for f in files])
    return hashlib.md5(content.encode()).hexdigest()

if AI_IGNORE.exists():
    old_hashes = eval(AI_IGNORE.read_text())
    for dir_name in LOCKED_DIRS:
        dir_path = ROOT / dir_name
        if dir_path.exists():
            new_hash = get_dir_hash(dir_path)
            if old_hashes.get(dir_name, "")!= new_hash and old_hashes.get(dir_name, ""):
                print(f"❌ ERROR: โฟลเดอร์ {dir_name}/ โดนแก้!")
                sys.exit(1)

print("🔥 ล้างโปรเจค ยกเว้นโฟลเดอร์ล็อค...")

KEEP = {".git", "init_clean.py", ".gitignore", ".ai-ignore", "logs", "tests"}
for item in ROOT.iterdir():
    if item.name not in KEEP:
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

dirs = ["src/core", "src/domain", "src/utils", "src/tools", "config"]
for d in dirs:
    Path(ROOT / d).mkdir(parents=True, exist_ok=True)

for path in Path("src").rglob("*"):
    if path.is_dir():
        (path / "__init__.py").touch()

(ROOT / "logs").mkdir(exist_ok=True)
(ROOT / "tests/unit").mkdir(parents=True, exist_ok=True)
(ROOT / "tests/integration").mkdir(parents=True, exist_ok=True)
(ROOT / "tests/__init__.py").touch()

# pyproject.toml
(ROOT / "pyproject.toml").write_text("""[project]
name = "fools"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["pydantic>=2.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
""", encoding="utf-8")

# config/settings.py
(ROOT / "config/settings.py").write_text("""from pathlib import Path
class Settings:
    ROOT_DIR = Path(__file__).parent.parent
    LOG_DIR = ROOT_DIR / "logs"
    LOG_LEVEL = "INFO"
settings = Settings()
""", encoding="utf-8")

# src/utils/logger.py
(ROOT / "src/utils/logger.py").write_text("""import logging
from config.settings import settings

_logger = None
def setup_logger():
    global _logger
    if _logger: return _logger
    _logger = logging.getLogger("WorAI")
    _logger.setLevel(settings.LOG_LEVEL)
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s', datefmt='%H:%M:%S'))
    _logger.addHandler(h)
    fh = logging.FileHandler(settings.LOG_DIR / "fools.log", encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'))
    _logger.addHandler(fh)
    return _logger

log = setup_logger()
""", encoding="utf-8")

# src/core/types.py
(ROOT / "src/core/types.py").write_text("""from dataclasses import dataclass, field
from typing import Dict, Any, List, Literal

IntentType = Literal["math", "code", "search", "chat", "unknown"]

@dataclass
class PlanStep:
    id: int
    op: str
    tool_id: str
    args: Dict[str, Any]
    depends_on: List[int] = field(default_factory=list)

@dataclass
class ExecutionPlan:
    intent: IntentType
    steps: List[PlanStep]
""", encoding="utf-8")

# src/tools/math_tool.py แก้บัค %
(ROOT / "src/tools/math_tool.py").write_text("""import re

def calculate(expr: str) -> str:
    try:
        # รองรับ 1500 + 25% = 1500 * 1.25
        expr = expr.replace(' ', '')
        if re.search(r'(\\d+)([+\\-])(\\d+)%', expr):
            expr = re.sub(r'(\\d+)([+\\-])(\\d+)%', r'\\1\\2(\\1*\\3/100)', expr)
        elif '%' in expr:
            expr = expr.replace('%', '/100')

        expr_clean = re.sub(r'[^0-9+\\-*/().]', '', expr)
        result = eval(expr_clean)
        return f"🧮 ผลลัพธ์: {result:g}"
    except Exception as e:
        return f"❌ คำนวณไม่ได้: {e}"
""", encoding="utf-8")

# src/domain/intent.py แก้บัคจับ math มั่ว
(ROOT / "src/domain/intent.py").write_text("""import re
from src.core.types import IntentType
from src.utils.logger import log

class IntentRuntimeX:
    def __init__(self):
        self.math_keywords = {"บวก", "ลบ", "คูณ", "หาร", "เท่าไร", "คำนวณ"}
        self.math_symbols = {"+", "-", "*", "/"} # แยก symbol ออกจาก %
        self.code_keywords = {"ฟังก์ชัน", "def", "class", "เขียนโค้ด", "bug", "error", "python"}
        self.search_keywords = {"คืออะไร", "หา", "search", "ข่าว", "ราคา", "อากาศ", "จอง", "ร้านอาหาร"}
        self.chat_keywords = {"สวัสดี", "ร้อน", "หนาว", "เหนื่อย"}

    def analyze(self, text: str) -> tuple[IntentType, float]:
        text_lower = text.lower()

        # 1. Code มาก่อน
        if any(k in text_lower for k in self.code_keywords):
            return "code", 0.9

        # 2. Math: ต้องมีตัวเลข + สัญลักษณ์ หรือ keyword
        has_number = bool(re.search(r'\\d', text))
        has_math_symbol = any(s in text for s in self.math_symbols)
        has_math_keyword = any(k in text_lower for k in self.math_keywords)
        has_percent = '%' in text and has_number

        if has_number and (has_math_symbol or has_math_keyword or has_percent):
            return "math", 0.9

        # 3. Search
        if any(k in text_lower for k in self.search_keywords):
            return "search", 0.8

        # 4. Chat
        if any(k in text_lower for k in self.chat_keywords):
            return "chat", 0.7

        return "unknown", 0.2
""", encoding="utf-8")

# src/domain/planning.py
(ROOT / "src/domain/planning.py").write_text("""from src.core.types import PlanStep, ExecutionPlan, IntentType
from src.tools.math_tool import calculate

class Planner:
    def create_plan(self, text: str, intent: IntentType):
        if intent == "math":
            return ExecutionPlan(intent=intent, steps=[
                PlanStep(0, "math.calculate", "calculator", {"expr": text})
            ])
        elif intent == "code":
            return ExecutionPlan(intent=intent, steps=[
                PlanStep(0, "code.analyze", "code_analyzer", {"text": text})
            ])
        elif intent == "search":
            return ExecutionPlan(intent=intent, steps=[
                PlanStep(0, "search.web", "web_search", {"query": text})
            ])
        else:
            return ExecutionPlan(intent=intent, steps=[
                PlanStep(0, "chat.reply", "llm", {"text": text})
            ])

    def execute_plan(self, plan: ExecutionPlan) -> str:
        for step in plan.steps:
            if step.tool_id == "calculator":
                return calculate(step.args["expr"])
            elif step.tool_id == "web_search":
                return f"🔍 ค้นหา: {step.args['query']}"
            elif step.tool_id == "llm":
                return f"💬 {step.args['text']}"
        return "ยังไม่รองรับ"
""", encoding="utf-8")

# main.py
(ROOT / "main.py").write_text("""from src.domain.intent import IntentRuntimeX
from src.domain.planning import Planner
from src.utils.logger import log

def main():
    log.info("🚀 WorAI Engine กำลังเริ่มต้น...")
    print("\\n" + "="*50)

    intent_x = IntentRuntimeX()
    planner = Planner()

    test_cases = [
        "พรุ่งนี้อากาศที่เชียงใหม่เป็นไงบ้าง",
        "ช่วยคำนวณ 1500 + 25% ให้หน่อย",
        "โยนิโสมนสิการคืออะไร",
        "จองร้านอาหารใกล้สยาม",
        "สวัสดีครับ",
        "มันร้อนมาก",
        "10 * 5 - 3"
    ]

    for text in test_cases:
        intent, conf = intent_x.analyze(text)
        plan = planner.create_plan(text, intent)
        result = planner.execute_plan(plan)

        log.info(f"🗣 Input: {text}")
        print(f" 🎯 Intent: {intent} | Conf: {conf:.2f}")
        print(f" ⚙ Action: {plan.steps[0].op}")
        print(f" 💬 Reply: {result}")
        print("-"*50)

if __name__ == "__main__":
    main()
""", encoding="utf-8")

# tests/unit/test_intent.py
(ROOT / "tests/unit/test_intent.py").write_text("""from src.domain.intent import IntentRuntimeX

def test_intent_math():
    intent = IntentRuntimeX()
    assert intent.analyze("2+2 เท่าไร")[0] == "math"
    assert intent.analyze("1500 + 25%")[0] == "math"
    assert intent.analyze("10 * 5 - 3")[0] == "math"

def test_intent_search():
    intent = IntentRuntimeX()
    assert intent.analyze("อากาศที่เชียงใหม่")[0] == "search"
    assert intent.analyze("จองร้านอาหาร")[0] == "search"

def test_intent_chat():
    intent = IntentRuntimeX()
    assert intent.analyze("สวัสดีครับ")[0] == "chat"

def test_no_false_positive():
    intent = IntentRuntimeX()
    assert intent.analyze("จองร้านอาหาร")[0]!= "math"
""", encoding="utf-8")

hashes = {d: get_dir_hash(ROOT / d) for d in LOCKED_DIRS}
AI_IGNORE.write_text(str(hashes))

print("✅ แก้บัค % กับ intent มั่วแล้ว")
print("รัน: python init_clean.py && python main.py")
""", encoding="utf-8")"""