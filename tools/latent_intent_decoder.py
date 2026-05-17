"""
LatentIntentDecoder v7.2
หน้าที่: ถอดรหัสเจตนาแฝงจาก "ข้อความ + บริบท 4 ข้อความล่าสุด"
หลักการ: ไม่จำ User, ไม่มโน, ตัดสินจากข้อมูลตรงหน้าเท่านั้น

เคสหลัก: "อืม เดี๋ยวดู" = ขู่ หรือ ปฏิเสธ? ดูที่บริบทก่อนหน้า
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class IntentResult:
    """ผลลัพธ์จากการถอดรหัสเจตนา"""
    goal: str # เป้าหมายหลัก: threat, soft_no, negotiating, general_chat
    confidence: float # ความมั่นใจ 0.0-1.0
    is_dangerous: bool # ต้อง de-escalate ทันทีหรือไม่
    threat_level: int # ระดับความอันตราย 0-10
    action: str # คำสั่งให้ orchestrator: apologize, close, help, continue
    context_reason: str # เหตุผลที่ตัดสินแบบนี้
    metadata: Dict[str, Any] # ข้อมูลเสริม

class LatentIntentDecoder:
    def __init__(self):
        # Regex patterns - compile ไว้ก่อนเพื่อความเร็ว
        self.threat_patterns = [
            re.compile(r'^(อืม\s*)?เดี๋ยวดู\s*$'),
            re.compile(r'^เดี๋ยวรู้\s*$'),
            re.compile(r'^คอยดู\s*$'),
            re.compile(r'^จำไว้\s*$'),
            re.compile(r'^ได้\s*เดี๋ยวดู\s*$'),
        ]

        self.excuse_patterns = [
            re.compile(r'อยาก.+(แต่|แต่ว่า)'),
            re.compile(r'ได้.+(แต่|แต่ว่า)'),
            re.compile(r'ติด.+(เลย|อะ|อ่ะ|ครับ|ค่ะ)'),
            re.compile(r'ไม่ว่าง|ไม่สะดวก'),
        ]

        # คำที่บ่งบอกบรรยากาศแย่
        self.negative_keywords = {
            'swear': ['มึง', 'สัส', 'เหี้ย', 'ควย', 'ดอก', 'สัด'],
            'insult': ['โง่', 'เอ๋อ', 'กาก', 'ห่วย', 'กระจอก', 'ปัญญาอ่อน'],
            'error': ['ผิด', 'ไม่ใช่', 'มั่ว', 'เพี้ยน', 'บ้ง'],
            'annoyance': ['น่ารำคาญ', 'รำคาญ', 'เซ็ง', 'เบื่อ']
        }

        # คำที่บอกว่า Bot เพิ่งพลาด
        self.bot_apology_keywords = [
            'ขออภัย', 'ขอโทษ', 'ผิดพลาด', 'เข้าใจผิด', 'ขอแก้', 'เมื่อกี้ผิด'
        ]

    def _analyze_context(self, history: List[Dict]) -> Dict[str, Any]:
        """
        วิเคราะห์ 4 ข้อความล่าสุดว่าเป็นบริบทลบหรือไม่

        Returns:
            {
                'is_negative': bool,
                'anger_score': int,
                'reasons': List[str],
                'user_anger_words': List[str],
                'bot_admitted_fault': bool
            }
        """
        if not history:
            return {
                'is_negative': False,
                'anger_score': 0,
                'reasons': ['no_history'],
                'user_anger_words': [],
                'bot_admitted_fault': False
            }

        # เอาแค่ 4 turns ล่าสุด
        recent = history[-4:] if len(history) >= 4 else history
        anger_score = 0
        reasons = []
        user_anger_words = []
        bot_admitted_fault = False

        for msg in recent:
            content = msg.get('content', '').lower()
            role = msg.get('role', 'user')

            if role == 'user':
                # เช็คคำหยาบ/ด่า
                for category, words in self.negative_keywords.items():
                    found = [w for w in words if w in content]
                    if found:
                        anger_score += len(found) * 2
                        user_anger_words.extend(found)
                        reasons.append(f'user_{category}')

                # เช็คการลากเสียง = ประชด/โมโห
                if re.search(r'([ก-๙a-z])\1{4,}', content):
                    anger_score += 3
                    reasons.append('elongation_sarcasm')

            elif role == 'assistant':
                # เช็ค Bot ยอมรับผิด
                if any(kw in content for kw in self.bot_apology_keywords):
                    anger_score += 4
                    bot_admitted_fault = True
                    reasons.append('bot_admitted_error')

        # Threshold: 3 แต้มขึ้นไป = บริบทลบ
        is_negative = anger_score >= 3

        return {
            'is_negative': is_negative,
            'anger_score': anger_score,
            'reasons': list(set(reasons)),
            'user_anger_words': list(set(user_anger_words)),
            'bot_admitted_fault': bot_admitted_fault
        }

    def decode(self, text: str, history: List[Dict]) -> IntentResult:
        """
        ฟังก์ชันหลัก: ถอดรหัสเจตนาจากข้อความ + history

        Args:
            text: ข้อความล่าสุดจาก user
            history: ประวัติการคุย [{role: 'user'|'assistant', content: str}]

        Returns:
            IntentResult object
        """
        if not text or not text.strip():
            return IntentResult(
                goal='empty',
                confidence=1.0,
                is_dangerous=False,
                threat_level=0,
                action='ask_clarify',
                context_reason='empty_input',
                metadata={}
            )

        text_clean = text.strip()
        text_lower = text_clean.lower()
        context = self._analyze_context(history)

        # === Priority 1: จับ "คำขู่สุภาพ" ===
        for pattern in self.threat_patterns:
            if pattern.match(text_lower):
                if context['is_negative']:
                    # บริบทลบ + เดี๋ยวดู = ขู่แน่นอน
                    return IntentResult(
                        goal='threat_or_warning',
                        confidence=1.0,
                        is_dangerous=True,
                        threat_level=min(10, 6 + context['anger_score']),
                        action='apologize_and_deescalate',
                        context_reason=f"negative_context: {', '.join(context['reasons'])}",
                        metadata={
                            'pattern_matched': pattern.pattern,
                            'anger_score': context['anger_score'],
                            'user_anger_words': context['user_anger_words']
                        }
                    )
                else:
                    # บริบทปกติ = ปฏิเสธนิ่ม
                    return IntentResult(
                        goal='soft_no',
                        confidence=0.9,
                        is_dangerous=False,
                        threat_level=1,
                        action='acknowledge_and_close',
                        context_reason='neutral_context',
                        metadata={'pattern_matched': pattern.pattern}
                    )

        # === Priority 2: จับ "ข้ออ้าง/ปฏิเสธมีเหตุผล" ===
        for pattern in self.excuse_patterns:
            if pattern.search(text_lower):
                # ถ้ายาวเกิน 15 ตัวอักษร = รู้สึกผิดเลยต้องอธิบายเยอะ
                is_guilty = len(text_clean) > 15
                return IntentResult(
                    goal='excuse_or_rejection',
                    confidence=0.85,
                    is_dangerous=False,
                    threat_level=2 if is_guilty else 1,
                    action='acknowledge_and_close',
                    context_reason='excuse_pattern_detected',
                    metadata={
                        'pattern_matched': pattern.pattern,
                        'is_guilty_excuse': is_guilty
                    }
                )

        # === Priority 3: จับ "คำถาม/ต่อรอง" ===
        question_indicators = ['?', 'เท่าไหร่', 'กี่', 'ยังไง', 'ทำไง', 'ไหม', 'หรือ']
        if any(ind in text_lower for ind in question_indicators):
            return IntentResult(
                goal='negotiating',
                confidence=0.8,
                is_dangerous=False,
                threat_level=0,
                action='help_find_solution',
                context_reason='question_detected',
                metadata={}
            )

        # === Default: คุยทั่วไป ===
        return IntentResult(
            goal='general_chat',
            confidence=0.5,
            is_dangerous=False,
            threat_level=0,
            action='continue_conversation',
            context_reason='no_pattern_matched',
            metadata={}
        )

# === ตัวอย่างการใช้งานใน Orchestrator ===
"""
from latent_intent_decoder import LatentIntentDecoder, IntentResult

