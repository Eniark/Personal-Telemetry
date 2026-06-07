from fastapi import FastAPI
from logger import logger
from dotenv import load_dotenv

import sqlite3
import uvicorn
import os
load_dotenv()

app = FastAPI()

db = sqlite3.connect(
    "activity.db",
    check_same_thread=False
)

@app.post("/browser_event")
async def event(payload: dict):
    db.execute("""
        INSERT INTO browser_activity(
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



if __name__ == "__main__":
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))

    uvicorn.run(
        "main:app", host=HOST, port=PORT, reload=True
    )