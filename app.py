from __future__ import annotations

import json
import mimetypes
import os
import random
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from jokes import JOKES


def resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent


ROOT = resource_root()
STATIC_DIR = ROOT / "static"
MIN_PIGEON_DISTANCE = 18
POSITION_GRID = tuple(
    (x, y)
    for y in (20, 38, 56, 74)
    for x in (10, 28, 46, 64, 82)
)


def build_scene(seed: int | None = None) -> dict:
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    count = rng.randint(8, 12)
    pair_left, pair_right = sorted(rng.sample(range(count), 2))

    joke_count = count - 2
    scene_jokes = rng.sample(JOKES, joke_count)
    male_on_left = rng.choice([True, False])

    pigeons = []
    available_positions = list(POSITION_GRID)
    rng.shuffle(available_positions)
    joke_index = 0

    def is_spaced(point: tuple[int, int], positions: list[tuple[int, int]]) -> bool:
        return all(
            ((point[0] - other[0]) ** 2 + (point[1] - other[1]) ** 2) ** 0.5
            >= MIN_PIGEON_DISTANCE
            for other in positions
        )

    def reserve_position(x_range: tuple[int, int], y_range: tuple[int, int]) -> tuple[int, int]:
        for point in available_positions:
            if x_range[0] <= point[0] <= x_range[1] and y_range[0] <= point[1] <= y_range[1]:
                available_positions.remove(point)
                return point

        return available_positions.pop()

    def pair_position() -> tuple[tuple[int, int], tuple[int, int]]:
        for first in available_positions:
            possible_seconds = [point for point in available_positions if point != first]
            rng.shuffle(possible_seconds)
            for second in possible_seconds:
                if abs(first[0] - second[0]) < 24:
                    continue
                left, right = sorted([first, second], key=lambda point: point[0])
                available_positions.remove(left)
                available_positions.remove(right)
                return left, right

        left = reserve_position((10, 34), (22, 78))
        right = reserve_position((66, 88), (22, 78))
        return left, right

    pair_left_position, pair_right_position = pair_position()

    for idx in range(count):
        if idx == pair_left:
            pigeons.append(
                {
                    "id": f"pigeon-{idx}",
                    "kind": "male" if male_on_left else "female",
                    "behavior": "kiss",
                    "pairRole": "left",
                    "x": pair_left_position[0],
                    "y": pair_left_position[1],
                    "facing": "right",
                    "isJoker": False,
                    "joke": None,
                    "delay": round(rng.uniform(0, 1.8), 2),
                    "scale": round(rng.uniform(0.96, 1.06), 2),
                }
            )
            continue

        if idx == pair_right:
            pigeons.append(
                {
                    "id": f"pigeon-{idx}",
                    "kind": "female" if male_on_left else "male",
                    "behavior": "kiss",
                    "pairRole": "right",
                    "x": pair_right_position[0],
                    "y": pair_right_position[1],
                    "facing": "left",
                    "isJoker": False,
                    "joke": None,
                    "delay": round(rng.uniform(0, 1.8), 2),
                    "scale": round(rng.uniform(0.96, 1.06), 2),
                }
            )
            continue

        x, y = reserve_position((8, 86), (18, 76))
        pigeons.append(
            {
                "id": f"pigeon-{idx}",
                "kind": "regular",
                "behavior": "wander",
                "pairRole": None,
                "x": x,
                "y": y,
                "facing": rng.choice(["left", "right"]),
                "isJoker": True,
                "joke": scene_jokes[joke_index],
                "delay": round(rng.uniform(0, 1.8), 2),
                "scale": round(rng.uniform(0.86, 1.16), 2),
            }
        )
        joke_index += 1

    return {"count": count, "pigeons": pigeons}


def build_version() -> dict:
    watched_files = [ROOT / "app.py", *STATIC_DIR.rglob("*")]
    newest_mtime = max(
        path.stat().st_mtime_ns for path in watched_files if path.is_file()
    )
    return {"version": str(newest_mtime)}


class PigeonHandler(BaseHTTPRequestHandler):
    server_version = "PigeonJokes/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._send_file(STATIC_DIR / "index.html")
            return

        if path == "/api/pigeons":
            self._send_json(build_scene())
            return

        if path == "/api/joke":
            self._send_json({"joke": random.SystemRandom().choice(JOKES)})
            return

        if path == "/api/version":
            self._send_json(build_version())
            return

        if path.startswith("/static/"):
            relative = unquote(path.removeprefix("/static/"))
            target = (STATIC_DIR / relative).resolve()
            if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR.resolve():
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            self._send_file(target)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), PigeonHandler)
    print(f"Serving pigeon jokes on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