decoder = LatentIntentDecoder()

def handle_user_message(user_text: str, history: List[Dict]) -> str:
    result = decoder.decode(user_text, history)

    if result.action == 'apologize_and_deescalate':
        # User โกรธ + ขู่ ต้องขอโทษทันที
        log_warning(f"User threat detected: {result.metadata}")
        return "ขอโทษครับพี่ ผมพลาดเอง มีอะไรให้แก้ไขบอกได้เลยนะครับ"

    elif result.action == 'acknowledge_and_close':
        # ปฏิเสธนิ่ม ปิดจ็อบสวยๆ
        return "โอเคครับ เข้าใจแล้ว ไว้โอกาสหน้านะครับ"

    elif result.action == 'help_find_solution':
        # User อยากต่อรอง หาทางออก
        return "ได้เลยครับ เดี๋ยวช่วยดูให้นะ อยากให้ปรับตรงไหนบอกได้เลย"

    else:
        # คุยทั่วไป
        return generate_normal_response(user_text, history)

# Unit Test
if __name__ == "__main__":
    decoder = LatentIntentDecoder()

    # Test 1: บริบทลบ + เดี๋ยวดู = ขู่
    history1 = [
        {'role': 'assistant', 'content': 'ขอโทษครับ ผมผิดเอง'},
        {'role': 'user', 'content': 'มึงโง่สัส'},
    ]
    r1 = decoder.decode("อืม เดี๋ยวดู", history1)
    assert r1.is_dangerous == True
    assert r1.threat_level >= 9
    print("Test 1 Pass:", r1)

    # Test 2: บริบทธรรมดา + เดี๋ยวดู = ปฏิเสธ
    history2 = [
        {'role': 'assistant', 'content': 'สนใจมั้ยครับ'},
        {'role': 'user', 'content': 'อืม'},
    ]
    r2 = decoder.decode("เดี๋ยวดู", history2)
    assert r2.is_dangerous == False
    assert r2.goal == 'soft_no'
    print("Test 2 Pass:", r2)

    print("\nAll tests passed ✅")
"""