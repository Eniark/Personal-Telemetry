from dataclasses import dataclass
from logger import logger
import datetime
from configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION

"""
ToDo: split to Base+child classes
tf
"""
@dataclass
class ActivityEvent:
    process: str
    started_at: int
    ended_at: int
    duration_ms: int
    id: int = None
    website: str | None = None
    website_title: str | None = None

class EventProcessor:
    def __init__(self, repository):
        self.repository = repository
        self.current: ActivityEvent = None

    def handle_browser_event(self, payload):
        if self.current is None:
            return  # the object has to exist since browser is opened first

        # Add the required fields for the website
        self.current.website = payload.get("website")
        self.current.website_title = payload.get("title")
        started_at__formatted = datetime.datetime.fromtimestamp(
            payload.get('started_at') / 1000
        ).strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION] # Converts Unix-style timetamp to human-readable format 
        self.current.started_at = started_at__formatted 

        self.repository.insert_browser_activity(self.current)
        logger.info(f"Browser Event: {payload.get('title')} - {started_at__formatted}")

    def handle_os_event(self, payload):

        ended_at = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]

        self.current = ActivityEvent(
            process=payload.get("process"),
            started_at=payload.get("started_at"),
            ended_at=ended_at,
            duration_ms=None,

        )

        last_row_id = self.repository.insert_os_activity(self.current)
        self.current.id = last_row_id
        logger.info(f"OS Event: {payload.get('process')} - {payload.get('started_at')}")
    
class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def insert_os_activity(self, activity):
        self.db.execute("""
            INSERT INTO os_activity
            (window, started_at)
            VALUES (?, ?)
        """, (
            activity.process,
            activity.started_at
        ))
        self.db.commit()
        return self.db.lastrowid

    def insert_browser_activity(self, activity): # not working properly
        self
        self.db.execute("""
            INSERT INTO browser_activity
            (website, started_at, ended_at, duration_ms, activity_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            activity.website,
            activity.started_at,
            activity.ended_at,
            activity.duration_ms,
            activity.id # id of parent activity 
            
        ))

        self.db.commit()