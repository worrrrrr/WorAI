"""
Pure Math Calculation Tool for WorAI Engine.
Fixed: SymPy solve() API usage and basic percentage handling.
"""

import logging
import re
from typing import Any, Dict, Optional, Union

from sympy import Eq, N, simplify, sympify, solve as sympy_solve
from sympy.parsing.sympy_parser import parse_expr

logger = logging.getLogger(__name__)

def _format_result(value: Any) -> Union[int, float, str]:
    """Format numeric results: round floats and keep algebraic strings."""
    try:
        if hasattr(value, 'is_number') and value.is_number:
            float_val = float(N(value))
            rounded = round(float_val, 4)
            return int(rounded) if rounded.is_integer() else rounded
        return str(value)
    except Exception:
        return str(value)

def tool_math(
    expression: Optional[str] = None,
    raw_text: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Perform safe mathematical calculations and algebraic simplifications."""
    try:
        # 1. Input Cleaning
        input_text = (expression or raw_text or "").strip()
        if not input_text:
            return {"success": False, "error": "ไม่พบนิพจน์"}

        # Remove common Thai prefixes/suffixes
        for pat in [r'^(คำนวณ|แก้สมการ|ลดรูป|หาค่า|ค่า|คิด|เท่ากับ)\s*', r'\s*(ให้หน่อย|หน่อย|ครับ|ค่ะ|นะ|ที|ให้ที)$']:
            input_text = re.sub(pat, "", input_text, flags=re.IGNORECASE)
        input_text = input_text.strip()
        
        if not input_text:
            return {"success": False, "error": "ไม่พบนิพจน์คณิตศาสตร์"}

        # 2. Handle Basic Percentage (e.g., 1500 + 25%)
        # Convert "A + B%" to "A + A * (B/100)" for standard arithmetic
        pct_match = re.match(r"^([\d.]+)\s*([+\-*/])\s*([\d.]+)\s*%$", input_text)
        if pct_match:
            base = float(pct_match.group(1))
            op = pct_match.group(2)
            percent = float(pct_match.group(3))
            
            if op == '+': result = base + (base * percent / 100)
            elif op == '-': result = base - (base * percent / 100)
            elif op == '*': result = base * (percent / 100)
            elif op == '/': 
                if percent == 0: return {"success": False, "error": "หารด้วยศูนย์ไม่ได้"}
                result = base / (percent / 100)
            else: result = base
            
            return {"success": True, "result": _format_result(result), "type": "percentage"}

        # 3. Normalize Symbols
        normalized = input_text.replace("^", "**").replace("÷", "/").replace("×", "*")
        
        # Handle implicit multiplication (e.g., 2x -> 2*x)
        normalized = re.sub(r"(\d)([a-zA-Z(])", r"\1*\2", normalized)
        normalized = re.sub(r"([a-zA-Z)])(\d)", r"\1*\2", normalized)

        # 4. Equation Solving (if '=' exists)
        if "=" in normalized:
            parts = normalized.split("=", 1)
            if len(parts) == 2:
                try:
                    left_side = sympify(parts[0].strip())
                    right_side = sympify(parts[1].strip())
                    eq = Eq(left_side, right_side)
                    
                    # ✅ FIX: Use sympy.solve(eq) instead of eq.solve()
                    sol = sympy_solve(eq, dict=True)
                    
                    if not sol:
                        return {"success": False, "error": "ไม่พบคำตอบ"}
                    
                    results = [_format_result(val) for s in sol for val in s.values()]
                    return {"success": True, "result": str(results), "type": "equation"}
                except Exception as e:
                    logger.error("Equation error: %s", e)
                    return {"success": False, "error": "แก้สมการไม่ได้"}

        # 5. General Arithmetic / Algebra Simplification
        try:
            parsed = parse_expr(normalized, evaluate=False)
            simplified = simplify(parsed)
            return {"success": True, "result": _format_result(simplified), "type": "calculation"}
        except Exception as e:
            logger.error("Calculation error: %s", e)
            return {"success": False, "error": "นิพจน์ไม่ถูกต้อง"}

    except Exception as e:
        logger.exception("Unexpected math error: %s", e)
        return {"success": False, "error": "ระบบคำนวณขัดข้อง"}