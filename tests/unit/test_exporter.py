from src.tools.exporter import tool_exporter
import os

def test_export_xlsx():
    data = [{"name": "A", "value": 10}, {"name": "B", "value": 20}]
    r = tool_exporter(data, filename="test_export", format="xlsx")
    assert r["success"] and os.path.exists(r["path"]) and r["rows"] == 2

def test_export_csv():
    r = tool_exporter({"col1": [1,2], "col2": [3,4]}, filename="test_csv", format="csv")
    assert r["success"] and r["format"] == "csv"