import sys
from src.core.router import IntentRouter
from src.domain.planner import ExecutionPlanner
from src.tools.registry import ToolRegistry
from src.utils import get_logger

logger = get_logger("WorAI")

def print_result(intent: str, route: str, tools: list, result: dict):
    print(f" 🎯 {intent} | 🛣 {route} | 🔧 {tools}")

    if result.get("status") == "error":
        print(f" 💬 ❌ {result.get('message', 'เกิดข้อผิดพลาด')}")
        return

    if result.get("status") == "clarify":
        print(f" 💬 ❓ {result.get('message', 'ช่วยระบุเพิ่มเติมได้ไหมครับ')}")
        return

    # แสดงทุก field ที่มีค่า
    shown = False
    priority_keys = ["answer", "response", "summary", "opinion", "result", "compare_table"]

    # โชว์ key สำคัญก่อน
    for key in priority_keys:
        if key in result and result[key]:
            print(f" 💬 {key}: {result[key]}")
            shown = True

    # โชว์ key ที่เหลือ
    for key, value in result.items():
        if key in ["status", "intent", "tool_results", "needs_llm"] + priority_keys:
            continue
        if value:
            print(f" 💬 {key}: {value}")
            shown = True

    if not shown:
        print(f" 💬 (ไม่มีผลลัพธ์)")
    print()

def main():
    logger.info("🚀 WorAI Engine Starting...")
    
    # 1. Load tools
    tools = ToolRegistry()
    
    # 2. Load router
    router = IntentRouter(
        intents_path="config/intents.yaml",
        rules_path="config/rules.yaml"
    )
    
    # 3. Load planner
    planner = ExecutionPlanner(tools)
    
    print("\n" + "="*70)
    print("🎯 WorAI Ready - 30 Intents Loaded")
    print("="*70 + "\n")
    
    # Test cases
    test_cases = [
        #"เปรียบเทียบ iPhone vs Samsung",        "ขอความคิดเห็นเรื่อง AI",        "คำนวณ 15 * 8 + 20",        "สวัสดี",        "อากาศเชียงใหม่เป็นไง",        "แก้สมการ x**2 - 4 = 0",        "9.8-9.11","9.8>9.11",        "แก้สมการ x**2 + 5x + 6 = 0"
        "6.8-6.11","ดูดวงให้หน่อย เกิด 8/8/1992 เวลา 16.49น.","วิเคราะห์ชื่อ วอ เทพซ่า"
    ]
    
    for text in test_cases:
        print(f"🗣  {text}")
        
        # 1. Classify
        route = router.classify(text)
        
        # 2. Execute
        result = planner.execute(route)
        
        # 3. Print
        print_result(
            route.intent_code,
            route.route_type,
            route.tools_to_call,
            result
        )
    
    # Interactive mode
    print("="*70)
    print("💬 พิมพ์ข้อความเพื่อคุย (พิมพ์ exit เพื่อออก)")
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("🗣  ").strip()
            if user_input.lower() in ["exit", "quit", "ออก"]:
                print("👋 บ๊ายบายครับ")
                break
            if not user_input:
                continue
                
            route = router.classify(user_input)
            result = planner.execute(route)
            print_result(
                route.intent_code,
                route.route_type,
                route.tools_to_call,
                result
            )
        except KeyboardInterrupt:
            print("\n👋 บ๊ายบายครับ")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"   💬 ❌ เกิดข้อผิดพลาด: {e}\n")

if __name__ == "__main__":
    main()