from sqlite3 import Connection

from shared.enums import EventType
from server.processing_layer.event import OperatingSystemEvent
from server.processing_layer.sql_queries import INSERT_OS_EVENTS_QUERY, INSERT_BROWSER_EVENTS_QUERY, UPDATE_EVENT_CLASS_QUERY
from server.event_classifier.backend.classifier import Classification
from server.logs.logger import logger
import json, sqlite3
from typing import Any

class TelemetryRepository:
    def __init__(self, db: Connection):
        self.db = db
        self.batch_size = 1

    def insert_events(self, events: dict[EventType, list[OperatingSystemEvent]]) -> bool:
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
                json.dumps(activity.previous_events),
                activity.class_.class_,
                activity.class_.classified_at,
                activity.class_.classified_by.value,
                activity.class_.classification_approved,
                activity.class_.confidence,
            )
            for activity in events[EventType.OS]
        ))

        self.db.executemany(INSERT_BROWSER_EVENTS_QUERY, (
            (
                activity.url,
                activity.title,
                activity.event_start_time,
                activity.event_end_time,
                activity.processing_time,
                activity.os_event_id,
                activity.class_.class_,
                activity.class_.classified_at,
                activity.class_.classified_by.value,
                activity.class_.classification_approved,
                activity.class_.confidence,
            )
            for activity in events[EventType.BROWSER]
        ))

        try:
            self.db.commit()
            logger.info(f"[DB] Inserted {len(events[EventType.OS])} OS events and {len(events[EventType.BROWSER])} Browser events into the database.")
            return True
        except sqlite3.Error as e:
            logger.error(F"[DB] Failed to insert {len(events[EventType.OS])} OS events and {len(events[EventType.BROWSER])} Browser events into the database.")
            print(e)

    def get_events(self, query: str, params: tuple = (), limit: int|None = None) -> tuple[list|None, list[Any]]:
        cursor = self.db.execute(query, params)
        data = cursor.fetchall()
        return data
    

    def update_classification(self, row_id: int, classification: Classification, table: str):
        self.db.execute(UPDATE_EVENT_CLASS_QUERY.format(table=table),
        (
            classification.class_,
            classification.classified_at,
            classification.classified_by,
            row_id
        ))
        self.db.commit()

    