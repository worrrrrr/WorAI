from typing import Dict, Any, Callable, List, Tuple
from src.utils import get_logger
import inspect

logger = get_logger("ToolRegistry")

class ToolRegistry:
    _instance = None
    _initialized = False

    def __new__(cls):
        # Singleton: สร้าง instance ครั้งเดียวทั้งโปรเจค
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # กัน init ซ้ำ ถ้าเคยสร้างแล้วให้ออกเลย
        if ToolRegistry._initialized:
            return
        ToolRegistry._initialized = True

        self.tools: Dict[str, Callable] = {}
        self._tool_modules: Dict[str, Tuple[str, str]] = {}
        self.logger = logger
        self._register_tool_mappings()

    def _register_tool_mappings(self):
        # เก็บ mapping ไว้ก่อน ยังไม่ import (lazy loading)
        self._tool_modules = {
            "math": ("src.tools.math", "tool_math"),
            "fact_retriever": ("src.tools.fact_retriever", "tool_fact_retriever"),
            "web_search": ("src.tools.search", "tool_web_search"),
            "action_executor": ("src.tools.action", "tool_action_executor"),
            "workflow_executor": ("src.tools.workflow", "tool_workflow_executor"),
            "logic": ("src.tools.logic", "tool_logic"),
            "comparator": ("src.tools.comparator", "tool_comparator"),
            "llm_handler": ("src.tools.llm_handler", "call_llm"),
            "math_advanced": ("src.tools.math_advanced", "tool_math_advanced"),
            "analyzer": ("src.tools.analyzer", "tool_analyzer"),
            "file_parser": ("src.tools.file_parser", "tool_file_parser"),
            "doc_generator": ("src.tools.doc_generator", "tool_doc_generator"),
            "translator": ("src.tools.translator", "tool_translator"),
            "chart_generator": ("src.tools.chart_generator", "tool_chart_generator"),
            "table_generator": ("src.tools.table_generator", "tool_table_generator"),
            "exporter": ("src.tools.exporter", "tool_exporter"),
            "name_analyzer": ("src.tools.name_analyzer", "tool_name_analyzer"),
            "astrology_analyzer": ("src.tools.astrology_analyzer", "tool_astrology_analyzer"),
            "tax_calculator": ("src.tools.tax_calculator", "tool_tax_calculator"),
            "knowledge_synthesizer": ("src.tools.knowledge_synthesizer", "tool_knowledge_synthesizer"),
        }
        self.logger.info(f"✅ Registered tool mappings for {len(self._tool_modules)} tools")

    def _load_tool(self, tool_name: str) -> bool:
        """Load tool แบบ lazy เมื่อต้องการใช้"""
        if tool_name in self.tools:
            return True
        
        if tool_name not in self._tool_modules:
            self.logger.warning(f"Tool {tool_name} not in mappings")
            return False
        
        try:
            module_path, func_name = self._tool_modules[tool_name]
            mod = __import__(module_path, fromlist=[func_name])
            func = getattr(mod, func_name)
            self.register(tool_name, func)
            return True
        except Exception as e:
            self.logger.warning(f"{tool_name} not loaded: {e}")
            return False

    def _auto_register_all(self):
        # เก็บไว้สำหรับ backward compatibility หรือ debug
        for tool_name in list(self._tool_modules.keys()):
            self._load_tool(tool_name)
        self.logger.info(f"✅ Registered {len(self.tools)} tools: {list(self.tools.keys())}")

    def register(self, name: str, func: Callable):
        self.tools[name] = func
    #   self.logger.info(f"🔌 Registered: {name}")

    def call(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if not tool_name:
            return {"success": False, "error": "Tool name is empty or None"}

        # Lazy load tool ถ้ายังไม่ได้โหลด
        if tool_name not in self.tools:
            if not self._load_tool(tool_name):
                self.logger.error(f"Tool {tool_name} not found in registry")
                return {"success": False, "error": f"Tool {tool_name} not found"}

        try:
            func = self.tools[tool_name]
            sig = inspect.signature(func)

            has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())

            # กรองเฉพาะ param ที่ function รับได้
            if has_kwargs:
                valid_kwargs = kwargs
            else:
                valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

            # Fallback: ถ้า function รับ 1 param และยังไม่มีค่า ให้ยัด raw_text/query เข้าไป
            if len(sig.parameters) == 1 and not valid_kwargs and not has_kwargs:
                param = list(sig.parameters.keys())[0]

                value = kwargs.get('raw_text') or kwargs.get('query') or kwargs.get('text') or str(kwargs)
                valid_kwargs = {param: value}

            result = func(**valid_kwargs)
            return result if isinstance(result, dict) else {"success": True, "result": result}

        except Exception as e:
            self.logger.error(f"Tool {tool_name} error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

    def has_tool(self, name: str) -> bool:
        return name in self.tools