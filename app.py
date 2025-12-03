from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)

ROWS = 8
COLS = 12

MANIFEST_DIR = "manifests"

def parse_manifest(text):
    grid = [[{"type": "UNUSED", "weight": 0, "id": None} for _ in range(COLS)] for _ in range(ROWS)]
    containers = []

    for raw in text.splitlines():
        line = raw.strip()

        if line.startswith('"'):
            line = line[1:]
        
        if line.endswith('"'):
            line = line[:-1]
        
        if not line:
            continue

        m = re.match(r"\[(\d+),(\d+)\],\s*\{(\d+)\},\s*(.+)", line)
        if not m:
            continue

        row = int(m.group(1))
        col = int(m.group(2))
        weight = int(m.group(3))
        token = m.group(4).strip()
        
        r = row - 1
        c = col - 1
        token_upper = token.upper()

        if token_upper == "NAN":
            grid[r][c] = {"type": "NAN", "weight": 0, "id": None}
        elif token_upper == "UNUSED":
            grid[r][c] = {"type": "UNUSED", "weight": 0, "id": None}
        else:
            containers.append({"id": token, "row": row, "col": col, "weight": weight})
            grid[r][c] = {"type": "CONTAINER", "weight": weight, "id": token}

    return grid, containers

@app.route("/", methods=["GET", "POST"])
def index():
    manifest_text = ""
    error = None

    if request.method == "POST":

        uploaded = request.files.get("file")
        if uploaded and uploaded.filename:
            if uploaded.filename.lower().endswith(".txt"):
                try:
                    manifest_text = uploaded.read().decode("utf-8")
                except:
                    error = "Error reading uploaded file."
            else:
                error = "Only .txt files can be uploaded."

        if not manifest_text:
            filename = request.form.get("filename", "").strip()
            if filename:
                path = os.path.join(MANIFEST_DIR, filename)
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        manifest_text = f.read()
                else:
                    error = f"Manifest '{filename}' not found in /manifests directory."

        if not manifest_text:
            manifest_text = request.form.get("manifest", "")

        if not manifest_text.strip():
            if not error:
                error = "No manifest provided."
            return render_template("index.html", error=error)

        grid, containers = parse_manifest(manifest_text)
        print("Parsed containers:", containers)

        return render_template("index.html", error=error)

    return render_template("index.html", error=error)


if __name__ == "__main__":
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    app.run(debug=True)