"""
Thai Name Numerology and Semantic Analyzer for WorAI Engine.
Granular breakdown of Thai names into semantic components and full numerology reduction.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from src.tools.fact_retriever import tool_fact_retriever as rag_call

logger = logging.getLogger("NameAnalyzer")

# Numerology mapping
THAI_NUMEROLOGY_MAP = {
    "ก": 1, "ด": 1, "ท": 1, "ถ": 1, "ภ": 1, "ฤ": 1, "า": 1, "ุ": 1, "ำ": 1, "่": 1,
    "A": 1, "a": 1, "I": 1, "i": 1, "J": 1, "j": 1, "Q": 1, "q": 1, "Y": 1, "y": 1,
    "ข": 2, "ช": 2, "บ": 2, "ป": 2, "ง": 2, "เ": 2, "แ": 2, "ู": 2, "้": 2,
    "B": 2, "b": 2, "K": 2, "k": 2, "R": 2, "r": 2,
    "ฆ": 3, "ฑ": 3, "ฒ": 3, "ต": 3, "ฃ": 3, "๋": 3,
    "C": 3, "c": 3, "G": 3, "g": 3, "L": 3, "l": 3, "S": 3, "s": 3,
    "ค": 4, "ธ": 4, "ร": 4, "ญ": 4, "ษ": 4, "โ": 4, "ะ": 4, "ิ": 4, "์": 4,
    "D": 4, "d": 4, "M": 4, "m": 4, "T": 4, "t": 4,
    "ฉ": 5, "ณ": 5, "ฌ": 5, "น": 5, "ม": 5, "ห": 5, "ฮ": 5, "ฎ": 5, "ฬ": 5, "ึ": 5,
    "E": 5, "e": 5, "H": 5, "h": 5, "N": 5, "n": 5, "X": 5, "x": 5,
    "จ": 6, "ล": 6, "ว": 6, "อ": 6, "ใ": 6,
    "U": 6, "u": 6, "V": 6, "v": 6, "W": 6, "w": 6,
    "ศ": 7, "ส": 7, "ซ": 7, "ี": 7, "ื": 7, "๊": 7,
    "O": 7, "o": 7, "Z": 7, "z": 7,
    "ย": 8, "พ": 8, "ฟ": 8, "ผ": 8, "ฝ": 8, "ั": 8,
    "F": 8, "f": 8, "P": 8, "p": 8,
    "ฏ": 9, "ฐ": 9, "ไ": 9,
}

# Common Thai name roots for decomposition
COMMON_ROOTS = [
    "วร", "กฤช", "สุนทร", "ธรรม", "นิติ", "กมล", "กนก", "กิตติ", "พร", "พงศ์", 
    "โชติ", "เมธา", "อภิ", "ปัญญา", "วิช", "ชาติ", "รัตน์", "มณี", "ชัย", "วัฒน์"
]

def _calculate_sum(text: str) -> int:
    return sum(THAI_NUMEROLOGY_MAP.get(c, 0) for d, c in enumerate(text) if c in THAI_NUMEROLOGY_MAP)

def _get_meaning(word: str) -> str:
    # Try explicit meaning lookup
    res = rag_call(query=f"{word} แปลว่า")
    if res.get("success"):
        return res.get("answer", "ไม่พบความหมาย")
    # Fallback to general lookup
    res = rag_call(query=word)
    if res.get("success"):
        return res.get("answer", "ไม่พบความหมาย")
    return "ไม่พบความหมาย"

def _decompose_thai(text: str) -> List[str]:
    """Simple greedy decomposition into common roots."""
    found = []
    current = text
    while current:
        match = None
        # Longest match first
        for root in sorted(COMMON_ROOTS, key=len, reverse=True):
            if current.startswith(root):
                match = root
                break
        if match:
            found.append(match)
            current = current[len(match):]
        else:
            # If no root matches, take first char as a placeholder or break
            # Real NLP would be better, but let's try to at least find known ones
            found.append(current[0])
            current = current[1:]
    return found

def tool_name_analyzer(**kwargs: Any) -> Dict[str, Any]:
    """
    Detailed Thai Name Analyzer (Semantic + Numerology).
    """
    raw_input = kwargs.get('name') or kwargs.get('raw_text') or ''
    input_text = str(raw_input).strip()

    # 1. Clean input: remove common prefixes and suffixes
    prefixes = ["วิเคราะห์", "ดูดวง", "ดู", "ตรวจ", "คำนวณ", "เลขศาสตร์", "ชื่อ-นามสกุล", "ชื่อนามสกุล", "ชื่อ"]
    suffixes = ["ให้หน่อย", "หน่อย", "ครับ", "ค่ะ", "ครับผม", "นะ", "ที", "ให้ที"]
    
    # Recursive cleaning
    changed = True
    while changed:
        old_text = input_text
        for p in prefixes:
            if input_text.startswith(p):
                input_text = input_text[len(p):].strip()
        for s in suffixes:
            if input_text.endswith(s):
                input_text = input_text[:-len(s)].strip()
        changed = (old_text != input_text)

    if not input_text:
        return {"success": False, "error": "กรุณาระบุชื่อ-นามสกุลที่ต้องการวิเคราะห์ครับ"}

    # 2. Split Name / Surname (Handle multi-part)
    parts = [p for p in re.split(r"\s+", input_text) if p]
    if len(parts) == 0:
        return {"success": False, "error": "ไม่พบชื่อที่จะวิเคราะห์"}
    
    first_name = parts[0]
    surname = " ".join(parts[1:]) if len(parts) > 1 else ""

    # 3. Analyze First Name
    fn_sum = _calculate_sum(first_name)
    fn_roots = _decompose_thai(first_name)
    fn_breakdown = []
    for root in fn_roots:
        if len(root) > 1:
            fn_breakdown.append({"word": root, "meaning": _get_meaning(root)})
    
    # 2. Analyze Surname
    sn_sum = 0
    sn_breakdown = []
    if surname:
        sn_sum = _calculate_sum(surname)
        sn_roots = _decompose_thai(surname)
        for root in sn_roots:
            if len(root) > 1:
                sn_breakdown.append({"word": root, "meaning": _get_meaning(root)})

    # 3. Combined Numerology
    grand_total = fn_sum + sn_sum
    
    # Reduction Chain
    def get_reduction_chain(n):
        chain = [n]
        curr = n
        while curr >= 10:
            curr = sum(int(d) for d in str(curr))
            chain.append(curr)
        return chain

    chain = get_reduction_chain(grand_total)
    
    # Get meanings for numbers
    number_meanings = {}
    nums_to_lookup = [fn_sum, sn_sum, grand_total] + chain
    for n in sorted(list(set(nums_to_lookup))):
        number_meanings[str(n)] = _get_meaning(f"เลขศาสตร์ {n}")

    result = {
        "success": True,
        "full_name": f"{first_name} {surname}".strip(),
        "first_name": {
            "text": first_name,
            "sum": fn_sum,
            "breakdown": fn_breakdown,
            "meaning": _get_meaning(first_name),
            "numerology_meaning": number_meanings.get(str(fn_sum))
        },
        "surname": {
            "text": surname,
            "sum": sn_sum,
            "breakdown": sn_breakdown,
            "meaning": _get_meaning(surname),
            "numerology_meaning": number_meanings.get(str(sn_sum))
        } if surname else None,
        "grand_total": grand_total,
        "reduction_chain": chain,
        "number_meanings": number_meanings,
        "summary": f"วิเคราะห์ชื่อ {first_name} ({fn_sum}) และนามสกุล {surname} ({sn_sum}) รวมได้ {grand_total} ลดทอนเหลือ {chain[-1]}"
    }

    return result
