"""
Design System Module for Personal Hub
Loads design tokens from design.md and provides programmatic access
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

class DesignSystem:
    """Design System Manager - โหลดและจัดการ Design Tokens"""
    
    def __init__(self):
        self._tokens = None
        self._doc_path = Path(__file__).parent / 'design.md'
        self._load_tokens()
    
    def _load_tokens(self):
        """Parse design.md และแยก JSON tokens"""
        if not self._doc_path.exists():
            self._tokens = self._get_default_tokens()
            return
        
        content = self._doc_path.read_text(encoding='utf-8')
        
        # หา JSON block ใน markdown
        json_match = re.search(r'```json\s*({.*?})\s*```', content, re.DOTALL)
        if json_match:
            try:
                self._tokens = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                self._tokens = self._get_default_tokens()
        else:
            self._tokens = self._get_default_tokens()
    
    def _get_default_tokens(self) -> Dict[str, Any]:
        """Default design tokens ถ้าไม่มีไฟล์"""
        return {
            "colors": {
                "primary": "#3B82F6",
                "secondary": "#8B5CF6",
                "accent": "#10B981",
                "background": "#0F172A",
                "surface": "#1E293B",
                "text": "#F8FAFC"
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            },
            "typography": {
                "fontFamily": "Inter, system-ui, sans-serif",
                "fontSize": {
                    "sm": "14px",
                    "base": "16px",
                    "lg": "18px",
                    "xl": "20px"
                }
            },
            "layouts": ["bento-grid", "sidebar", "dashboard"],
            "themes": ["dark", "light", "auto"]
        }
    
    def get_tokens(self) -> Dict[str, Any]:
        """คืนค่า design tokens ทั้งหมด"""
        return self._tokens or {}
    
    def get_color(self, name: str) -> Optional[str]:
        """ดึงค่าสีตามชื่อ"""
        colors = self._tokens.get('colors', {})
        return colors.get(name)
    
    def get_spacing(self, name: str) -> Optional[str]:
        """ดึงค่า spacing ตามชื่อ"""
        spacing = self._tokens.get('spacing', {})
        return spacing.get(name)
    
    def get_layout(self, name: str) -> Optional[Dict]:
        """ดึง layout configuration"""
        layouts = self._tokens.get('layouts', {})
        if isinstance(layouts, list):
            return {"name": name} if name in layouts else None
        return layouts.get(name)
    
    def validate(self) -> bool:
        """ตรวจสอบว่า tokens ครบถ้วน"""
        required = ['colors', 'spacing', 'typography']
        return all(key in self._tokens for key in required)


# Singleton instance
_design_system_instance = None

def get_design_system() -> DesignSystem:
    """Get singleton DesignSystem instance"""
    global _design_system_instance
    if _design_system_instance is None:
        _design_system_instance = DesignSystem()
    return _design_system_instance
