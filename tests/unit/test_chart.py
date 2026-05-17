from src.tools.chart_generator import tool_chart_generator
import os

def test_bar():
    data = {"labels": ["ม.ค.", "ก.พ.", "มี.ค."], "values": [10, 15, 7]}
    r = tool_chart_generator(data, chart_type="bar", title="ยอดขาย", filename="test_bar")
    assert r["success"] and os.path.exists(r["path"])

def test_line_multi():
    data = {"labels": ["Q1","Q2","Q3"], "datasets": [{"label":"2024","data":[1,2,3]},{"label":"2025","data":[2,3,4]}]}
    r = tool_chart_generator(data, chart_type="line", filename="test_line")
    assert r["success"]