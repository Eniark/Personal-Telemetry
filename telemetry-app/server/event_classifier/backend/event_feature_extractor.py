
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from datetime import datetime 
from shared.enums import EventType
from urllib.parse import urlsplit

from server.processing_layer.event import Event, OperatingSystemEvent, BrowserEvent

@dataclass(slots=True)
class EnrichedEvent:
    title: str| None = None
    executable: str| None = None
    previous_event_1_executable: str| None = None
    previous_event_2_executable: str| None = None
    previous_event_3_executable: str| None = None
    previous_event_4_executable: str| None = None
    previous_event_5_executable: str| None = None
    previous_event_1_publisher: str| None = None
    previous_event_2_publisher: str| None = None
    previous_event_3_publisher: str| None = None
    previous_event_4_publisher: str| None = None
    previous_event_5_publisher: str| None = None
    week_day: int| None = None
    publisher: str| None = None
    domain: str| None = None
    hour: int| None = None 
    duration_seconds: float| None = None
    previous_events_duration_seconds: float| None = None
    previous_events_num_unique_executables: int| None = None
    previous_events_num_unique_publishers: int| None = None

class EventFeatureExtractor:
    def get_enriched_features(self, event: "Event") -> EnrichedEvent:
        week_day, hour, duration_seconds = self.get_time_info(event=event)

        if isinstance(event, OperatingSystemEvent):
            [
                previous_event_1_publisher,
                previous_event_1_executable,
                previous_event_2_publisher,
                previous_event_2_executable,
                previous_event_3_publisher,
                previous_event_3_executable,
                previous_event_4_publisher,
                previous_event_4_executable,
                previous_event_5_publisher,
                previous_event_5_executable,
                previous_events_num_unique_executables,
                previous_events_num_unique_publishers,
                previous_events_duration_seconds
            ] = self.get_previous_events_info(event=event)

            return EnrichedEvent(
                title = event.title,
                executable = event.process,
                previous_event_1_publisher = previous_event_1_publisher, 
                previous_event_1_executable = previous_event_1_executable, 
                previous_event_2_publisher = previous_event_2_publisher, 
                previous_event_2_executable = previous_event_2_executable, 
                previous_event_3_publisher = previous_event_3_publisher, 
                previous_event_3_executable = previous_event_3_executable, 
                previous_event_4_publisher = previous_event_4_publisher, 
                previous_event_4_executable = previous_event_4_executable, 
                previous_event_5_publisher = previous_event_5_publisher, 
                previous_event_5_executable = previous_event_5_executable, 
                previous_events_num_unique_executables = previous_events_num_unique_executables, 
                previous_events_num_unique_publishers = previous_events_num_unique_publishers, 
                previous_events_duration_seconds = previous_events_duration_seconds,
                week_day = week_day,
                publisher = event.publisher,
                hour = hour,
                duration_seconds = duration_seconds
            )
        else:
            domain = self.get_url_info(event=event)
            return EnrichedEvent(
                title = event.title,
                domain = domain,
                executable = event.process,
                week_day = week_day,
                publisher = event.publisher,
                hour = hour,
                duration_seconds = duration_seconds
            )

    @staticmethod
    def get_time_info(event):
        if isinstance(event, Event):
            start_date = event.event_start_time
            end_date = event.event_end_time
        else:
            start_date = event['event_start_time']
            end_date = event['event_end_time']

        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        week_day = start_date.weekday()
        hour = start_date.hour
        duration_seconds = (end_date - start_date).total_seconds()
        return week_day, hour, duration_seconds


    @staticmethod
    def get_previous_events_info(event: "Event") -> tuple[any]:
        num_previous_events = 5
        features_for_classifier = {}
        required_features = ["executable", "publisher"]

        seen_values = {
            feature: set()
            for feature in required_features
        }
        previous_events_duration_seconds = 0

        for i in range(num_previous_events):
            try:
                previous_event = event.previous_events[i]
                for feature in required_features:
                    value = previous_event.get(feature)

                    features_for_classifier[f"previous_event_{i + 1}_{feature}"] = value

                    if value is not None:
                        seen_values[feature].add(value)
                _, _, duration_seconds = EventFeatureExtractor.get_time_info(previous_event)
                previous_events_duration_seconds += duration_seconds
            except IndexError:
                for feature in required_features:
                    features_for_classifier[f"previous_event_{i + 1}_{feature}"] = None

        return (
            features_for_classifier['previous_event_1_executable'], features_for_classifier['previous_event_1_publisher'], 
            features_for_classifier['previous_event_2_executable'], features_for_classifier['previous_event_2_publisher'],
            features_for_classifier['previous_event_3_executable'], features_for_classifier['previous_event_3_publisher'],
            features_for_classifier['previous_event_4_executable'], features_for_classifier['previous_event_4_publisher'],
            features_for_classifier['previous_event_5_executable'], features_for_classifier['previous_event_5_publisher'],
            len(seen_values['executable']), len(seen_values['publisher']), previous_events_duration_seconds
        )

    @staticmethod
    def get_url_info(event: "BrowserEvent") -> tuple[any]:
        domain = urlsplit(event.url).hostname
        return domain
    
            



