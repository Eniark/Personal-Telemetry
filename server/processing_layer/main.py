from __future__ import annotations

from server.db.repository import ActivityRepository
from server.processing_layer.event import BrowserEvent, OperatingSystemEvent, Event
from server.event_classifier.backend.classifier import Classifier
from .enums import EventType
from server.logger import logger
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class EventProcessor:
    def __init__(self, repository: ActivityRepository, classifiers: list[Classifier]) -> None:
        self.repository = repository
        self.events: list[Event] = {
            category: [] 
            for category in EventType
        }
        self.classifiers = classifiers
        self._browser_events_window: list[BrowserEvent] = []

    def _flush_if_needed(self) -> None:  
        if len(self.events[EventType.OS]) > self.repository.batch_size:    
            with tracer.start_as_current_span('insert_os_events_into_db'):
                successful_transaction = self.repository.insert_os_events(self.events[EventType.OS])
            if successful_transaction:
                with tracer.start_as_current_span('insert_browser_events_into_db'):  
                    self.repository.insert_browser_events(self.events[EventType.BROWSER])
                for category in EventType:
                    self.events[category].clear()
        
        
    def handle_browser_event(self, event: BrowserEvent):
        self._browser_events_window.append(event) # the events are inserted in _handle_late_os_event due to late browser events
        logger.info(f"Added Browser Event to tracker: {event.url} - {event.id}")


    def handle_os_event(self, event: OperatingSystemEvent):
        self._handle_late_os_event(event)

        self.events[EventType.OS].append(event)
        logger.info(f"Added OS Event to tracker: {event.process} - {event.id}")
        self._flush_if_needed()
    
    def _handle_late_os_event(self, event: OperatingSystemEvent) -> None:
        if event.category == EventType.BROWSER and len(self._browser_events_window) != 0:
            for browser_event in self._browser_events_window:
                browser_event.os_event_id = event.id
                logger.info(f"Browser Event: {browser_event.url} - {browser_event.os_event_id}")
            self.events[EventType.BROWSER].extend(self._browser_events_window)
            self._browser_events_window.clear()