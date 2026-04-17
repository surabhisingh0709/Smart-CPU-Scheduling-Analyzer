from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

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

    output = result.stdout

    # 🔥 NEW PART — convert output → JSON
    lines = output.strip().split("\n")

    gantt = []
    metrics = {}

    i = 0
    while i < len(lines) and lines[i] != "---":
        parts = lines[i].split()
        gantt.append({
            "pid": int(parts[0]),
            "start": int(parts[1]),
            "end": int(parts[2])
        })
        i += 1

    # skip ---
    i += 1

    if i < len(lines):
        vals = lines[i].split()
        metrics = {
            "avg_waiting": float(vals[0]),
            "avg_turnaround": float(vals[1])
        }

    # 🔹 Final clean response
    return jsonify({
        "gantt": gantt,
        "metrics": metrics
    })


if __name__ == "__main__":
    app.run(debug=True)