from typing import Dict, Any, List
from src.core.types import RouteDecision
from src.tools.registry import ToolRegistry
from src.tools.llm_handler import call_llm
from src.utils import get_logger
from config import settings

class ExecutionPlanner:
    def __init__(self, tools: ToolRegistry):
        self.logger = get_logger("ExecutionPlanner")
        self.tools = tools

        # map พารามิเตอร์จาก router -> tool
        self.param_map = {
            "qa_factual": {"query": ["query", "raw_text"]},
            "qa_opinion": {"topic": ["topic", "raw_text"]},
            "qa_comparative": {"items": ["items", "raw_text"]},
            "qa_analytical": {"topic": ["topic", "raw_text"]},
            "qa_calculation": {"query": ["query", "raw_text"]},
            "qa_logic": {"query": ["query", "raw_text"]},
            "search_web": {"query": ["query", "raw_text"]},
            "search_knowledge": {"query": ["query", "raw_text"]},
            "search_history": {"query": ["query", "raw_text"]},
            "search_news": {"query": ["query", "raw_text"]},
            "compute_simple": {"expression": ["expression", "raw_text"]},
            "compute_advanced": {"expression": ["expression", "raw_text"]},
            "compute_currency": {"raw_text": ["raw_text"]},
            "compute_unit": {"raw_text": ["raw_text"]},
            "workflow_action": {"task": ["task", "title", "raw_text"]},
            "workflow_update": {"task_id": ["task_id"], "update": ["update", "raw_text"]},
            "workflow_status": {"task_id": ["task_id", "raw_text"]},
            "workflow_assign": {"task_id": ["task_id"], "assignee": ["assignee"]},
            "send_communicate": {"message": ["message", "raw_text"], "to": ["to"]},
            "send_schedule": {"title": ["title", "raw_text"], "time": ["time"]},
            "send_reminder": {"message": ["message", "raw_text"], "time": ["time"]},
            "send_email": {"message": ["message", "raw_text"], "to": ["to"]},
            "send_line": {"message": ["message", "raw_text"], "to": ["to"]},
            "doc_summarize": {"file_path": ["file_path", "raw_text"]},
            "doc_extract": {"file_path": ["file_path"], "field": ["field"]},
            "doc_translate": {"file_path": ["file_path"], "lang": ["lang"]},
            "doc_create": {"content": ["content", "raw_text"], "format": ["format"]},
            "data_chart": {"data": ["data"], "type": ["type"]},
            "data_table": {"data": ["data"]},
            "data_export": {"data": ["data"], "format": ["format"]},
            "code_explain": {"code": ["code", "raw_text"]},
            "code_generate": {"description": ["description", "raw_text"], "language": ["language"]},
            "code_debug": {"error_log": ["error_log", "raw_text"]},
            "code_refactor": {"code": ["code", "raw_text"]},
            "help_guide": {"query": ["query", "raw_text"]},
            "system_capabilities": {"query": ["query", "raw_text"]},
            "system_privacy": {"query": ["query", "raw_text"]},
            "name_numerology": {"name": ["name", "raw_text"]},
            "astrology_analysis": {
                "birth_date": ["birth_date", "raw_text"],
                "birth_time": ["birth_time", "raw_text"],
                "birth_place": ["birth_place", "raw_text"],
                "gender": ["gender", "raw_text"],
                "raw_text": ["raw_text"],
            },
            "qa_tax_calculation": {"raw_text": ["raw_text"]},
            "knowledge_synthesize": {"raw_text": ["raw_text"]},
        }

        # ลำดับความสำคัญ tool สำหรับแต่ละ intent
        self.tool_priority = {
            "qa_factual": ['fact_retriever'],
            "qa_comparative": ['comparator'],
            "qa_analytical": ['analyzer'],
            "qa_calculation": ['math'],
            "qa_logic": ['logic'],
            "search_web": ['web_search'],
            "search_knowledge": ['fact_retriever'],
            "search_history": ['history_search'],
            "search_news": ['web_search'],
            "compute_simple": ['math'],
            "compute_advanced": ['math_advanced'],
            "compute_currency": ['math'],
            "compute_unit": ['math'],
            "workflow_action": ['workflow_executor'],
            "workflow_update": ['workflow_executor'],
            "workflow_status": ['workflow_executor'],
            "workflow_assign": ['workflow_executor'],
            "send_communicate": ['action_executor'],
            "send_schedule": ['calendar'],
            "send_reminder": ['reminder'],
            "send_email": ['action_executor'],
            "send_line": ['action_executor'],
            "doc_summarize": ['file_parser'],
            "doc_extract": ['file_parser'],
            "doc_translate": ['translator'],
            "doc_create": ['doc_generator'],
            "data_chart": ['chart_generator'],
            "data_table": ['table_generator'],
            "data_export": ['exporter'],
            "qa_opinion": [],
            "qa_philosophical": [],
            "search_recipe": [],
            "code_explain": [],
            "code_generate": [],
            "code_debug": [],
            "code_refactor": [],
            "help_guide": ['fact_retriever'],
            "system_capabilities": ['fact_retriever'],
            "system_privacy": ['fact_retriever'],
            "name_numerology": ['name_analyzer'],
            "astrology_analysis": ['astrology_analyzer'],
            "qa_tax_calculation": ['tax_calculator'],
            "knowledge_synthesize": ['knowledge_synthesizer'],
            "personality_joke": [],
        }

    def _map_params(self, route_params: Dict, intent_code: str) -> Dict:
        """แปลง params จาก router ให้ตรงกับ tool"""
        mapping = self.param_map.get(intent_code, {})
        result = {}
        for desired_key, source_keys in mapping.items():
            for src in source_keys:
                if src in route_params and route_params[src]:
                    result[desired_key] = route_params[src]
                    break

        # fallback: ถ้าไม่มีอะไรเลย ใส่ raw_text
        if not result and "raw_text" in route_params:
            raw = route_params["raw_text"]
            # ใส่ทุก field ที่ tool อาจต้องการ
            for key in ["query", "expression", "message", "task", "topic", "items", "code", "description"]:
                result[key] = raw
        return result

    def _format_output(self, intent_code: str, result: Dict) -> Dict:
        """แยก output ตาม output_schema ของแต่ละ intent"""
        # Core
        if intent_code in ["greeting", "farewell", "gratitude", "personality_chat"]:
            return {"response": result.get("response", "รับทราบครับ")}
        if intent_code == "escalate_handoff":
            return {"message": result.get("message", "กำลังส่งต่อให้เจ้าหน้าที่ครับ")}
        if intent_code == "clarify":
            return {"question": result.get("question", "ช่วยระบุเพิ่มเติมได้ไหมครับ")}

        # QA
        if intent_code == "qa_factual":
            return {"answer": result.get("answer", result.get("response", "")), "source": result.get("source", "internal_kb")}
        if intent_code == "qa_opinion":
            return {"opinion": result.get("opinion", result.get("response", "")), "reasons": result.get("reasons", "")}
        if intent_code == "qa_comparative":
            return {"compare_table": result.get("compare_table", ""), "summary": result.get("summary", result.get("response", ""))}
        if intent_code == "qa_analytical":
            return {"analysis": result.get("analysis", result.get("response", "")), "insight": result.get("insight", "")}
        if intent_code == "qa_calculation":
            return {"result": result.get("result", ""), "formula": result.get("formula", "")}
        if intent_code == "qa_logic":
            return {"reasoning": result.get("reasoning", ""), "conclusion": result.get("conclusion", "")}
        if intent_code == "qa_philosophical":
            return {"reflection": result.get("response", "")}

        # Search
        if intent_code == "search_web":
            return {"links": result.get("links", ""), "snippet": result.get("snippet", result.get("response", ""))}
        if intent_code == "search_knowledge":
            return {"answer": result.get("answer", result.get("response", "")), "source": result.get("source", "internal_kb")}
        if intent_code == "search_history":
            return {"conversations": result.get("conversations", "")}
        if intent_code == "search_news":
            return {"news_items": result.get("news_items", result.get("response", ""))}
        if intent_code == "search_recipe":
            return {"recipe": result.get("response", "")}

        # Compute
        if intent_code in ["compute_simple", "compute_advanced", "compute_currency", "compute_unit"]:
            return {"result": result.get("result", ""), "steps": result.get("steps", "")}

        # Workflow
        if intent_code == "workflow_action":
            return {"task_id": result.get("task_id", "")}
        if intent_code == "workflow_update":
            return {"status": result.get("status", result.get("response", ""))}
        if intent_code == "workflow_status":
            return {"status": result.get("status", ""), "details": result.get("details", "")}
        if intent_code == "workflow_assign":
            return {"assignee": result.get("assignee", ""), "task_id": result.get("task_id", "")}

        # Communication
        if intent_code in ["send_communicate", "send_email", "send_line"]:
            return {"status": result.get("status", result.get("response", ""))}
        if intent_code == "send_schedule":
            return {"event_id": result.get("event_id", ""), "time": result.get("time", "")}
        if intent_code == "send_reminder":
            return {"reminder_id": result.get("reminder_id", "")}

        # Document
        if intent_code == "doc_summarize":
            return {"summary": result.get("summary", result.get("response", ""))}
        if intent_code == "doc_extract":
            return {"data": result.get("data", "")}
        if intent_code == "doc_translate":
            return {"translated_text": result.get("translated_text", "")}
        if intent_code == "doc_create":
            return {"file_url": result.get("file_url", "")}

        # Data
        if intent_code == "data_chart":
            return {"chart_url": result.get("chart_url", "")}
        if intent_code == "data_table":
            return {"table": result.get("table", "")}
        if intent_code == "data_export":
            return {"file_url": result.get("file_url", "")}

        # Code
        if intent_code == "code_explain":
            return {"explanation": result.get("explanation", result.get("response", ""))}
        if intent_code == "code_generate":
            return {"code": result.get("code", result.get("response", ""))}
        if intent_code == "code_debug":
            return {"fix_suggestion": result.get("response", "")}
        if intent_code == "code_refactor":
            return {"refactored_code": result.get("response", "")}

        # System
        if intent_code == "help_guide":
            return {"help_text": result.get("answer", result.get("response", ""))}
        if intent_code == "system_capabilities":
            return {"capabilities": result.get("answer", result.get("response", ""))}
        if intent_code == "system_privacy":
            return {"privacy_info": result.get("answer", result.get("response", ""))}
        if intent_code == "system_time":
            from datetime import datetime
            return {"current_time": datetime.now().strftime("%H:%M:%S")}
        if intent_code == "system_status":
            return {"status_report": "ระบบทำงานปกติ 🟢 ทุกโมดูลพร้อมใช้งาน"}

        # Personality
        if intent_code == "personality_joke":
            return {"joke": result.get("response", "")}
        if intent_code == "personality_change":
            return {"status": "รับทราบครับ ผมจะปรับบุคลิกตามที่คุณต้องการ"}

        # Numerology
        if intent_code == "name_numerology":
            return {
                "full_name": result.get("full_name", ""),
                "first_name": result.get("first_name", {}),
                "surname": result.get("surname", {}),
                "grand_total": result.get("grand_total", ""),
                "reduction_chain": result.get("reduction_chain", []),
                "number_meanings": result.get("number_meanings", {}),
                "summary": result.get("summary", ""),
            }

        # Astrology
        if intent_code == "astrology_analysis":
            p1 = result.get("person1", {})
            return {
                "bazi": p1.get("bazi", {}),
                "western": p1.get("western", {}),
                "vedic": p1.get("vedic", {}),
                "harmony": p1.get("harmony", {}),
                "synastry": result.get("synastry", {}),
                "input": result.get("input", {}),
                "sinsae_reading": result.get("sinsae_reading", ""),
            }
        if intent_code == "qa_tax_calculation":
            return {
                "tax_payable": result.get("tax_payable", ""),
                "net_income": result.get("net_income", ""),
                "breakdown": result.get("breakdown", []),
                "summary": result.get("summary", ""),
            }
        if intent_code == "knowledge_synthesize":
            return {
                "summary": result.get("summary", ""),
                "new_rules_count": result.get("new_rules_count", 0),
                "file_path": result.get("file_path", ""),
                "insight": result.get("insight", ""),
            }

        # default
        return {"response": result.get("response", str(result))}

    def execute(self, route: RouteDecision) -> Dict[str, Any]:
        """รัน intent ตาม route"""
        # 1. ต้องถามเพิ่ม
        if route.needs_clarification or route.intent_code == "clarify":
            return {
                "status": "clarify",
                "message": route.clarification_question or "ขอข้อมูลเพิ่มเติมหน่อยครับ"
            }

        # 2. ทักทาย / direct response (Phase 1: Early Exit for greetings)
        if route.route_type in ["direct", "response"]:
            # Handle greeting responses directly
            if route.intent_code == "greeting" and "response" in route.params:
                return {
                    "status": "ready",
                    "response": route.params["response"],
                    "needs_llm": False
                }
            res = self._format_output(route.intent_code, {})
            return {
                "status": "ready",
                **res,
                "needs_llm": False
            }

        # 3. ส่งต่อให้คน
        if route.route_type == "human_handoff":
            return {
                "status": "ready",
                "response": "👤 รับทราบครับ กำลังส่งต่อให้เจ้าหน้าที่ดูแล ครู่หนึ่งนะครับ"
            }

        # 4. LLM ล้วน
        if route.route_type == "llm_summary":
            mode_map = {
                "qa_opinion": "opinion",
                "qa_philosophical": "opinion",
                "search_recipe": "summary",
                "code_explain": "summary",
                "code_generate": "summary",
                "code_debug": "analysis",
                "code_refactor": "summary",
                "personality_joke": "opinion"
            }
            mode = mode_map.get(route.intent_code, "opinion")
            topic = route.params.get("raw_text", "")
            llm_res = call_llm(topic, mode=mode)

            if llm_res.get("success"):
                return {
                    "status": "ready",
                    "intent": route.intent_code,
                    **self._format_output(route.intent_code, llm_res),
                    "needs_llm": False
                }
            return {"status": "error", "message": llm_res.get("error", "LLM error")}

        # 5. เรียก tool ตาม priority
        tools_to_run = self.tool_priority.get(route.intent_code, route.tools_to_call)
        if not tools_to_run:
            return {
                "status": "error",
                "message": f"Intent {route.intent_code} ยังไม่ได้ต่อ tool ไว้ครับ"
            }

        results = {}
        mapped = self._map_params(route.params, route.intent_code)
        last_error = "No tools executed"

        self.logger.info(f"🚀 Executing {route.intent_code} with tools: {tools_to_run}")

        for tool in tools_to_run:
            self.logger.info(f"🔧 Calling tool: {tool}")
            res = self.tools.call(tool, **mapped)
            results[tool] = res

            if res.get("success"):
                # ถ้าเป็น tool_then_llm ต้องเอา result ไปให้ LLM สรุปต่อ
                if route.route_type == "tool_then_llm":
                    llm_res = call_llm(str(res), mode="summary")
                    if llm_res.get("success"):
                        res.update(llm_res)
                        res["success"] = True

                return {
                    "status": "ready",
                    "intent": route.intent_code,
                    **self._format_output(route.intent_code, res),
                    "tool_results": results,
                    "needs_llm": False
                }
            else:
                last_error = res.get('error', 'Unknown error')
                self.logger.warning(f"⚠ Tool {tool} failed: {last_error}")

        return {
            "status": "error",
            "message": f"ทำงานไม่สำเร็จ: {last_error}",
            "tool_results": results
        }
