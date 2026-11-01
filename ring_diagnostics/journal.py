# Durable, ordered JSONL records and concise console status for capture sessions.
import datetime
import hashlib
import json
import os
import platform
import sys
import time
import uuid
from pathlib import Path


def create_session(directory: Path) -> tuple[object, str, Path]:
    session_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "-" + uuid.uuid4().hex[:8]
    session_directory = directory / session_id
    session_directory.mkdir(parents=True, mode=0o700)
    file_path = session_directory / "events.jsonl"
    descriptor = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    return os.fdopen(descriptor, "w", encoding="utf-8", buffering=1), session_id, file_path


def record(stream: object, session_id: str, sequence: int, event: str, console: bool = True, **fields: object) -> None:
    data = {"schema_version": 1, "session_id": session_id, "sequence": sequence,
            "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="microseconds"),
            "monotonic_ns": time.monotonic_ns(), "event": event, **fields}
    stream.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")
    stream.flush()
    os.fsync(stream.fileno())
    if console:
        print(json.dumps(data, ensure_ascii=False, sort_keys=True), flush=True)


def environment() -> dict:
    return {"platform": platform.platform(), "macos_version": platform.mac_ver()[0],
            "machine": platform.machine(), "python": sys.version, "executable": sys.executable,
            "backend": "IOKit IOHIDDevice", "diagnostic_version": "0.1.0",
            "physical_mode": "unknown", "actions_enabled": False,
            "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(Path(__file__).parent.glob('*.py'))}}
