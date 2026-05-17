"""
Logic & Reasoning Tool for WorAI Engine.
Supports: Boolean Truth Tables (SymPy) and Knight/Knave Puzzles (Z3/Brute Force).
"""

import logging
import re
from typing import Any, Dict, List, Optional
from itertools import product

from sympy import sympify
from sympy.logic.boolalg import truth_table

# Optional Dependency: Z3 Solver for complex logical constraints
try:
    from z3 import Solver, Bool, BoolRef, And, Or, Not, Implies, sat
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    logging.warning("Z3 solver not found. Knight/Knave puzzles will use brute force.")

logger = logging.getLogger(__name__)

def tool_logic(raw_text: str, **kwargs: Any) -> Dict[str, Any]:
    """Main entry point for logic tasks."""
    try:
        text = raw_text.strip()
        if not text:
            return {"success": False, "error": "ไม่พบข้อความ"}

        # 1. Detect Knight/Knave Puzzles
        if re.search(r'\bsays\b', text, re.IGNORECASE) and re.search(r'\b(knight|knave)\b', text, re.IGNORECASE):
            if Z3_AVAILABLE:
                return _solve_knights_knaves_z3(text)
            else:
                return _solve_knights_knaves_brute(text)
        
        # 2. Default to Boolean Expression/Truth Table
        return _solve_boolean_expression(text)

    except Exception as e:
        logger.exception("Logic tool error: %s", e)
        return {"success": False, "error": f"เกิดข้อผิดพลาด: {str(e)}"}

def _solve_boolean_expression(text: str) -> Dict[str, Any]:
    """Generate truth table for boolean expressions using SymPy."""
    # Clean up command words
    expr_str = re.sub(r'ตรรกะ|logic|แสดงตาราง|truth table|แสดงวิธีคิด', '', text, flags=re.IGNORECASE).strip()
    
    # Map natural language to symbolic logic
    replacements = {
        r'\bAND\b': '&', r'\bOR\b': '|', r'\bNOT\b': '~', 
        r'\bXOR\b': '^', r'\bIMPLIES\b': '>>', r'\bIFF\b': '=='
    }
    for pattern, replacement in replacements.items():
        expr_str = re.sub(pattern, replacement, expr_str, flags=re.IGNORECASE)
    
    expr_str = expr_str.replace('->', '>>').replace('<->', '==')

    if not expr_str:
        raise ValueError("ไม่พบนิพจน์ตรรกะ")

    try:
        expr = sympify(expr_str)
        variables = sorted([str(s) for s in expr.free_symbols], key=str)
        
        if not variables:
            return {"success": True, "result": f"ผลลัพธ์: {expr}", "type": "boolean_eval"}

        # Generate Truth Table
        header = variables + ["Result"]
        table_lines = ["| " + " | ".join(header) + " |"]
        table_lines.append("|" + "---|" * len(header))

        for row in truth_table(expr, variables):
            # row[0] is input tuple, row[1] is output boolean
            vals = ['T' if v else 'F' for v in row[0]] + ['T' if row[1] else 'F']
            table_lines.append("| " + " | ".join(vals) + " |")

        return {
            "success": True, 
            "result": "\n".join(table_lines), 
            "type": "truth_table", 
            "engine": "sympy"
        }
    except Exception as e:
        logger.error("SymPy parsing error: %s", e)
        return {"success": False, "error": "นิพจน์ตรรกะไม่ถูกต้อง"}

