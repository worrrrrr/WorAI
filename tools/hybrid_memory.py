"""
Hybrid Memory System - ระบบความจำครบวงจร 3 ชั้น
1. Working Memory (Context Window): ความจำชั่วคราวในการสนทนาปัจจุบัน
2. Short-Term Cache: เก็บ context ย้อนหลัง 5-10_turns พร้อมสรุปอัตโนมัติ
3. Long-Term Profile: บันทึกข้อมูลผู้ใช้ถาวร (นิสัย, ความชอบ, pattern)
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque
import re


@dataclass
class MemoryEntry:
    """โครงสร้างข้อมูลความจำแต่ละรายการ"""
    id: str
    timestamp: float
    content: str
    category: str  # 'fact', 'preference', 'pattern', 'context', 'summary'
    importance: float  # 0.0-1.0
    expiry_turns: int  # จำนวน turn ก่อนหมดอายุ (-1 = ถาวร)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MemoryEntry':
        return cls(**data)


class WorkingMemory:
    """
    ชั้นที่ 1: Context Window
    เก็บการสนทนาปัจจุบันแบบ Sliding Window
    """
    
    def __init__(self, max_tokens: int = 4000, max_turns: int = 20):
        self.max_tokens = max_tokens
        self.max_turns = max_turns
        self.turns: deque = deque(maxlen=max_turns)
        self.current_token_count = 0
        
    def add_turn(self, role: str, content: str, metadata: Optional[Dict] = None):
        """เพิ่มการสนทนาใหม่"""
        turn = {
            'role': role,  # 'user' หรือ 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'token_count': self._estimate_tokens(content),
            'metadata': metadata or {}
        }
        
        # ลบ turn เก่าถ้าเกิน limit
        while self.current_token_count + turn['token_count'] > self.max_tokens and len(self.turns) > 0:
            old_turn = self.turns.popleft()
            self.current_token_count -= old_turn['token_count']
        
        self.turns.append(turn)
        self.current_token_count += turn['token_count']
        
    def get_context(self, include_system_prompt: bool = True) -> List[Dict]:
        """ดึง context ปัจจุบันสำหรับส่งให้ LLM"""
        context = []
        if include_system_prompt:
            context.append({
                'role': 'system',
                'content': self._generate_system_prompt()
            })
        context.extend(list(self.turns))
        return context
    
    def get_recent_turns(self, n: int = 5) -> List[Dict]:
        """ดึงการสนทนาล่าสุด n turns"""
        return list(self.turns)[-n:]
    
    def clear(self):
        """ล้างความจำชั่วคราว"""
        self.turns.clear()
        self.current_token_count = 0
        
    def _estimate_tokens(self, text: str) -> int:
        """ประมาณจำนวน tokens (อย่างง่าย: 1 token ≈ 4 characters)"""
        return len(text) // 4 + 1
    
    def _generate_system_prompt(self) -> str:
        """สร้าง system prompt จาก context ปัจจุบัน"""
        return f"You are an AI assistant with access to {len(self.turns)} recent conversation turns. Maintain context and provide consistent responses."


class ShortTermCache:
    """
    ชั้นที่ 2: Short-Term Cache
    เก็บ context ย้อนหลังพร้อมระบบสรุปอัตโนมัติ
    """
    
    def __init__(self, max_entries: int = 50, auto_summary_threshold: int = 10):
        self.max_entries = max_entries
        self.auto_summary_threshold = auto_summary_threshold
        self.entries: deque = deque(maxlen=max_entries)
        self.summaries: List[Dict] = []
        
    def add_entry(self, content: str, category: str = 'context', 
                  importance: float = 0.5, metadata: Optional[Dict] = None):
        """เพิ่ม entry ใหม่"""
        entry = MemoryEntry(
            id=self._generate_id(content),
            timestamp=datetime.now().timestamp(),
            content=content,
            category=category,
            importance=importance,
            expiry_turns=5,  # หมดอายุใน 5 turns
            metadata=metadata or {}
        )
        self.entries.append(entry)
        
        # ตรวจสอบว่าต้องสรุปไหม
        if len(self.entries) >= self.auto_summary_threshold:
            self._auto_summarize()
            
    def _auto_summarize(self):
        """สรุป entries เก่าๆ เพื่อประหยัดพื้นที่"""
        if len(self.entries) < self.auto_summary_threshold:
            return
            
        # เอา entries เก่าที่สุดมาสรุป
        old_entries = list(self.entries)[:self.auto_summary_threshold // 2]
        summary_content = self._generate_summary(old_entries)
        
        summary = MemoryEntry(
            id=self._generate_id(summary_content),
            timestamp=datetime.now().timestamp(),
            content=summary_content,
            category='summary',
            importance=0.7,
            expiry_turns=20,  # สรุปอยู่ได้นานกว่า
            metadata={'source_count': len(old_entries)}
        )
        self.summaries.append(summary.to_dict())
        
        # ลบ entries ที่ถูกสรุปแล้ว
        for _ in range(len(old_entries)):
            if self.entries:
                self.entries.popleft()
                
    def _generate_summary(self, entries: List[MemoryEntry]) -> str:
        """สร้างสรุปจาก entries"""
        contents = [e.content for e in entries]
        return f"Summary of {len(contents)} interactions: " + "; ".join(contents[:5]) + ("..." if len(contents) > 5 else "")
    
    def get_relevant_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """ดึง context ที่เกี่ยวข้องกับ query"""
        # อย่างง่าย: ค้นหาด้วย keyword matching
        query_lower = query.lower()
        scored_entries = []
        
        for entry in self.entries:
            score = self._calculate_relevance(entry.content, query_lower)
            if score > 0.1:  # threshold
                scored_entries.append((score, entry))
        
        # เรียงตามคะแนน
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry.to_dict() for _, entry in scored_entries[:top_k]]
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """คำนวณความเกี่ยวข้อง (อย่างง่าย)"""
        content_lower = content.lower()
        words = query.split()
        matches = sum(1 for word in words if word in content_lower)
        return matches / len(words) if words else 0
    
    def _generate_id(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def clear_expired(self, current_turn: int):
        """ลบ entries ที่หมดอายุ"""
        self.entries = deque(
            [e for e in self.entries if e.expiry_turns == -1 or current_turn % (e.expiry_turns + 1) != 0],
            maxlen=self.max_entries
        )


class LongTermProfile:
    """
    ชั้นที่ 3: Long-Term Profile
    บันทึกข้อมูลผู้ใช้ถาวร
    """
    
    def __init__(self, storage_path: str = "data/memory/user_profile.json"):
        self.storage_path = storage_path
        self.profile: Dict[str, Any] = {
            'basic_info': {},
            'preferences': {},
            'personality_traits': {},
            'conversation_patterns': [],
            'important_facts': [],
            'learning_history': []
        }
        self._load_profile()
        
    def _load_profile(self):
        """โหลดโปรไฟล์จากไฟล์"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.profile = json.load(f)
            except:
                pass  # ใช้ default ถ้าโหลดไม่ได้
                
    def save_profile(self):
        """บันทึกโปรไฟล์ลงไฟล์"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)
            
    def update_trait(self, trait_name: str, value: Any, confidence: float = 0.8):
        """อัปเดต personality trait"""
        if 'personality_traits' not in self.profile:
            self.profile['personality_traits'] = {}
            
        current = self.profile['personality_traits'].get(trait_name, {'value': None, 'confidence': 0})
        
        # Update ด้วย weighted average
        new_confidence = min(1.0, current['confidence'] + confidence * 0.2)
        if current['value'] is None:
            new_value = value
        else:
            # ถ้าเป็นตัวเลข ใช้ average, ถ้าเป็น string ใช้ค่าล่าสุดถ้า confidence สูง
            if isinstance(current['value'], (int, float)) and isinstance(value, (int, float)):
                new_value = (current['value'] * current['confidence'] + value * confidence) / (current['confidence'] + confidence)
            elif confidence > current['confidence']:
                new_value = value
            else:
                new_value = current['value']
                
        self.profile['personality_traits'][trait_name] = {
            'value': new_value,
            'confidence': new_confidence,
            'last_updated': datetime.now().isoformat()
        }
        self.save_profile()
        
    def add_preference(self, category: str, preference: str, strength: float = 0.7):
        """เพิ่ม preference"""
        if category not in self.profile['preferences']:
            self.profile['preferences'][category] = []
            
        # ตรวจสอบว่ามีอยู่แล้วไหม
        existing = next((p for p in self.profile['preferences'][category] 
                        if p.get('item') == preference), None)
                        
        if existing:
            existing['strength'] = min(1.0, existing['strength'] + strength * 0.3)
            existing['count'] = existing.get('count', 1) + 1
        else:
            self.profile['preferences'][category].append({
                'item': preference,
                'strength': strength,
                'count': 1,
                'first_seen': datetime.now().isoformat()
            })
        self.save_profile()
        
    def add_important_fact(self, fact: str, category: str = 'fact'):
        """เพิ่มข้อเท็จจริงสำคัญ"""
        fact_entry = {
            'content': fact,
            'category': category,
            'added_at': datetime.now().isoformat(),
            'reinforced_count': 1
        }
        
        # ตรวจสอบว่ามีอยู่แล้วไหม
        existing = next((f for f in self.profile['important_facts'] 
                        if f.get('content') == fact), None)
                        
        if existing:
            existing['reinforced_count'] += 1
        else:
            self.profile['important_facts'].append(fact_entry)
            
        self.save_profile()
        
    def add_pattern(self, pattern_type: str, description: str, frequency: int = 1):
        """เพิ่ม conversation pattern"""
        pattern = {
            'type': pattern_type,
            'description': description,
            'frequency': frequency,
            'last_observed': datetime.now().isoformat()
        }
        self.profile['conversation_patterns'].append(pattern)
        
        # จำกัดจำนวน pattern
        if len(self.profile['conversation_patterns']) > 20:
            self.profile['conversation_patterns'] = self.profile['conversation_patterns'][-20:]
            
        self.save_profile()
        
    def get_profile_summary(self) -> str:
        """สร้างสรุปโปรไฟล์สำหรับใช้ใน context"""
        summary_parts = []
        
        if self.profile.get('personality_traits'):
            traits = [f"{k}: {v['value']}" for k, v in self.profile['personality_traits'].items() 
                     if v.get('confidence', 0) > 0.5]
            if traits:
                summary_parts.append(f"Personality: {', '.join(traits)}")
                
        if self.profile.get('preferences'):
            prefs = []
            for cat, items in self.profile['preferences'].items():
                strong_items = [i['item'] for i in items if i.get('strength', 0) > 0.6]
                if strong_items:
                    prefs.append(f"{cat}: {', '.join(strong_items)}")
            if prefs:
                summary_parts.append(f"Preferences: {'; '.join(prefs)}")
                
        if self.profile.get('important_facts'):
            facts = [f['content'] for f in self.profile['important_facts'][-5:]]
            if facts:
                summary_parts.append(f"Key Facts: {'; '.join(facts)}")
                
        return " | ".join(summary_parts) if summary_parts else "No long-term memory yet"
    
    def extract_insights_from_conversation(self, user_input: str, response: str) -> Dict:
        """วิเคราะห์การสนทนาเพื่อหา insights สำหรับอัปเดตโปรไฟล์"""
        insights = {
            'traits_to_update': {},
            'preferences_to_add': [],
            'facts_to_remember': [],
            'patterns_to_record': []
        }
        
        # ตัวอย่าง: ตรวจจับ pattern การพูด
        if re.search(r'คิดมาก|กังวล|เครียด', user_input):
            insights['traits_to_update']['anxiety_level'] = ('high', 0.7)
            insights['patterns_to_record'].append(('stress_indicator', user_input[:50]))
            
        if re.search(r'ไม่ชุ่ย|ละเอียด|production', user_input):
            insights['preferences_to_add'].append(('work_style', 'detail_oriented'))
            insights['traits_to_update']['conscientiousness'] = ('high', 0.8)
            
        if re.search(r'เอาแบบเดิม|ที่เคยทำ|เหมือนเก่า', user_input):
            insights['patterns_to_record'].append(('consistency_seeker', 'prefers_consistent_output'))
            
        # ตรวจจับข้อเท็จจริงสำคัญ (ตัวอย่างง่ายๆ)
        if re.search(r'ฉันชื่อ|ผมชื่อ|เกิดปี|ทำงานเป็น', user_input):
            insights['facts_to_remember'].append(user_input)
            
        return insights
    
    def apply_insights(self, insights: Dict):
        """นำ insights ไปอัปเดตโปรไฟล์"""
        for trait, (value, confidence) in insights.get('traits_to_update', {}).items():
            self.update_trait(trait, value, confidence)
            
        for category, item in insights.get('preferences_to_add', []):
            self.add_preference(category, item)
            
        for fact in insights.get('facts_to_remember', []):
            self.add_important_fact(fact)
            
        for pattern_type, description in insights.get('patterns_to_record', []):
            self.add_pattern(pattern_type, description)


class HybridMemoryManager:
    """
    ผู้จัดการระบบความจำครบวงจร
    รวม Working Memory + Short-Term Cache + Long-Term Profile
    """
    
    def __init__(self, user_id: str = "default", config: Optional[Dict] = None):
        self.user_id = user_id
        self.config = config or {}
        
        # Initialize ทั้ง 3 ชั้น
        self.working_memory = WorkingMemory(
            max_tokens=self.config.get('max_context_tokens', 4000),
            max_turns=self.config.get('max_context_turns', 20)
        )
        
        self.short_term_cache = ShortTermCache(
            max_entries=self.config.get('max_cache_entries', 50),
            auto_summary_threshold=self.config.get('auto_summary_threshold', 10)
        )
        
        self.long_term_profile = LongTermProfile(
            storage_path=f"data/memory/{user_id}_profile.json"
        )
        
        self.current_turn = 0
        
    def process_interaction(self, user_input: str, response: str, 
                           metadata: Optional[Dict] = None):
        """ประมวลผลการสนทนาหนึ่งรอบ"""
        self.current_turn += 1
        
        # 1. เพิ่ม vào Working Memory
        self.working_memory.add_turn('user', user_input, metadata)
        self.working_memory.add_turn('assistant', response, metadata)
        
        # 2. เพิ่มเข้า Short-Term Cache
        self.short_term_cache.add_entry(
            content=f"User: {user_input} | Assistant: {response}",
            category='context',
            importance=0.6,
            metadata={'turn': self.current_turn}
        )
        
        # 3. วิเคราะห์และอัปเดต Long-Term Profile
        insights = self.long_term_profile.extract_insights_from_conversation(user_input, response)
        self.long_term_profile.apply_insights(insights)
        
        # 4. ทำความสะอาด cache ที่หมดอายุ
        self.short_term_cache.clear_expired(self.current_turn)
        
    def get_full_context(self, query: str = "") -> List[Dict]:
        """ดึง context ครบทุกชั้นสำหรับการตอบคำถาม"""
        context = []
        
        # 1. System prompt พร้อม long-term profile
        profile_summary = self.long_term_profile.get_profile_summary()
        system_prompt = f"""You are an AI assistant with long-term memory.
