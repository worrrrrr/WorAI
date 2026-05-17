from src.tools.analyzer import tool_analyzer

def test_analyzer_structure():
    r = tool_analyzer("AI ในการศึกษา")
    assert r["success"]
    assert r["topic"] == "AI ในการศึกษา"
    assert isinstance(r["why"], list) and len(r["why"]) >= 1
    assert isinstance(r["pros"], list)
    assert isinstance(r["cons"], list)
    assert "trend" in r

def test_analyzer_fallback():
    r = tool_analyzer("test")
    assert r["success"] and r["impact"]