from dataclasses import dataclass
from logger import logger
import datetime
from configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION

"""
ToDo: split to Base+child classes
"""

@dataclass
class Event:
    started_at: int
    ended_at: int
    duration_ms: int

@dataclass
class OperatingSystemEvent(Event):
    process: str

    def __repr__(self):
        return f"OS Activity: {self.process=}, {self.started_at=}"

@dataclass
class BrowserEvent(Event):
    os_event_id: int = None
    website: str | None = None
    website_title: str | None = None

    def __repr__(self):
        return f"Browser Activity: {self.website=}, {self.os_event_id=}"

class EventProcessor:
    def __init__(self, repository):
        self.repository = repository
        self.os_activity_last_row_id = self.repository.get_max_id("os_activity")
        self.os_activities = []
        self.browser_activities = []
        self.batch_size = 5

    def handle_browser_event(self, payload):
        started_at = datetime.datetime.fromtimestamp(
            payload.get('started_at') / 1000
        ).strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION] # Converts Unix-style timetamp to human-readable format 

        event = BrowserEvent(
            os_event_id=self.os_activity_last_row_id,
            started_at=started_at,
            ended_at=payload.get("ended_at"),
            duration_ms=None,
            website = payload.get("website"),
            website_title = payload.get("title")
        )

        self.browser_activities.append(event)

        
        if len(self.browser_activities) > self.batch_size:  # fix data sync issue
            self.repository.insert_browser_activities(self.browser_activities)
            self.browser_activities = []
        logger.info(f"Browser Event: {event.website} - {event.os_event_id}")

    def handle_os_event(self, payload):
        ended_at = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]
        event = OperatingSystemEvent(
            process=payload.get("process"),
            started_at=payload.get("started_at"),
            ended_at=ended_at,
            duration_ms=None,
        )

        self.os_activities.append(event)
        self.os_activity_last_row_id += 1
        if len(self.os_activities) > self.batch_size:
            self.repository.insert_os_activities(self.os_activities)
            self.os_activities = []
        logger.info(f"OS Event: {event.process} - {self.os_activity_last_row_id}")
    
class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def insert_os_activities(self, activities):
        cursor = self.db.executemany("""
            INSERT INTO os_activity
            (window, started_at)
            VALUES (?, ?)
        """, (
            [
                (
                    activity.process,
                    activity.started_at
                )
                for activity in activities
            ]
        ))
        self.db.commit()
        return cursor.lastrowid

    def insert_browser_activities(self, activities): # not working properly
        self.db.executemany("""
            INSERT INTO browser_activity
            (website, started_at, ended_at, duration_ms, activity_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            [
                (
                    activity.website,
                    activity.started_at,
                    activity.ended_at,
                    activity.duration_ms,
                    activity.os_event_id
                )
                for activity in activities
            ] 
            
        ))

        self.db.commit()
    
    def get_max_id(self, table_name):
        allowed_tables = ["os_activity"]
        if table_name not in allowed_tables:
            raise ValueError("Unknown table name.")

        cursor = self.db.execute(f"SELECT MAX(seq) FROM sqlite_sequence WHERE name=\'{table_name}\'")
        return cursor.fetchone()[0] or 0