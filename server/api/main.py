from fastapi import FastAPI
from shared.configs import DB_PATH
import sqlite3
import uvicorn
import os
import datetime
from server.processing_layer.event import PhoneMapper
from server.processing_layer.main import EventProcessor, ActivityRepository, BrowserEvent, OperatingSystemEvent
from shared.configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION
from server.api.models import PhoneEventSchema, OSEventSchema, BrowserEventSchema
from shared.utils import get_env_variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

def create_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield ActivityRepository(conn)
    finally:
        conn.close()

# FIXME: Global SQLite connection shared across FastAPI's async worker threads is ANTI-pattern. It WILL lead to database locking and potential corruption.
# SUGGESTION: Use Dependency Injection (`Depends()`) to yield a database connection per request, or use async (`aiosqlite`).
db = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)
db = ActivityRepository(db)
event_processor = EventProcessor(db)

@app.post("/browser_event")
async def browser_event_endpoint(payload: BrowserEventSchema):
    event_time = datetime.datetime.fromtimestamp(
            payload.eventTime / 1000
        ).strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION] # Converts Unix-style timetamp to human-readable format 

    event = BrowserEvent(
        os_event_id=event_processor.os_activity_last_row_id,
        event_time=event_time,
        ended_at=payload.ended_at,
        website = payload.website,
        website_title = payload.title
    )
    event_processor.handle_browser_event(event)
    return {"ok": True}

@app.post("/os_event")
async def os_event_endpoint(payload: OSEventSchema):
    ended_at = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]
    event = OperatingSystemEvent(
        process=payload.process,
        event_time=payload.event_time,
        ended_at=ended_at,
        category=payload.category,
        publisher=payload.publisher,
        type="PC"
    )
    event_processor.handle_os_event(event)
    return {"ok": True}

@app.post("/phone_event")
async def phone_event_endpoint(payload: list[PhoneEventSchema]): # the phone sends batches every 15 minutes
    for phone_event in payload:
        event = PhoneMapper.to_os_event(phone_event)
        event_processor.handle_os_event(event)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    HOST, PORT = get_env_variables()

    # FIXME: Weird hack to force 0.0.0.0.
    # SUGGESTION: TRUST YOUR ENVIRONMENTAL VARIABLES. Avoids accidental issues with "listen all" when testing on localhost
    if HOST=='127.0.0.1':
        HOST = '0.0.0.0' # allows the API to listen to all devices in the network

    uvicorn.run(
        "server.api.main:app", host=HOST, port=PORT, reload=True
    )