User Profile: {profile_summary}
Current Turn: {self.current_turn}
Maintain consistency with previous interactions and user preferences."""
        
        context.append({'role': 'system', 'content': system_prompt})
        
        # 2. Working Memory (recent turns)
        context.extend(self.working_memory.get_context(include_system_prompt=False))
        
        # 3. Short-Term Cache (relevant context)
        if query:
            relevant = self.short_term_cache.get_relevant_context(query, top_k=3)
            for entry in relevant:
                context.append({
                    'role': 'system',
                    'content': f"[Relevant Memory] {entry['content']}"
                })
        
        return context
    
    def get_user_profile(self) -> Dict:
        """ดึงข้อมูลโปรไฟล์ผู้ใช้"""
        return self.long_term_profile.profile
    
    def search_memory(self, query: str, scope: str = 'all') -> List[Dict]:
        """ค้นหาในความจำ"""
        results = []
        
        if scope in ['all', 'short_term']:
            results.extend(self.short_term_cache.get_relevant_context(query))
            
        if scope in ['all', 'long_term']:
            # ค้นหาใน long-term profile
            profile_text = json.dumps(self.long_term_profile.profile)
            if query.lower() in profile_text.lower():
                results.append({'source': 'long_term', 'content': 'Found in profile'})
                
        return results
    
    def reset_conversation(self, keep_profile: bool = True):
        """รีเซ็ตการสนทนา แต่เก็บ profile ไว้"""
        self.working_memory.clear()
        self.short_term_cache.entries.clear()
        self.current_turn = 0
        
        if not keep_profile:
            # ล้าง long-term profile ด้วย
            self.long_term_profile.profile = {
                'basic_info': {},
                'preferences': {},
                'personality_traits': {},
                'conversation_patterns': [],
                'important_facts': [],
                'learning_history': []
            }
            self.long_term_profile.save_profile()
    
    def export_memory(self, format: str = 'json') -> str:
        """export ความจำทั้งหมด"""
        data = {
            'user_id': self.user_id,
            'current_turn': self.current_turn,
            'working_memory': list(self.working_memory.turns),
            'short_term_cache': [e.to_dict() for e in self.short_term_cache.entries],
            'summaries': self.short_term_cache.summaries,
            'long_term_profile': self.long_term_profile.profile
        }
        
        if format == 'json':
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            return str(data)


# Example Usage
if __name__ == "__main__":
    # สร้าง manager
    manager = HybridMemoryManager(user_id="user_001")
    
    # จำลองการสนทนา
    interactions = [
        ("สวัสดี ผมชื่อต้น ชอบเขียนโค้ดแบบละเอียด ไม่ชุ่ย", 
         "สวัสดีครับคุณต้น ยินดีที่ได้รู้จักครับ ผมจะจดจำสไตล์การทำงานของคุณนะครับ"),
        
        ("ช่วยวิเคราะห์ดวงให้หน่อย เอาแบบลึกๆ ไม่ชุ่ย", 
         "ได้ครับ ผมจะวิเคราะห์อย่างละเอียดให้..."),
        
        ("ผมคิดมากเรื่องงานบ่อยๆ กังวลว่าจะผิดพลาด", 
         "เข้าใจเลยครับ ความกังวลเป็นเรื่องปกติ ลองใช้เทคนิคนี้ดูนะครับ..."),
        
        ("เอาแบบเดิมที่เคยทำให้เลย", 
         "ได้ครับ ผมจะใช้รูปแบบเดียวกับครั้งก่อนให้นะครับ")
    ]
    
    print("=== Processing Interactions ===")
    for user_input, response in interactions:
        manager.process_interaction(user_input, response)
        print(f"Turn {manager.current_turn}: Processed")
    
    print("\n=== User Profile Summary ===")
    print(manager.long_term_profile.get_profile_summary())
    
    print("\n=== Full Context for Query ===")
    context = manager.get_full_context("ช่วยวิเคราะห์ดวงให้หน่อย")
    print(f"Context has {len(context)} messages")
    for msg in context[:5]:  # แสดง 5 ข้อแรก
        print(f"- {msg['role']}: {msg['content'][:100]}...")
    
    print("\n=== Search Memory ===")
    results = manager.search_memory("คิดมาก")
    print(f"Found {len(results)} results")
    
    print("\n=== Export Memory ===")
    exported = manager.export_memory()
    print(f"Exported {len(exported)} characters")
