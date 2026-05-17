"""
Latent Intent Decoder - Production Ready
วิเคราะห์เจตนาแฝง ความคาดหวัง และบุคลิกภาพจากภาษาพูดแบบไทย
"""

import re
from typing import Dict, List, Any, Optional


class LatentIntentDecoder:
    """
    ถอดรหัสความตั้งใจแฝง (Latent Intent) จากข้อความภาษาไทย
    โดยวิเคราะห์จาก:
    1. รูปแบบภาษา (Linguistic Patterns)
    2. ประวัติการสนทนา (Conversation History)
    3. โปรไฟล์ผู้ใช้ (User Profile - MBTI/Cognitive Functions)
    """

    # Mapping รูปแบบภาษา -> ความหมายแฝง
    CONTEXT_MAPPING = {
        r'เอาแบบนั้น': {'action': 'continue_previous_topic'},
        r'ลึกๆ': {'depth': 'blueprint'},
        r'ไม่ชุ่ย': {'constraint': 'production_ready'},
        r'ละเอียด': {'constraint': 'edge_cases_included'},
        r'เอาให้สุด': {'constraint': 'no_simplification'},
        r'ที่เคยทำ|แบบเดิม|เหมือนเดิม': {'format': 'match_previous_output'},
        r'ไม่ต้องแก้': {'delivery': 'one_shot', 'qa': 'self_critique_mandatory'},
        r'จัดมา': {'urgency': 'high', 'clarification': 'not_needed'},
        r'อ่านขาด': {'add': ['root_cause_analysis', 'cognitive_pattern']},
        r'ตรงๆ': {'style': 'no_fluff', 'remove_hedging': True},
        r'ทำไม': {'intent': 'root_cause_seeking'},
        r'จริงๆ': {'constraint': 'authenticity_required'},
        r'แน่ชัด': {'constraint': 'certainty_required'},
        r'เสี่ยง': {'focus': 'risk_analysis'},
        r'โอกาส': {'focus': 'opportunity_analysis'},
    }

    # บุคลิกภาพที่พบบ่อยในภาษาไทย
    PERSONALITY_INDICATORS = {
        r'คิดมาก': {'trait': 'overthinking', 'cognitive': 'Ti_Ni_loop'},
        r'กังวล': {'trait': 'anxiety', 'cognitive': 'Si_Fe_stress'},
        r'มั่นใจ': {'trait': 'confidence', 'cognitive': 'Te_dom'},
        r'สงสัย': {'trait': 'curiosity', 'cognitive': 'Ti_neutral'},
        r'เบื่อ': {'trait': 'boredom', 'cognitive': 'Ne_underused'},
        r'อัดอั้น': {'trait': 'frustration', 'cognitive': 'Fi_explosion'},
    }

    def __init__(self):
        self.last_successful_spec: Optional[Dict[str, Any]] = None
        self.conversation_context: List[Dict[str, Any]] = []

    def decode(
        self, 
        text: str, 
        history: Optional[List[str]] = None, 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ถอดรหัสความตั้งใจแฝงจากข้อความ
        
        Args:
            text: ข้อความที่ต้องการวิเคราะห์
            history: ประวัติการสนทนาก่อนหน้า
            user_profile: โปรไฟล์ผู้ใช้ (MBTI, Cognitive Functions)
            
        Returns:
            Dictionary containing decoded intent spec
        """
        if history is None:
            history = []
        if user_profile is None:
            user_profile = {}

        text_lower = text.lower()
        constraints: List[str] = []
        implicit_context: Dict[str, Any] = {}
        personality_traits: List[str] = []
        cognitive_patterns: List[str] = []

        # 1. ถอดรหัสภาษาพูด ใช้ Regex จับรูปแบบ
        for pattern, mapping in self.CONTEXT_MAPPING.items():
            if re.search(pattern, text_lower):
                for key, value in mapping.items():
                    if key in ['constraint', 'requirement', 'quality', 'qa', 'style']:
                        if isinstance(value, str):
                            constraints.append(value)
                        elif isinstance(value, bool) and value:
                            constraints.append(key)
                    elif key == 'add':
                        implicit_context.setdefault('extras', []).extend(value)
                    elif key == 'focus':
                        implicit_context['focus_area'] = value
                    elif key == 'intent':
                        implicit_context['primary_intent'] = value
                    else:
                        implicit_context[key] = value

        # 2. วิเคราะห์บุคลิกภาพจากภาษาที่ใช้
        for pattern, mapping in self.PERSONALITY_INDICATORS.items():
            if re.search(pattern, text_lower):
                personality_traits.append(mapping['trait'])
                cognitive_patterns.append(mapping['cognitive'])

        # 3. หา Goal: Priority Explicit > History > Unknown
        explicit_goal = self._extract_explicit(text_lower, history)

        # 4. หา Depth: Priority Explicit > Profile > Default
        inferred_depth = self._infer_depth(implicit_context, user_profile)

        # 5. ใช้ History เพิ่ม Quality Constraints
        if any('ชุ่ย' in h or 'ผิด' in h or 'ไม่ดี' in h for h in history):
            if 'triple_check_required' not in constraints:
                constraints.append('triple_check_required')
            if inferred_depth == 'analysis':
                inferred_depth = 'blueprint'

        # 6. วิเคราะห์ความเร่งด่วนและความสำคัญ
        urgency_level = self._assess_urgency(text_lower, implicit_context)

        # 7. ตัดสินใจถามกลับ: ถามได้ 1 ครั้งเท่านั้น ถ้าจำเป็นจริงๆ
        must_ask = self._determine_clarification_need(
            text_lower, explicit_goal, implicit_context, urgency_level
        )

        # 8. สร้าง Final Spec ที่ Type-safe และ Production Ready
        final_spec = {
            'goal': explicit_goal if explicit_goal != 'unknown' else 'strategic_consulting',
            'depth': inferred_depth,
            'format': implicit_context.get('format', 'strategic_blueprint'),
            'constraints': sorted(list(set(constraints))),
            'extras': implicit_context.get('extras', []),
            'personality_traits': personality_traits,
            'cognitive_patterns': cognitive_patterns,
            'focus_area': implicit_context.get('focus_area'),
            'primary_intent': implicit_context.get('primary_intent'),
            'must_ask': must_ask,
            'urgency_high': urgency_level == 'high',
            'confidence_score': self._calculate_confidence(
                text_lower, implicit_context, history
            ),
        }

        # เก็บ Spec ที่สำเร็จไว้ใช้อ้างอิง (ถ้าไม่ต้องถามกลับ)
        if not must_ask:
            self.last_successful_spec = final_spec
            self.conversation_context.append({
                'text': text,
                'spec': final_spec,
                'timestamp': len(self.conversation_context)
            })

        return final_spec

    def _extract_explicit(self, text_lower: str, history: List[str]) -> str:
        """แยกเป้าหมายที่ระบุชัดเจนออกจากข้อความ"""
        
        # ตรวจสอบการอ้างอิงถึงงานก่อนหน้า
        if re.search(r'เอาแบบนั้น|ที่เคยทำ|แบบเดิม|เหมือนเดิม', text_lower):
            if self.last_successful_spec:
                return self.last_successful_spec['goal']
            return 'match_previous'

        # ตรวจสอบหัวข้อเฉพาะ
        if any(word in text_lower for word in ['ตัวตน', 'ฉัน', 'ผม', 'ตัวเอง', 'นิสัย']):
            return 'strategic_identity_analysis'
        
        if any(word in text_lower for word in ['งาน', 'โปรเจค', 'ธุรกิจ', 'บริษัท']):
            return 'project_strategy'
        
        if any(word in text_lower for word in ['ตัดสินใจ', 'เลือก', 'ทาง']):
            return 'decision_framework'
        
        if any(word in text_lower for word in ['วิเคราะห์', 'อ่าน', 'ดู']):
            return 'deep_analysis'
        
        if any(word in text_lower for word in ['วางแผน', 'กลยุทธ์', 'แผน']):
            return 'strategic_planning'

        return 'unknown'

    def _infer_depth(
        self, 
        implicit_context: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """อนุมานระดับความลึกของการวิเคราะห์"""
        
        # Priority 1: Explicit request
        if 'depth' in implicit_context:
            return implicit_context['depth']

        # Priority 2: User profile cognitive functions
        ti_score = user_profile.get('Ti', 0)
        ni_score = user_profile.get('Ni', 0)
        
        if ti_score > 6.0 or ni_score > 6.0:
            return 'blueprint'
        
        # Priority 3: Context clues
        if implicit_context.get('extras'):
            return 'blueprint'

        # Default
        return 'analysis'

    def _assess_urgency(
        self, 
        text_lower: str, 
        implicit_context: Dict[str, Any]
    ) -> str:
        """ประเมินระดับความเร่งด่วน"""
        
        if 'urgency' in implicit_context:
            return 'high'
        
        urgency_indicators = [
            r'\bด่วน\b', r'\bเร็ว\b', r'\bตอนนี้\b', 
            r'\bทันที\b', r'\bเร่ง\b', r'\b ASAP\b'
        ]
        
        for pattern in urgency_indicators:
            if re.search(pattern, text_lower):
                return 'high'
        
        return 'normal'

    def _determine_clarification_need(
        self,
        text_lower: str,
        explicit_goal: str,
        implicit_context: Dict[str, Any],
        urgency_level: str
    ) -> Optional[str]:
        """ตัดสินใจว่าต้องถามกลับหรือไม่ (ถามได้แค่ 1 ครั้ง)"""
        
        # ไม่ต้องถามถ้า:
        # 1. ผู้ใช้บอก "จัดมา" หรือแสดงความเร่งด่วน
        # 2. เป้าหมายชัดเจน
        # 3. มี context เพียงพอ
        
        if 'clarification' in implicit_context:
            return None
            
        if urgency_level == 'high':
            return None
            
        if explicit_goal != 'unknown':
            return None

        # ต้องถามถ้าเป้าหมายไม่ชัดและไม่เร่งด่วน
        clarification_questions = {
            'strategic_identity_analysis': "รับทราบครับ ขอ Confirm 1 ข้อ: เรื่องนี้เกี่ยวกับ 'ตัวพี่' หรือ 'งาน' ครับ?",
            'project_strategy': "รับทราบครับ ขอ Confirm: โปรเจคนี้เกี่ยวกับด้านไหนครับ? (เทคโนโลยี, ธุรกิจ, หรือบุคคล)",
            'decision_framework': "รับทราบครับ ขอ Confirm: การตัดสินใจนี้เกี่ยวกับเรื่องอะไรครับ? (งาน, ความสัมพันธ์, หรือการเงิน)",
        }

        # Default clarification
        return "รับทราบครับ ขอ Confirm 1 ข้อ: เรื่องนี้เกี่ยวกับ 'ตัวพี่' หรือ 'งาน' ครับ?"

    def _calculate_confidence(
        self,
        text_lower: str,
        implicit_context: Dict[str, Any],
        history: List[str]
    ) -> float:
        """คำนวณคะแนนความมั่นใจในการตีความ (0.0 - 1.0)"""
        
        confidence = 0.5  # Base confidence
        
        # เพิ่มความมั่นใจถ้ามี pattern ชัดเจน
        if implicit_context:
            confidence += 0.2
            
        # เพิ่มความมั่นใจถ้ามี history
        if history:
            confidence += 0.1
            
        # เพิ่มความมั่นใจถ้ามี goal ชัดเจน
        if self._extract_explicit(text_lower, history) != 'unknown':
            confidence += 0.2
            
        # ลดความมั่นใจถ้ามีคำกำกวม
        ambiguous_words = ['อาจจะ', 'น่าจะ', 'คง', 'บ้าง']
        if any(word in text_lower for word in ambiguous_words):
            confidence -= 0.1
            
        return min(max(confidence, 0.0), 1.0)

    def get_personality_insights(self, text: str) -> Dict[str, Any]:
        """วิเคราะห์บุคลิกภาพจากภาษาที่ใช้"""
        
        text_lower = text.lower()
        insights = {
            'dominant_traits': [],
            'cognitive_functions': [],
            'stress_indicators': [],
            'communication_style': '',
        }

        # วิเคราะห์ traits
        for pattern, mapping in self.PERSONALITY_INDICATORS.items():
            if re.search(pattern, text_lower):
                insights['dominant_traits'].append(mapping['trait'])
                insights['cognitive_functions'].append(mapping['cognitive'])

        # วิเคราะห์ stress indicators
        stress_words = ['เครียด', 'กดดัน', 'เหนื่อย', 'ท้อ', 'หมดแรง']
        if any(word in text_lower for word in stress_words):
            insights['stress_indicators'].append('high_stress')

        # กำหนด communication style
        if len(insights['dominant_traits']) >= 2:
            insights['communication_style'] = 'complex_emotional'
        elif insights['dominant_traits']:
            insights['communication_style'] = 'emotionally_expressive'
        else:
            insights['communication_style'] = 'task_oriented'

        return insights

    def validate_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """ตรวจสอบความถูกต้องของ Spec ก่อนใช้งาน"""
        
        required_fields = ['goal', 'depth', 'format', 'constraints']
        validation_errors = []

        for field in required_fields:
            if field not in spec:
                validation_errors.append(f"Missing required field: {field}")

        # Validate depth
        valid_depths = ['surface', 'analysis', 'blueprint', 'master']
        if spec.get('depth') not in valid_depths:
            validation_errors.append(f"Invalid depth: {spec.get('depth')}")

        # Validate constraints is list of strings
        if not isinstance(spec.get('constraints'), list):
            validation_errors.append("Constraints must be a list")
        else:
            for constraint in spec['constraints']:
                if not isinstance(constraint, str):
                    validation_errors.append(f"Constraint must be string: {constraint}")

        return {
            'is_valid': len(validation_errors) == 0,
            'errors': validation_errors,
            'spec': spec
        }


# Test Cases
def run_tests():
    """รันชุดทดสอบเพื่อตรวจสอบความถูกต้อง"""
    
    decoder = LatentIntentDecoder()
    
    # Test Case 1: คำสั่งสั้นๆ แต่มีความหมายลึกซึ้ง
    test1_input = "เอาแบบเดิม ลึกๆ ไม่ชุ่ย จัดมา"
    test1_result = decoder.decode(test1_input, history=[], user_profile={})
    
    expected_1 = {
        'goal': 'match_previous',
        'depth': 'blueprint',
        'constraints': ['production_ready'],
        'urgency_high': True,
        'must_ask': None,
    }
    
    print("Test 1: 'เอาแบบเดิม ลึกๆ ไม่ชุ่ย จัดมา'")
    print(f"Result: {test1_result}")
    print(f"Goal matches: {test1_result['goal'] == expected_1['goal']}")
    print(f"Depth matches: {test1_result['depth'] == expected_1['depth']}")
    print(f"Urgency matches: {test1_result['urgency_high'] == expected_1['urgency_high']}")
    print(f"Must ask is None: {test1_result['must_ask'] is None}")
    print(f"Has production_ready constraint: {'production_ready' in test1_result['constraints']}")
    print("-" * 50)
    
    # Test Case 2: วิเคราะห์บุคลิกภาพ
    test2_input = "ผมคิดมากเรื่องนี้มาก กังวลว่าจะผิดพลาด"
    test2_result = decoder.decode(test2_input, history=[], user_profile={})
    
    print("Test 2: 'ผมคิดมากเรื่องนี้มาก กังวลว่าจะผิดพลาด'")
    print(f"Personality traits: {test2_result['personality_traits']}")
    print(f"Cognitive patterns: {test2_result['cognitive_patterns']}")
    print(f"Has overthinking: {'overthinking' in test2_result['personality_traits']}")
    print(f"Has Ti_Ni_loop: {'Ti_Ni_loop' in test2_result['cognitive_patterns']}")
    print("-" * 50)
    
    # Test Case 3: มีประวัติการสนทนา
    test3_input = "เอาแบบนั้น แต่ละเอียดกว่านี้"
    test3_history = ["งานที่แล้วชุ่ยไปหน่อย"]
    decoder.decode("สร้างระบบใหม่", history=test3_history, user_profile={})  # สร้าง context
    test3_result = decoder.decode(test3_input, history=test3_history, user_profile={})
    
    print("Test 3: 'เอาแบบนั้น แต่ละเอียดกว่านี้' (มี history)")
    print(f"Constraints: {test3_result['constraints']}")
    print(f"Has edge_cases_included: {'edge_cases_included' in test3_result['constraints']}")
    print(f"Has triple_check_required: {'triple_check_required' in test3_result['constraints']}")
    print("-" * 50)
    
    # Test Case 4: Personality Insights
    test4_input = "ฉันเบื่อมาก อัดอั้นกับงานนี้สุดๆ"
    test4_insights = decoder.get_personality_insights(test4_input)
    
    print("Test 4: Personality Insights")
    print(f"Traits: {test4_insights['dominant_traits']}")
    print(f"Style: {test4_insights['communication_style']}")
    print(f"Has boredom: {'boredom' in test4_insights['dominant_traits']}")
    print(f"Has frustration: {'frustration' in test4_insights['dominant_traits']}")
    print("-" * 50)
    
    # Test Case 5: Validation
    test5_spec = decoder.decode("วางแผนกลยุทธ์ธุรกิจ ลึกๆ ไม่ชุ่ย", history=[], user_profile={})
    test5_validation = decoder.validate_spec(test5_spec)
    
    print("Test 5: Spec Validation")
    print(f"Is valid: {test5_validation['is_valid']}")
    print(f"Errors: {test5_validation['errors']}")
    print("-" * 50)
    
    print("\n=== สรุปผลการทดสอบ ===")
    all_passed = (
        test1_result['goal'] == 'match_previous' and
        test1_result['depth'] == 'blueprint' and
        test1_result['urgency_high'] is True and
        test1_result['must_ask'] is None and
        'production_ready' in test1_result['constraints'] and
        'overthinking' in test2_result['personality_traits'] and
        'edge_cases_included' in test3_result['constraints'] and
        test5_validation['is_valid'] is True
    )
    
    if all_passed:
        print("✅ ทุกการทดสอบผ่าน! Latent Intent Decoder พร้อมใช้งาน Production")
    else:
        print("❌ มีการทดสอบที่ไม่ผ่าน ต้องตรวจสอบ")
    
    return all_passed


if __name__ == "__main__":
    run_tests()
