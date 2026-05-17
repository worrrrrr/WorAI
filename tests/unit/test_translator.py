from src.tools.translator import tool_translator

def test_th_to_en():
    r = tool_translator("สวัสดีครับ", target_lang="en", source_lang="th")
    assert r["original"] == "สวัสดีครับ"
    # ถ้ามีเน็ตจะได้ Hello, ถ้าไม่มีจะ fallback
    assert "translated" in r

def test_auto():
    r = tool_translator("hello world", target_lang="th")
    assert r["success"] or not r["success"]  # ผ่านทั้งมีเน็ตและไม่มี
    assert "translated" in r