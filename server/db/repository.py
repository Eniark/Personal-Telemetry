from sqlite3 import Connection

from server.processing_layer.event import BrowserEvent, OperatingSystemEvent
from server.processing_layer.sql_queries import INSERT_OS_EVENTS_QUERY, INSERT_BROWSER_EVENTS_QUERY, SELECT_OS_EVENTS_QUERY, SELECT_BROWSER_EVENTS_QUERY, UPDATE_EVENT_CLASS_QUERY
from server.event_classifier.backend.classifier import Classification
import json, sqlite3
from typing import Any

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
    
    def _get_events(
        self,
        query: str,
        params: tuple = (),
        get_headers: bool = True,
    ) -> tuple[list | None, list[Any]]:

        cursor = self.db.execute(query, params)

        headers = (
            [column[0] for column in cursor.description]
            if get_headers
            else None
        )

        return headers, cursor.fetchall()

    def get_events(self, query: str, params: tuple=(), get_headers: bool=True, limit: int|None = None) -> tuple[list|None, list[Any]]:
        headers = None
        cursor = self.db.execute(query, params)

        if get_headers:
            headers = [value[0] for value in cursor.description]
        
        data = cursor.fetchall()
        return (headers, data)
    

    def update_classification(self, event_id: int, classification: Classification):
        self.db.execute(UPDATE_EVENT_CLASS_QUERY,
        (
            classification.class_,
            classification.classified_at,
            classification.classified_by,
            event_id
        ))
        self.db.commit()
        print(event_id, classification)