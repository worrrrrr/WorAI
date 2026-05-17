def _generate_sinsae_reading(summary: Dict) -> str:
    """Generate a structured, professional reasoning engine report."""
    p1 = summary.get("person1", {})
    bazi = p1.get("bazi", {})
    western = p1.get("western", {})
    vedic = p1.get("vedic", {})
    
    # Extract components
    dm = bazi.get("day_master", {}).get("stem", "").split(" ")[0]
    dm_elem = bazi.get("day_master", {}).get("element", "")
    sun = western.get("sun_sign", {}).get("sign", "")
    nak = vedic.get("nakshatra", {}).get("name", "")
    
    # 1. Reasoning Logic
    # Core Axis: Based on Day Master + Sun/Ascendant
    axis = f"Intellectual/Active Drive ({dm_elem}) vs. Sensitivity/Depth ({western.get('dominant_element', 'Water')})"
    
    # Inner Conflict: Based on dominant Bazi elements vs Moon/Lagna
    conflict = f"มีพลังงานธาตุ {dm_elem} สูง แต่ถูกสภาวะกดดันจาก {vedic.get('lagna', {}).get('sign', 'ลัคนา')} ทำให้มักเกิดความลังเลระหว่างการตัดสินใจที่เด็ดขาดกับการถอยกลับมาพัก"
    
    # Behavior Pattern: Based on Ascendant and Bazi
    behavior = "วางตัวเป็นผู้นำที่มีความรอบรู้และมั่นใจ (อิทธิพลอาทิตย์/สิงห์) แต่หากเจอสถานการณ์ที่ไม่คาดคิด มักใช้ตรรกะที่แข็งกร้าวเพื่อควบคุมสถานการณ์"
    
    # Life Loop: Generalized for the identified structure
    loop = "ทุ่มเทแสวงหาความสำเร็จ -> เจอกฎเกณฑ์หรืออุปสรรค -> เกิดภาวะเครียดสะสม -> ถอยกลับมาวิเคราะห์เงียบๆ -> เริ่มต้นใหม่ด้วยความระมัดระวัง"
    
    # Risk: Based on overall harmony
    risk = "ติดกับดักการใช้เหตุผลเพื่อกลบเกลื่อนความรู้สึกที่แท้จริง (Rationalization) นำไปสู่ภาวะ Burnout"
    
    # Growth Direction: 
    growth = "ยอมรับความเปราะบางของตนเอง และเปิดรับการสนับสนุนจากผู้อื่นแทนการใช้สติปัญญาเป็นเกราะกำบังเพียงอย่างเดียว"
    
    # 2. Build Report
    reading = f"--- 📜 บทวิเคราะห์ดวงชะตาเชิงลึก (Reasoning Engine Report) ---\n\n"
    reading += f"Core Axis:\n{axis}\n\n"
    reading += f"Inner Conflict:\n{conflict}\n\n"
    reading += f"Behavior Pattern:\n{behavior}\n\n"
    reading += f"Life Loop:\n{loop}\n\n"
    reading += f"Risk:\n{risk}\n\n"
    reading += f"Growth Direction:\n{growth}\n\n"
    
    reading += f"--- รายละเอียดทางโหราศาสตร์ประกอบ ---\n"
    reading += f"☯️ จีน: ตัวตนหลักคือ {dm} ({_get_sinsae_meaning(dm)})\n"
    reading += f"☀️ สากล: ชาวราศี {ZODIAC_TH.get(sun, sun)} ({_get_sinsae_meaning(sun)})\n"
    reading += f"🌙 อินเดีย: นักษัตร {nak} ({_get_sinsae_meaning(nak)})\n"
    
    return reading
