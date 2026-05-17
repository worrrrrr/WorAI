from src.domain.intent import IntentRuntimeX

def test_intent_math():
    intent = IntentRuntimeX()
    assert intent.analyze("2+2 เท่าไร")[0] == "math"
    assert intent.analyze("1500 + 25%")[0] == "math"
    assert intent.analyze("10 * 5 - 3")[0] == "math"
    assert intent.analyze("10 - 9.8 * 3")[0] == "math"
    assert intent.analyze("(10 - 9.8)* 3")[0] == "math"
    assert intent.analyze("23x+100=491")[0] == "math"

def test_intent_search():
    intent = IntentRuntimeX()
    assert intent.analyze("อากาศที่เชียงใหม่")[0] == "search"
    assert intent.analyze("จองร้านอาหาร")[0] == "search"

def test_intent_chat():
    intent = IntentRuntimeX()
    assert intent.analyze("สวัสดีครับ")[0] == "chat"

def test_no_false_positive():
    intent = IntentRuntimeX()
    assert intent.analyze("จองร้านอาหาร")[0]!= "math"
