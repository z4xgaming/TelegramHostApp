# main.py - Real bot hosting + auto library install + auto-restart 10s
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, os, time, sys, shutil, threading

app = FastAPI(title="Telegram Bot Hosting API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.expanduser("~/TelegramHostApp")
BOTS_DIR = os.path.join(BASE_DIR, "running_bots")
SHARED_VENV = os.path.join(BASE_DIR, "shared_venv")
os.makedirs(BOTS_DIR, exist_ok=True)

PROCESSES = {}
AUTO_RESTART = {}   # bot_id -> bool
WATCHDOG_TIMEOUT = 10  # seconds

class BotCreate(BaseModel):
    name: str
    token: str
    code: str
    requirements: str = ""

def ensure_venv():
    """Ek shared venv - Termux ki jagah project folder mein"""
    if not os.path.exists(SHARED_VENV):
        print("[*] Creating shared venv (in project folder)...")
        subprocess.run([sys.executable, "-m", "venv", SHARED_VENV], timeout=300)
        pip = os.path.join(SHARED_VENV, "bin", "pip")
        subprocess.run([pip, "install", "--upgrade", "pip"], timeout=300)
        subprocess.run([pip, "install", "python-telegram-bot", "requests"], timeout=900)
    return os.path.join(SHARED_VENV, "bin", "python")

def install_requirements(req_text, log_file):
    """Bot file ke andar se libraries install - Termux pe nahi"""
    if not req_text.strip():
        return
    pip = os.path.join(SHARED_VENV, "bin", "pip")
    req_file = os.path.join(BASE_DIR, "_temp_req.txt")
    with open(req_file, "w") as f:
        f.write(req_text)
    log_file.write(f"[*] Installing {len(req_text.splitlines())} libraries...\n")
    log_file.flush()
    try:
        subprocess.run([pip, "install", "-r", req_file], timeout=1800, check=False,
                       stdout=log_file, stderr=log_file)
    finally:
        if os.path.exists(req_file):
            os.remove(req_file)

def auto_install_from_code(bot_dir, code, log_file):
    """Bot code ke andar se requirements auto-detect karke install"""
    imports = set()
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            imports.add(line.split()[1].split(".")[0])
        elif line.startswith("from ") and " import " in line:
            imports.add(line.split()[1].split(".")[0])
    # Skip stdlib
    stdlib = {"os","sys","time","json","re","random","datetime","asyncio","logging",
              "math","subprocess","threading","collections","typing","pathlib"}
    to_install = [i for i in imports if i not in stdlib and i != "telegram"]
    if to_install:
        log_file.write(f"[*] Auto-detected libraries: {', '.join(to_install)}\n")
        log_file.flush()
        pip = os.path.join(SHARED_VENV, "bin", "pip")
        subprocess.run([pip, "install"] + to_install, timeout=1800, check=False,
                       stdout=log_file, stderr=log_file)

def watchdog(bot_id):
    """Har 10 sec mein bot alive check - dead to auto-restart"""
    while AUTO_RESTART.get(bot_id, False):
        time.sleep(WATCHDOG_TIMEOUT)
        if bot_id not in PROCESSES:
            break
        if not AUTO_RESTART.get(bot_id, False):
            break
        proc = PROCESSES[bot_id]["proc"]
        if proc.poll() is not None:
            # Bot crash ho gaya - restart karo
            info = PROCESSES[bot_id]
            info["log"].write(f"\n[!] Bot crashed - auto-restarting at {time.strftime('%H:%M:%S')}\n")
            info["log"].flush()
            try:
                env = os.environ.copy()
                tok_path = os.path.join(info["dir"], "token.txt")
                if os.path.exists(tok_path):
                    env["BOT_TOKEN"] = open(tok_path).read().strip()
                py = os.path.join(SHARED_VENV, "bin", "python")
                info["proc"] = subprocess.Popen(
                    [py, os.path.join(info["dir"], "bot.py")],
                    env=env, stdout=info["log"], stderr=subprocess.STDOUT)
            except Exception as e:
                info["log"].write(f"[!] Restart failed: {e}\n")
                info["log"].flush()

@app.get("/")
def root():
    return {"status": "API running", "app": "Telegram Bot Hosting"}

@app.post("/bot/create")
def create_bot(bot: BotCreate):
    try:
        py = ensure_venv()
        bot_id = f"bot_{int(time.time())}"
        bot_dir = os.path.join(BOTS_DIR, bot_id)
        os.makedirs(bot_dir, exist_ok=True)
        bot_file = os.path.join(bot_dir, "bot.py")
        with open(bot_file, "w") as f:
            f.write(bot.code)
        with open(os.path.join(bot_dir, "token.txt"), "w") as f:
            f.write(bot.token)
        log_file = open(os.path.join(bot_dir, "log.txt"), "w")
        # Auto-install libraries (bot ke andar se)
        if bot.requirements:
            install_requirements(bot.requirements, log_file)
        else:
            auto_install_from_code(bot_dir, bot.code, log_file)
        env = os.environ.copy()
        env["BOT_TOKEN"] = bot.token
        proc = subprocess.Popen([py, bot_file], env=env,
                                stdout=log_file, stderr=subprocess.STDOUT)
        PROCESSES[bot_id] = {"proc": proc, "name": bot.name,
                             "dir": bot_dir, "log": log_file}
        AUTO_RESTART[bot_id] = True
        threading.Thread(target=watchdog, args=(bot_id,), daemon=True).start()
        return {"status": "success", "bot_id": bot_id, "message": "Bot deployed with auto-restart!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bot/{bot_id}/status")
def bot_status(bot_id: str):
    """REAL status - actually process check karta hai"""
    if bot_id not in PROCESSES:
        return {"status": "unknown", "running": False, "pid": ""}
    proc = PROCESSES[bot_id]["proc"]
    alive = proc.poll() is None
    return {"status": "running" if alive else "stopped",
            "running": alive,
            "pid": str(proc.pid) if alive else "",
            "auto_restart": AUTO_RESTART.get(bot_id, False)}

@app.post("/bot/{bot_id}/stop")
def stop_bot(bot_id: str):
    if bot_id not in PROCESSES:
        raise HTTPException(404, "Bot not found")
    AUTO_RESTART[bot_id] = False  # Watchdog band
    PROCESSES[bot_id]["proc"].terminate()
    return {"status": "stopped", "bot_id": bot_id}

@app.post("/bot/{bot_id}/restart")
def restart_bot(bot_id: str):
    if bot_id not in PROCESSES:
        raise HTTPException(404, "Bot not found")
    p = PROCESSES[bot_id]
    try: p["proc"].terminate()
    except: pass
    time.sleep(1)
    env = os.environ.copy()
    tok_path = os.path.join(p["dir"], "token.txt")
    if os.path.exists(tok_path):
        env["BOT_TOKEN"] = open(tok_path).read().strip()
    py = os.path.join(SHARED_VENV, "bin", "python")
    p["proc"] = subprocess.Popen([py, os.path.join(p["dir"], "bot.py")],
                                  env=env, stdout=p["log"], stderr=subprocess.STDOUT)
    AUTO_RESTART[bot_id] = True
    return {"status": "restarted", "bot_id": bot_id}

@app.get("/bot/{bot_id}/logs")
def get_logs(bot_id: str):
    if bot_id not in PROCESSES:
        raise HTTPException(404, "Bot not found")
    log_path = os.path.join(PROCESSES[bot_id]["dir"], "log.txt")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return {"logs": f.read()[-5000:]}
    return {"logs": "No logs yet"}

@app.get("/bots")
def list_bots():
    bots = []
    for bid, info in PROCESSES.items():
        alive = info["proc"].poll() is None
        bots.append({"id": bid, "name": info["name"],
                     "status": "running" if alive else "stopped",
                     "auto_restart": AUTO_RESTART.get(bid, False)})
    return {"bots": bots}

@app.delete("/bot/{bot_id}")
def delete_bot(bot_id: str):
    if bot_id in PROCESSES:
        AUTO_RESTART[bot_id] = False
        try: PROCESSES[bot_id]["proc"].terminate()
        except: pass
        shutil.rmtree(PROCESSES[bot_id]["dir"], ignore_errors=True)
        del PROCESSES[bot_id]
    return {"status": "deleted"}
