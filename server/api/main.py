from fastapi import FastAPI
import uvicorn
import datetime
import server.logs.tracing
from shared.configs import DB_PATH
from server.db.db_connect import create_db_connection
from server.processing_layer.event import PhoneMapper
from server.processing_layer.main import EventProcessor, TelemetryRepository, BrowserEvent, OperatingSystemEvent
from shared.configs import TIMESTAMP_FORMAT, LISTEN_TO_ALL_DEVICES
from server.api.models import PhoneEventSchema, OSEventSchema, BrowserEventSchema
from server.event_classifier.backend.classifier import HardCodedClassifier, MLClassifier, LLMClassifier
from shared.utils import convert_date_to_readable_format, get_env_variables
from dotenv import load_dotenv
from server.processing_layer.enums import EventType
from server.logger import logger
from uuid import uuid4
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

load_dotenv()

app = FastAPI()
FastAPIInstrumentor().instrument_app(app)
tracer = trace.get_tracer(__name__)


hardcoded_classifier = HardCodedClassifier()
ml_classifier = MLClassifier()
llm_classifier = LLMClassifier()


db = create_db_connection(DB_PATH)
repository = TelemetryRepository(db)
event_processor = EventProcessor(repository, [hardcoded_classifier, ml_classifier, llm_classifier])

@app.post("/browser_event")
async def browser_event_endpoint(payload: BrowserEventSchema):
    processing_time = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    event_start_time = convert_date_to_readable_format(payload.eventStartTime / 1000)
    event_end_time = convert_date_to_readable_format(payload.eventStartTime / 1000)
    event = BrowserEvent(
        event_start_time=event_start_time,
        event_end_time=event_end_time,
        processing_time=processing_time,
        url = payload.url,
        title = payload.title,
        category=EventType.BROWSER
    )
    event_processor.handle_browser_event(event)
    return {"ok": True}

@app.post("/os_event")
async def os_event_endpoint(payload: OSEventSchema):
    processing_time = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    category = EventType.OS if payload.category == EventType.OS.value else EventType.BROWSER
    event = OperatingSystemEvent(
        process=payload.executable,
        title = payload.title,
        description=None,
        event_start_time=payload.event_start_time,
        event_end_time=payload.event_end_time,
        processing_time=processing_time,
        category=category,
        publisher=payload.publisher,
        id=str(uuid4()),
        previous_events=payload.recent_windows
    )
    logger.info(f"OS Event Start: {event.process} - {event.id}")
    with tracer.start_as_current_span('handle_os_event'):
        event_processor.handle_os_event(event)

    logger.info(f"OS Event End: {event.process} - {event.id}\n")
    return {"ok": True}

@app.post("/phone_event")
async def phone_event_endpoint(payload: list[PhoneEventSchema]): # the phone sends batches every 15 minutes
    for phone_event in payload:
        event = PhoneMapper.to_os_event(phone_event)
        event_processor.handle_os_event(event)
        logger.info(f"Phone Event: {event.process} - {event.id}")
    return {"ok": True}

@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    HOST, PORT = get_env_variables()

    if LISTEN_TO_ALL_DEVICES:
        HOST = '0.0.0.0'

    uvicorn.run(
        "server.api.main:app", host=HOST, port=PORT, reload=True
    )