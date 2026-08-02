from __future__ import annotations
import sqlite3
from server.logger import logger
from server.processing_layer.event import BrowserEvent, OperatingSystemEvent
from server.processing_layer.classifier import HardCodedClassifier, MLClassifier, LLMClassifier
from sqlite3 import Connection

class EventProcessor:
    def __init__(self, repository: ActivityRepository, classifiers: list[HardCodedClassifier|MLClassifier|LLMClassifier]) -> None:
        self.repository = repository
        self.os_event_last_id: int = self.repository.get_max_id("os_events")
        self.events: dict[int, OperatingSystemEvent] = {}
        self.batch_size = 5
        self.classifiers: list[HardCodedClassifier|MLClassifier|LLMClassifier] = classifiers

    def _flush_if_needed(self) -> None:
        if len(self.events) >= self.batch_size:
            os_events = self.events.values()
            successful_transaction = self.repository.insert_os_events(os_events)
            if successful_transaction:
                for os_event in os_events:
                    browser_events = os_event.linked_browser_events
                    self.repository.insert_browser_events(browser_events)
            else:
                self.os_event_last_id -= len(self.events) # roll back to the latest event id
            self.events.clear()
            
        
    def handle_browser_event(self, event: BrowserEvent):
        os_event = self.events.get(self.os_event_last_id)
        if os_event:
            os_event.linked_browser_events.append(event)
        self._flush_if_needed()
        logger.info(f"Browser Event: {event.website} - {event.os_event_id}")

    def handle_os_event(self, event: OperatingSystemEvent):
        self.events[self.os_event_last_id + 1] = event
        self.os_event_last_id += 1 # in the future when saving to disk will be added, this will be changed 
        self._flush_if_needed()
        logger.info(f"OS Event: {event.process} - {self.os_event_last_id}")
    
class ActivityRepository:
    def __init__(self, db: Connection):
        self.db = db

    def insert_os_events(self, activities: list[OperatingSystemEvent]) -> None:
        # in SQLite executemany does not return the list of last inserted IDs.
        self.db.executemany("""
            INSERT INTO os_events
            (window, executable, event_start_time, type)
            VALUES (?, ?, ?);
        """, (
            (
                activity.title,
                activity.process,
                activity.event_time,
                activity.type
            )
            for activity in activities
        ))
        try:
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(e)
        

    def insert_browser_events(self, activities: list[BrowserEvent]) -> None:
        self.db.executemany("""
            INSERT INTO browser_events
            (website, event_start_time, event_end_time, os_event_id)
            VALUES (?, ?, ?, ?);
        """, (
            (
                activity.website,
                activity.event_time,
                activity.ended_at,
                activity.os_event_id
            )
            for activity in activities
        ))

        self.db.commit()

    
    def get_max_id(self, table_name: str) -> int:
        allowed_tables = ["os_events"]
        if table_name not in allowed_tables:
            raise ValueError("Unknown table name.")

        cursor = self.db.execute(f"SELECT COALESCE(MAX(id), 0) FROM \'{table_name}\'") # SQLite does not support ? substitution for table names, hence doing an f-string
        return cursor.fetchone()[0] or 0