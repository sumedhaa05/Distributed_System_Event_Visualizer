from dataclasses import dataclass, asdict
from typing import Dict, List

@dataclass
class Event:
    process: str
    sequence: int
    kind: str
    timestamp: int
    detail: str = ""

@dataclass
class Message:
    sender: str
    receiver: str
    timestamp: int
    payload: str

class Process:
    def __init__(self, name: str, bus):
        self.name = name
        self.clock = 0
        self.sequence = 0
        self.log: List[Event] = []
        self.bus = bus

    def _record(self, kind: str, detail: str):
        self.sequence += 1
        event = Event(self.name, self.sequence, kind, self.clock, detail)
        self.log.append(event)
        return event

    def internal_event(self, detail="Internal event"):
        self.clock += 1
        return self._record("Internal", detail)

    def send(self, receiver: str, payload="Message"):
        self.clock += 1
        message = Message(self.name, receiver, self.clock, payload)
        self._record("Send", f"To {receiver}: {payload} (message timestamp={message.timestamp})")
        self.bus.deliver(message)
        return message

    def receive(self, message: Message):
        self.clock = max(self.clock, message.timestamp) + 1
        return self._record(
            "Receive",
            f"From {message.sender}: {message.payload} (message timestamp={message.timestamp})"
        )

class MessageBus:
    def __init__(self):
        self.processes: Dict[str, Process] = {}

    def register(self, process: Process):
        self.processes[process.name] = process

    def deliver(self, message: Message):
        self.processes[message.receiver].receive(message)

class LamportSimulator:
    def __init__(self, process_names):
        self.bus = MessageBus()
        self.processes = {name: Process(name, self.bus) for name in process_names}
        for process in self.processes.values():
            self.bus.register(process)

    def as_dict(self):
        events = [asdict(e) for p in self.processes.values() for e in p.log]
        ordered = sorted(events, key=lambda e: (e["timestamp"], e["process"]))
        sends = {}
        receives = []
        for event in events:
            if event["kind"] == "Send":
                # Each send is uniquely identified by sender and its send timestamp.
                sends[(event["process"], event["timestamp"])] = event
            elif event["kind"] == "Receive":
                receives.append(event)

        checks = []
        for receive in receives:
            # Extract sender and message timestamp from the recorded detail.
            detail = receive["detail"]
            sender = detail.split("From ", 1)[1].split(":", 1)[0]
            msg_ts = int(detail.rsplit("message timestamp=", 1)[1].rstrip(")"))
            send = sends.get((sender, msg_ts))
            checks.append({
                "sender": sender,
                "receiver": receive["process"],
                "send_timestamp": msg_ts,
                "receive_timestamp": receive["timestamp"],
                "passed": bool(send and receive["timestamp"] > send["timestamp"])
            })

        return {
            "processes": [
                {"name": p.name, "clock": p.clock, "events": [asdict(e) for e in p.log]}
                for p in self.processes.values()
            ],
            "events": ordered,
            "checks": checks,
            "consistent": all(c["passed"] for c in checks)
        }
