from flask import Flask, render_template, request, jsonify
from simulator import LamportSimulator

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json(silent=True) or {}
    names = data.get("processes", ["P1", "P2", "P3"])
    events = data.get("events", [])
    delay = float(data.get("delay", 0))
    if not isinstance(names, list) or not names or len(names) > 8:
        return jsonify({"error": "Create between 1 and 8 processes."}), 400
    if len(set(names)) != len(names) or any(not isinstance(n, str) or not n.strip() for n in names):
        return jsonify({"error": "Process names must be unique and non-empty."}), 400
    sim = LamportSimulator(names)
    try:
        for item in events:
            kind = item.get("kind")
            process = item.get("process")
            if process not in sim.processes:
                raise ValueError(f"Unknown process: {process}")
            p = sim.processes[process]
            if kind == "Internal":
                p.internal_event(item.get("detail", "Internal task"))
            elif kind == "Send":
                receiver = item.get("receiver")
                if receiver not in sim.processes or receiver == process:
                    raise ValueError("Choose a valid receiver different from the sender.")
                p.send(receiver, item.get("detail", "Message"))
            else:
                raise ValueError("Unknown event type.")
    except (ValueError, KeyError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(sim.as_dict())

@app.route("/api/demo", methods=["GET"])
def demo():
    sim = LamportSimulator(["P1", "P2", "P3"])
    p1, p2, p3 = (sim.processes[n] for n in ["P1", "P2", "P3"])
    p1.internal_event("Compute task A")
    p2.internal_event("Read local data")
    p1.send("P2", "Job #1")
    p3.internal_event("Initialize process")
    p2.internal_event("Process job")
    p3.send("P1", "Status request")
    p2.send("P3", "Job result")
    p1.internal_event("Handle status request")
    p3.internal_event("Save result")
    return jsonify(sim.as_dict())

if __name__ == "__main__":
    app.run(debug=True)
