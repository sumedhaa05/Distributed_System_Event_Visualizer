# Distributed System Event Visualizer

An interactive Flask mini project based on the Lamport Logical Clock Simulator report.

## Features
- Create 1–8 distributed processes.
- Generate Internal and Send events.
- Automatically generate Receive events when messages are delivered.
- Apply Lamport clock rules:
  - Internal / Send: `C = C + 1`
  - Receive: `C = max(C, message_timestamp) + 1`
- View each process's local event timeline.
- View a merged global event order sorted by `(timestamp, process name)`.
- Check send/receive causality.
- Load a ready-made three-process demo.
- Includes unit tests.

## Requirements
- Python 3.9 or newer
- pip

## Run on Windows (PowerShell)

1. Extract the ZIP file.
2. Open the extracted folder in VS Code.
3. Open the VS Code terminal and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

4. Open this address in your browser:

`http://127.0.0.1:5000`

If PowerShell blocks activation, run this once in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Project structure

```text
distributed_system_event_visualizer/
├── app.py
├── simulator.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
└── tests/
    └── test_simulator.py
```

## Notes
- The demo delivers messages immediately. The UI represents message causality, not real network transport.
- The global event list is a deterministic total order for display. Lamport timestamps guarantee causal ordering, but do not by themselves identify every pair of concurrent events.
- The optional network-delay feature from the original report is not implemented in this starter version.
