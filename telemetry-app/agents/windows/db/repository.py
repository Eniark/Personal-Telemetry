
from sqlite3 import Connection, Row
from .sql_queries import UPSERT_EVENTS_QUERY, SELECT_EVENTS_QUERY
import agents.windows.db.init_db
import json

class EventRepository:
    def __init__(self, db: Connection):
        self.db = db
        self.db.row_factory = Row

    def upsert_events(self, events: list[dict], are_acknowledged: bool) -> bool:
        self.db.executemany(UPSERT_EVENTS_QUERY, (
            (
                event["id"],
                event["title"],
                event["executable"],
                event["publisher"],
                event["event_start_time"],
                event["event_end_time"],
                event["category"],
                json.dumps(event["recent_windows"]),
                are_acknowledged,
                json.dumps(event["browser_events"]),
                event["sent_at"],
            ) for event in events
        ))

        self.db.commit()

    def get_pending_events(self):
        cursor = self.db.execute(SELECT_EVENTS_QUERY)
        pending_events = cursor.fetchall()
           
        return [
            {
                "id" : event["event_id"], 
                "title" : event["title"], 
                "executable" : event["executable"], 
                "publisher" : event["publisher"], 
                "event_start_time" : event["event_start_time"], 
                "event_end_time" : event["event_end_time"], 
                "category" : event["type"], 
                "recent_windows" : json.loads(event["previous_events"]), 
                "browser_events" : json.loads(event["browser_events"]), 
                "sent_at" : event["sent_at"], 
            } for event in pending_events
        ]