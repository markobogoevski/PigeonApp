from __future__ import annotations

import threading
import webbrowser
from http.server import ThreadingHTTPServer

from app import PigeonHandler


def start_server() -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), PigeonHandler)
    host, port = server.server_address
    url = f"http://{host}:{port}/"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, url


def run_controller(server: ThreadingHTTPServer, url: str) -> None:
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print(f"Pigeon Joke Square is running at {url}")
        print("Close this window to stop the app.")
        try:
            threading.Event().wait()
        finally:
            server.shutdown()
        return

    root = tk.Tk()
    root.title("Pigeon Joke Square")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=18)
    frame.grid(row=0, column=0, sticky="nsew")

    title = ttk.Label(frame, text="Pigeon Joke Square is running", font=("", 12, "bold"))
    title.grid(row=0, column=0, columnspan=2, sticky="w")

    url_label = ttk.Label(frame, text=url)
    url_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 14))

    open_button = ttk.Button(frame, text="Open App", command=lambda: webbrowser.open(url))
    open_button.grid(row=2, column=0, sticky="ew", padx=(0, 8))

    def quit_app() -> None:
        server.shutdown()
        root.destroy()

    quit_button = ttk.Button(frame, text="Quit", command=quit_app)
    quit_button.grid(row=2, column=1, sticky="ew")

    root.protocol("WM_DELETE_WINDOW", quit_app)
    root.mainloop()


def main() -> None:
    server, url = start_server()
    webbrowser.open(url)
    run_controller(server, url)


if __name__ == "__main__":
    main()
