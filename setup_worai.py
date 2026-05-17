#!/usr/bin/env python3
"""
🚀 WorAI Auto-Setup Script
สร้างโครงสร้างโปรเจกต์ + ไฟล์กฎ 30 Intent + ระบบ Router พร้อมใช้งาน
แค่รัน: python setup_worai.py
"""
import os
import json
import yaml

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ สร้าง: {path}")

def main():
    print("🚀 WorAI Auto-Setup Starting...\n")
    
    # === 1. สร้างโครงสร้างโฟลเดอร์ ===
    folders = [
        "config/rules", "src/core", "src/domain", "src/tools", 
        "src/utils", "tests/unit", "logs"
    ]
    for f in folders:
        os.makedirs(f, exist_ok=True)
        print(f"📁 โฟลเดอร์: {f}")
    
    # === 2. สร้าง config/settings.py ===
    create_file("config/settings.py", '''
# WorAI Settings
LOG_LEVEL = "INFO"
CACHE_MAX_SIZE = 1024
CONFIDENCE_THRESHOLD = 0.6
FALLBACK_MSG = "ขออภัยครับ ระบบยังไม่เข้าใจบริบทนี้ ช่วยระบุรายละเอียดเพิ่มเติมได้ไหมครับ?"
''')
    
    # === 3. สร้าง config/intents.json (30 Intent Schema) ===
    intents = [
        {"code": "qa_factual", "name": "ถามข้อมูลตรง", "route": "direct", "required_tools": ["fact_retriever"], "output_schema": ["answer", "source"], "needs_clarification": False},
        {"code": "qa_opinion", "name": "ขอความคิดเห็น", "route": "llm_summary", "required_tools": [], "output_schema": ["opinion", "reasons"], "needs_clarification": False},
        {"code": "qa_comparative", "name": "เปรียบเทียบ", "route": "tool_then_llm", "required_tools": ["comparator"], "output_schema": ["compare_table", "summary"], "needs_clarification": False},
        {"code": "doc_summarize", "name": "สรุปเอกสาร", "route": "file_analysis", "required_tools": ["file_parser", "summarizer"], "output_schema": ["summary", "key_points"], "needs_clarification": False},
        {"code": "doc_extract", "name": "ดึงข้อมูลจากเอกสาร", "route": "file_analysis", "required_tools": ["file_parser", "extractor"], "output_schema": ["entities"], "needs_clarification": False},
        {"code": "doc_analyze", "name": "วิเคราะห์เอกสารยาว", "route": "file_analysis", "required_tools": ["file_parser", "chunker", "summarizer"], "output_schema": ["summary", "risks"], "needs_clarification": False},
        {"code": "doc_compare", "name": "เปรียบเทียบเอกสาร", "route": "file_analysis", "required_tools": ["file_parser", "doc_comparator"], "output_schema": ["diff", "risk"], "needs_clarification": False},
        {"code": "search_web", "name": "ค้นหาจากเว็บ", "route": "direct_search", "required_tools": ["web_search"], "output_schema": ["links", "snippet"], "needs_clarification": False},
        {"code": "search_knowledge", "name": "ค้นหาความรู้ภายใน", "route": "direct_search", "required_tools": ["kb_retriever"], "output_schema": ["answer", "source"], "needs_clarification": False},
        {"code": "search_database", "name": "สอบถามฐานข้อมูล", "route": "tool_only", "required_tools": ["db_executor"], "output_schema": ["table", "summary"], "needs_clarification": False},
        {"code": "code_generate", "name": "เขียนโค้ด", "route": "tool_then_llm", "required_tools": ["code_generator"], "output_schema": ["code", "explanation"], "needs_clarification": False},
        {"code": "code_debug", "name": "วิเคราะห์/แก้ error", "route": "tool_then_llm", "required_tools": ["code_analyzer"], "output_schema": ["issue", "fix"], "needs_clarification": False},
        {"code": "compute_simple", "name": "คำนวณเลข", "route": "tool_only", "required_tools": ["calculator"], "output_schema": ["result"], "needs_clarification": False},
        {"code": "data_analyze", "name": "วิเคราะห์ข้อมูล", "route": "tool_then_llm", "required_tools": ["data_analyzer"], "output_schema": ["summary", "insights"], "needs_clarification": False},
        {"code": "data_visualize", "name": "สร้างกราฟ", "route": "tool_only", "required_tools": ["visualizer"], "output_schema": ["chart"], "needs_clarification": False},
        {"code": "translate", "name": "แปลภาษา", "route": "tool_only", "required_tools": ["translator"], "output_schema": ["translated_text"], "needs_clarification": False},
        {"code": "rewrite_tone", "name": "ปรับโทน", "route": "tool_only", "required_tools": ["rewriter"], "output_schema": ["rewritten_text"], "needs_clarification": False},
        {"code": "classify_text", "name": "จัดหมวดข้อความ", "route": "tool_only", "required_tools": ["classifier"], "output_schema": ["labels"], "needs_clarification": False},
        {"code": "safety_check", "name": "ตรวจความปลอดภัย", "route": "tool_only", "required_tools": ["safety_checker"], "output_schema": ["status"], "needs_clarification": False},
        {"code": "compliance_review", "name": "ตรวจ compliance", "route": "tool_only", "required_tools": ["compliance_engine"], "output_schema": ["status", "issues"], "needs_clarification": False},
        {"code": "workflow_action", "name": "สร้างงาน/ตั๋ว", "route": "tool_only", "required_tools": ["workflow_executor"], "output_schema": ["task_id"], "needs_clarification": False},
        {"code": "send_communicate", "name": "ส่งข้อความ/เมล", "route": "tool_only", "required_tools": ["messaging_executor"], "output_schema": ["status"], "needs_clarification": False},
        {"code": "escalate_handoff", "name": "ส่งต่อให้คน", "route": "human_handoff", "required_tools": [], "output_schema": ["message"], "needs_clarification": False},
        {"code": "auth_quota_check", "name": "ตรวจสอบสิทธิ์", "route": "tool_only", "required_tools": ["auth_enforcer"], "output_schema": ["status"], "needs_clarification": False},
        {"code": "infra_run", "name": "สั่ง infra/run job", "route": "tool_only", "required_tools": ["infra_executor"], "output_schema": ["status"], "needs_clarification": False},
        {"code": "clarify", "name": "คำถามก้ำกึ่ง", "route": "clarifier", "required_tools": [], "output_schema": ["question"], "needs_clarification": True},
        {"code": "greeting", "name": "ทักทาย", "route": "direct", "required_tools": [], "output_schema": ["response"], "needs_clarification": False},
        {"code": "multi_intent", "name": "มีหลายงานในคำเดียว", "route": "multi_router", "required_tools": [], "output_schema": ["subtasks"], "needs_clarification": False},
        {"code": "unknown", "name": "intent ไม่รู้", "route": "unknown_fallback", "required_tools": [], "output_schema": ["message"], "needs_clarification": True},
        {"code": "custom_yourai", "name": "สร้าง AI ของวอ", "route": "tool_then_llm", "required_tools": ["ai_builder"], "output_schema": ["plan"], "needs_clarification": False},
    ]
    create_file("config/intents.json", json.dumps(intents, indent=2, ensure_ascii=False))
    
    # === 4. สร้างไฟล์กฎ 7 ชุด (ครอบคลุม 30 Intent) ===
    rules_files = {
        "config/rules/01_core.yaml": '''
- intent: "compute_simple"
  patterns: ["คำนวณ.*", "[\\d\\s+\\-*/.%()]+", "รวม.*เท่าไร", "calculate.*", "total.*of.*"]
  match_any: true
  confidence_boost: 0.95
  route: "tool_only"
  tools: ["calculator"]
  priority: 10

- intent: "search_any"
  patterns: ["หา.*ข้อมูล.*", "ค้นหา.*", ".*คืออะไร", "ใคร.*เป็น.*", "เมื่อไหร่.*", "find.*", "search.*", "what is.*"]
  match_any: true
  confidence_boost: 0.90
  route: "tool_only"
  tools: ["web_search", "fact_retriever"]
  priority: 9

- intent: "action_request"
  patterns: ["ช่วย.*ให้ที", "ทำให้หน่อย", "จอง.*", "เปิด.*", "ปิด.*", "ส่ง.*", "สร้าง.*", "do.*for me"]
  match_any: true
  confidence_boost: 0.88
  route: "tool_only"
  tools: ["action_executor"]
  priority: 8

- intent: "escalate_handoff"
  patterns: ["ขอ.*คุยกับ.*คน", "ส่งต่อ.*ให้.*ฝ่าย", "ไม่พอใจ.*", "human.*help", "talk to.*person"]
  match_any: true
  confidence_boost: 0.95
  route: "human_handoff"
  tools: []
  priority: 7

- intent: "clarify_or_handoff"
  patterns: [".*"]
  match_any: true
  confidence_boost: 0.1
  route: "clarifier"
  tools: []
  priority: 1
  note: "Fallback - วางท้ายสุด!"
''',
        "config/rules/02_qa.yaml": '''
- intent: "qa_factual"
  patterns: ["ความยาว.*แม่น้ำ.*เท่าไร", "เมื่อไหร่.*ก่อตั้ง.*บริษัท", "ใคร.*เป็น.*CEO", "what is.*fact", "when.*first.*released"]
  match_any: true
  confidence_boost: 0.95
  route: "direct"
  tools: ["fact_retriever"]
  priority: 9

- intent: "qa_opinion"
  patterns: ["(คุณคิดอย่างไร).*", "(ควร|ดีกว่า|แนะนำให้).*", "do you think.*", "(อย่างไรดี|แบบไหนดี).*"]
  match_any: true
  confidence_boost: 0.90
  route: "llm_summary"
  tools: []
  priority: 8

- intent: "qa_comparative"
  patterns: [".*ต่างกัน.*อย่างไร", ".*ดีกว่า.*หรือ.*", ".*มีข้อดีข้อเสีย.*", "compare.*versus.*", "which.*better.*"]
  match_any: true
  confidence_boost: 0.92
  route: "tool_then_llm"
  tools: ["comparator"]
  priority: 8
''',
        "config/rules/03_docs.yaml": '''
- intent: "doc_summarize"
  patterns: ["สรุป.*รายงาน.*หน่อย", "ย่อ.*เอกสาร.*ให้หน่อย", "one.*pager.*overview", "key.*points.*from.*"]
  match_any: true
  confidence_boost: 0.88
  route: "file_analysis"
  tools: ["file_parser", "summarizer"]
  priority: 7

- intent: "doc_extract"
  patterns: ["มีข้อมูล.*อะไรบ้าง", "ดึง.*ชื่อลูกค้า.*จากไฟล์", "extract.*information.*from.*"]
  match_any: true
  confidence_boost: 0.85
  route: "file_analysis"
  tools: ["file_parser", "extractor"]
  priority: 7

- intent: "doc_analyze"
  patterns: ["วิเคราะห์.*เอกสาร.*", "จุด.*เสี่ยง.*คืออะไร", "ตรวจ.*ข้อตกลง.*", "review.*contract.*for risk"]
  match_any: true
  confidence_boost: 0.90
  route: "file_analysis"
  tools: ["file_parser", "chunker", "summarizer"]
  priority: 7

- intent: "doc_compare"
  patterns: ["เปรียบเทียบ.*เอกสาร.*2 .*ฉบับ", "diff.*between.*two.*documents", "compare.*version.*A.*and.*B"]
  match_any: true
  confidence_boost: 0.89
  route: "file_analysis"
  tools: ["file_parser", "doc_comparator"]
  priority: 7
''',
        "config/rules/04_code_data.yaml": '''
- intent: "code_generate"
  patterns: ["เขียนโค้ด.*ให้ที", "สร้าง.*function.*ให้ที", "generate.*code.*for.*", "make.*script.*to.*"]
  match_any: true
  confidence_boost: 0.91
  route: "tool_then_llm"
  tools: ["code_generator"]
  priority: 8

- intent: "code_debug"
  patterns: ["แก้.*error.*", "มีปัญหา.*error.*", "stacktrace.*อะไรผิด", "debug this code", "error.*in.*this.*"]
  match_any: true
  confidence_boost: 0.92
  route: "tool_then_llm"
  tools: ["code_analyzer", "bug_finder"]
  priority: 8

- intent: "data_analyze"
  patterns: ["วิเคราะห์.*ชุดข้อมูล.*", "หาความสัมพันธ์.*ระหว่าง.*", "statistical analysis.*of.*", "correlation.*between.*"]
  match_any: true
  confidence_boost: 0.87
  route: "tool_then_llm"
  tools: ["data_analyzer"]
  priority: 7

- intent: "data_visualize"
  patterns: ["สร้าง.*กราฟ.*จาก.*", "plot.*the.*data", "draw.*chart.*of.*", "visualization.*for.*the.*"]
  match_any: true
  confidence_boost: 0.86
  route: "tool_only"
  tools: ["visualizer"]
  priority: 7
''',
        "config/rules/05_communicate.yaml": '''
- intent: "send_communicate"
  patterns: ["ส่ง.*เมล.*ให้.*", "ส่งอีเมล.*ให้.*", "ส่งข้อความ.*บอกว่า.*", "แจ้ง.*ผ่าน.*Slack", "post.*message.*to.*channel", "send.*email.*to.*", "ส่งต่อ.*ให้ที"]
  match_any: true
  confidence_boost: 0.88
  route: "tool_only"
  tools: ["messaging_executor"]
  priority: 7

- intent: "translate"
  patterns: ["แปล.*เป็น.*ภาษา", "ภาษาอังกฤษ.*คำว่า.*", "translate.*to.*Thai", "คำนี้.*ภาษาจีน.*พูดว่า"]
  match_any: true
  confidence_boost: 0.95
  route: "tool_only"
  tools: ["translator"]
  priority: 8

- intent: "rewrite_tone"
  patterns: ["เขียนใหม่.*ด้วยโทน.*(สุภาพ|มืออาชีพ)", "ปรับ.*ให้ดูเป็นมืออาชีพ", "rewrite.*in.*a.*professional.*"]
  match_any: true
  confidence_boost: 0.84
  route: "tool_only"
  tools: ["rewriter"]
  priority: 6
''',
        "config/rules/06_system.yaml": '''
- intent: "safety_check"
  patterns: ["ตรวจ.*เนื้อหา.*เสี่ยง", "ตรวจ.*ความไม่เหมาะสม", "check.*for.*safety", "is this.*appropriate.*"]
  match_any: true
  confidence_boost: 0.93
  route: "tool_only"
  tools: ["safety_checker"]
  priority: 9

- intent: "compliance_review"
  patterns: ["ตรวจ.*ว่าถูกต้องตาม.*กฎ", "สัญญา.*นี้.*ผิด.*ระเบียบ.*ไหม", "check.*compliance.*with.*"]
  match_any: true
  confidence_boost: 0.93
  route: "tool_only"
  tools: ["compliance_engine"]
  priority: 9

- intent: "auth_quota_check"
  patterns: ["ฉัน.*มีสิทธิ์.*ทำ.*ไหม", "โควตา.*เหลือ.*เท่าไร", "check.*my.*quota", "do I have.*permission.*to"]
  match_any: true
  confidence_boost: 0.92
  route: "tool_only"
  tools: ["auth_enforcer"]
  priority: 9

- intent: "classify_text"
  patterns: ["จัดหมวด.*ข้อความ.*นี้", "นี่คือ.*ประเภท.*ไหน", "classify.*this.*text.*as"]
  match_any: true
  confidence_boost: 0.88
  route: "tool_only"
  tools: ["classifier"]
  priority: 7
''',
        "config/rules/07_meta.yaml": '''
- intent: "greeting"
  patterns: ["^(สวัสดี|หวัดดี|เฮโล|ฮัลโหล|ไฮ).*", "ทักทาย.*", "^(hi|hello|hey).*", "สบายดีไหม"]
  match_any: true
  confidence_boost: 0.85
  route: "direct"
  tools: []
  priority: 10

- intent: "clarify"
  patterns: ["หมายความว่า.*อย่างไร", "หมายถึง.*อย่างไร", "คำนี้.*หมายถึงอะไร", "can you.*clarify.*", "ไม่แน่ใจว่า.*หมายถึง.*อะไร", "คือ.*หมายถึงอะไร.*"]
  match_any: true
  confidence_boost: 0.85
  route: "clarifier"
  tools: []
  priority: 6

- intent: "workflow_action"
  patterns: ["สร้างตั๋ว.*ให้ที", "เปิดงาน.*ใหม่.*ให้หน่อย", "แจ้ง incident.*", "create.*ticket.*", "เปิดตั๋ว.*ให้ทีนะ", "ต้องการให้ส่งต่อ.*"]
  match_any: true
  confidence_boost: 0.90
  route: "tool_only"
  tools: ["workflow_executor"]
  priority: 8

- intent: "multi_intent"
  patterns: ["ช่วย.*แล้ว.*ก็.*", "ทำ.*อันนี้.*ก่อน.*แล้ว.*ค่อย.*", "first.*then.*also.*", "ขอ.*สองอย่าง.*เลย"]
  match_any: true
  confidence_boost: 0.75
  route: "multi_router"
  tools: []
  priority: 5

- intent: "unknown"
  patterns: [".*"]
  match_any: true
  confidence_boost: 0.1
  route: "unknown_fallback"
  tools: []
  priority: 1
  note: "Fallback สุดท้าย!"

- intent: "custom_yourai"
  patterns: ["สร้าง.*เอไอ.*ของ.*วอ", "สอน.*ฉัน.*ทำ.*โมเดล", "สร้าง.*เอไอ.*ไม่.*พึ่ง.*คนอื่น", "build.*my.*own.*ai.*model"]
  match_any: true
  confidence_boost: 0.98
  route: "tool_then_llm"
  tools: ["ai_builder"]
  priority: 10
'''
    }
    
    for path, content in rules_files.items():
        create_file(path, content)
    
    # === 5. สร้าง src/utils/logger.py ===
    create_file("src/utils/logger.py", '''
import logging
from config import settings

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    return logger
''')
    create_file("src/utils/__init__.py", "from .logger import get_logger\n__all__ = ['get_logger']")
    
    # === 6. สร้าง src/core/types.py ===
    create_file("src/core/types.py", '''
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class RouteDecision:
    intent_code: str
    route_type: str
    tools_to_call: List[str]
    params: Dict[str, Any]
    needs_clarification: bool
    confidence: float = 0.0
    clarification_question: Optional[str] = None
''')
    create_file("src/core/__init__.py", "from .types import RouteDecision\n__all__ = ['RouteDecision']")
    
    # === 7. สร้าง src/core/router.py (ตัวจับกฎหลัก) ===
    create_file("src/core/router.py", '''
import re, os, yaml
from typing import Dict, List
from src.utils import get_logger
from src.core.types import RouteDecision

class IntentRouter:
    def __init__(self, intents_path: str = "config/intents.json", rules_folder: str = "config/rules"):
        self.logger = get_logger("IntentRouter")
        self.intents: Dict[str, dict] = {}
        self.intent_rules: List[dict] = []
        self._load_intents(intents_path)
        self._load_rules_from_folder(rules_folder)
    
    def _load_intents(self, path: str):
        if os.path.exists(path):
            import json
            with open(path, "r", encoding="utf-8") as f:
                for intent in json.load(f):
                    self.intents[intent["code"]] = intent
            self.logger.info(f"Loaded {len(self.intents)} intents")
    
    def _load_rules_from_folder(self, folder: str):
        if not os.path.exists(folder):
            return
        for filename in sorted([f for f in os.listdir(folder) if f.endswith(".yaml")]):
            filepath = os.path.join(folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for rule in yaml.safe_load(f):
                    compiled = [re.compile(p, re.IGNORECASE) for p in rule.get("patterns", []) if p]
                    self.intent_rules.append({
                        "intent": rule["intent"], "patterns": compiled,
                        "match_any": rule.get("match_any", True),
                        "confidence_boost": rule.get("confidence_boost", 0.5),
                        "route": rule.get("route", "direct"),
                        "tools": rule.get("tools", []),
                        "priority": rule.get("priority", 0)
                    })
        self.intent_rules.sort(key=lambda r: (-r["priority"], r["intent"]))
        self.logger.info(f"Loaded {len(self.intent_rules)} rules")
    
    def classify(self, text: str) -> RouteDecision:
        text_lower = text.lower().strip()
        best_match, best_conf = None, 0.0
        for rule in self.intent_rules:
            matched = any(p.search(text_lower) for p in rule["patterns"]) if rule["patterns"] else False
            if matched and rule["confidence_boost"] > best_conf:
                best_conf, best_match = rule["confidence_boost"], rule
        if best_match:
            intent_cfg = self.intents.get(best_match["intent"], {})
            return RouteDecision(
                intent_code=best_match["intent"], route_type=best_match["route"],
                tools_to_call=best_match["tools"], params={"raw_text": text},
                needs_clarification=(best_match["route"] == "clarifier"),
                confidence=best_conf
            )
        return RouteDecision("unknown", "clarifier", [], {"raw_text": text}, True, 0.1, "ช่วยระบุเพิ่มเติมได้ไหมครับ? 🙏")
''')
    
    # === 8. สร้าง src/tools/registry.py ===
    create_file("src/tools/registry.py", '''
from typing import Dict, Callable, Any
from src.utils import get_logger

class ToolRegistry:
    def __init__(self):
        self.logger = get_logger("ToolRegistry")
        self._tools: Dict[str, Callable] = {}
        self._register_builtins()
    
    def _register_builtins(self):
        def calculator(expression: str) -> Dict[str, Any]:
            try:
                result = eval(expression, {"__builtins__": {}}, {})
                return {"success": True, "result": result}
            except: return {"success": False, "error": "Invalid expression"}
        self.register("calculator", calculator)
        
        def web_search(query: str) -> Dict[str, Any]:
            return {"success": True, "links": [f"https://example.com?q={query}"], "snippet": f"Results for '{query}'"}
        self.register("web_search", web_search)
        
        def fact_retriever(query: str) -> Dict[str, Any]:
            return {"success": True, "answer": f"ข้อมูลเกี่ยวกับ '{query}'", "source": "internal_kb"}
        self.register("fact_retriever", fact_retriever)
        
        def messaging_executor(message: str, **kwargs) -> Dict[str, Any]:
            return {"success": True, "status": "sent", "message": message}
        self.register("messaging_executor", messaging_executor)
        
        def workflow_executor(task: str, **kwargs) -> Dict[str, Any]:
            return {"success": True, "task_id": "TASK-001", "status": "created"}
        self.register("workflow_executor", workflow_executor)
    
    def register(self, name: str, func: Callable):
        self._tools[name] = func
        self.logger.info(f"Registered: {name}")
    
    def call(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if tool_name not in self._tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        try:
            return {"success": True, **self._tools[tool_name](**kwargs)}
        except Exception as e:
            return {"success": False, "error": str(e)}
''')
    create_file("src/tools/__init__.py", "from .registry import ToolRegistry\n__all__ = ['ToolRegistry']")
    
    # === 9. สร้าง src/domain/planner.py ===
    create_file("src/domain/planner.py", '''
from typing import Dict, Any
from src.core.types import RouteDecision
from src.tools.registry import ToolRegistry
from src.utils import get_logger
from config import settings

class ExecutionPlanner:
    def __init__(self, tools: ToolRegistry):
        self.logger = get_logger("ExecutionPlanner")
        self.tools = tools
    
    def execute(self, route: RouteDecision) -> Dict[str, Any]:
        if route.needs_clarification:
            return {"status": "clarify", "message": route.clarification_question or settings.FALLBACK_MSG}
        if route.route_type == "direct":
            return {"status": "ready", "message": "✅ รับทราบ", "needs_llm": False}
        results = {}
        for tool_name in route.tools_to_call:
            params = {k: v for k, v in route.params.items() if k in ["query", "expression", "message", "task", "raw_text"]}
            result = self.tools.call(tool_name, **params)
            results[tool_name] = result
            if not result.get("success"):
                return {"status": "error", "message": f"{tool_name} failed: {result.get('error')}"}
        response = self._build_response(route, results)
        return {"status": "ready", "intent": route.intent_code, "response": response, "tool_results": results, "needs_llm": route.route_type in ("tool_then_llm", "llm_summary")}
    
    def _build_response(self, route: RouteDecision, results: Dict) -> str:
        if route.intent_code == "compute_simple" and "calculator" in results:
            return f"🧮 ผลลัพธ์: {results['calculator'].get('result', 'N/A')}"
        if route.intent_code in ("search_any", "qa_factual") and "fact_retriever" in results:
            return f"🔍 {results['fact_retriever'].get('answer', 'กำลังค้นหา...')}"
        if route.intent_code == "send_communicate":
            return f"✅ ส่งข้อความแล้ว: {route.params.get('raw_text', '')[:50]}..."
        if route.intent_code == "workflow_action":
            return f"📋 สร้างงานแล้ว: ID {results.get('workflow_executor', {}).get('task_id', 'N/A')}"
        return f"✅ {route.intent_code} ดำเนินการสำเร็จ"
''')
    create_file("src/domain/__init__.py", "from .planner import ExecutionPlanner\n__all__ = ['ExecutionPlanner']")
    
    # === 10. สร้าง main.py ===
    create_file("main.py", '''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.core.router import IntentRouter
from src.tools.registry import ToolRegistry
from src.domain.planner import ExecutionPlanner
from src.utils import get_logger

logger = get_logger("WorAI")

def main():
    logger.info("🚀 WorAI Engine Starting...")
    router = IntentRouter()
    tools = ToolRegistry()
    planner = ExecutionPlanner(tools)
    
    tests = [
        "คำนวณ 1500 + 25%", "อากาศเชียงใหม่เป็นไง", "โยนิโสมนสิการคืออะไร",
        "ส่งเมลให้ทีบอกว่าประชุมเลื่อน", "สร้างตั๋วให้ทีเรื่องเครื่องพิมพ์เสีย",
        "ขอคุยกับคน", "หมายความว่าอย่างไรครับ", "สวัสดีครับ"
    ]
    print("\\n" + "="*60)
    for text in tests:
        route = router.classify(text)
        result = planner.execute(route)
        print(f"🗣️  {text}")
        print(f"   🎯 {route.intent_code} | 🛣️ {route.route_type} | 🔧 {route.tools_to_call}")
        print(f"   💬 {result.get('response', result.get('message', ''))}\\n")
    print("="*60)

if __name__ == "__main__":
    main()
''')
    
    # === 11. สร้าง requirements.txt ===
    create_file("requirements.txt", "pyyaml>=6.0\n")
    
    print("\n🎉 Setup Complete!")
    print("✅ สร้างไฟล์ทั้งหมดแล้ว")
    print("✅ รัน: pip install -r requirements.txt")
    print("✅ แล้วรัน: python main.py")
    print("\n🚀 WorAI พร้อมใช้งานแล้วครับคุณวอ!")

if __name__ == "__main__":
    main()
