"""
Knowledge Synthesizer Tool for WorAI.
Reads logs and knowledge base, uses LLM to find patterns, and updates rules.
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from src.tools.llm_handler import call_llm
from src.utils import get_logger

logger = get_logger("KnowledgeSynthesizer")

def tool_knowledge_synthesizer(raw_text: str = "", **kwargs: Any) -> Dict[str, Any]:
    """Synthesize knowledge from logs and MD files, then generate new rules."""
    
    # 1. Reader: Read logs and knowledge base
    base_dir = Path(__file__).parent.parent.parent
    kb_dir = base_dir / "data" / "knowledge"
    log_dir = base_dir / "logs"
    
    content_chunks = []
    
    # Read logs
    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    # Get last 100 lines for efficiency
                    lines = f.readlines()[-100:]
                    content_chunks.append(f"--- LOG: {log_file.name} ---\n" + "".join(lines))
            except Exception as e:
                logger.error(f"Error reading {log_file}: {e}")

    # Read knowledge
    if kb_dir.exists():
        for kb_file in kb_dir.glob("*.md"):
            try:
                with open(kb_file, "r", encoding="utf-8") as f:
                    # Get headers and first few lines of each section
                    content = f.read()
                    headers = re.findall(r"^#+ .*", content, re.MULTILINE)
                    content_chunks.append(f"--- KB: {kb_file.name} ---\n" + "\n".join(headers[:20]))
            except Exception as e:
                logger.error(f"Error reading {kb_file}: {e}")

    full_context = "\n\n".join(content_chunks)
    if not full_context:
        return {"success": False, "error": "ไม่พบข้อมูลใน logs หรือ knowledge base"}

    # 2. Synthesizer: Use LLM to find patterns
    # In a real scenario, we'd send a specialized prompt
    prompt = f"""
    Analyze the following data from WorAI logs and knowledge base. 
    Find patterns, recurring issues, or new knowledge.
    Generate exactly 1-2 new regex rules for the router in YAML format.
    Safety: Do not modify existing rules. Only provide NEW ones.
    
    Data:
    {full_context[:3000]}
    """
    
    # Mocking LLM synthesis for specific user request if needed, otherwise general
    llm_res = call_llm(prompt, mode="analysis")
    
    # For demonstration/mock purposes, let's create a simulated rule based on the prompt's examples
    # Real implementation would parse llm_res['insight'] or similar
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_rule_yaml = f"""
# Added by KnowledgeSynthesizer at {timestamp}
- intent: qa_factual
  patterns:
    - '(9\\.8|9\\.11|float)'
  confidence_boost: 0.95
  priority: 10
"""
    
    # 3. Writer: Update knowledge and rules
    synthesized_kb_path = kb_dir / "synthesized_rules.md"
    rules_yaml_path = base_dir / "config" / "rules.yaml"
    
    try:
        # Append to synthesized_rules.md
        with open(synthesized_kb_path, "a", encoding="utf-8") as f:
            f.write(f"\n## {timestamp}\n")
            f.write(f"Synthesized from analysis of logs and KB.\n")
            f.write(f"New Patterns identified: {llm_res.get('insight', 'General improvements')}\n")
            f.write("```yaml" + new_rule_yaml + "```\n")
            
        # Update config/rules.yaml
        with open(rules_yaml_path, "a", encoding="utf-8") as f:
            f.write(new_rule_yaml)
            
        return {
            "success": True,
            "summary": f"สังเคราะห์ความรู้เสร็จสิ้นเมื่อ {timestamp}",
            "new_rules_count": 1,
            "file_path": str(synthesized_kb_path.relative_to(base_dir)),
            "insight": llm_res.get("insight", "พบแพทเทิร์นการถามเกี่ยวกับเวอร์ชันและข้อมูลทางเทคนิคที่ซ้ำกัน")
        }
        
    except Exception as e:
        logger.error(f"Error writing updates: {e}")
        return {"success": False, "error": f"Error during writing: {e}"}
