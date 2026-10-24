import datetime

from server.db.repository import TelemetryRepository
from server.processing_layer.event import BrowserEvent, OperatingSystemEvent, Event
from server.event_classifier.backend.classifier import Classifier, Classification
from server.event_classifier.backend.enums import ClassificationRole

from shared.enums import EventType
from shared.configs import TIMESTAMP_FORMAT
from server.logger import logger
from opentelemetry import trace
from .event_filter import EventFilter


tracer = trace.get_tracer(__name__)


class EventProcessor:
    def __init__(self, repository: TelemetryRepository, classifiers: list[Classifier]) -> None:
        self.repository = repository
        self.event_filter = EventFilter()
        self.events: list[Event] = {
            category: [] 
            for category in EventType
        }
        self.classifiers = classifiers
        self._browser_events_window: list[BrowserEvent] = []

    def _flush_if_needed(self) -> None:  
        if len(self.events[EventType.OS]) > self.repository.batch_size:    
            with tracer.start_as_current_span('insert_os_events_into_db'):
                successful_transaction = self.repository.insert_events(self.events)
                if successful_transaction:
                    logger.info(f"Inserted {len(self.events[EventType.OS])} OS events and {len(self.events[EventType.BROWSER])} Browser events into the database.")
                    for category in EventType:
                        self.events[category].clear()
                else:
                    logger.error("Failed to insert events into the database.")
        
        
    def handle_browser_event(self, event: BrowserEvent):
        if not self.event_filter.is_valid_event(event):
            logger.warning(f"Filtered out Browser Event: {event.url} - {event.id}")
            return

        self._browser_events_window.append(event) # the events are inserted in _handle_late_os_event due to late browser events
        logger.info(f"Added Browser Event to tracker: {event.url} - {event.id}")


    def handle_os_event(self, event: OperatingSystemEvent):
        self._handle_late_os_event(event)

        if not self.event_filter.is_valid_event(event):
            logger.warning(f"Filtered out OS Event: {event.process} - {event.id}")
            return
        
        self.add_class(event=event)
        self.events[EventType.OS].append(event)
        logger.info(f"Added OS Event to tracker: {event.process} - {event.id}")
        self._flush_if_needed()
    
    def _handle_late_os_event(self, event: OperatingSystemEvent) -> None:
        if event.category == EventType.BROWSER and len(self._browser_events_window) != 0:
            for browser_event in self._browser_events_window:
                browser_event.os_event_id = event.id # attaching the OS event ID to the browser events that arrived before the OS event
                logger.info(f"Browser Event: {browser_event.url} - {browser_event.os_event_id}")
            self.events[EventType.BROWSER].extend(self._browser_events_window)
            self._browser_events_window.clear()
    
    def add_class(self, event: Event) -> Event:
        for classifier in self.classifiers:
            confidence, class_ = classifier.classify(event)
            if class_:
                break
        event.class_ = Classification(
            class_=class_,
            classified_by=ClassificationRole.AI,
            classified_at=datetime.datetime.now().strftime(TIMESTAMP_FORMAT),
            confidence=confidence
        )
        if confidence > 0.9:
            event.class_.classification_approved = True
        else:
            event.class_.classification_approved = False
            print(class_, confidence)
        print('Added class')
        
