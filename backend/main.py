# main.py - Telegram Bot Hosting API (Real Working)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, os, signal, json, time

app = FastAPI(title="Telegram Bot Hosting API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BOTS_DIR = os.path.expanduser("~/TelegramHostApp/running_bots")
os.makedirs(BOTS_DIR, exist_ok=True)
PROCESSES = {}

class BotCreate(BaseModel):
    name: str
    token: str
    code: str

@app.get("/")
def root():
    return {"status": "API running", "app": "Telegram Bot Hosting"}

@app.post("/bot/create")
def create_bot(bot: BotCreate):
    try:
        bot_id = f"bot_{int(time.time())}"
        bot_dir = os.path.join(BOTS_DIR, bot_id)
        os.makedirs(bot_dir, exist_ok=True)
        bot_file = os.path.join(bot_dir, "bot.py")
        with open(bot_file, "w") as f:
            f.write(bot.code)
        env = os.environ.copy()
        env["BOT_TOKEN"] = bot.token
        log_file = open(os.path.join(bot_dir, "log.txt"), "w")
        proc = subprocess.Popen(["python", bot_file], env=env, stdout=log_file, stderr=subprocess.STDOUT)
        PROCESSES[bot_id] = {"proc": proc, "name": bot.name, "dir": bot_dir, "log": log_file}
        return {"status": "success", "bot_id": bot_id, "message": "Bot deployed!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bot/{bot_id}/stop")
def stop_bot(bot_id: str):
    if bot_id not in PROCESSES:
        raise HTTPException(404, "Bot not found")
    PROCESSES[bot_id]["proc"].terminate()
    return {"status": "stopped", "bot_id": bot_id}

@app.post("/bot/{bot_id}/restart")
def restart_bot(bot_id: str):
    if bot_id not in PROCESSES:
        raise HTTPException(404, "Bot not found")
    p = PROCESSES[bot_id]
    p["proc"].terminate()
    time.sleep(1)
    env = os.environ.copy()
    env["BOT_TOKEN"] = open(os.path.join(p["dir"], "token.txt")).read().strip() if os.path.exists(os.path.join(p["dir"], "token.txt")) else ""
    p["proc"] = subprocess.Popen(["python", os.path.join(p["dir"], "bot.py")], env=env,
                                  stdout=p["log"], stderr=subprocess.STDOUT)
    return {"status": "restarted", "bot_id": bot_id}

@app.get("/bot/{bot_id}/logs")
def get_logs(bot_id: str):
    if bot_id not in PROCESSES:
        raise HTTPException(404, "Bot not found")
    log_path = os.path.join(PROCESSES[bot_id]["dir"], "log.txt")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return {"logs": f.read()[-3000:]}
    return {"logs": "No logs yet"}

@app.get("/bots")
def list_bots():
    bots = []
    for bid, info in PROCESSES.items():
        status = "running" if info["proc"].poll() is None else "stopped"
        bots.append({"id": bid, "name": info["name"], "status": status})
    return {"bots": bots}

@app.delete("/bot/{bot_id}")
def delete_bot(bot_id: str):
    if bot_id in PROCESSES:
        try: PROCESSES[bot_id]["proc"].terminate()
        except: pass
        del PROCESSES[bot_id]
    return {"status": "deleted"}
