from flask import Flask, render_template, request, jsonify
from balancer.Problem import Problem
from balancer.Node import SHIP_ROWS, SHIP_COLS
import os
import time
import sys
import signal
from datetime import datetime

app = Flask(__name__)
MANIFEST_DIR = "manifests"

SESSION_START_TIME = datetime.now()
FULL_LOG = []

CURRENT_LOG_STRING = "" 

def get_desktop_path(): 
    onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    if os.path.exists(onedrive_desktop):
        return onedrive_desktop
    
    return os.path.join(os.path.expanduser("~"), "Desktop")

def write_to_log(message):
    global CURRENT_LOG_STRING
    timestamp = datetime.now().strftime("%m/%d/%Y: %H:%M")
    entry = f"{timestamp} {message}"
    
    FULL_LOG.append(entry)
    
    if CURRENT_LOG_STRING:
        CURRENT_LOG_STRING += "\n" + entry
    else:
        CURRENT_LOG_STRING = entry
        
    return entry

def save_session_log_to_desktop():
    write_to_log("Program was shut down.")
    
    filename = f"FormosaSolutionsPort{SESSION_START_TIME.strftime('%m_%d_%Y_%H%M')}.txt"
    filepath = os.path.join(get_desktop_path(), filename)
    
    try:
        with open(filepath, "w") as f:
            f.write(CURRENT_LOG_STRING)
        print(f"\n[SYSTEM] Log file saved to Desktop: {filepath}")
    except Exception as e:
        print(f"\n[ERROR] Could not save log to desktop: {e}")

def signal_handler(sig, frame):
    print("\n[SYSTEM] Closing program...")
    save_session_log_to_desktop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@app.route("/add_comment", methods=["POST"])
def add_comment():
    global CURRENT_LOG_STRING
    try:
        data = request.json
        comment = data.get("content", "").strip()
        
        if comment:
            # Specify "[COMMENT]" for easier readability
            write_to_log(f"[COMMENT] {comment}")
            
        return jsonify({"log": CURRENT_LOG_STRING}), 200
    except Exception as e:
        print(f"Error adding comment: {e}")
        return jsonify({"error": str(e)}), 500

def write_outbound_manifest(ship_state, original_filename):
    base_name = original_filename.replace(".txt", "")
    out_name = f"{base_name}OUTBOUND.txt"
    filepath = os.path.join(get_desktop_path(), out_name)
    try:
        with open(filepath, "w") as f:
            for r in range(SHIP_ROWS):
                for c in range(SHIP_COLS):
                    slot = ship_state[r][c]
                    line = f"[{r+1:02},{c+1:02}], {{{slot.weight:05}}}, {slot.description}\n"
                    f.write(line)
        return out_name
    except Exception as e:
        print(f"Error writing outbound: {e}")
        return None

class CapturingProblem(Problem):
    def __init__(self, manifest_text):
        super().__init__(manifest_text)
        self.steps = [] 
        self.total_cost = 0
        self.final_node = None
        self.final_time_minutes = 0

    def solution_log(self, goalNode, total_time=0):
        self.final_time_minutes = total_time
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
        self.final_node = goalNode 

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
    global CURRENT_LOG_STRING
    
    if not FULL_LOG:
        write_to_log("Program was started.")

    manifest_text = ""
    error = None
    steps = None
    grid_json = None
    filename_display = ""
    time_taken = None
    
    total_time_display = 0

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

        if manifest_text == "":
            error = "File is blank"
    
        
        if manifest_text.strip():
            
            try:
                container_count = 0
                start_time = time.time()
                solver = CapturingProblem(manifest_text)
                initial_tuple_grid = solver.initial_state.state 
                grid_json = grid_to_json(initial_tuple_grid)

                for r in range(SHIP_ROWS):
                    for c in range(SHIP_COLS):
                        slot = initial_tuple_grid[r][c]
                        if slot.description not in ("UNUSED", "NAN"):
                            container_count += 1
                
                write_to_log(f"Manifest {filename_display} is opened, there are {container_count} containers on the ship.")

                solver.run_a_star()
                final_time = time.time()
                time_taken = round((final_time - start_time) * 1000)
                steps = solver.steps

                if steps:
                    write_to_log(f"Balance solution found, it will require {len(steps)} moves/{solver.total_cost} minutes.")
                    for step in steps:
                        src, dst = step
                        src_str = f"[{src[0]+1:02},{src[1]+1:02}]"
                        dst_str = f"[{dst[0]+1:02},{dst[1]+1:02}]"
                        write_to_log(f"{src_str} was moved to {dst_str}")
                    
                    out_filename = write_outbound_manifest(solver.final_node.state, filename_display)
                    if out_filename:
                        write_to_log(f"Finished a Cycle. Manifest {out_filename} was written to desktop, and a reminder pop-up to operator to send file was displayed.")
                    else:
                        write_to_log("Finished a Cycle. Error writing outbound manifest.")

                elif solver.initial_state.is_balanced():
                    write_to_log("Status: Ship is already balanced.")

                total_time_display = solver.final_time_minutes
                
                if not steps and not solver.initial_state.is_balanced():
                    error = "No solution found."
                
            except Exception as e:
                error = f"Algorithm Error: {e}"
                print(f"Error: {e}")

    return render_template("index.html", error=error, manifest=manifest_text, grid=grid_json, steps=steps, filename=filename_display, time=time_taken, total_time=total_time_display, log_content=CURRENT_LOG_STRING)

if __name__ == "__main__":
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    if not FULL_LOG:
        write_to_log("Program was started.")
    app.run(debug=True, use_reloader=False)