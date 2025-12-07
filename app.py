from flask import Flask, render_template, request
from balancer.Problem import Problem
from balancer.Node import SHIP_ROWS, SHIP_COLS
import os
import time

app = Flask(__name__)
MANIFEST_DIR = "manifests"

class CapturingProblem(Problem):
    def __init__(self, manifest_text):
        super().__init__(manifest_text)
        self.steps = [] 
        self.total_cost = 0

    def solution_log(self, goalNode):
        solution_nodes = []
        current_node = goalNode
        while current_node:
            solution_nodes.append(current_node)
            current_node = current_node.parent
        
        solution_nodes.reverse()
        
        for node in solution_nodes:
            if node.prev_state:
                self.steps.append(node.prev_state)
        
        self.total_cost = goalNode.g_cost

def grid_to_json(ship_state):
    grid_data = []
    for r in range(SHIP_ROWS):
        row_data = []
        for c in range(SHIP_COLS):
            slot = ship_state[r][c]
            row_data.append({
                "weight": slot.weight,
                "name": slot.description,
                "r": r,
                "c": c
            })
        grid_data.append(row_data)
    return grid_data

@app.route("/", methods=["GET", "POST"])
def index():
    manifest_text = ""
    error = None
    steps = None
    grid_json = None
    filename_display = ""
    time_taken = None

    if request.method == "POST":
        
        uploaded = request.files.get("file")
        if uploaded and uploaded.filename:
            if uploaded.filename.lower().endswith(".txt"):
                try:
                    manifest_text = uploaded.read().decode("utf-8")
                    filename_display = uploaded.filename
                except:
                    error = "Error reading uploaded file."
            else:
                error = "Only .txt files can be uploaded."
        
        if not manifest_text:
            fname = request.form.get("filename", "").strip()
            if fname:
                path = os.path.join(MANIFEST_DIR, fname)
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        manifest_text = f.read()
                    filename_display = fname
                else:
                    error = f"Manifest '{fname}' not found."
        
        if not manifest_text:
            manifest_text = request.form.get("manifest", "")

        if manifest_text.strip():
            try:
                start_time = time.time()
                
                solver = CapturingProblem(manifest_text)
                
                initial_tuple_grid = solver.initial_state.state 
                grid_json = grid_to_json(initial_tuple_grid)

                solver.run_a_star()
                
                final_time = time.time()
                time_taken = round((final_time - start_time) * 1000)
                
                steps = solver.steps
                
                if not steps and not solver.initial_state.is_balanced():
                    error = "No solution found or ship is already balanced."
                
            except Exception as e:
                error = f"Algorithm Error: {e}"
                print(f"Error: {e}")

    return render_template("index.html", error=error, manifest=manifest_text, grid=grid_json, steps=steps, filename=filename_display, time=time_taken)

if __name__ == "__main__":
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    app.run(debug=True)