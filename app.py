from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

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

    # 🔹 Run C++ program
    result = subprocess.run(
        ["./scheduler.exe"],
        input=input_data,
        text=True,
        capture_output=True
    )

    lines = result.stdout.strip().split("\n")

    gantt = []
    metrics = {}

    i = 0

    # 🔥 SKIP FIRST LINE (algorithm name like SJF)
    i += 1

    # 🔹 READ GANTT DATA
    while i < len(lines) and lines[i] != "---":
        parts = lines[i].split()
        gantt.append({
            "pid": f"P{parts[0]}",   # 👈 IMPORTANT (frontend expects P1, P2)
            "start": int(parts[1]),
            "end": int(parts[2])
        })
        i += 1

    # skip ---
    i += 1

    # 🔹 READ METRICS
    if i < len(lines):
        vals = lines[i].split()
        metrics = {
            "avg_waiting": float(vals[0]),
            "avg_turnaround": float(vals[1])
        }

    return jsonify({
        "gantt": gantt,
        "metrics": metrics
    })


if __name__ == "__main__":
    app.run(debug=True)