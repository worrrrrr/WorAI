# GEMINI.md - WorAI Project Instructions

WorAI is a Thai-language AI system designed to handle 50+ unique intent types using a custom routing and tool execution architecture. It utilizes internal knowledge bases, specialized tools (math, astrology, analysis), and LLM fallback.

## Project Overview

- **Name:** WorAI (internal: "fools")
- **Main Technologies:** Python 3.10+, Pydantic, YAML, Pytest.
- **Core Goal:** Provide a modular, rule-based AI that can route Thai language queries to specific tools or LLM summarization.

## Architecture

1.  **Intent Classification (`src/core/router.py`):**
    - Uses `config/intents.yaml` for intent definitions and `config/rules.yaml` for regex-based matching patterns.
    - Routes user input to specific `route_type` (e.g., `tool_only`, `tool_then_llm`, `llm_summary`, `direct`).
2.  **Execution Planning (`src/domain/planner.py`):**
    - Orchestrates the execution of tools based on the classified intent.
    - Uses `ToolRegistry` to manage available tools.
3.  **Tool System (`src/tools/`):**
    - Modular tools for various tasks: `fact_retriever`, `math`, `comparator`, `astrology_analyzer`, `chart_generator`, `tax_calculator`, etc.
    - `tool_fact_retriever` reads from the internal knowledge base in `data/knowledge/`.
    - `tool_tax_calculator` calculates Thai personal income tax.
    - `tool_knowledge_synthesizer` reads logs/KB to automate rule generation.
4.  **Knowledge Base (`data/knowledge/`):**
    - Markdown files organized by topic (e.g., `common.md`, `python.md`, `astrology.md`).
    - Uses headers (`#` and `##`) for retrieval by `tool_fact_retriever`.

## Building and Running

- **Environment:** Requires Python 3.10 or higher.
- **Install Dependencies:**
  ```bash
  pip install pydantic pyyaml
  ```
- **Run the Application:**
  ```bash
  python main.py
  ```
- **Run Tests:**
  ```bash
  pytest
  ```

## Development Conventions

- ** Thai Language Support:** Ensure all user-facing strings and knowledge base content support Thai.
- **Path Management:** Always use `Path(__file__).parent` or relative paths from the root. Never hardcode absolute paths.
- **Type Safety:** Use `pydantic` for data models and `typing` for function signatures.
- **Configuration:** Intent types and matching rules are stored in `config/*.yaml`. Do not hardcode rules in the router.
- **Knowledge Base:** Follow the markdown header format for new knowledge entries in `data/knowledge/`.
- **Imports:** 
  1. Standard library
  2. Third-party (e.g., `pydantic`, `yaml`)
  3. Internal modules (e.g., `src.core`, `src.utils`)
- **Logging:** Use the logger provided by `src.utils.get_logger`.

## Key Files

- `main.py`: Entry point and CLI loop.
- `config/intents.yaml`: Definitions of all supported intents.
- `config/rules.yaml`: Regex patterns for intent classification.
- `src/core/router.py`: Logic for matching input to intents.
- `src/domain/planner.py`: Logic for tool orchestration.
- `src/tools/`: Directory containing all specialized tool implementations.
- `data/knowledge/`: Directory containing topic-specific knowledge in Markdown.
- `AGENTS.md`: High-level instructions for AI agents (Claude/Cursor).
