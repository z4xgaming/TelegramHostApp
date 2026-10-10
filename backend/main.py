# main.py - Instant deploy + background library install
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, os, time, sys, shutil, threading, re

app = FastAPI(title="Telegram Bot Hosting API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.expanduser("~/TelegramHostApp")
BOTS_DIR = os.path.join(BASE_DIR, "running_bots")
SHARED_VENV = os.path.join(BASE_DIR, "shared_venv")
os.makedirs(BOTS_DIR, exist_ok=True)

PROCESSES = {}
AUTO_RESTART = {}
INSTALLING = set()  # bots jinki libraries install ho rahi hain

IMPORT_TO_PIP = {
    "telegram": "python-telegram-bot", "Crypto": "pycryptodome",
    "Cryptodome": "pycryptodome", "PIL": "Pillow", "cv2": "opencv-python-headless",
    "jwt": "PyJWT", "dotenv": "python-dotenv", "bs4": "beautifulsoup4",
    "yaml": "PyYAML", "dateutil": "python-dateutil", "pytz": "pytz",
    "aiohttp": "aiohttp", "numpy": "numpy", "pandas": "pandas",
    "sqlalchemy": "SQLAlchemy", "psutil": "psutil", "telethon": "Telethon",
    "pyrogram": "pyrogram", "tgcrypto": "TgCrypto", "requests": "requests",
}

STDLIB = {"os","sys","time","json","re","random","datetime","asyncio","logging",
          "math","subprocess","threading","collections","typing","pathlib",
          "base64","hashlib","hmac","secrets","string","urllib","io","functools",
          "itertools","uuid","signal","codecs","concurrent","inspect","traceback",
          "warnings","abc","copy","enum","glob","shutil","tempfile","zipfile","socket"}

class BotCreate(BaseModel):
    name: str
    token: str
    code: str
    requirements: str = ""

def ensure_venv():
    if not os.path.exists(SHARED_VENV):
        subprocess.run([sys.executable, "-m", "venv", SHARED_VENV], timeout=300)
        pip = os.path.join(SHARED_VENV, "bin", "pip")
        subprocess.run([pip, "install", "--upgrade", "pip", "wheel", "setuptools"], timeout=300)
        subprocess.run([pip, "install", "python-telegram-bot", "requests", "PyJWT"], timeout=900)
    return os.path.join(SHARED_VENV, "bin", "python")

def detect_libraries(code):
    imports = set()
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            for p in line[7:].split(","):
                imports.add(p.strip().split()[0].split(".")[0])
        elif line.startswith("from ") and " import " in line:
            imports.add(line[5:].split(" import ")[0].strip().split(".")[0])
    return imports

def install_and_start(bot_id, code, req_text, token):
    """Background: libraries install + bot start"""
    info = PROCESSES[bot_id]
    log_file = info["log"]
    try:
        INSTALLING.add(bot_id)
        log_file.write(f"[*] Background install starting at {time.strftime('%H:%M:%S')}\n")
        log_file.flush()

        # Libraries detect karo
        to_install = set()
        if req_text.strip():
            for line in req_text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    to_install.add(line)
        for imp in detect_libraries(code):
            if imp in STDLIB or imp.startswith("_"): continue
            to_install.add(IMPORT_TO_PIP.get(imp, imp))

        if to_install:
            log_file.write(f"[*] Installing {len(to_install)} libraries: {', '.join(sorted(to_install))}\n")
            log_file.flush()
            pip = os.path.join(SHARED_VENV, "bin", "pip")
            for lib in sorted(to_install):
                log_file.write(f"[*] Installing {lib}...\n")
                log_file.flush()
                try:
                    subprocess.run([pip, "install", "--no-cache-dir", lib],
                                   timeout=1800, check=False,
                                   stdout=log_file, stderr=subprocess.STDOUT)
                    log_file.write(f"[+] {lib} installed\n")
                except Exception as e:
                    log_file.write(f"[!] {lib} failed: {e}\n")
                log_file.flush()

        log_file.write("[*] Starting bot process...\n")
        log_file.flush()

        env = os.environ.copy()
        env["BOT_TOKEN"] = token
        py = os.path.join(SHARED_VENV, "bin", "python")
        proc = subprocess.Popen([py, os.path.join(info["dir"], "bot.py")],
                                env=env, stdout=log_file, stderr=subprocess.STDOUT)
        info["proc"] = proc
        AUTO_RESTART[bot_id] = True
        threading.Thread(target=watchdog, args=(bot_id,), daemon=True).start()
        log_file.write(f"[+] Bot started PID: {proc.pid}\n")
        log_file.flush()
    except Exception as e:
        log_file.write(f"[!] Install error: {e}\n")
        log_file.flush()
    finally:
        INSTALLING.discard(bot_id)

def watchdog(bot_id):
    while AUTO_RESTART.get(bot_id, False):
        time.sleep(10)
        if bot_id not in PROCESSES or not AUTO_RESTART.get(bot_id, False):
            break
        info = PROCESSES[bot_id]
        proc = info.get("proc")
        if proc and proc.poll() is not None:
            info["log"].write(f"\n[!] Process died (exit {proc.returncode}) - restarting...\n")
            info["log"].flush()
            try:
                env = os.environ.copy()
                tok = os.path.join(info["dir"], "token.txt")
                if os.path.exists(tok): env["BOT_TOKEN"] = open(tok).read().strip()
                py = os.path.join(SHARED_VENV, "bin", "python")
                info["proc"] = subprocess.Popen([py, os.path.join(info["dir"], "bot.py")],
                                                env=env, stdout=info["log"], stderr=subprocess.STDOUT)
            except Exception as e:
                info["log"].write(f"[!] Restart failed: {e}\n")
                info["log"].flush()

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/bot/create")
def create_bot(bot: BotCreate):
    try:
        ensure_venv()
        bot_id = f"bot_{int(time.time()*1000)}"
        bot_dir = os.path.join(BOTS_DIR, bot_id)
        os.makedirs(bot_dir, exist_ok=True)
        with open(os.path.join(bot_dir, "bot.py"), "w") as f:
            f.write(bot.code)
        with open(os.path.join(bot_dir, "token.txt"), "w") as f:
            f.write(bot.token)
        log_file = open(os.path.join(bot_dir, "log.txt"), "w")
        log_file.write(f"[*] Deploy at {time.strftime('%H:%M:%S')}\n")
        log_file.flush()

        PROCESSES[bot_id] = {"proc": None, "name": bot.name,
                             "dir": bot_dir, "log": log_file}
        # Background thread mein install + start
        threading.Thread(target=install_and_start,
                         args=(bot_id, bot.code, bot.requirements, bot.token),
                         daemon=True).start()
        return {"status": "success", "bot_id": bot_id,
                "message": "Deploy started - libraries installing in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bot/{bot_id}/status")
def bot_status(bot_id: str):
    if bot_id not in PROCESSES:
        return {"status": "unknown", "running": False, "installing": False,
                "pid": "", "auto_restart": False}
    info = PROCESSES[bot_id]
    if bot_id in INSTALLING:
        return {"status": "installing", "running": False, "installing": True,
                "pid": "", "auto_restart": False}
    proc = info.get("proc")
    if proc is None:
        return {"status": "waiting", "running": False, "installing": False,
                "pid": "", "auto_restart": False}
    alive = proc.poll() is None
    return {"status": "running" if alive else "stopped",
            "running": alive, "installing": False,
            "pid": str(proc.pid) if alive else "",
            "exit_code": None if alive else proc.returncode,
            "auto_restart": AUTO_RESTART.get(bot_id, False)}

@app.post("/bot/{bot_id}/stop")
def stop_bot(bot_id: str):
    if bot_id not in PROCESSES: raise HTTPException(404, "not found")
    AUTO_RESTART[bot_id] = False
    proc = PROCESSES[bot_id].get("proc")
    if proc:
        try: proc.terminate()
        except: pass
    return {"status": "stopped", "bot_id": bot_id}

@app.post("/bot/{bot_id}/restart")
def restart_bot(bot_id: str):
    if bot_id not in PROCESSES: raise HTTPException(404, "not found")
    p = PROCESSES[bot_id]
    proc = p.get("proc")
    if proc:
        try: proc.terminate()
        except: pass
    time.sleep(1)
    env = os.environ.copy()
    tok = os.path.join(p["dir"], "token.txt")
    if os.path.exists(tok): env["BOT_TOKEN"] = open(tok).read().strip()
    py = os.path.join(SHARED_VENV, "bin", "python")
    p["proc"] = subprocess.Popen([py, os.path.join(p["dir"], "bot.py")],
                                  env=env, stdout=p["log"], stderr=subprocess.STDOUT)
    AUTO_RESTART[bot_id] = True
    return {"status": "restarted", "bot_id": bot_id}

@app.get("/bot/{bot_id}/logs")
def get_logs(bot_id: str):
    if bot_id not in PROCESSES: raise HTTPException(404, "not found")
    lp = os.path.join(PROCESSES[bot_id]["dir"], "log.txt")
    if os.path.exists(lp):
        with open(lp, "r", errors="ignore") as f:
            return {"logs": f.read()[-8000:]}
    return {"logs": "No logs"}

@app.get("/bots")
def list_bots():
    return {"bots": [{"id": b, "name": i["name"],
                      "status": "installing" if b in INSTALLING else ("running" if i.get("proc") and i["proc"].poll() is None else "stopped"),
                      "auto_restart": AUTO_RESTART.get(b, False)}
                     for b, i in PROCESSES.items()]}

@app.delete("/bot/{bot_id}")
def delete_bot(bot_id: str):
    if bot_id in PROCESSES:
        AUTO_RESTART[bot_id] = False
        proc = PROCESSES[bot_id].get("proc")
        if proc:
            try: proc.terminate()
            except: pass
        shutil.rmtree(PROCESSES[bot_id]["dir"], ignore_errors=True)
        del PROCESSES[bot_id]
    return {"status": "deleted"}
