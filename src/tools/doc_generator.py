import os
from src.utils import get_logger

logger = get_logger("doc_generator")

def tool_doc_generator(content: str, filename: str = "output", format: str = "docx") -> dict:
    """สร้างไฟล์ docx หรือ pdf จากข้อความ"""
    try:
        os.makedirs("/mnt/data", exist_ok=True)

        if format == "docx":
            from docx import Document
            doc = Document()
            for line in content.split("\n"):
                doc.add_paragraph(line)
            path = f"/mnt/data/{filename}.docx"
            doc.save(path)

        elif format == "pdf":
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            path = f"/mnt/data/{filename}.pdf"
            c = canvas.Canvas(path, pagesize=A4)
            y = 800
            for line in content.split("\n"):
                c.drawString(50, y, line[:95])
                y -= 18
                if y < 50:
                    c.showPage()
                    y = 800
            c.save()
        else:
            return {"success": False, "error": "format ต้องเป็น docx หรือ pdf"}

        return {"success": True, "path": path, "format": format}
    except Exception as e:
        logger.error(f"doc_generator error: {e}")
        return {"success": False, "error": str(e)}