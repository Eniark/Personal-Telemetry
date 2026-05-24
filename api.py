from fastapi import FastAPI
import sqlite3
import logging

logging.basicConfig(
    filename="Logs/logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

db = sqlite3.connect(
    "activity.db",
    check_same_thread=False
)

@app.post("/event")
async def event(payload: dict):
    logging.info("Test")
    db.execute("""
        INSERT INTO events(
            website
            started_at,
            ended_at,
            duration_ms
        )
        VALUES (?,?,?,?)
    """, (
        payload.get("website"),
        payload.get("started_at"),
        payload.get("ended_at"),
        payload.get("duration_ms")
    ))

    db.commit()

    return {"ok": True}