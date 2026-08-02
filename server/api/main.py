from fastapi import FastAPI
from shared.configs import DB_PATH
import sqlite3
import uvicorn
import datetime
from server.processing_layer.event import PhoneMapper
from server.processing_layer.main import EventProcessor, ActivityRepository, BrowserEvent, OperatingSystemEvent
from shared.configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION
from server.api.models import PhoneEventSchema, OSEventSchema, BrowserEventSchema
from server.processing_layer.classifier import HardCodedClassifier, MLClassifier, LLMClassifier
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

hardCodedClassifier = HardCodedClassifier()
mlClassifier = MLClassifier()
llMClassifier = LLMClassifier()

# add parallel connections to the database?
db = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)
db = ActivityRepository(db)
event_processor = EventProcessor(db, [hardCodedClassifier, mlClassifier, llMClassifier])

@app.post("/browser_event")
async def browser_event_endpoint(payload: BrowserEventSchema):
    event_time = datetime.datetime.fromtimestamp(
            payload.eventTime / 1000
        ).strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION] # Converts Unix-style timetamp to human-readable format 

    event = BrowserEvent(
        os_event_id=event_processor.os_event_last_id,
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
        type="PC",
        linked_browser_events=[]
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

    uvicorn.run(
        "server.api.main:app", host=HOST, port=PORT, reload=True
    )