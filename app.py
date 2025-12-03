from flask import Flask, render_template, request
import re

app = Flask(__name__)

ROWS = 8
COLS = 12

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
    if request.method == "POST":
        manifest_text = request.form.get("manifest", "")
        grid, containers = parse_manifest(manifest_text)
        print("Parsed containers:", containers)
        return render_template("index.html", grid=grid)

    return render_template("index.html", grid=None)


if __name__ == "__main__":
    app.run(debug=True)