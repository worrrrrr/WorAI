import os
import json
import pandas as pd
from src.utils import get_logger

logger = get_logger("exporter")

def tool_exporter(data, filename: str = "export", format: str = "xlsx") -> dict:
    """
    data: list[dict] หรือ dict
    format: "xlsx", "csv", "json", "txt"
    """
    try:
        os.makedirs("/mnt/data", exist_ok=True)
        path = f"/mnt/data/{filename}.{format}"

        # แปลงเป็น DataFrame ให้ง่าย
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # ถ้า dict มี key เป็น list ยาวเท่ากัน
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([{"value": str(data)}])

        if format == "xlsx":
            df.to_excel(path, index=False, engine='openpyxl')
        elif format == "csv":
            df.to_csv(path, index=False, encoding='utf-8-sig')
        elif format == "json":
            df.to_json(path, orient="records", force_ascii=False, indent=2)
        elif format == "txt":
            with open(path, "w", encoding="utf-8") as f:
                f.write(df.to_string(index=False))
        else:
            return {"success": False, "error": f"format {format} ไม่รองรับ"}

        return {"success": True, "path": path, "format": format, "rows": len(df)}
    except Exception as e:
        logger.error(f"exporter error: {e}")
        return {"success": False, "error": str(e)}