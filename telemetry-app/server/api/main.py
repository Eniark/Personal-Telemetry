from fastapi import FastAPI
import uvicorn
import datetime
import server.logs.tracing
from shared.configs import DB_PATH
from server.db.db_connect import create_db_connection
from server.processing_layer.event import PhoneMapper
from server.processing_layer.main import EventProcessor, TelemetryRepository, BrowserEvent, OperatingSystemEvent
from shared.configs import TIMESTAMP_FORMAT, LISTEN_TO_ALL_DEVICES
from server.api.models import PhoneEventSchema, OSEventSchema
from server.event_classifier.backend.classifier import HardCodedClassifier, MLClassifier, LLMClassifier
from server.event_classifier.backend.pipeline import ClassifierPipeline
from server.event_classifier.backend.event_feature_extractor import EventFeatureExtractor

from shared.utils import get_env_variables
from dotenv import load_dotenv
from shared.enums import EventType
from server.logs.logger import logger
from uuid import uuid4
from opentelemetry import trace
from .middleware import register_middleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

load_dotenv()

app = FastAPI()
register_middleware(app)
FastAPIInstrumentor().instrument_app(app)
tracer = trace.get_tracer(__name__)


hardcoded_classifier = ClassifierPipeline(preprocessor=EventFeatureExtractor(), classifier=HardCodedClassifier())
ml_classifier = ClassifierPipeline(preprocessor=EventFeatureExtractor(), classifier=MLClassifier())
llm_classifier = ClassifierPipeline(preprocessor=EventFeatureExtractor(), classifier= LLMClassifier())

db = create_db_connection(DB_PATH)
repository = TelemetryRepository(db)
event_processor = EventProcessor(repository, [
    # hardcoded_classifier, 
    ml_classifier, 
    # llm_classifier
])

@app.post("/os_event")
async def os_event_endpoint(payload: OSEventSchema):
    event = OperatingSystemEvent.from_schema(payload)
    logger.info(f"[API] OS Event: {event.process} - {event.id} - Browser Events: {len(event.related_browser_events)}")
    with tracer.start_as_current_span('handle_os_event'):
        event_processor.handle_os_event(event)
    return {"ok": True}

@app.post("/phone_event")
async def phone_event_endpoint(payload: list[PhoneEventSchema]): # the phone sends batches every 15 minutes
    for phone_event in payload:
        event = PhoneMapper.to_os_event(phone_event)
        logger.info(f"[API] Phone Event: {event.process} - {event.id}")
        with tracer.start_as_current_span('handle_phone_event'):
            event_processor.handle_os_event(event)
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