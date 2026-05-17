def tool_web_search(query: str = None, raw_text: str = None, **kwargs): 
    q = query or raw_text or "ค้นหา"
    return {"success": True, "snippet": f"ผลการค้นหาเว็บสำหรับ '{q}' (จำลอง)", "links": [f"https://google.com/search?q={q}"]}
def tool_fact_retriever(query: str = None, raw_text: str = None, **kwargs): 
    return {"success": True, "answer": f"ข้อมูลความรู้ภายในเกี่ยวกับ '{query or raw_text}'", "source": "internal_kb"}
