import json
from src.utils import get_logger

logger = get_logger("analyzer")

# พยายามใช้ LLM ถ้ามี ไม่งั้น fallback เป็น template
try:
    from src.tools.llm_handler import call_llm
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

def tool_analyzer(topic: str) -> dict:
    """
    วิเคราะห์หัวข้อแบบครบ: สาเหตุ, ผลกระทบ, แนวโน้ม, ข้อดีข้อเสีย
    """
    topic = topic.strip()
    try:
        if HAS_LLM:
            prompt = f"""วิเคราะห์หัวข้อ "{topic}" เป็นภาษาไทย
ตอบเป็น JSON เท่านั้น ห้ามมีข้อความอื่น:
{{"why": ["สาเหตุหลัก 2-3 ข้อ"], "impact": ["ผลกระทบ 2-3 ข้อ"], "trend": "แนวโน้มใน 1-2 ปี", "pros": ["ข้อดี 2 ข้อ"], "cons": ["ข้อเสีย 2 ข้อ"]}}"""
            raw = call_llm(prompt)
            # llm_handler อาจคืน dict หรือ str
            text = raw.get("result") if isinstance(raw, dict) else str(raw)
            data = json.loads(text)
        else:
            raise RuntimeError("LLM not available")

    except Exception as e:
        logger.warning(f"LLM fallback: {e}")
        # fallback ไม่ต้องพึ่งเน็ต
        data = {
            "why": [f"ความต้องการด้าน {topic} เพิ่มขึ้น", f"เทคโนโลยีสนับสนุน {topic}"],
            "impact": [f"เปลี่ยนวิธีทำงานเกี่ยวกับ {topic}", f"สร้างโอกาสใหม่"],
            "trend": f"{topic} มีแนวโน้มเติบโตต่อเนื่อง",
            "pros": ["เข้าใจง่าย", "ต่อยอดได้เร็ว"],
            "cons": ["ต้องเรียนรู้เพิ่ม", "อาจมีต้นทุนเริ่มต้น"]
        }

    return {
        "success": True,
        "topic": topic,
        "why": data.get("why", []),
        "impact": data.get("impact", []),
        "trend": data.get("trend", ""),
        "pros": data.get("pros", []),
        "cons": data.get("cons", []),
    }