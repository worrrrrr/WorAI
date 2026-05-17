import pytest
from src.tools.math_advanced import tool_math_advanced

def test_derivative():
    r = tool_math_advanced("ดิฟ x**2 + 3*x")
    assert r["success"] and r["result"] == "2*x + 3"

def test_integral():
    r = tool_math_advanced("อินทิเกรต sin(x)")
    assert r["success"] and "-cos(x)" in r["result"]

def test_definite_integral():
    r = tool_math_advanced("integrate x from 0 to 2")
    assert r["success"] and r["result"] == "2"

def test_solve():
    r = tool_math_advanced("แก้สมการ x**2 - 4 = 0")
    assert r["success"] and set(r["result"]) == {"-2", "2"}

def test_matrix():
    r = tool_math_advanced("เมทริกซ์ [[1,2],[3,4]] * [[5,6],[7,8]]")
    assert r["success"] and r["result"] == [[19, 22], [43, 50]]

def test_complex():
    r = tool_math_advanced("(3+4j)*(2-1j)")
    assert r["success"]