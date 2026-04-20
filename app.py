from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys

app = Flask(__name__)
CORS(app)

@app.route('/run', methods=['POST'])
def run_scheduler():
    data = request.json

    processes = data["processes"]
    algorithm = data["algorithm"]
    quantum = data.get("quantum", 2)

    # 🔹 Convert input to C++ format
    input_data = str(len(processes)) + "\n"

    for p in processes:
        input_data += f"{p['pid']} {p['arrival']} {p['burst']} {p['priority']}\n"

    input_data += algorithm + "\n"

    if algorithm == "RR":
        input_data += str(quantum) + "\n"

    print("Sending to C++:", input_data)  # Debug

    # 🔹 Run C++ program
    result = subprocess.run(
        ["./scheduler.exe"],
        input=input_data,
        text=True,
        capture_output=True
    )

    print("C++ stdout:", result.stdout)  # Debug
    print("C++ stderr:", result.stderr)  # Debug

    lines = result.stdout.strip().split("\n")

    gantt = []
    metrics = {}

    i = 0

    # 🔹 READ GANTT DATA (C++ outputs: pid start end for each block)
    while i < len(lines) and lines[i] != "---":
        if lines[i].strip() == "":
            i += 1
            continue
        parts = lines[i].split()
        if len(parts) >= 3:
            # Check if it's a valid Gantt line (all numbers)
            try:
                pid = int(parts[0])
                start = int(parts[1])
                end = int(parts[2])
                gantt.append({
                    "pid": f"P{pid}",
                    "start": start,
                    "end": end
                })
            except ValueError:
                pass  # Skip non-numeric lines (like algorithm name)
        i += 1

    # skip ---
    i += 1

    # 🔹 READ METRICS
    if i < len(lines):
        try:
            vals = lines[i].split()
            if len(vals) >= 2:
                metrics = {
                    "avg_waiting": float(vals[0]),
                    "avg_turnaround": float(vals[1])
                }
        except:
            metrics = {"avg_waiting": 0, "avg_turnaround": 0}

    return jsonify({
        "gantt": gantt,
        "metrics": metrics
    })


if __name__ == "__main__":
    app.run(debug=True)