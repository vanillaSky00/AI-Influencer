# High-tech dark Tkinter chat that talks to your FastAPI Celery backend.
# Endpoints used:
#   POST /avatar/reply   -> {task_id, status}
#   POST /avatar/post    -> {task_id, status}
#   POST /tasks/{id}     -> {status: pending|success|failed|..., data?}

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading, time, json
from functools import partial
import os

try:
    import requests
except ImportError:
    raise SystemExit("Please install 'requests':  pip install requests")

# -------------------- CONFIG --------------------
API_BASE = os.getenv("API_BASE", "http://web:8000")   # change if your FastAPI runs elsewhere
POLL_INTERVAL = 1.0                   # seconds between task-status checks
# ------------------------------------------------

PALETTE = {
    "bg": "#0b1220",          # page background (very dark blue/slate)
    "panel": "#0f172a",       # panel cards (slate-900)
    "border": "#1f2937",      # borders (slate-700)
    "text": "#e5e7eb",        # main text (gray-200)
    "muted": "#9ca3af",       # muted text (gray-400)
    "accent": "#06b6d4",      # cyan-500-ish
    "accent2": "#4f46e5",     # indigo-600
    "user_bubble": "#1e3a8a", # indigo-800
    "bot_bubble": "#0ea5e9",  # cyan-500
    "bot_text": "#041016",    # near-black for cyan contrast
}

def http_json(method, url, **kw):
    headers = kw.pop("headers", {})
    headers["Content-Type"] = "application/json"
    data = kw.pop("json", None)
    r = requests.request(method, url, headers=headers, json=data, timeout=30, **kw)
    r.raise_for_status()
    if r.content:
        return r.json()
    return {}

class ChatUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Meow Bot")
        root.geometry("420x600")
        root.configure(bg=PALETTE["bg"])

        # ---- Top header / mode ----
        header = tk.Frame(root, bg=PALETTE["panel"], highlightthickness=1, highlightbackground=PALETTE["border"])
        header.pack(fill=tk.X, padx=10, pady=(10,6))
        title = tk.Label(header, text="Vanilla Meow", fg=PALETTE["text"], bg=PALETTE["panel"],
                         font=("SF Pro Display", 12, "bold"))
        title.pack(side=tk.LEFT, padx=10, pady=8)

        self.mode = tk.StringVar(value="reply")  # "reply" or "post"
        mode_wrap = tk.Frame(header, bg=PALETTE["panel"])
        mode_wrap.pack(side=tk.RIGHT, padx=8)
        ttk.Style().configure("TButton", padding=3)
        self.reply_btn = tk.Radiobutton(mode_wrap, text="Reply", variable=self.mode, value="reply",
                                        fg=PALETTE["text"], bg=PALETTE["panel"], selectcolor=PALETTE["panel"],
                                        activebackground=PALETTE["panel"], font=("SF Pro Text", 10))
        self.post_btn  = tk.Radiobutton(mode_wrap, text="Post",  variable=self.mode, value="post",
                                        fg=PALETTE["text"], bg=PALETTE["panel"], selectcolor=PALETTE["panel"],
                                        activebackground=PALETTE["panel"], font=("SF Pro Text", 10))
        self.reply_btn.pack(side=tk.LEFT, padx=(0,8))
        self.post_btn.pack(side=tk.LEFT)

        # ---- Chat area ----
        body = tk.Frame(root, bg=PALETTE["panel"], highlightthickness=1, highlightbackground=PALETTE["border"])
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,6))

        self.chat = scrolledtext.ScrolledText(body, wrap=tk.WORD, state="disabled",
                                              bg=PALETTE["panel"], fg=PALETTE["text"],
                                              insertbackground=PALETTE["text"], bd=0, padx=10, pady=10, height=20)
        self.chat.pack(fill=tk.BOTH, expand=True)

        # text tags for bubble-ish look
        self.chat.tag_configure("user", foreground="white", background=PALETTE["user_bubble"], lmargin1=80, lmargin2=80, rmargin=10, spacing3=6)
        self.chat.tag_configure("bot", foreground=PALETTE["bot_text"], background=PALETTE["bot_bubble"], lmargin1=10, lmargin2=10, rmargin=80, spacing3=6)
        self.chat.tag_configure("sys", foreground=PALETTE["muted"], spacing3=4)

        # ---- Composer ----
        composer = tk.Frame(root, bg=PALETTE["panel"], highlightthickness=1, highlightbackground=PALETTE["border"])
        composer.pack(fill=tk.X, padx=10, pady=(0,10))

        self.entry = tk.Entry(composer, bg=PALETTE["bg"], fg=PALETTE["text"],
                              insertbackground=PALETTE["text"], relief=tk.FLAT,
                              font=("SF Mono", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10,6), pady=10)
        self.entry.bind("<Return>", lambda e: self.send())

        self.send_btn = tk.Button(composer, text="Send",
                                  command=self.send,
                                  fg="white", bg=PALETTE["accent2"], activebackground=PALETTE["accent"],
                                  relief=tk.FLAT, padx=10, pady=6, font=("SF Pro Text", 10, "bold"))
        self.send_btn.pack(side=tk.LEFT, padx=(0,10), pady=8)

        self.append("sys", "🐱 Cat Avatar console ready. Choose Reply or Post, type a prompt, and hit Send.")

    # ---------- UI helpers ----------
    def append(self, tag, text):
        self.chat.config(state="normal")
        if tag in ("user","bot"):
            # add some padding and rounded illusion with spaces
            padded = "  " + text.strip() + "  "
            self.chat.insert(tk.END, padded + "\n", tag)
        else:
            self.chat.insert(tk.END, text + "\n", tag)
        self.chat.config(state="disabled")
        self.chat.see(tk.END)

    def set_busy(self, busy: bool):
        self.send_btn.config(state=("disabled" if busy else "normal"))
        self.entry.config(state=("disabled" if busy else "normal"))

    # ---------- Actions ----------
    def send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.append("user", text)
        self.append("sys", "… queued task, waiting for result")
        self.set_busy(True)
        threading.Thread(target=self._background_send, args=(text, self.mode.get()), daemon=True).start()

    def _background_send(self, text: str, mode: str):
        try:
            # queue task
            endpoint = "/avatar/reply" if mode == "reply" else "/avatar/post"
            data = http_json("POST", API_BASE + endpoint, json={"prompt": text})
            task_id = data.get("task_id")
            if not task_id:
                raise RuntimeError(f"Missing task_id from {endpoint}: {data}")

            # poll until done
            while True:
                time.sleep(POLL_INTERVAL)
                status = http_json("GET", f"{API_BASE}/tasks/{task_id}")
                state = status.get("status", "unknown").lower()
                if state in ("pending", "started", "received"):
                    continue
                if state == "success":
                    payload = status.get("data")
                    reply = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
                    self.root.after(0, partial(self._on_success, reply))
                    return
                if state == "failed" or state == "failure":
                    err = status.get("error", "(unknown error)")
                    self.root.after(0, partial(self._on_error, f"Task failed: {err}"))
                    return
                # unexpected state
                self.root.after(0, partial(self._on_error, f"Task state: {state}"))
                return

        except Exception as e:
            self.root.after(0, partial(self._on_error, str(e)))

    def _on_success(self, reply: str):
        self.append("bot", reply)
        self.set_busy(False)

    def _on_error(self, msg: str):
        self.append("sys", f"⚠️ {msg}")
        self.set_busy(False)

def main():
    root = tk.Tk()

    # global window styling
    root.configure(bg=PALETTE["bg"])
    # subtle drop-shadow effect using overrideredirect hack is possible but not portable; keeping defaults.

    app = ChatUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()



## TODO: leave button