#!/usr/bin/env python3
"""
Local Qwen2.5-3B chat, the fast (Ollama 4-bit) way.

Double-click / pin this and it will:
  1. make sure the Ollama server is running (starts it if not),
  2. make sure the qwen2.5:3b model is present (pulls it ONCE; cached forever after),
  3. open a chat in this window.

One conversation per window (fresh history each launch), seeded with a "be helpful,
accurate, but brief" system prompt because CPU generation is slow.

No third-party dependencies — standard library only.
"""

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen2.5:3b"
SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer accurately, but keep your replies fairly "
    "brief and to the point — you are running locally on a CPU, so long answers are "
    "slow to produce. Give a short, direct answer and only expand if the user asks "
    "for more detail."
)


# ---------- console helpers ----------

def _setup_console():
    """Best-effort UTF-8 output + a friendly window title on Windows."""
    for stream in (sys.stdout, sys.stdin):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("Local Qwen2.5 Chat (Ollama)")
            # enable ANSI escape processing so we could colourise later
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


# ---------- ollama plumbing ----------

def find_ollama():
    """Locate the ollama executable on PATH or in the default install dir."""
    exe = shutil.which("ollama")
    if exe:
        return exe
    cand = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                        "Programs", "Ollama", "ollama.exe")
    return cand if os.path.isfile(cand) else None


def server_up():
    try:
        urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=3)
        return True
    except Exception:
        return False


def ensure_server(exe):
    if server_up():
        return
    if not exe:
        sys.exit("Ollama is not installed. Get it from https://ollama.com/download")
    print("Starting the Ollama server ...", flush=True)
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
    subprocess.Popen([exe, "serve"], creationflags=flags,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):              # wait up to ~30s
        if server_up():
            return
        time.sleep(0.5)
    sys.exit("Could not reach the Ollama server at " + OLLAMA_URL)


def model_present():
    try:
        with urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=5) as r:
            tags = json.load(r)
        return any(m.get("name") == MODEL for m in tags.get("models", []))
    except Exception:
        return False


def ensure_model(exe):
    if model_present():
        return
    print(f"First run: downloading {MODEL} (~2 GB). This happens only once ...\n",
          flush=True)
    if exe:
        subprocess.run([exe, "pull", MODEL], check=True)
    else:
        # Fallback: pull via the HTTP API with a minimal progress line.
        body = json.dumps({"model": MODEL}).encode()
        req = urllib.request.Request(OLLAMA_URL + "/api/pull", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3600) as r:
            for line in r:
                try:
                    status = json.loads(line).get("status", "")
                except Exception:
                    status = ""
                if status:
                    print("  " + status, end="\r", flush=True)
        print()


# ---------- chat loop ----------

def stream_reply(history):
    """POST the history, stream tokens to the screen, return the full text."""
    body = json.dumps({"model": MODEL, "messages": history, "stream": True}).encode()
    req = urllib.request.Request(OLLAMA_URL + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    parts = []
    print("Assistant: ", end="", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            for line in r:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                chunk = obj.get("message", {}).get("content", "")
                if chunk:
                    print(chunk, end="", flush=True)
                    parts.append(chunk)
                if obj.get("done"):
                    break
    except KeyboardInterrupt:
        print("  [stopped]", flush=True)
    except urllib.error.URLError as e:
        print(f"\n[error talking to Ollama: {e}]")
        return None
    print()
    return "".join(parts)


def chat():
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("=" * 64)
    print(f"  Local chat with {MODEL}  (4-bit, via Ollama)")
    print("  Type your message and press Enter.")
    print("  Ctrl+C stops a long answer.  Type /exit (or close the window) to quit.")
    print("=" * 64)
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        if user.lower() in ("/exit", "/quit", "/bye"):
            print("Bye!")
            return
        if not user:
            continue
        history.append({"role": "user", "content": user})
        reply = stream_reply(history)
        if reply is None:                 # request failed; drop the user turn
            history.pop()
        else:
            history.append({"role": "assistant", "content": reply})


def main():
    _setup_console()
    exe = find_ollama()
    ensure_server(exe)
    ensure_model(exe)
    chat()


if __name__ == "__main__":
    main()
