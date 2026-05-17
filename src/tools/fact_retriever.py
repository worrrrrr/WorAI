from typing import Dict, Any, List
from src.utils import get_logger
import os
import glob
import re
import traceback

logger = get_logger("FactRetriever")
KB_CACHE = {}

def _get_kb_dir():
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_dir = os.path.dirname(src_dir)
    kb_dir = os.path.join(project_dir, "data", "knowledge")
    return kb_dir

def _load_kb():
    global KB_CACHE
    kb_dir = _get_kb_dir()
    
    if not os.path.exists(kb_dir):
        return {}

    KB_CACHE.clear()
    md_files = glob.glob(os.path.join(kb_dir, "*.md"))
    
    for file_path in md_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 1. Index by headers
            lines = content.split("\n")
            current_title = None
            current_body = []
            
            for line in lines:
                if line.startswith("### ") or line.startswith("## "):
                    if current_title:
                        KB_CACHE[current_title] = {"body": "\n".join(current_body).strip(), "source": filename}
                    current_title = line.lstrip("#").strip()
                    current_body = []
                else:
                    if current_title:
                        current_body.append(line)
            
            if current_title:
                KB_CACHE[current_title] = {"body": "\n".join(current_body).strip(), "source": filename}
            
            # 2. Index by table rows (Special for name.md)
            if filename == "name.md":
                # Match | Name | ... | Meaning |
                rows = re.findall(r'^\|\s*([^|]+)\s*\|\s*[^|]+\s*\|\s*[^|]+\s*\|\s*([^|]+)\s*\|', content, re.MULTILINE)
                for name, meaning in rows:
                    name = name.strip()
                    if name and name != "ชื่อ":
                        KB_CACHE[f"ความหมาย: {name}"] = {
                            "body": f"ชื่อ {name} แปลว่า {meaning.strip()}",
                            "source": filename
                        }
                        
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")

    return KB_CACHE

def tool_fact_retriever(query: str) -> Dict[str, Any]:
    if not KB_CACHE:
        _load_kb()

    query_clean = query.lower().strip()
    
    # 1. Priority: Numeric match (Numerology)
    num_match = re.search(r'\d+', query)
    if num_match:
        target_num = num_match.group()
        for title, data in KB_CACHE.items():
            if data['source'] == "numerology.md" and f"หมายเลข {target_num}:" in title:
                 return {"success": True, "answer": data['body'], "source": f"{data['source']} > {title}"}

    # 2. Priority: Astrology Specifics (Day Master, Zodiac)
    if any(k in query_clean for k in ["day master", "ราศี", "nakshatra"]):
        # Extract the core term (e.g., "Jia", "Taurus", "Ashwini")
        core_term = re.sub(r'(day master|ราศี|nakshatra)\s*', '', query_clean).strip()
        
        for title, data in KB_CACHE.items():
            if data['source'] == "astrology.md":
                # Match bold items: **Name**: Description
                matches = re.findall(r'\*\*([^*]+)\*\*:\s*([^\n]+)', data['body'])
                for key, val in matches:
                    key_clean = key.lower()
                    if core_term in key_clean or key_clean in core_term:
                         return {"success": True, "answer": f"{key}: {val}", "source": f"astrology.md > {title}"}
                
                # Match list items if bold is not found: - Name: Description
                matches = re.findall(r'-\s*\*?([^*:]+)\*?:\s*([^\n]+)', data['body'])
                for key, val in matches:
                    key_clean = key.lower()
                    if core_term in key_clean or key_clean in core_term:
                         return {"success": True, "answer": f"{key}: {val}", "source": f"astrology.md > {title}"}

    # 2. Priority: Explicit Meaning match (Name)
    if "แปลว่า" in query_clean or "หมายถึง" in query_clean:
        word = re.sub(r'(แปลว่า|หมายถึง|คืออะไร|ความหมาย|ชื่อ)\s*', '', query_clean).strip()
        if f"ความหมาย: {word}" in KB_CACHE:
            data = KB_CACHE[f"ความหมาย: {word}"]
            return {"success": True, "answer": data['body'], "source": data['source']}

    # 3. Match from Knowledge Base titles
    for title, data in KB_CACHE.items():
        if query_clean == title.lower():
            return {"success": True, "answer": data['body'], "source": f"{data['source']} > {title}"}

    # 4. Fuzzy match in titles
    for title, data in KB_CACHE.items():
        if query_clean in title.lower():
            return {"success": True, "answer": data['body'], "source": f"{data['source']} > {title}"}

    # 5. Search in body
    for title, data in KB_CACHE.items():
        if query_clean in data['body'].lower():
             return {"success": True, "answer": data['body'], "source": f"{data['source']} > {title}"}

    return {"success": False, "error": f"ไม่พบข้อมูลเกี่ยวกับ '{query}'"}
