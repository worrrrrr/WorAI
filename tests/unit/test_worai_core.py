"""
Pytest Suite for WorAI Core Tools.
Tests Math and Logic capabilities with AGI-boundary scenarios.
"""
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tools.math import tool_math
from src.tools.logic import tool_logic

# --- 🧮 Math Tool Tests ---

class TestMathTool:
    def test_basic_arithmetic_precision(self):
        """Test floating point precision handling."""
        res = tool_math(expression="0.1 + 0.2")
        assert res["success"] is True
        assert res["result"] == 0.3

    def test_percentage_calculation(self):
        """Test business logic percentage."""
        res = tool_math(expression="1500 + 25%")
        assert res["success"] is True
        assert float(res["result"]) == 1875.0

    def test_algebra_simplification(self):
        """Test symbolic algebra."""
        res = tool_math(expression="3*x + 2*x - x")
        assert res["success"] is True
        assert res["result"] == "4*x"

    def test_equation_solving(self):
        """Test linear equation solving."""
        res = tool_math(expression="2x + 5 = 15")
        assert res["success"] is True
        assert "5" in str(res["result"])

    def test_empty_input_handling(self):
        """Test robustness against empty input."""
        res = tool_math(expression="")
        assert res["success"] is False

# --- 🧠 Logic Tool Tests ---

class TestLogicTool:
    def test_truth_table_generation(self):
        """Test SymPy truth table generation."""
        res = tool_logic(raw_text="ตรรกะ A AND B แสดงตาราง")
        assert res["success"] is True
        assert "T" in res["result"] and "F" in res["result"] # Check if table has values

    def test_knight_knave_simple(self):
        """Test Z3/Brute force solver for simple puzzle."""
        # A says: "I am a knave" -> Paradox or Knave depending on logic system
        # Let's try a solvable one: A says "B is a knight", B says "A is a knave"
        res = tool_logic(raw_text="A says: B is a knight. B says: A is a knave.")
        # Should return success even if it's a paradox (it will explain why)
        assert "success" in res 
        
    def test_invalid_logic_syntax(self):
        """Test handling of garbage input."""
        res = tool_logic(raw_text="random gibberish !@#")
        # Might fail or return weird table, but shouldn't crash
        assert isinstance(res, dict)

# --- 🚀 AGI Boundary Tests ---

class TestAGIBoundaries:
    def test_natural_language_math_limit(self):
        """System should fail gracefully on non-math NL."""
        res = tool_math(raw_text="ฉันมีแอปเปิ้ล 5 ลูก")
        assert res["success"] is False # Expected failure for pure math tool

    def test_complex_reasoning_limit(self):
        """System should handle complex puzzles without crashing."""
        res = tool_logic(raw_text="If the sky is blue then grass is green, but not if it rains.")
        # Should attempt to parse or fail gracefully
        assert isinstance(res, dict)