def _solve_knights_knaves_z3(text: str) -> Dict[str, Any]:
    """Solve Knight/Knave puzzles using Z3 Solver."""
    text_clean = re.sub(r'แสดงวิธีคิด', '', text, flags=re.IGNORECASE)
    
    # Extract "Person says: Statement" patterns
    statements = re.findall(r'(\w+)\s+says:?\s*(.*?)(?=\s*\w+\s+says:|$)', text_clean, re.IGNORECASE | re.DOTALL)
    
    if not statements:
        return {"success": False, "error": "ไม่พบรูปแบบ 'X says: ...'"}

    people = sorted(set([s[0].upper() for s in statements]))
    z3_vars = {p: Bool(p) for p in people} # True = Knight, False = Knave

    s = Solver()
    explanation = ["🧠 ใช้ Z3 Solver แก้โจทย์ตรรกะ:", "กำหนดให้ True = Knight (พูดจริง), False = Knave (พูดโกหก)\n"]

    for person, stmt in statements:
        p_var = z3_vars[person.upper()]
        explanation.append(f"👤 {person} กล่าวว่า: '{stmt.strip()}'")
        
        stmt_z3 = _build_z3_expr(stmt.strip().rstrip('.'), z3_vars, person.upper())
        
        if stmt_z3 is None:
            explanation.append(f"   ⚠️ ไม่สามารถแปลงประโยคนี้ได้ ข้ามไป")
            continue

        # Core Logic: Person is Knight IFF Statement is True
        s.add(p_var == stmt_z3)
        explanation.append(f"   ✅ Constraint: {person} == ({stmt_z3})")

    explanation.append("\n⏳ กำลังคำนวณคำตอบ...")
    
    if s.check() == sat:
        m = s.model()
        result = []
        for p in people:
            status = "Knight 🛡️" if m.evaluate(z3_vars[p]) else "Knave 🤥"
            result.append(f"{p}: {status}")
        
        explanation.append("\n✅ คำตอบที่สอดคล้องกับทุกเงื่อนไข:")
        explanation.extend(result)
        return {"success": True, "result": "\n".join(explanation), "type": "knight_knave", "engine": "z3"}
    else:
        explanation.append("\n❌ UNSAT: โจทย์ขัดแย้งกันเอง ไม่มีคำตอบที่เป็นไปได้")
        return {"success": True, "result": "\n".join(explanation), "type": "knight_knave", "engine": "z3"}

def _build_z3_expr(stmt: str, z3_vars: Dict[str, BoolRef], speaker: str) -> BoolRef:
    """แปลงประโยคเป็น Z3 Expression - แก้บัค bool แล้ว"""
    stmt = stmt.lower()

    # 1. X is a knight/knave
    m = re.match(r'(\w+)\s+is\s+a\s+(knight|knave)', stmt)
    if m:
        person, role = m.groups()
        var = z3_vars.get(person.upper())
        if var is None:  # <<<< แก้ตรงนี้ จาก if not var
            return None
        return var if role == 'knight' else Not(var)

    # 2. X and Y are knaves/knights
    m = re.match(r'(\w+)\s+and\s+(\w+)\s+are\s+(knights|knaves)', stmt)
    if m:
        p1, p2, role = m.groups()
        v1 = z3_vars.get(p1.upper())
        v2 = z3_vars.get(p2.upper())
        if v1 is None or v2 is None:  # <<<< แก้ตรงนี้ด้วย
            return None
        return And(v1, v2) if role == 'knights' else And(Not(v1), Not(v2))

    # 3. X or Y is a knight/knave
    m = re.match(r'(\w+)\s+or\s+(\w+)\s+is\s+a\s+(knight|knave)', stmt)
    if m:
        p1, p2, role = m.groups()
        v1 = z3_vars.get(p1.upper())
        v2 = z3_vars.get(p2.upper())
        if v1 is None or v2 is None:  # <<<< แก้ตรงนี้ด้วย
            return None
        expr = Or(v1, v2)
        return expr if role == 'knight' else Not(expr)

    # 4. i am a knight - คนพูดถึงตัวเอง
    m = re.match(r'i\s+am\s+a\s+(knight|knave)', stmt)
    if m:
        role = m.group(1)
        var = z3_vars.get(speaker.upper())
        if var is None:
            return None
        return var if role == 'knight' else Not(var)

    return None

def _solve_knights_knaves_brute(text: str) -> Dict[str, Any]:
    """Fallback brute-force solver if Z3 is not available."""
    text_clean = re.sub(r'แสดงวิธีคิด', '', text, flags=re.IGNORECASE)
    statements = re.findall(r'(\w+)\s+says:?\s*(.*?)(?=\s*\w+\s+says:|$)', text_clean, re.IGNORECASE | re.DOTALL)
    people = sorted(set([s[0].upper() for s in statements]))
    
    explanation = ["🐢 ใช้ Brute Force (เนื่องจากไม่มี Z3):\n"]
    
    for values in product([True, False], repeat=len(people)):
        assignment = dict(zip(people, values))
        is_valid = True
        
        for person, stmt in statements:
            # Simplified check for brute force (limited support)
            # In a real scenario, we'd need a full parser here too.
            # For now, we just assume valid if Z3 is missing to avoid complexity spike.
            pass 

    explanation.append("⚠️ Brute Force ยังไม่รองรับโจทย์ซับซ้อน กรุณาติดตั้ง `z3-solver`")
    return {"success": False, "error": "ต้องการไลบรารี z3-solver เพื่อแก้โจทย์นี้"}
