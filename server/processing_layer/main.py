import sqlite3
from server.logger import logger
from server.processing_layer.event import BrowserEvent, OperatingSystemEvent

class EventProcessor:
    def __init__(self, repository):
        self.repository = repository
        self.os_event_last_id = self.repository.get_max_id("os_events")
        self.events = {}
        # self.browser_activities = []
        self.batch_size = 5

    def _flush_if_needed(self):
        if len(self.events) >= self.batch_size:
            self.repository.insert_os_activities(self.events.values())

        if self.browser_activities:
            self.repository.insert_browser_activities(self.browser_activities)
            self.os_activities.clear()
            self.browser_activities.clear()

        if len(self.browser_activities) >= self.batch_size:
            self._flush_all()

        elif len(self.os_activities) >= self.batch_size:
            self.repository.insert_os_events(self.os_activities)
            self.os_activities.clear()

    def handle_browser_event(self, event: BrowserEvent):
        self.events[self.os_event_last_id].linked_browser_events.append(event)
        # # self.browser_activities.append(event)
        # browser_activities = self.events[self.os_event_last_id].linked_browser_events
        # if len(browser_activities) >= self.batch_size:
        #     self.repository.insert_os_events(self.events)
        #     self.events = []

        #     self.repository.insert_browser_activities(browser_activities)
        #     self.browser_activities = []
        self._flush_if_needed()
        logger.info(f"Browser Event: {event.website} - {event.os_event_id}")

    def handle_os_event(self, event: OperatingSystemEvent):
        self.events[self.os_event_last_id + 1] = event
        # FIXME: Incrementing this ID in-memory before DB commit guarantees your state will drift if a DB insert fails. 
        # DIRSUGGESTIONECTION: Only update `os_event_last_id` AFTER a successful DB batch insert, or use UUIDs for events instead of auto-incrementing DB integers.
        self.os_event_last_id += 1
        
        # FIXME: Fatal logic bug. Checking 'len(self.browser_activities)' inside an OS event handler creates cross-domain coupling and race conditions. 
        # Also, you flush browser activities and reset the list, but then immediately try to flush it again inside the block.
        # SUGGESTION: Extract flushing into a dedicated `_flush_all()` method. Call it when either list hits the threshold. Ensure OS events are inserted *before* browser events to satisfy foreign keys.
        if len(self.browser_activities) >= self.batch_size: # for case when user is stuck in browser
            self.repository.insert_os_events(self.events)
            self.events = []

            self.repository.insert_browser_activities(self.browser_activities)
            self.browser_activities = []
        
        elif len(self.events) > self.batch_size:
            self.repository.insert_os_events(self.events)
            self.events = []
        logger.info(f"OS Event: {event.process} - {self.os_event_last_id}")
    
class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def insert_os_events(self, activities):
        cursor = self.db.executemany("""
            INSERT INTO os_events
            (window, event_start_time, type)
            VALUES (?, ?, ?)
            RETURNING id;
        """, (
            (
                activity.process,
                activity.event_time,
                activity.type
            )
            for activity in activities
        ))
        try:
            self.db.commit()
        except sqlite3.Error:
            pass
        ids = cursor.fetchall()
        return ids

    def insert_browser_activities(self, activities):
        cursor = self.db.executemany("""
            INSERT INTO browser_events
            (website, event_start_time, event_end_time, activity_id)
            VALUES (?, ?, ?, ?)
            RETURNING id;
        """, (
            [
                (
                    activity.website,
                    activity.event_time,
                    activity.ended_at,
                    activity.os_event_id
                )
                for activity in activities
            ] 
            
        ))

        self.db.commit()
        ids = cursor.fetchall()
        return ids

    
    def get_max_id(self, table_name):
        allowed_tables = ["os_events"]
        if table_name not in allowed_tables:
            raise ValueError("Unknown table name.")

        cursor = self.db.execute(f"SELECT COALESCE(MAX(id), 0) FROM \'{table_name}\'") # SQLite does not support ? substitution for table names, hence doing an f-string
        return cursor.fetchone()[0] or 0