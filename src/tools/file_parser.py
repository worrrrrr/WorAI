import os
from src.utils import get_logger

logger = get_logger("file_parser")

def tool_file_parser(path: str, max_chars: int = 2000) -> dict:
    """อ่าน PDF/DOCX/TXT/MD แล้วคืนสรุป"""
    try:
        ext = os.path.splitext(path)[1].lower()
        text = ""

        if ext == ".pdf":
            import fitz # PyMuPDF
            doc = fitz.open(path)
            text = "\n".join(page.get_text() for page in doc)

        elif ext == ".docx":
            from docx import Document
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)

        elif ext in [".txt", ".md"]:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        else:
            return {"success": False, "error": f"ไม่รองรับ {ext}"}

        summary = text[:max_chars] + ("..." if len(text) > max_chars else "")
        return {
            "success": True,
            "path": path,
            "length": len(text),
            "summary": summary,
            "full_text": text
        }
    except Exception as e:
        logger.error(f"file_parser error: {e}")
        return {"success": False, "error": str(e)}