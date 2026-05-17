from typing import Dict, Any
from src.utils import get_logger

logger = get_logger("LLMHandler")

def call_llm(prompt: str, mode: str = "opinion") -> Dict[str, Any]:
    """
    Mock LLM - ของจริงต้องต่อ OpenAI/Claude/MetaAI API
    mode: opinion | summary | analysis
    """
    logger.info(f"LLM call mode={mode}, prompt={prompt[:100]}...")

    if mode == "opinion":
        return {
            "success": True,
            "opinion": f"ความคิดเห็นต่อ '{prompt}': โดยรวมมีทั้งข้อดีและข้อเสีย ขึ้นอยู่กับบริบทการใช้งาน",
            "reasons": "- ข้อดี: ช่วยประหยัดเวลา เพิ่มประสิทธิภาพ\n- ข้อเสีย: อาจมีค่าใช้จ่าย ต้องเรียนรู้\n- สรุป: ควรพิจารณาความจำเป็นและงบประมาณ"
        }

    elif mode == "summary":
        # ถ้า prompt เป็น dict ของ tool result
        if prompt.startswith("{") and "'success': True" in prompt:
            return {
                "success": True,
                "summary": "จากข้อมูลที่ได้ สรุปว่าแต่ละตัวมีจุดเด่นต่างกัน ควรเลือกตามการใช้งาน",
                "response": "จากข้อมูลที่ได้ สรุปว่าแต่ละตัวมีจุดเด่นต่างกัน ควรเลือกตามการใช้งาน"
            }
        return {
            "success": True,
            "summary": f"สรุปจากข้อมูล: {prompt[:150]}...",
            "response": f"สรุปจากข้อมูล: {prompt[:150]}..."
        }

    elif mode == "analysis":
        return {
            "success": True,
            "analysis": f"วิเคราะห์ '{prompt}': พบแนวโน้มหลายด้าน",
            "insight": "- ปัจจัยหลัก:...\n- ผลกระทบ:...\n- ข้อเสนอแนะ:..."
        }

    else:
        return {
            "success": False,
            "error": f"Unknown LLM mode: {mode}. Use: opinion, summary, analysis"
        }