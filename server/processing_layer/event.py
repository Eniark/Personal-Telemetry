from dataclasses import dataclass, field
import datetime

from server.api.models import PhoneEventSchema
from server.processing_layer.enums import EventType
from shared.configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION


@dataclass(slots=True, frozen=True)
class Event:
    event_start_time: int
    event_end_time: int
    title: str | None
    processing_time: str | None = field(default=None, kw_only=True)

@dataclass(slots=True, frozen=True)
class BrowserEvent(Event):
    url: str
    os_event_id: int | None = None

    def __repr__(self):
        return f"Browser Activity: {self.url=}, {self.os_event_id=}"
    

@dataclass(slots=True, frozen=True)
class OperatingSystemEvent(Event):
    category: EventType
    process: str
    publisher: str
    type: str
    linked_browser_events: list[BrowserEvent]

    def __repr__(self):
        return f"OS Activity: {self.process=}, {self.event_start_time=}, {self.type=}"
    

class PhoneMapper:
    @staticmethod
    def to_os_event(payload: PhoneEventSchema):
        processing_time = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]

        return OperatingSystemEvent(
            process=payload.appName,
            type="Phone",
            event_start_time=payload.eventStartTime,
            event_end_time=payload.eventEndTime,
            processing_time=processing_time,
            publisher=payload.packageName,
            category='OS'
        )