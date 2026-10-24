
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import datetime 
import json

if TYPE_CHECKING:
    from shared.enums import EventType
    from server.processing_layer.event import Event

@dataclass(slots=True)
class EnrichedEvent:
    title: str
    executable: str
    previous_event_1_executable: str
    previous_event_2_executable: str
    previous_event_3_executable: str
    previous_event_4_executable: str
    previous_event_5_executable: str
    previous_event_1_publisher: str
    previous_event_2_publisher: str
    previous_event_3_publisher: str
    previous_event_4_publisher: str
    previous_event_5_publisher: str
    week_day: int
    publisher: str
    domain: str
    hour: int 
    duration_seconds: float
    previous_events_duration_seconds: float
    previous_events_num_unique_executables: int
    previous_events_num_unique_publishers: int

class EventFeatureExtractor:
    def __init__(self, event: Event):
        self.event = event

    def get_enriched_features(self) -> EnrichedEvent:
        start_date, end_date, week_day, hour, duration_seconds = self.get_time_info(event=self.event)


    @staticmethod
    def get_time_info(event):
        start_date = datetime.strptime(event.event_start_time, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(event.event_end_time, "%Y-%m-%d %H:%M:%S")
        week_day = start_date.weekday()
        hour = start_date.hour
        duration_seconds = (end_date - start_date).total_seconds()
        return start_date, end_date, week_day, hour, duration_seconds


    @staticmethod
    def get_previous_events_info(event):
        previous_events = json.loads(event.previous_events)



