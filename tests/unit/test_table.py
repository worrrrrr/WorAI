from src.tools.table_generator import tool_table_generator
import os

def test_png():
    data = [{"ชื่อ":"A","ยอด":10},{"ชื่อ":"B","ยอด":20}]
    r = tool_table_generator(data, title="ยอดขาย", filename="test_table", format="png")
    assert r["success"] and os.path.exists(r["path"])

def test_html():
    data = [[1,2],[3,4]]
    r = tool_table_generator(data, headers=["X","Y"], format="html", filename="test_html")
    assert r["success"] and r["path"].endswith(".html")