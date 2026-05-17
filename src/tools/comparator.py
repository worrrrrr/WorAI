from typing import Dict, Any, List
import re
from src.utils import get_logger

logger = get_logger("Comparator")

def tool_comparator(items: str) -> Dict[str, Any]:
    """
    เปรียบเทียบ 2-3 อย่าง เช่น "iPhone vs Samsung"
    Output: compare_table, summary
    """
    logger.info(f"Comparing: {items}")

    # แยกคำด้วย vs, กับ, เทียบ, และ
    parts = re.split(r'\s+(?:vs|versus|กับ|เทียบกับ|เปรียบเทียบ|และ)\s+', items, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]

    # ลบคำว่า "เปรียบเทียบ" ออกจากหัว
    if parts and parts[0].lower().startswith(('เปรียบเทียบ', 'เทียบ')):
        parts[0] = re.sub(r'^(เปรียบเทียบ|เทียบ)\s*', '', parts[0], flags=re.IGNORECASE).strip()

    if len(parts) < 2:
        return {
            "success": False,
            "error": "ต้องมีอย่างน้อย 2 อย่างให้เทียบ เช่น 'A vs B'"
        }

    if len(parts) > 3:
        parts = parts[:3] # เอาแค่ 3 อันแรก

    # สร้างตาราง markdown
    headers = " | ".join(parts)
    separator = " | ".join(["---"] * len(parts))

    rows = [
        f"| ราคา | ต้องค้นข้อมูลเพิ่ม | ต้องค้นข้อมูลเพิ่ม |",
        f"| ข้อดี | ต้องค้นข้อมูลเพิ่ม | ต้องค้นข้อมูลเพิ่ม |",
        f"| ข้อเสีย | ต้องค้นข้อมูลเพิ่ม | ต้องค้นข้อมูลเพิ่ม |",
        f"| เหมาะกับ | ต้องค้นข้อมูลเพิ่ม | ต้องค้นข้อมูลเพิ่ม |"
    ]

    # ปรับแถวตามจำนวน items
    if len(parts) == 3:
        rows = [row + " | ต้องค้นข้อมูลเพิ่ม |" for row in rows]

    table = f"| หัวข้อ | {headers} |\n| {separator} |\n" + "\n".join(rows)

    return {
        "success": True,
        "type": "comparative",
        "compare_table": table,
        "summary": f"เปรียบเทียบเบื้องต้นระหว่าง {' กับ '.join(parts)} - ต้องค้นข้อมูลจริงเพิ่ม",
        "items": parts
    }