def _generate_sinsae_reading(summary: Dict) -> str:
    """Combine all data into a cohesive professional Sin-sae consultation."""
    p1 = summary.get("person1", {})
    bazi = p1.get("bazi", {})
    western = p1.get("western", {})
    vedic = p1.get("vedic", {})
    harmony = p1.get("harmony", {}).get("overall_harmony", {})
    
    dm = bazi.get("day_master", {}).get("stem", "").split(" ")[0]
    sun = western.get("sun_sign", {}).get("sign", "")
    nak = vedic.get("nakshatra", {}).get("name", "")
    
    reading = f"--- 📜 บทวิเคราะห์ดวงชะตาเชิงลึกโดยซินแซ WorAI ---\n\n"
    reading += f"✨ วิเคราะห์พื้นฐานดวงชะตา: {summary['input']['thai_date']}\n"
    reading += f"ระดับความสอดคล้องของชีวิต (Harmony): {harmony.get('level', 'ปานกลาง')} ({harmony.get('score', 0)}%)\n\n"
    
    reading += f"☯️ [ภาคจีน - โป๊ยหยี่สี่เถียว]\n"
    reading += f"ตัวตนหลัก (Day Master) คือ '{dm}' ซึ่งเปรียบดั่ง {_get_sinsae_meaning(dm)}\n"
    reading += f"วิเคราะห์สมดุลธาตุ: {summary['person1']['harmony']['element_alignment']['interpretation']}\n\n"
    
    reading += f"☀️ [ภาคสากล - Western Astrology]\n"
    reading += f"ชาวราศี {ZODIAC_TH.get(sun)}: {_get_sinsae_meaning(sun)}\n"
    reading += f"ลัคนา (ตัวตนภายนอก) ของคุณคือราศี {ZODIAC_TH.get(western['ascendant']['sign'], western['ascendant']['sign'])} ซึ่งส่งผลต่อภาพลักษณ์ที่คุณแสดงออกต่อผู้อื่น\n\n"
    
    reading += f"🌙 [ภาคอินเดีย - Vedic / Nakshatra]\n"
    reading += f"พระจันทร์เสวยนักษัตร {nak} (Nakshatra): {_get_sinsae_meaning(nak)}\n"
    reading += f"ดวงเมืองเกิด (Lagna) สถิตราศี {ZODIAC_TH.get(vedic['lagna']['sign'], vedic['lagna']['sign'])}\n\n"
    
    reading += f"💡 [บทสรุปและคำแนะนำจากซินแซ]\n"
    reading += f"{harmony.get('summary', 'ชีวิตมีทางเดินที่หลากหลาย จงใช้สติเป็นที่ตั้ง')}\n"
    reading += f"\n--- ขอให้โชคดีและรุ่งเรืองครับ ---"
    
    return reading
