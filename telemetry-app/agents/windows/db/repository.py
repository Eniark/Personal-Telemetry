
from sqlite3 import Connection
from .sql_queries import INSERT_EVENTS_QUERY

class EventRepository:
    def __init__(self, db: Connection):
        self.db = db

    def insert_event(self, event: dict) -> bool:
        self.db.execute(INSERT_EVENTS_QUERY, (
            (
                event["event_id"],
                event["title"],
                event["executable"],
                event["publisher"],
                event["description"],
                event["event_start_time"],
                event["event_end_time"],
                event["type"],
                event["processing_time"],
                event["previous_events"],
                event["acknowledged"],
                event["browser_events"],
                event["sent_at"],
            )
        ))

        self.db.commit()