import re
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from src.utils import get_logger

logger = get_logger("math_advanced")
transformations = standard_transformations + (implicit_multiplication_application,)

def _clean(s: str) -> str:
    s = s.replace('^', '**').replace('×', '*').replace('÷', '/')
    s = re.sub(r'([0-9])x', r'\1*x', s)
    return s.strip()

def _parse(s: str):
    return parse_expr(_clean(s), transformations=transformations, evaluate=True)

def tool_math_advanced(expression: str) -> dict:
    try:
        txt = expression.strip()
        low = txt.lower()
        x = sp.symbols('x')

        # --- 1. อนุพันธ์ ---
        if any(k in low for k in ['ดิฟ', 'อนุพันธ์', 'diff', 'derivative']):
            m = re.search(r'(?:ดิฟ|diff|derivative|อนุพันธ์)\s+(.+)', low)
            expr_str = m.group(1) if m else low
            f = _parse(expr_str)
            var = x if f.has(x) else (list(f.free_symbols)[0] if f.free_symbols else x)
            res = sp.diff(f, var)
            return {"success": True, "type": "derivative", "result": str(res), "latex": sp.latex(res)}

        # --- 2. อินทิเกรต ---
        if any(k in low for k in ['อินทิเกรต', 'integrate', 'integral']):
            m = re.search(r'(?:อินทิเกรต|integrate|integral)\s+(.+?)(?:\s+from\s+(\S+)\s+to\s+(\S+))?$', low)
            if not m:
                f = _parse(low)
                res = sp.integrate(f, x)
            else:
                f = _parse(m.group(1))
                if m.group(2):
                    a = _parse(m.group(2)); b = _parse(m.group(3))
                    res = sp.integrate(f, (x, a, b))
                else:
                    res = sp.integrate(f, x)
            return {"success": True, "type": "integral", "result": str(res), "latex": sp.latex(res)}

        # --- 3. แก้สมการ ---
        if any(k in low for k in ['แก้สมการ', 'solve', 'สมการ']):
            m = re.search(r'(?:แก้สมการ|solve)\s+(.+)', low)
            eq_str = m.group(1) if m else low
            if '=' in eq_str:
                l, r = eq_str.split('=', 1)
                eq = sp.Eq(_parse(l), _parse(r))
            else:
                eq = _parse(eq_str)
            sols = sp.solve(eq, x, dict=False)
            # แปลงให้เป็น ["-2", "2"] แบบที่ test ต้องการ
            out = []
            for s in sols if isinstance(sols, list) else [sols]:
                if isinstance(s, dict):
                    out.extend([str(v) for v in s.values()])
                else:
                    out.append(str(s))
            return {"success": True, "type": "solve", "result": out}

        # --- 4. เมทริกซ์ ---
        if 'เมทริกซ์' in low or 'matrix' in low or '[[' in txt:
            mats = re.findall(r'\[\[.*?\]\]', txt)
            if mats:
                if 'det' in low or 'ดีเทอร์มิแนนต์' in low:
                    m = sp.Matrix(eval(mats[0]))
                    return {"success": True, "type": "det", "result": str(m.det())}
                if 'inv' in low or 'อินเวอร์ส' in low:
                    m = sp.Matrix(eval(mats[0]))
                    return {"success": True, "type": "inverse", "result": str(m.inv().tolist())}
                if len(mats) >= 2:
                    a, b = sp.Matrix(eval(mats[0])), sp.Matrix(eval(mats[1]))
                    op = '*' if '*' in txt else '+' if '+' in txt else '-'
                    res = {'*': a*b, '+': a+b, '-': a-b}[op]
                    return {"success": True, "type": "matrix", "result": res.tolist()}

        # --- 5. คำนวณทั่วไป ---
        val = _parse(low)
        return {"success": True, "type": "eval", "result": str(val), "latex": sp.latex(val)}

    except Exception as e:
        logger.error(f"math_advanced error: {e}")
        return {"success": False, "error": str(e)}