from dataclasses import dataclass
import datetime

from server.api.models import PhoneEventSchema
from server.processing_layer.enums import EventCategory
from shared.configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION


@dataclass(slots=True, frozen=True)
class Event:
    event_time: int
    ended_at: int

@dataclass(slots=True, frozen=True)
class BrowserEvent(Event):
    os_event_id: int | None = None
    website: str | None = None
    website_title: str | None = None

    def __repr__(self):
        return f"Browser Activity: {self.website=}, {self.os_event_id=}"
    

@dataclass(slots=True, frozen=True)
class OperatingSystemEvent(Event):
    category: EventCategory
    process: str
    publisher: str
    type: str
    linked_browser_events: list[BrowserEvent]

    def __repr__(self):
        return f"OS Activity: {self.process=}, {self.event_time=}, {self.type=}"
    

class PhoneMapper:
    @staticmethod
    def to_os_event(payload: PhoneEventSchema):
        ended_at = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]

        return OperatingSystemEvent(
            process=payload.appName,
            type="Phone",
            event_time=payload.event_time,
            ended_at=ended_at,
            publisher=payload.packageName,
            category='OS'
        )