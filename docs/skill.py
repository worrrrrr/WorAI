"""
Skill Registry Module for Personal Hub
Manages skills, tools, and provides fuzzy matching capabilities
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher

class SkillRegistry:
    """Skill Registry - จัดการ skills และรองรับ fuzzy matching"""
    
    def __init__(self):
        self._skills = []
        self._doc_path = Path(__file__).parent / 'skill.md'
        self._load_skills()
    
    def _load_skills(self):
        """Parse skill.md และแยก skills"""
        if not self._doc_path.exists():
            self._skills = self._get_default_skills()
            return
        
        content = self._doc_path.read_text(encoding='utf-8')
        
        # หา skill blocks ใน markdown
        skill_pattern = r'###\s*Skill:\s*(.+?)\n(.*?)(?=###\s*Skill:|$)'
        matches = re.findall(skill_pattern, content, re.DOTALL)
        
        if matches:
            for name, desc in matches:
                skill = self._parse_skill_block(name.strip(), desc.strip())
                if skill:
                    self._skills.append(skill)
        else:
            self._skills = self._get_default_skills()
    
    def _parse_skill_block(self, name: str, description: str) -> Optional[Dict]:
        """Parse skill block จาก markdown"""
        # แยก keywords
        keywords_match = re.search(r'Keywords:\s*(.+)', description)
        keywords = []
        if keywords_match:
            keywords = [k.strip() for k in keywords_match.group(1).split(',')]
        
        # แยก input/output
        input_match = re.search(r'Input:\s*(.+)', description)
        output_match = re.search(r'Output:\s*(.+)', description)
        
        return {
            'name': name,
            'description': description.split('\n')[0],
            'keywords': keywords,
            'input': input_match.group(1).strip() if input_match else 'any',
            'output': output_match.group(1).strip() if output_match else 'text'
        }
    
    def _get_default_skills(self) -> List[Dict]:
        """Default skills ถ้าไม่มีไฟล์"""
        return [
            {
                'name': 'Tech Trend Analyzer',
                'description': 'วิเคราะห์เทคโนโลยีที่กำลังมาแรง',
                'keywords': ['เทรนด์', 'เทคโนโลยี', 'วิเคราะห์', 'trend', 'tech'],
                'input': 'topic or query',
                'output': 'trend analysis report'
            },
            {
                'name': 'Code Generator',
                'description': 'สร้างโค้ดอัตโนมัติ',
                'keywords': ['สร้าง', 'โค้ด', 'generate', 'code', 'build'],
                'input': 'requirements',
                'output': 'source code'
            },
            {
                'name': 'Bug Fixer',
                'description': 'แก้ไขข้อผิดพลาดในโค้ด',
                'keywords': ['แก้', 'บั๊ก', 'error', 'fix', 'debug'],
                'input': 'error message or code',
                'output': 'fixed code'
            },
            {
                'name': 'Design Builder',
                'description': 'สร้าง UI ตาม design system',
                'keywords': ['design', 'ui', 'layout', 'สร้าง', 'ออกแบบ'],
                'input': 'design requirements',
                'output': 'UI components'
            }
        ]
    
    def get_all_skills(self) -> List[Dict]:
        """คืนค่า skills ทั้งหมด"""
        return self._skills
    
    def find_skill(self, query: str, threshold: float = 0.4) -> Optional[Dict]:
        """ค้นหา skill ด้วย fuzzy matching"""
        query_lower = query.lower()
        best_match = None
        best_score = 0.0
        
        for skill in self._skills:
            # ตรวจสอบชื่อ
            name_score = SequenceMatcher(None, query_lower, skill['name'].lower()).ratio()
            
            # ตรวจสอบ keywords
            keyword_scores = [
                SequenceMatcher(None, query_lower, kw.lower()).ratio()
                for kw in skill.get('keywords', [])
            ]
            max_keyword_score = max(keyword_scores) if keyword_scores else 0.0
            
            # คะแนนสูงสุดจากชื่อหรือ keywords
            score = max(name_score, max_keyword_score)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = skill.copy()
                best_match['confidence'] = round(score, 2)
        
        return best_match
    
    def find_skills(self, query: str, limit: int = 5, threshold: float = 0.3) -> List[Dict]:
        """ค้นหา multiple skills ที่เกี่ยวข้อง"""
        results = []
        
        for skill in self._skills:
            match = self.find_skill(query, threshold)
            if match and match['name'] == skill['name']:
                results.append(match)
        
        # เรียงตาม confidence
        results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return results[:limit]
    
    def get_skill_by_name(self, name: str) -> Optional[Dict]:
        """ดึง skill ตามชื่อตรงๆ"""
        for skill in self._skills:
            if skill['name'].lower() == name.lower():
                return skill.copy()
        return None
    
    def validate(self) -> bool:
        """ตรวจสอบว่า skills โหลดสำเร็จ"""
        return len(self._skills) > 0


# Singleton instance
_skill_registry_instance = None

def get_skill_registry() -> SkillRegistry:
    """Get singleton SkillRegistry instance"""
    global _skill_registry_instance
    if _skill_registry_instance is None:
        _skill_registry_instance = SkillRegistry()
    return _skill_registry_instance
