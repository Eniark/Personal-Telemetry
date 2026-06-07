from fastapi import FastAPI
from dotenv import load_dotenv
from configs import DB_PATH
from processing_layer.main import EventProcessor
import sqlite3
import uvicorn
import os
load_dotenv()

app = FastAPI()

db = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

event_processor = EventProcessor(db)

@app.post("/browser_event")
async def event(payload: dict):
    event_processor.handle_browser_event(payload)
    return {"ok": True}

@app.post("/os_event")
async def event(payload: dict):
    event_processor.handle_os_event(payload)
    return {"ok": True}



if __name__ == "__main__":
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))

    uvicorn.run(
        "api.main:app", host=HOST, port=PORT, reload=True
    )