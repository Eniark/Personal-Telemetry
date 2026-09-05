from __future__ import annotations
import sqlite3

from server.processing_layer.event import BrowserEvent, OperatingSystemEvent, Event
from server.processing_layer.classifier import Classifier
from sqlite3 import Connection
from .enums import EventType
from server.logger import logger
from .sql_queries import INSERT_OS_EVENTS_QUERY, INSERT_BROWSER_EVENTS_QUERY
import json

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
            successful_transaction = self.repository.insert_os_events(self.events[EventType.OS])
            if successful_transaction:
                self.repository.insert_browser_events(self.events[EventType.BROWSER])
                for category in EventType:
                    self.events[category].clear()
            
        
    def handle_browser_event(self, event: BrowserEvent):
        self._browser_events_window.append(event) # the events are inserted in _handle_late_os_event due to late browser events


    def handle_os_event(self, event: OperatingSystemEvent):
        self._handle_late_os_event(event)

        self.events[EventType.OS].append(event)
        self._flush_if_needed()
    
    def _handle_late_os_event(self, event: OperatingSystemEvent) -> None:
        if event.category == EventType.BROWSER and len(self._browser_events_window) != 0:
            for browser_event in self._browser_events_window:
                browser_event.os_event_id = event.id
                logger.info(f"Browser Event: {browser_event.url} - {browser_event.os_event_id}")
            self.events[EventType.BROWSER].extend(self._browser_events_window)
            self._browser_events_window.clear()

    
class ActivityRepository:
    def __init__(self, db: Connection):
        self.db = db
        self.batch_size = 5

    def insert_os_events(self, activities: list[OperatingSystemEvent]) -> bool:
        # in SQLite executemany does not return the list of last inserted IDs.
        self.db.executemany(INSERT_OS_EVENTS_QUERY, (
            (
                activity.id,
                activity.title,
                activity.process,
                activity.publisher,
                activity.description,
                activity.event_start_time,
                activity.event_end_time,
                activity.processing_time,
                activity.category.value,
                json.dumps(activity.previous_events)
            )
            for activity in activities
        ))
        try:
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(e)
        

    def insert_browser_events(self, activities: list[BrowserEvent]) -> None:
        self.db.executemany(INSERT_BROWSER_EVENTS_QUERY, (
            (
                activity.url,
                activity.title,
                activity.event_start_time,
                activity.event_end_time,
                activity.processing_time,
                activity.os_event_id
            )
            for activity in activities
        ))

        self.db.commit()