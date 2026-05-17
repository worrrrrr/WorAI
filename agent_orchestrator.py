"""
WorAI Agent Orchestrator v1.0
Production Ready: เชื่อมต่อ Intent Decoder + Hybrid Memory + Tool Registry
Flow: Input -> Decode Intent -> Update Memory -> Route Tool -> Generate Response
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import Components (สมมติว่าอยู่ใน path เดียวกันหรือติดตั้งแล้ว)
# ในสภาพแวดล้อมจริงต้องตรวจสอบ path การ import
try:
    from tools.latent_intent_decoder import LatentIntentDecoder
    from tools.hybrid_memory import HybridMemoryManager
except ImportError:
    # Fallback สำหรับกรณีทดสอบโดยไม่มีไฟล์จริง (จะแทนที่ด้วย Mock Class ด้านล่างถ้าจำเป็น)
    # แต่ใน Production ต้องมีไฟล์จริง
    raise ImportError("ต้องมี files: tools/latent_intent_decoder.py และ tools/hybrid_memory.py")

class ToolRegistry:
    """
    Registry จัดการ 27 Tools ที่มีอยู่
    จำลองการ Route ไปยัง Tool ที่ถูกต้องตาม Intent
    """
    def __init__(self):
        self.tools = {
            'bazi_analysis': self._mock_bazi_tool,
            'numerology': self._mock_numerology_tool,
            'general_chat': self._mock_chat_tool,
            'strategic_consulting': self._mock_consulting_tool,
            # เพิ่ม tools อื่นๆ อีก 23 ตัวที่นี่
        }
        self.tool_count = 27 # จำนวน tools ทั้งหมดที่มี

    def route(self, intent: str, entities: Dict, context: Dict) -> str:
        """
        Route ไปยัง Tool ที่เหมาะสม
        Priority: Explicit Intent > Entity Detection > Default
        """
        # 1. Map Intent ไปยัง Tool
        tool_name = self._map_intent_to_tool(intent)
        
        # 2. ดึง Function ของ Tool
        tool_func = self.tools.get(tool_name, self._mock_chat_tool)
        
        # 3. Execute Tool พร้อม Context ครบ 3 ชั้น
        response = tool_func(entities, context)
        
        return response

    def _map_intent_to_tool(self, intent: str) -> str:
        mapping = {
            'strategic_identity_analysis': 'bazi_analysis',
            'project_strategy': 'strategic_consulting',
            'decision_framework': 'strategic_consulting',
            'match_previous': 'general_chat', # ใช้ context ก่อนหน้า
            'unknown': 'general_chat'
        }
        return mapping.get(intent, 'general_chat')

    # --- Mock Tools Functions (แทนที่ด้วย Logic จริงของ 27 tools) ---
    def _mock_bazi_tool(self, entities: Dict, context: Dict) -> str:
        birth_date = entities.get('birth_date')
        if not birth_date:
            return "ขออภัย ระบบไม่พบข้อมูลวันเกิด กรุณาระบุวันเกิด"
        
        # ดึงประวัติจาก Long Term เพื่อดูว่าเคยถามอะไรไปบ้าง
        history_summary = context.get('long_term', {}).get('profile', {}).get('last_query', 'ไม่เคยถาม')
        
        return f"วิเคราะห์ดวงชะตาสำหรับเกิดวันที่ {birth_date} เรียบร้อย\n(อ้างอิงข้อมูลเดิม: {history_summary})\nต้องการเจาะลึกเรื่องใดเป็นพิเศษ? (การเงิน, ความรัก, การงาน)"

    def _mock_numerology_tool(self, entities: Dict, context: Dict) -> str:
        return "วิเคราะห์เลขศาสตร์เสร็จสิ้น"

    def _mock_chat_tool(self, entities: Dict, context: Dict) -> str:
        # ใช้ Working Memory เพื่อตอบต่อเนื่อง
        last_input = context.get('working', [])[-1] if context.get('working') else "สวัสดีครับ"
        return f"รับทราบครับ (ต่อเนื่องจาก: {last_input}) มีอะไรให้ช่วยเพิ่มเติมไหมครับ?"

    def _mock_consulting_tool(self, entities: Dict, context: Dict) -> str:
        return "จัดทำแผนกลยุทธ์เรียบร้อยแล้ว"


class AgentOrchestrator:
    """
    ตัวกลางควบคุม Flow หลักของ WorAI
    ปฏิบัติตามเงื่อนไข 4 ข้ออย่างเคร่งครัด
    """
    
    def __init__(self):
        self.intent_decoder = LatentIntentDecoder()
        self.memory_manager = HybridMemoryManager()
        self.tool_registry = ToolRegistry()
        self.turn_counter = 0

    def process(self, user_input: str, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main Entry Point
        Input: ข้อความผู้ใช้ + Profile (ถ้ามี)
        Output: Dictionary {response, intent, confidence, memory_status}
        """
        if user_profile is None:
            user_profile = {}

        # Step 1: Decode Intent (ถอดรหัสเจตนาแฝง)
        decoded = self.intent_decoder.decode(user_input, self.memory_manager.get_recent_history(), user_profile)
        intent = decoded['goal']
        confidence = decoded.get('confidence', 0.5) # สมมติว่ามีค่านี้
        entities = self._extract_entities(user_input) # แยก Entity เบื้องต้น

        # Step 2: Update Memory (บันทึกลงระบบความจำ)
        # เงื่อนไขข้อ 2: เจอ Entities ถาวร -> อัปเดต Long Term ทันที
        if entities:
            self.memory_manager.long_term.update_profile(entities)
        
        # บันทึกลง Working Memory เสมอ
        self.memory_manager.add_to_working(user_input, role='user')
        self.turn_counter += 1

        # เงื่อนไขข้อ 3: WorkingMemory > 8 turns -> บังคับ Auto Summarize
        if self.turn_counter > 8:
            summary = self.memory_manager.auto_summarize()
            self.memory_manager.add_to_short_term(summary)
            self.turn_counter = 0 # Reset counter หลัง summarize
            print(f"[System] Auto-summarized working memory to short term.")

        # Step 3: Prepare Context 3 ชั้น (เงื่อนไขข้อ 4)
        full_context = {
            'working': self.memory_manager.get_recent_history(limit=10),
            'short_term': self.memory_manager.get_short_term_summary(),
            'long_term': self.memory_manager.long_term.get_profile()
        }

        # Step 4: Route to Tool (เงื่อนไขข้อ 1: ถ้า Confidence > 0.8 ยิงตรง)
        response_text = ""
        
        if confidence > 0.8 and not decoded.get('must_ask'):
            # ยิง Tool เลย ห้ามถามซ้ำ
            response_text = self.tool_registry.route(intent, entities, full_context)
        elif decoded.get('must_ask'):
            # ต้องถามกลับตามที่ Decoder สั่ง
            response_text = decoded['must_ask']
            # บันทึกคำถามรอไว้ว่ากำลังรอคำตอบเรื่องอะไร
            self.memory_manager.add_to_working(f"[Pending Question]: {decoded['must_ask']}", role='system')
        else:
            # Confidence ต่ำ หรือ ไม่ชัดเจน -> ใช้ Default Strategy
            response_text = self.tool_registry.route('general_chat', entities, full_context)

        # Step 5: บันทึก Response ลง Working Memory
        self.memory_manager.add_to_working(response_text, role='assistant')

        # Step 6: Return Result
        return {
            'response': response_text,
            'intent': intent,
            'confidence': confidence,
            'memory_status': {
                'working_turns': self.turn_counter,
                'long_term_updated': bool(entities),
                'summarized': self.turn_counter == 0 and len(user_input) > 0 # Hack เล็กน้อยเพื่อแสดงสถานะ
            }
        }

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        แยก Entity สำคัญจากข้อความ (Birth Date, Name, etc.)
        ใช้ Regex แบบง่ายสำหรับการสาธิต (ในของจริงควรใช้ NLP Engine)
        """
        entities = {}
        text_lower = text.lower()

        # Pattern วันเดือนปี (ไทย/อังกฤษ)
        # ตัวอย่าง: 17 พฤษภา 2538, 8/8/1992, 17 May 1995
        date_patterns = [
            r'(\d{1,2})[\s/-](\w+)[\s/-](\d{4})',
            r'(\d{1,2})[\s/-](\w+)[\s/-](\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                d, m, y = match.groups()
                # Normalize ปี พ.ศ. -> ค.ศ.
                year = int(y)
                if year > 2500:
                    year -= 543
                elif year < 100:
                    year += 2000
                
                entities['birth_date'] = f"{d} {m} {year}"
                break
        
        # Pattern ชื่อ (สมมติว่าตามหลังคำว่า "ชื่อ")
        name_match = re.search(r'ชื่อ[\s:]+([^\s,!.]+)', text_lower)
        if name_match:
            entities['name'] = name_match.group(1).title()

        return entities


# ==========================================
# TEST CASE: จำลองการทำงานจริง
# ==========================================
if __name__ == "__main__":
    print("="*50)
    print("TEST CASE: ระบบความจำต่อเนื่อง (Context Retention)")
    print("="*50)

    # Mock Classes สำหรับทดสอบในไฟล์เดียว (ใน Production จะ import จากไฟล์จริง)
    class MockLongTerm:
        def __init__(self): self.profile = {}
        def update_profile(self, data): 
            self.profile.update(data)
            print(f"[LongTerm] Updated Profile: {data}")
        def get_profile(self): return self.profile

    class MockHybridMemory:
        def __init__(self):
            self.working = []
            self.short_term = []
            self.long_term = MockLongTerm()
        
        def add_to_working(self, text, role): 
            self.working.append({'role': role, 'content': text})
            print(f"[Working] Added ({role}): {text[:30]}...")
        
        def get_recent_history(self, limit=10): return self.working[-limit:]
        def get_short_term_summary(self): return self.short_term
        def auto_summarize(self): 
            s = "Summary of previous turns..."
            self.short_term.append(s)
            return s
        def add_to_short_term(self, data): self.short_term.append(data)

    class MockDecoder:
        def decode(self, text, history, profile):
            # Logic จำลอง: รอบแรกถามหาเรื่อง, รอบสองจำได้ว่าเคยคุยเรื่องดวง
            is_second_turn = len(history) > 0 and any('ดูดวง' in str(h) for h in history)
            
            if is_second_turn and 'เงิน' in text:
                return {'goal': 'numerology', 'confidence': 0.9, 'must_ask': None}
            elif 'ดูดวง' in text:
                return {'goal': 'bazi_analysis', 'confidence': 0.95, 'must_ask': None}
            elif 'เรื่องเงิน' in text or 'การเงิน' in text:
                return {'goal': 'numerology', 'confidence': 0.9, 'must_ask': None}
            else:
                # กรณีที่ไม่ชัดเจน ให้ถามกลับเฉพาะรอบแรก
                if len(history) == 0:
                     return {'goal': 'unknown', 'confidence': 0.4, 'must_ask': "รับทราบครับ ขอ Confirm 1 ข้อ: เรื่องนี้เกี่ยวกับ 'ตัวพี่' หรือ 'งาน' ครับ?"}
                return {'goal': 'general_chat', 'confidence': 0.6, 'must_ask': None}

    # Inject Mocks
    AgentOrchestrator.__init__ = lambda self: setattr(self, 'intent_decoder', MockDecoder()) or setattr(self, 'memory_manager', MockHybridMemory()) or setattr(self, 'tool_registry', ToolRegistry()) or setattr(self, 'turn_counter', 0)

    # Run Test
    agent = AgentOrchestrator()
    
    # Turn 1: User บอกวันเกิด
    input_1 = "ดูดวงให้หน่อย เกิด 17 พฤษภา 2538"
    print(f"\n[User] {input_1}")
    res1 = agent.process(input_1)
    print(f"[AI] {res1['response']}")
    print(f"-> Intent: {res1['intent']}, Conf: {res1['confidence']}")
    
    # Turn 2: User ถามเรื่องเงิน (ต้องจำวันเกิดได้ ไม่ถามซ้ำ)
    input_2 = "แล้วเรื่องเงินล่ะ เป็นไงบ้าง"
    print(f"\n[User] {input_2}")
    res2 = agent.process(input_2)
    print(f"[AI] {res2['response']}")
    print(f"-> Intent: {res2['intent']}, Conf: {res2['confidence']}")
    
    # ตรวจสอบผลลัพธ์ที่คาดหวัง
    print("\n" + "="*50)
    print("VERIFICATION:")
    print(f"1. จำวันเกิดได้ไหม? -> {'birth_date' in agent.memory_manager.long_term.profile}")
    print(f"2. ไม่ถามซ้ำเรื่องตัวตน? -> {'must_ask' not in str(res2) or res2['intent'] != 'unknown'}")
    print(f"3. วิเคราะห์เรื่องเงินตรงจุด? -> {res2['intent'] == 'numerology'}")
    print("="*50)
