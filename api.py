from fastapi import FastAPI
import sqlite3
from logger import logger

app = FastAPI()

db = sqlite3.connect(
    "activity.db",
    check_same_thread=False
)

@app.post("/event")
async def event(payload: dict):
    db.execute("""
        INSERT INTO events(
            website,
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
    logger.info("Insertion Successful")

    return {"ok": True}