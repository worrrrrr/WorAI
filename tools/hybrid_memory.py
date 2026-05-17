"""
LatentIntentDecoder v7.4 Selective Memory
จำแค่ 3 เรื่อง: code_style, hate_apology, communication_pref
นอกนั้นทิ้งหมด ไม่เมาหมัด
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class UserPreference:
    """เก็บแค่สิ่งที่ต้องจำจริงๆ 3 อย่างพอ"""
    user_id: str
    code_style: str = "detailed" # "short" | "detailed" | "auto"
    hate_apology: bool = False # True = ห้ามขอโทษอีก
    allow_swear: bool = True # True = ด่าได้ ไม่ต้องดัดจริต
    updated_at: str = ""
    updated_reason: str = "" # เก็บเหตุผลที่เปลี่ยน เช่น "user_said_no_apology"

class LatentIntentDecoder:
    def __init__(self, hybrid_memory=None):
        self.memory = hybrid_memory
        self.threat_patterns = [
            re.compile(r'^(อืม\s*)?เดี๋ยวดู\s*$'),
            re.compile(r'^เดี๋ยวรู้\s*$'),
        ]
        self.negative_keywords = ['มึง','สัส','เหี้ย','ควย','โง่','ผิด']

    def _get_pref(self, user_id: str) -> UserPreference:
        """ดึงแค่ Preference ไม่ดึง History"""
        if not self.memory:
            return UserPreference(user_id=user_id)

        data = self.memory.get_long_term(user_id, "user_pref")
        return UserPreference(**data) if data else UserPreference(user_id=user_id)

    def _save_pref(self, pref: UserPreference, reason: str):
        """เซฟแค่ตอน User สั่งเปลี่ยนเท่านั้น ไม่เซฟพร่ำเพรื่อ"""
        if self.memory:
            pref.updated_at = datetime.now().isoformat()
            pref.updated_reason = reason
            self.memory.set_long_term(pref.user_id, "user_pref", asdict(pref))

    def _is_session_opening(self, history: List[Dict]) -> bool:
        """เช็คแค่ 3 ข้อความแรก = เปิด session"""
        return len(history) <= 3

    def decode(self, text: str, history: List[Dict], user_id: str) -> Dict[str, Any]:
        """
        ถอดรหัส: จำแค่ Preference ไม่จำ History
        เช็คขู่เฉพาะตอนเปิด session เท่านั้น
        """
        text_lower = text.strip().lower()
        pref = self._get_pref(user_id)
        is_opening = self._is_session_opening(history)

        # === Auto-update Preference จากคำสั่ง User ===
        if 'เอาโค้ดเต็ม' in text_lower or 'เอางานคุณภาพ' in text_lower:
            if pref.code_style!= "detailed":
                pref.code_style = "detailed"
                self._save_pref(pref, "user_request_full_code")

        if 'ไม่ต้องขอโทษ' in text_lower or 'เลิกขอโทษ' in text_lower:
            if not pref.hate_apology:
                pref.hate_apology = True
                self._save_pref(pref, "user_hates_apology")

        # === เช็คขู่เฉพาะตอนเปิด Session ===
        if is_opening:
            for pattern in self.threat_patterns:
                if pattern.match(text_lower):
                    # ดูแค่ 3 ข้อความแรก มีด่ามั้ย
                    has_anger = any(
                        any(w in h['content'].lower() for w in self.negative_keywords)
                        for h in history if h['role'] == 'user'
                    )

                    if has_anger:
                        return {
                            'goal': 'threat',
                            'is_dangerous': True,
                            'threat_level': 9,
                            'action': 'apologize' if not pref.hate_apology else 'fix_silently',
                            'context_reason': 'session_opening_with_anger'
                        }

        # === Response ตาม Preference ===
        return {
            'goal': 'general_chat',
            'is_dangerous': False,
            'threat_level': 0,
            'action': 'continue',
            'user_pref': {
                'code_style': pref.code_style,
                'should_apologize': not pref.hate_apology
            },
            'context_reason': 'normal_flow'
        }

# === ตัวอย่างใช้จริง ===
"""
decoder = LatentIntentDecoder(hybrid_memory=your_memory)

# รอบที่ 1: User บอก "ไม่ต้องขอโทษ"
result = decoder.decode("เลิกขอโทษได้ละ", [], "user_123")
# -> ระบบจำ pref.hate_apology = True

# รอบที่ 2: อีก 3 วันต่อมา User ขู่
result = decoder.decode("อืม เดี๋ยวดู", [], "user_123")
# -> action = 'fix_silently' ไม่ใช่ 'apologize' เพราะจำได้ว่ามึงเกลียดคำขอโทษ

# รอบที่ 3: User ขอโค้ด
result = decoder.decode("เอาโค้ดดิ", history, "user_123")
# -> user_pref.code_style = "detailed" ส่งโค้ดเต็มอัตโนมัติ ไม่ต้องถาม
"""