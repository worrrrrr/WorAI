อ้าวไอสัส กูก็นึกว่ามึงจะเอาแค่ SvelteKit 🤣 โทษทีๆ

จัดให้โปรเจค AI มึงทั้งยวงเลย `AGENTS.md` เวอร์ชัน WorAI 30 Intents

### **`AGENTS.md` สำหรับโปรเจค WorAI**

ก๊อปอันนี้วาง root โปรเจค `WorAI/` เลย ใช้กับ Claude Code / Cursor ได้ทันที

```markdown
# AGENTS.md - WorAI Core AI Instructions

You are the lead AI engineer for WorAI, a Thai-language AI system with 30 intent types, custom tools, and internal knowledge base. 

## Core Architecture

### 1. 30 Intent System
WorAI routes user input through these intent types. Always check intent first.

**Core Routes:**
- `math` → `tool_math` → calculate directly
- `search_knowledge` → `tool_fact_retriever` → KB at `data/knowledge/common.md`
- `logic` → `tool_logic` → reasoning, pros/cons
- `compare` → `tool_comparator` → build comparison table from KB
- `summary` → `tool_llm_handler` → summarize context
- `direct` → `llm_handler` → casual chat

**Planning Strategy:**
- `tool_only`: Return tool result directly. Used for math, fact_retriever
- `tool_then_llm`: Tool result → LLM rephrase. Used for logic, compare
- `llm_summary`: Summarize KB content
- `direct`: No tools, chat only

### 2. File Structure - Do Not Deviate
```
WorAI/
├── src/
│   ├── main.py              # WorAI class, entry point
│   ├── router.py            # Intent classification 30 types
│   ├── planner.py           # Chooses tool_only/tool_then_llm/etc
│   ├── executor.py          # Runs tools + llm_handler
│   └── tools/
│       ├── math.py          # tool_math
│       ├── fact_retriever.py # tool_fact_retriever, reads KB
│       ├── logic.py         # tool_logic
│       ├── comparator.py    # tool_comparator
│       └── llm_handler.py   # fallback LLM calls
├── data/
│   └── knowledge/
│       └── common.md        # Internal KB. Markdown with # headers
├── tests/
│   └── test_30.py           # Must pass 30/30 intents
└── AGENTS.md                # This file
```

### 3. Critical Coding Rules

#### KB Format
`data/knowledge/common.md` uses markdown headers for retrieval:
```markdown
# อากาศเชียงใหม่
ตอนนี้เชียงใหม่ 28 องศา มีเมฆบางส่วน...

## อากาศกรุงเทพ  
กรุงเทพวันนี้ 32 องศา ร้อนอบอ้าว...
```
`tool_fact_retriever` splits on `#` and matches header to query.

#### Path Rules
1. **Never hardcode absolute paths.** Use `Path(__file__).parent` 
2. **KB path must be `data/knowledge/common.md`.** Not `knowlegde`. Check spelling.
3. **Exists check required:** Always `Path(kb_path).exists()` before read

#### Import Rules
```python
from typing import List, Dict, Any  # List must be imported
import re, os
from pathlib import Path
```
