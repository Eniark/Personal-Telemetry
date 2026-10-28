import datetime

from server.db.repository import TelemetryRepository
from server.processing_layer.event import BrowserEvent, OperatingSystemEvent, Event
from server.event_classifier.backend.classifier import Classifier, Classification
from server.event_classifier.backend.enums import ClassificationRole
from server.event_classifier.backend.pipeline import ClassifierPipeline
from shared.utils import convert_date_to_readable_format


from shared.enums import EventType
from shared.configs import TIMESTAMP_FORMAT
from server.logs.logger import logger
from opentelemetry import trace
from .event_filter import EventFilter


tracer = trace.get_tracer(__name__)


class EventProcessor:
    def __init__(self, repository: TelemetryRepository, classifiers: list[ClassifierPipeline]) -> None:
        self.repository = repository
        self.event_filter = EventFilter()
        self.events: list[Event] = {
            category: [] 
            for category in EventType
        }
        self.classifiers = classifiers

    def _flush_if_needed(self) -> None:  
        if len(self.events[EventType.OS]) > self.repository.batch_size:    
            with tracer.start_as_current_span('insert_os_events_into_db'):
                successful_transaction = self.repository.insert_events(self.events)
                if successful_transaction:
                    for category in EventType:
                        self.events[category].clear()
        
        
    def handle_browser_event(self, event: BrowserEvent, parent_event_id: int):
        if not self.event_filter.is_valid_event(event):
            logger.warning(f"[Event Processor] Filtered out Browser Event: {event.title} - {event.url}")
            return

        self.add_class(event=event)
        self.events[EventType.BROWSER].append(event)
        logger.info(f"[Event Processor] Added Browser Event to tracker: {event.title} - {event.url}")


    def handle_os_event(self, event: OperatingSystemEvent):
        if not self.event_filter.is_valid_event(event):
            logger.warning(f"[Event Processor] Filtered out OS Event: {event.process} - {event.id}")
            return
        
        for browser_event in event.related_browser_events:
            browser_event = BrowserEvent.from_schema(browser_event)
            
            logger.info(f"[API] Browser Event: {browser_event.title} - {browser_event.url}")
            self.handle_browser_event(browser_event, parent_event_id=event.id)

        self.add_class(event=event)
        self.events[EventType.OS].append(event)
        logger.info(f"[Event Processor] Added OS Event to tracker: {event.process} - {event.id}")
        self._flush_if_needed()
    
    def add_class(self, event: Event) -> Event:
        
        for classifier in self.classifiers:
            confidence, class_ = classifier.enrich_and_predict(event=event)
            if class_:
                break
        class_ = Classification( # move this upstream to correctly assign the classified_by field 
            class_=class_,
            classified_by=ClassificationRole.AI,
            classified_at=datetime.datetime.now().strftime(TIMESTAMP_FORMAT),
            confidence=confidence
        )
        class_.classification_approved = confidence > 0.9

        event.class_ = class_
        
