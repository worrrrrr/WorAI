# src/core/types.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

# ✅ เพิ่ม IntentType เพื่อแก้ ImportError
class IntentType(Enum):
    QA_FACTUAL = "qa_factual"
    QA_OPINION = "qa_opinion"
    QA_COMPARATIVE = "qa_comparative"
    DOC_SUMMARIZE = "doc_summarize"
    DOC_EXTRACT = "doc_extract"
    DOC_ANALYZE = "doc_analyze"
    DOC_COMPARE = "doc_compare"
    SEARCH_WEB = "search_web"
    SEARCH_KNOWLEDGE = "search_knowledge"
    SEARCH_DATABASE = "search_database"
    CODE_GENERATE = "code_generate"
    CODE_DEBUG = "code_debug"
    COMPUTE_SIMPLE = "compute_simple"
    DATA_ANALYZE = "data_analyze"
    DATA_VISUALIZE = "data_visualize"
    TRANSLATE = "translate"
    REWRITE_TONE = "rewrite_tone"
    CLASSIFY_TEXT = "classify_text"
    SAFETY_CHECK = "safety_check"
    COMPLIANCE_REVIEW = "compliance_review"
    WORKFLOW_ACTION = "workflow_action"
    SEND_COMMUNICATE = "send_communicate"
    ESCALATE_HANDOFF = "escalate_handoff"
    AUTH_QUOTA_CHECK = "auth_quota_check"
    INFRA_RUN = "infra_run"
    CLARIFY = "clarify"
    GREETING = "greeting"
    MULTI_INTENT = "multi_intent"
    UNKNOWN = "unknown"
    CUSTOM_YOURAI = "custom_yourai"

@dataclass
class RouteDecision:
    intent_code: str
    route_type: str
    tools_to_call: List[str]
    params: Dict[str, Any]
    needs_clarification: bool
    confidence: float = 0.0
    clarification_question: Optional[str] = None