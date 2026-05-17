import os
import matplotlib
matplotlib.use('Agg')  # ไม่ต้องเปิดหน้าต่าง
import matplotlib.pyplot as plt
from src.utils import get_logger

logger = get_logger("chart_generator")

def tool_chart_generator(data: dict, chart_type: str = "bar", title: str = "Chart", filename: str = "chart") -> dict:
    """
    data = {"labels": ["A","B","C"], "values": [10,20,15]}
    หรือ data = {"labels": [...], "datasets": [{"label":"2024","data":[...]}, {"label":"2025","data":[...]}]}
    chart_type: "bar", "line", "pie"
    """
    try:
        os.makedirs("/mnt/data", exist_ok=True)
        path = f"/mnt/data/{filename}.png"

        plt.figure(figsize=(8, 5))
        labels = data.get("labels", [])

        if chart_type == "pie":
            values = data.get("values", [])
            plt.pie(values, labels=labels, autopct='%1.1f%%')
        elif chart_type == "line":
            if "datasets" in data:
                for ds in data["datasets"]:
                    plt.plot(labels, ds["data"], marker='o', label=ds.get("label"))
                plt.legend()
            else:
                plt.plot(labels, data.get("values", []), marker='o')
        else:  # bar default
            if "datasets" in data:
                x = range(len(labels))
                width = 0.8 / len(data["datasets"])
                for i, ds in enumerate(data["datasets"]):
                    offset = [xi + i*width for xi in x]
                    plt.bar(offset, ds["data"], width=width, label=ds.get("label"))
                plt.xticks([xi + width for xi in x], labels)
                plt.legend()
            else:
                plt.bar(labels, data.get("values", []))

        plt.title(title)
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()

        return {"success": True, "path": path, "type": chart_type, "title": title}
    except Exception as e:
        logger.error(f"chart_generator error: {e}")
        return {"success": False, "error": str(e)}