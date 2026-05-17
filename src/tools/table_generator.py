import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.utils import get_logger

logger = get_logger("table_generator")

def tool_table_generator(data, headers=None, title: str = "Table", filename: str = "table", format: str = "png") -> dict:
    """
    data: list of dict หรือ list of list
    ตัวอย่าง: [{"ชื่อ":"A","ยอด":10},{"ชื่อ":"B","ยอด":20}]
    format: "png", "html", "md"
    """
    try:
        os.makedirs("/mnt/data", exist_ok=True)

        # แปลงเป็น DataFrame
        if isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=headers)

        path = f"/mnt/data/{filename}.{format}"

        if format == "html":
            html = f"<h3>{title}</h3>" + df.to_html(index=False, border=0)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)

        elif format == "md":
            md = f"### {title}\n\n" + df.to_markdown(index=False)
            with open(path, "w", encoding="utf-8") as f:
                f.write(md)

        else: # png default
            fig, ax = plt.subplots(figsize=(len(df.columns)*1.5 + 1, len(df)*0.5 + 1))
            ax.axis('off')
            tbl = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            tbl.scale(1, 1.5)
            plt.title(title, pad=20)
            plt.tight_layout()
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()

        return {"success": True, "path": path, "format": format, "rows": len(df), "cols": len(df.columns)}
    except Exception as e:
        logger.error(f"table_generator error: {e}")
        return {"success": False, "error": str(e)}