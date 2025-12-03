from flask import Flask, render_template, request
from balancer.Problem import Problem
import os
import re

app = Flask(__name__)


MANIFEST_DIR = "manifests"


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

        #OOP/Algorithm Testing
        print()
        test = Problem(manifest_text)
        test.run_a_star()
        print()

        return render_template("index.html", error=error)

    return render_template("index.html", error=error)


if __name__ == "__main__":
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    app.run(debug=True)