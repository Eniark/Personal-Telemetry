from dataclasses import dataclass
from logger import logger

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
    website: str | None = None
    website_title: str | None = None

class EventProcessor:
    def __init__(self, db):
        self.db = db
        self.current: ActivityEvent = None

    def handle_browser_event(self, payload):
        if self.current is None:
            return  # the object has to exist since browser is opened first

        # Add the required fields for the website
        self.current.website = payload.get("website")
        self.current.website_titletitle = payload.get("title")
        self.current.duration_ms = payload.get("duration_ms")
        logger.info(f"Browser Event: {payload.get('title')} - {payload.get('started_at')}")

    def handle_os_event(self, payload):
        self.current = ActivityEvent(
            process=payload.get("process"),
            started_at=payload.get("started_at"),
            ended_at=None, # need to finisht this later  
            duration_ms=None,

        )
        logger.info(f"OS Event: {payload.get('process')} - {payload.get('started_at')}")
    
class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def insert(self, activity):
        self.db.execute("""
            INSERT INTO browser_activity
            (website, started_at, ended_at, duration_ms)
            VALUES (?, ?, ?, ?)
        """, (
            activity.url,
            activity.started_at,
            activity.ended_at,
            activity.duration_ms
        ))
        self.db.commit()