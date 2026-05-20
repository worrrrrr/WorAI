"""
Architecture Configuration Module for Personal Hub
Loads architecture specs from architect.md and provides programmatic access
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

class ArchitectureConfig:
    """Architecture Config Manager - โหลดและจัดการ Architecture Specs"""
    
    def __init__(self):
        self._config = None
        self._doc_path = Path(__file__).parent / 'architect.md'
        self._load_config()
    
    def _load_config(self):
        """Parse architect.md และแยก configuration"""
        if not self._doc_path.exists():
            self._config = self._get_default_config()
            return
        
        content = self._doc_path.read_text(encoding='utf-8')
        
        # หา JSON block ใน markdown
        json_match = re.search(r'```json\s*({.*?})\s*```', content, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                self._config = self._merge_with_defaults(parsed)
            except json.JSONDecodeError:
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()
    
    def _merge_with_defaults(self, parsed: Dict) -> Dict:
        """Merge parsed config กับ defaults"""
        defaults = self._get_default_config()
        
        # Merge layers
        if 'layers' in parsed:
            defaults['layers'] = parsed['layers']
        
        # Merge tech stack
        if 'tech_stack' in parsed:
            defaults['tech_stack'].update(parsed['tech_stack'])
        
        # Merge data flow
        if 'data_flow' in parsed:
            defaults['data_flow'] = parsed['data_flow']
        
        return defaults
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default architecture config ถ้าไม่มีไฟล์"""
        return {
            "name": "Personal Hub Architecture",
            "version": "1.0.0",
            "layers": [
                {
                    "name": "Presentation Layer",
                    "tech": ["Astro 5.0", "React Islands", "Tailwind CSS"],
                    "responsibility": "UI rendering and user interaction"
                },
                {
                    "name": "Application Layer",
                    "tech": ["Hono", "Cloudflare Workers"],
                    "responsibility": "Business logic and API endpoints"
                },
                {
                    "name": "Data Layer",
                    "tech": ["SQLite WASM", "Turso"],
                    "responsibility": "Data persistence and caching"
                },
                {
                    "name": "AI Layer",
                    "tech": ["WebLLM", "Vercel AI SDK"],
                    "responsibility": "AI inference and processing"
                }
            ],
            "tech_stack": {
                "frontend": "Astro 5.0 + Tailwind CSS v4",
                "backend": "Hono (Edge Runtime)",
                "database": "SQLite (WASM) / Turso",
                "ai": "WebLLM / Vercel AI SDK",
                "deployment": "Cloudflare Pages / Vercel"
            },
            "data_flow": [
                "User Input → Validation → Skill Routing",
                "Skill Processing → Data Fetching → Analysis",
                "Response Generation → Caching → Delivery"
            ],
            "agents": {
                "auto_generator": "Creates code from requirements",
                "self_healing": "Detects and fixes errors automatically",
                "template_curator": "Manages templates and tech trends"
            }
        }
    
    def get_stack(self) -> Dict[str, Any]:
        """คืนค่า tech stack ทั้งหมด"""
        return self._config or {}
    
    def get_layers(self) -> List[Dict]:
        """คืนค่า architecture layers"""
        return self._config.get('layers', []) if self._config else []
    
    def get_layer_by_name(self, name: str) -> Optional[Dict]:
        """ดึง layer ตามชื่อ"""
        layers = self.get_layers()
        for layer in layers:
            if layer.get('name', '').lower() == name.lower():
                return layer
        return None
    
    def get_tech_for_layer(self, layer_name: str) -> List[str]:
        """ดึงเทคโนโลยีที่ใช้ใน layer นั้นๆ"""
        layer = self.get_layer_by_name(layer_name)
        return layer.get('tech', []) if layer else []
    
    def get_agents(self) -> Dict[str, str]:
        """คืนค่า agents configuration"""
        return self._config.get('agents', {}) if self._config else {}
    
    def validate(self) -> bool:
        """ตรวจสอบว่า config ครบถ้วน"""
        if not self._config:
            return False
        
        required = ['layers', 'tech_stack', 'data_flow']
        return all(key in self._config for key in required)


# Singleton instance
_architecture_config_instance = None

def get_architecture_config() -> ArchitectureConfig:
    """Get singleton ArchitectureConfig instance"""
    global _architecture_config_instance
    if _architecture_config_instance is None:
        _architecture_config_instance = ArchitectureConfig()
    return _architecture_config_instance
