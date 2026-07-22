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

# FIXME: Global SQLite connection shared across FastAPI's async worker threads is ANTI-pattern. It WILL lead to database locking and potential corruption.
# SUGGESTION: Use Dependency Injection (`Depends()`) to yield a database connection per request, or use async (`aiosqlite`).
db = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)
db = ActivityRepository(db)
event_processor = EventProcessor(db)

# FIXME: All your POST endpoints are named `async def event`. In Python, the later definitions overwrite the earlier ones in the module namespace. While FastAPI routes might still technically fire, it ruins OpenAPI schema generation and internal references.
# SUGGESTION: Rename pls.
@app.post("/browser_event")
# FIXME: Typing payloads as `dict` defeats the core strength of FastAPI (auto-validation, 422 error handling, Swagger UI generation).
# SUGGESTION: Define Pydantic `BaseModel` classes for your incoming payloads and type hint them here (e.g., `payload: BrowserPayloadSchema`).
async def event(payload: dict):
    # FIXME: If `eventTime` is missing from the payload, `payload.get('eventTime')` returns `None`. `None / 1000` will crash the server with a TypeError.
    # SUGGESTION: PYDANTIC (auto-validates)
    event_time = datetime.datetime.fromtimestamp(
            payload.get('eventTime') / 1000
        ).strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION] # Converts Unix-style timetamp to human-readable format 

    event = BrowserEvent(
        os_event_id=event_processor.os_activity_last_row_id,
        event_time=event_time,
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
        event_time=payload.get("event_time"),
        ended_at=ended_at,
        category=payload.get("category"),
        publisher=payload.get("publisher"),
        type="PC"
    )
    event_processor.handle_os_event(event)
    return {"ok": True}

@app.post("/phone_event")
async def event(payload: list[dict]): # the phone sends batches every 15 minutes
    # FIXME: Leftover debug print statement in an API endpoint. This will spam the production console.
    # SUGGESTION: Replace with `logger.debug()`.
    print(payload)
    for phone_event in payload:
        event = PhoneMapper.to_os_event(phone_event)
        event_processor.handle_os_event(event)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    # FIXME: `os.getenv` returns `None` if the variable is missing. `int(None)` will throw a TypeError and the app will completely fail to start.
    # SUGGESTION: Add env vars validation in config on-import (hint: vars() in the end of the file will yield everything, and you can check if anything is none = raise)
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))

    # FIXME: Weird hack to force 0.0.0.0.
    # SUGGESTION: TRUST YOUR ENVIRONMENTAL VARIABLES. Avoids accidental issues with "listen all" when testing on localhost
    if HOST=='127.0.0.1':
        HOST = '0.0.0.0' # allows the API to list to all network sources: WiFi,

    uvicorn.run(
        "api.main:app", host=HOST, port=PORT, reload=True
    )