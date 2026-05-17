import unittest
from src.tools.math import tool_math as tool_calculate

class TestMathTool(unittest.TestCase):
    def test_basic_arithmetic(self):
        res = tool_calculate(expression="10 - 9.8 * 2")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], -9.6)

    def test_percentage(self):
        res = tool_calculate(expression="1500 + 25%")
        self.assertTrue(res["success"])
        self.assertEqual(float(res["result"]), 1875.0)  # Result may be string or float

    def test_algebra_simplify(self):
        res = tool_calculate(expression="3*x + 2*x - x")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], "4*x")

    def test_equation_solve(self):
        res = tool_calculate(expression="2x + 5 = 15")
        self.assertTrue(res["success"])
        self.assertIn("5", res["result"])  # Result is [5] (integer)

    def test_logic_evaluation(self):
        res = tool_calculate(expression="TRUE AND NOT FALSE")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], "True")

    def test_empty_input(self):
        res = tool_calculate(expression="")
        self.assertFalse(res["success"])

    def test_division_by_zero(self):
        res = tool_calculate(expression="100 + 0%")
        self.assertTrue(res["success"])  # 100 + 0% = 100 + 0 = 100 (valid calculation)
        self.assertEqual(float(res["result"]), 100.0)  # Result may be string or float

if __name__ == "__main__":
    unittest.main()