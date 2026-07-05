from logger import logger
from processing_layer.event import BrowserEvent, OperatingSystemEvent

class EventProcessor:
    def __init__(self, repository):
        self.repository = repository
        self.os_activity_last_row_id = self.repository.get_max_id("os_activity")
        self.os_activities = []
        self.browser_activities = []
        self.batch_size = 5

    def handle_browser_event(self, event: BrowserEvent):
        self.browser_activities.append(event)
        
        if len(self.browser_activities) > self.batch_size:  # fix data sync issue
            self.repository.insert_browser_activities(self.browser_activities)
            self.browser_activities = []
        logger.info(f"Browser Event: {event.website} - {event.os_event_id}")

    def handle_os_event(self, event: OperatingSystemEvent):
        self.os_activities.append(event)
        self.os_activity_last_row_id += 1
        if len(self.browser_activities) > self.batch_size: # for case when user is stuck in browser
            self.repository.insert_os_activities(self.os_activities)
            self.os_activities = []

            self.repository.insert_browser_activities(self.browser_activities)
            self.browser_activities = []
        
        elif len(self.os_activities) > self.batch_size:
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
            (website, started_at, ended_at, activity_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            [
                (
                    activity.website,
                    activity.started_at,
                    activity.ended_at,
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