from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bikin database
conn = sqlite3.connect("data.db", check_same_thread=False)
conn.execute("""
CREATE TABLE IF NOT EXISTS targets (
    id TEXT PRIMARY KEY,
    nama TEXT,
    last_seen TEXT
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id TEXT,
    cmd TEXT,
    value TEXT,
    status TEXT DEFAULT 'pending'
)
""")

@app.get("/register/{target_id}")
def register(target_id: str, nama: str = "Unknown"):
    conn.execute(
        "INSERT OR REPLACE INTO targets VALUES (?, ?, ?)",
        (target_id, nama, datetime.now().isoformat())
    )
    conn.commit()
    return {"status": "ok"}

@app.post("/block/{target_id}/{package}")
def block_app(target_id: str, package: str):
    conn.execute(
        "INSERT INTO commands (target_id, cmd, value) VALUES (?, ?, ?)",
        (target_id, "BLOCK", package)
    )
    conn.commit()
    return {"status": f"block {package} queued"}

@app.get("/get_commands/{target_id}")
def get_commands(target_id: str):
    cur = conn.execute(
        "SELECT id, cmd, value FROM commands WHERE target_id = ? AND status = 'pending'",
        (target_id,)
    )
    cmds = [{"id": row[0], "cmd": row[1], "value": row[2]} for row in cur.fetchall()]
    return {"commands": cmds}

@app.post("/done/{cmd_id}")
def mark_done(cmd_id: int):
    conn.execute("UPDATE commands SET status = 'done' WHERE id = ?", (cmd_id,))
    conn.commit()
    return {"status": "ok"}

@app.get("/list_targets")
def list_targets():
    cur = conn.execute("SELECT id, nama, last_seen FROM targets")
    return [{"id": r[0], "nama": r[1], "last_seen": r[2]} for r in cur.fetchall()]
