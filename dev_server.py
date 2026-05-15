from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WATCHED_SUFFIXES = {".py"}


def snapshot() -> dict[Path, int]:
    files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix in WATCHED_SUFFIXES
        and "__pycache__" not in path.parts
    ]
    return {path: path.stat().st_mtime_ns for path in files}


def start_app() -> subprocess.Popen:
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    return subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env)


def stop_app(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def main() -> None:
    process = start_app()
    previous = snapshot()

    try:
        while True:
            time.sleep(0.75)
            current = snapshot()
            if current != previous:
                previous = current
                print("Change detected; restarting Python server.", flush=True)
                stop_app(process)
                process = start_app()

            if process.poll() is not None:
                print("Python server stopped; restarting.", flush=True)
                process = start_app()
    finally:
        stop_app(process)


if __name__ == "__main__":
    main()
