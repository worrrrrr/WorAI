import re, os, yaml, pickle, hashlib, sys
from typing import Dict, List, Optional, Set, Tuple
from src.utils import get_logger
from src.core.types import RouteDecision
from collections import defaultdict

# Global caches for Phase 2 optimizations
_pattern_cache: Dict[str, re.Pattern] = {}
_rule_index_cache: Optional[Dict[str, List[int]]] = None  # Keyword -> rule indices mapping
_config_hash_cache: Optional[str] = None  # Hash of config files for cache invalidation
_gw_cache: Optional[Dict] = None  # Greeting/quick-win cache
_config_pickle_cache: Optional[Dict] = None  # Phase 2: Config Pickle Caching

class IntentRouter:
    # Common greetings and direct responses for early exit (Phase 1: Early Exit)
    GREETINGS = {
        'สวัสดี', 'หวัดดี', 'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
        'good evening', 'อรุณสวัสดิ์', 'ราตรีสวัสดิ์', 'สบายดีไหม', 'เป็นไง', 'ว่าไง'
    }
    
    GREETING_RESPONSES = {
        's': 'สวัสดีครับ! มีอะไรให้ช่วยวันนี้บอกได้เลยนะครับ 😊',
        'm': 'สวัสดีตอนเช้าครับ! วันนี้วันดีๆ เริ่มต้นด้วยรอยยิ้มกันนะ 🌅',
        'a': 'สวัสดีตอนบ่ายครับ! ช่วงบ่ายๆ แบบนี้ดื่มกาแฟพักสมองบ้างนะครับ ☕',
        'e': 'สวัสดีตอนเย็นครับ! หลังเลิกงานพักผ่อนให้เพียงพอนะครับ 🌆',
        'n': 'สวัสดีครับ! ดึกป่านนี้ยังไม่นอนเหรอครับ ดูแลสุขภาพด้วยนะ 🌙',
        'd': 'สบายดีครับ! แล้วคุณล่ะครับ สบายดีไหม? 😊',
        'default': 'สวัสดีครับ! มีอะไรให้ช่วยวันนี้บอกได้เลยนะครับ 😊'
    }

    def __init__(self, intents_path: str = "config/intents.yaml", rules_path: str = "config/rules.yaml"):
        self.logger = get_logger("IntentRouter")
        self.intents: Dict[str, dict] = {}
        self._rules_path = rules_path
        self._intents_path = intents_path
        self._rules_loaded = False
        self.intent_rules: List[dict] = []
        self._keyword_index: Dict[str, List[int]] = {}  # Phase 2: Rule Indexing
        self._cache_file = "/tmp/worai_config_cache.pkl"  # Phase 2: Config Pickle Caching
        
        # Phase 2: Config Pickle Caching - พยายามโหลดจาก cache ก่อน
        if not self._load_from_pickle_cache():
            # ถ้าไม่มี cache หรือ cache เก่า โหลดปกติ
            self._load_intents(intents_path)
        
        # Phase 1: Lazy Load Rules - โหลด rules เมื่อจำเป็นเท่านั้น
        # ไม่โหลดตอน init เพื่อลด startup time

    def _ensure_rules_loaded(self):
        """Phase 1: Lazy Load Rules - โหลด rules เฉพาะเมื่อต้องการใช้"""
        if not self._rules_loaded:
            self._load_rules(self._rules_path)
            self._rules_loaded = True

    def _load_intents(self, path: str):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                for intent in data:
                    self.intents[intent["code"]] = intent
            self.logger.info(f"Loaded {len(self.intents)} intents")

    @staticmethod
    def _compile_pattern(pattern_str: str) -> re.Pattern:
        """Phase 1: Cache Compiled Patterns - แคช regex ที่ compile แล้ว"""
        global _pattern_cache
        if pattern_str not in _pattern_cache:
            _pattern_cache[pattern_str] = re.compile(pattern_str, re.IGNORECASE)
        return _pattern_cache[pattern_str]

    def _compute_config_hash(self) -> str:
        """Phase 2: Config Caching - คำนวณ hash ของ config files สำหรับ cache invalidation"""
        hasher = hashlib.md5()
        for path in [self._intents_path, self._rules_path]:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    hasher.update(f.read())
        return hasher.hexdigest()
    
    def _load_from_pickle_cache(self) -> bool:
        """Phase 2: Config Pickle Caching - โหลด config จาก pickle cache ถ้ามีและยังใหม่อยู่"""
        global _config_pickle_cache
        
        try:
            # ตรวจสอบว่า cache file มีอยู่ไหม
            if not os.path.exists(self._cache_file):
                self.logger.debug("No pickle cache found")
                return False
            
            # โหลด cache
            with open(self._cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # ตรวจสอบ version และ hash
            current_hash = self._compute_config_hash()
            if cache_data.get('config_hash') != current_hash:
                self.logger.debug("Cache hash mismatch, rebuilding")
                return False
            
            # ใช้ cache ได้
            self.intents = cache_data['intents']
            self.intent_rules = cache_data['intent_rules']
            self._keyword_index = cache_data.get('keyword_index', {})
            self._rules_loaded = True
            
            self.logger.info(f"✅ Loaded config from pickle cache ({len(self.intents)} intents, {len(self.intent_rules)} rules)")
            return True
            
        except Exception as e:
            self.logger.debug(f"Pickle cache load failed: {e}")
            return False
    
    def _save_to_pickle_cache(self):
        """Phase 2: Config Pickle Caching - บันทึก config ลง pickle cache"""
        try:
            cache_data = {
                'config_hash': self._compute_config_hash(),
                'intents': self.intents,
                'intent_rules': self.intent_rules,
                'keyword_index': self._keyword_index
            }
            
            with open(self._cache_file, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            self.logger.debug(f"Saved config to pickle cache ({self._cache_file})")
        except Exception as e:
            self.logger.debug(f"Pickle cache save failed: {e}")

    def _build_keyword_index(self):
        """Phase 2: Rule Indexing - สร้าง inverted index จาก keywords ไปยัง rules"""
        self._keyword_index = defaultdict(list)
        
        # Thai stop words to exclude from indexing
        thai_stopwords = {
            'ที่', 'ใน', 'บน', 'ใต้', 'เหนือ', 'ของ', 'กับ', 'และ', 'หรือ', 'แต่', 'ก็', 'คือ',
            'เป็น', 'อยู่', 'มี', 'ไม่', 'ได้', 'ให้', 'ไป', 'มา', 'ทำ', 'การ', 'ความ', 'อัน',
            'ซึ่ง', 'ว่า', 'ดัง', 'เช่น', 'ถ้า', 'หาก', 'เมื่อ', 'จน', 'ตั้งแต่', 'ถึง', 'สำหรับ'
        }
        
        for idx, rule in enumerate(self.intent_rules):
            # Extract keywords from patterns (simple extraction - can be improved with NLP)
            for pattern_obj in rule.get("patterns", []):
                if hasattr(pattern_obj, 'pattern'):
                    pattern_str = pattern_obj.pattern
                    # Extract simple words (Thai and English)
                    import re as regex_module
                    # Thai words (sequences of Thai characters)
                    thai_words = regex_module.findall(r'[\u0E00-\u0E7F]+', pattern_str)
                    # English words
                    eng_words = regex_module.findall(r'[a-zA-Z]+', pattern_str.lower())
                    
                    all_words = thai_words + eng_words
                    
                    for word in all_words:
                        if word not in thai_stopwords and len(word) > 1:
                            if idx not in self._keyword_index[word]:
                                self._keyword_index[word].append(idx)
        
        self.logger.info(f"Built keyword index with {len(self._keyword_index)} keywords")

    def _load_rules(self, path: str):
        """อ่าน rules จากไฟล์เดียว"""
        if not os.path.exists(path):
            self.logger.error(f"Rules file not found: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f)
            for rule in rules:
                # Phase 1: Cache Compiled Patterns
                compiled = [
                    self._compile_pattern(p) 
                    for p in rule.get("patterns", []) if p
                ]
                self.intent_rules.append({
                    "intent": rule["intent"],
                    "patterns": compiled,
                    "match_any": rule.get("match_any", True),
                    "confidence_boost": rule.get("confidence_boost", 0.5),
                    "route": rule.get("route", "tool_only"),
                    "tools": rule.get("tools", []),
                    "priority": rule.get("priority", 0)
                })
        # sort priority สูง -> ต่ำ
        self.intent_rules.sort(key=lambda r: (-r["priority"], r["intent"]))
        
        # Phase 2: Build keyword index after loading rules
        self._build_keyword_index()
        
        # Phase 2: Save to pickle cache after loading
        self._save_to_pickle_cache()
        
        self.logger.info(f"Loaded {len(self.intent_rules)} rules")

    def _check_greeting(self, text: str) -> Optional[RouteDecision]:
        """Phase 1: Early Exit - ตรวจสอบคำทักทายก่อนประมวลผล rules"""
        text_lower = text.lower().strip()
        
        # Check exact match first (fastest)
        if text_lower in self.GREETINGS:
            return RouteDecision(
                intent_code="greeting",
                route_type="response",
                tools_to_call=[],
                params={"raw_text": text, "response": self.GREETING_RESPONSES['default']},
                needs_clarification=False,
                confidence=1.0,
                clarification_question=None
            )
        
        # Check partial matches
        for greeting in self.GREETINGS:
            if greeting in text_lower:
                # Determine time-based response
                import datetime
                hour = datetime.datetime.now().hour
                if hour < 6:
                    response_key = 'n'
                elif hour < 12:
                    response_key = 'm'
                elif hour < 17:
                    response_key = 'a'
                elif hour < 21:
                    response_key = 'e'
                else:
                    response_key = 'n'
                
                return RouteDecision(
                    intent_code="greeting",
                    route_type="response",
                    tools_to_call=[],
                    params={"raw_text": text, "response": self.GREETING_RESPONSES.get(response_key, self.GREETING_RESPONSES['default'])},
                    needs_clarification=False,
                    confidence=0.95,
                    clarification_question=None
                )
        
        return None

    def classify(self, text: str) -> RouteDecision:
        text_lower = text.lower().strip()
        self.logger.info(f"🔍 Classifying: '{text}'")

        # Phase 1: Early Exit - ตรวจสอบคำทักทายก่อน (เร็วมาก ~0.01ms)
        greeting_result = self._check_greeting(text)
        if greeting_result:
            self.logger.info(f"✅ Greeting detected -> {greeting_result.intent_code}")
            return greeting_result

        # Phase 1: Lazy Load Rules - โหลด rules ตอนนี้เท่านั้นที่จำเป็น
        self._ensure_rules_loaded()

        # Phase 2: Rule Indexing - ใช้ keyword index เพื่อลดจำนวน rules ที่ต้องตรวจสอบ
        candidate_indices = None
        
        # Extract keywords from query
        import re as regex_module
        thai_words = regex_module.findall(r'[\u0E00-\u0E7F]+', text_lower)
        eng_words = regex_module.findall(r'[a-zA-Z]+', text_lower)
        query_words = thai_words + eng_words
        
        # Find candidate rules using keyword index
        for word in query_words:
            if word in self._keyword_index:
                if candidate_indices is None:
                    candidate_indices = set(self._keyword_index[word])
                else:
                    candidate_indices &= set(self._keyword_index[word])
        
        # If we found candidates via indexing, only check those rules
        # Otherwise, fall back to checking all rules
        rules_to_check = []
        if candidate_indices is not None and len(candidate_indices) > 0:
            rules_to_check = [self.intent_rules[i] for i in sorted(candidate_indices)]
            self.logger.debug(f"Keyword indexing reduced rules from {len(self.intent_rules)} to {len(rules_to_check)}")
        else:
            rules_to_check = self.intent_rules

        # วนตาม priority เจอตัวแรกที่ match หยุดเลย
        for rule in rules_to_check:
            if not rule["patterns"]:
                continue

            matched = False
            for pattern in rule["patterns"]:
                if pattern.search(text_lower):
                    self.logger.info(f"✅ Matched '{pattern.pattern}' -> {rule['intent']}")
                    matched = True
                    if rule["match_any"]:
                        break

            if matched:
                intent_cfg = self.intents.get(rule["intent"], {})
                return RouteDecision(
                    intent_code=rule["intent"],
                    route_type=rule["route"],
                    tools_to_call=rule["tools"],
                    params={"raw_text": text},
                    needs_clarification=(rule["route"] == "clarifier"),
                    clarification_question=intent_cfg.get("clarification_question"),
                    confidence=rule["confidence_boost"]
                )

        self.logger.warning(f"⚠️ No rule matched, fallback to unknown")
        return RouteDecision(
            "unknown", "clarifier", [], {"raw_text": text}, True, 0.1,
            "ช่วยระบุเพิ่มเติมได้ไหมครับ? 🙏"
        )