from fastapi import FastAPI
from dotenv import load_dotenv
from configs import DB_PATH
import sqlite3
import uvicorn
import os
import datetime
from processing_layer.event import PhoneMapper
from processing_layer.main import EventProcessor, ActivityRepository, BrowserEvent, OperatingSystemEvent
from configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION
load_dotenv()

app = FastAPI()

db = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)
db = ActivityRepository(db)
event_processor = EventProcessor(db)

@app.post("/browser_event")
async def event(payload: dict):
    started_at = datetime.datetime.fromtimestamp(
            payload.get('started_at') / 1000
        ).strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION] # Converts Unix-style timetamp to human-readable format 

    event = BrowserEvent(
        os_event_id=event_processor.os_activity_last_row_id,
        started_at=started_at,
        ended_at=payload.get("ended_at"),
        website = payload.get("website"),
        website_title = payload.get("title")
    )
    event_processor.handle_browser_event(event)
    return {"ok": True}

@app.post("/os_event")
async def event(payload: dict):
    ended_at = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]
    event = OperatingSystemEvent(
        process=payload.get("process"),
        started_at=payload.get("started_at"),
        ended_at=ended_at,
        type="PC"
    )
    event_processor.handle_os_event(event)
    return {"ok": True}

@app.post("/phone_event")
async def event(payload: list[dict]): # the phone sends batches every 15 minutes
    print(payload)
    for phone_event in payload:
        event = PhoneMapper.to_os_event(phone_event)
        event_processor.handle_os_event(event)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))

    if HOST=='127.0.0.1':
        HOST = '0.0.0.0' # allows the API to list to all network sources: WiFi,

    uvicorn.run(
        "api.main:app", host=HOST, port=PORT, reload=True
    )