import re, os, yaml
from typing import Dict, List
from src.utils import get_logger
from src.core.types import RouteDecision

class IntentRouter:
    def __init__(self, intents_path: str = "config/intents.yaml", rules_path: str = "config/rules.yaml"):
        self.logger = get_logger("IntentRouter")
        self.intents: Dict[str, dict] = {}
        self.intent_rules: List[dict] = []
        self._load_intents(intents_path)
        self._load_rules(rules_path) # << เปลี่ยนเป็นอ่านไฟล์เดียว

    def _load_intents(self, path: str):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                for intent in data:
                    self.intents[intent["code"]] = intent
            self.logger.info(f"Loaded {len(self.intents)} intents")

    def _load_rules(self, path: str):
        """อ่าน rules จากไฟล์เดียว"""
        if not os.path.exists(path):
            self.logger.error(f"Rules file not found: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f)
            for rule in rules:
                compiled = [re.compile(p, re.IGNORECASE) for p in rule.get("patterns", []) if p]
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
        self.logger.info(f"Loaded {len(self.intent_rules)} rules")

    def classify(self, text: str) -> RouteDecision:
        text_lower = text.lower().strip()
        self.logger.info(f"🔍 Classifying: '{text}'")

        # วนตาม priority เจอตัวแรกที่ match หยุดเลย
        for rule in self.intent_rules:
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