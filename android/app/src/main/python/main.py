"""
Bot Runner - app ke andar Python
Ye code app ke andar run karega, Termux ki zaroorat nahi
"""

import os
import sys
import json
import threading
import time
import traceback

# Global state
_current_bot = None
_bot_thread = None
_bot_running = False
_log_buffer = []

def log(msg):
    """Log buffer mein add karo"""
    global _log_buffer
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    _log_buffer.append(line)
    if len(_log_buffer) > 500:
        _log_buffer = _log_buffer[-500:]
    print(line)

def get_logs():
    """Saare logs return karo"""
    return "\n".join(_log_buffer)

def clear_logs():
    global _log_buffer
    _log_buffer = []

def run_bot(code, token):
    """Bot ko background thread mein chalao"""
    global _bot_running, _current_bot
    try:
        _bot_running = True
        os.environ["BOT_TOKEN"] = token

        # User code ko exec karo
        globals_dict = {
            "__name__": "__main__",
            "BOT_TOKEN": token,
            "os": os,
            "sys": sys,
            "print": lambda *a, **kw: log(" ".join(str(x) for x in a)),
        }

        log("🚀 Bot starting...")
        exec(code, globals_dict)
        log("✅ Bot code executed")
    except Exception as e:
        log(f"❌ Bot error: {e}")
        log(traceback.format_exc())
    finally:
        _bot_running = False

def start_bot(code, token):
    """Bot start karo (naya thread)"""
    global _bot_thread, _bot_running
    if _bot_running:
        return "already_running"

    clear_logs()
    _bot_thread = threading.Thread(target=run_bot, args=(code, token), daemon=True)
    _bot_thread.start()
    return "started"

def stop_bot():
    """Bot stop karo"""
    global _bot_running
    _bot_running = False
    log("⏹️ Stop signal received")
    return "stopped"

def is_running():
    """Bot chal raha hai kya?"""
    return _bot_running

def greet(name):
    """Test function"""
    return f"Hello {name} from Python!"

def test_libraries():
    """Saari libraries test karo"""
    results = {}
    libs = ["telegram", "requests", "aiohttp", "jwt", "dotenv", "pytz",
            "dateutil", "sqlalchemy", "aiosqlite", "colorama", "emoji"]
    for lib in libs:
        try:
            __import__(lib)
            results[lib] = "✅ OK"
        except Exception as e:
            results[lib] = f"❌ {e}"
    return json.dumps(results, indent=2)
