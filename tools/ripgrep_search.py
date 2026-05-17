import subprocess, json
from pathlib import Path
from.base import ICodeSearch

class RipgrepCodeSearch(ICodeSearch):
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()

    def search(self, query: str, file_type: str = None, **kwargs) -> Dict:
        cmd = ["rg", "--json", "-n", query]
        if file_type:
            cmd.extend(["-t", file_type])
        cmd.append(str(self.root_dir))

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            matches = []
            first_file = ""
            for line in res.stdout.splitlines():
                data = json.loads(line)
                if data["type"] == "match":
                    file_path = data["data"]["path"]["text"]
                    if not first_file: first_file = file_path
                    matches.append({
                        "file": file_path,
                        "line": data["data"]["line_number"],
                        "text": data["data"]["lines"]["text"].strip()
                    })
            return {"success": True, "path": first_file, "matches": matches}
        except Exception as e:
            return {"success": False, "error": str(e)}