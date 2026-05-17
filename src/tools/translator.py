from src.utils import get_logger

logger = get_logger("translator")

def tool_translator(text: str, target_lang: str = "en", source_lang: str = "auto") -> dict:
    """
    แปลข้อความ
    target_lang: "en", "th", "ja", "zh-CN" ฯลฯ
    """
    try:
        from deep_translator import GoogleTranslator

        # deep_translator ใช้ 'auto' ได้เลย
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)

        return {
            "success": True,
            "original": text,
            "translated": translated,
            "source": source_lang,
            "target": target_lang
        }
    except Exception as e:
        logger.error(f"translator error: {e}")
        # fallback ไม่พึ่งเน็ต
        return {
            "success": False,
            "error": str(e),
            "original": text,
            "translated": text,
            "note": "fallback คืนข้อความเดิม"
        }