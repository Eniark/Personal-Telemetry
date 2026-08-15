from dataclasses import dataclass, field
import datetime

from server.api.models import PhoneEventSchema
from server.processing_layer.enums import EventType
from shared.configs import TIMESTAMP_FORMAT
from shared.utils import convert_date_to_readable_format


@dataclass(slots=True)
class Event:
    event_start_time: int
    event_end_time: int
    title: str | None = field(default=None, kw_only=True)
    processing_time: str | None = field(default=None, kw_only=True)
    category: EventType

@dataclass(slots=True)
class BrowserEvent(Event):
    url: str 
    os_event_id: int | None = None

    def __repr__(self):
        return f"<Browser Activity: {self.url=}, {self.os_event_id=}>"
    

@dataclass(slots=True)
class OperatingSystemEvent(Event):
    process: str
    publisher: str
    description: str | None = None
    linked_browser_events: list[BrowserEvent] = field(default_factory=list, kw_only=True)

    def __repr__(self):
        return f"<OS Activity: {self.process=}, linked_browser_events={len(self.linked_browser_events)}, {self.category=}>"
    

class PhoneMapper:
    @staticmethod
    def to_os_event(payload: PhoneEventSchema):
        processing_time = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        event_start_time = convert_date_to_readable_format(payload.eventStartTime / 1000)
        event_end_time = convert_date_to_readable_format(payload.eventEndTime / 1000)

        return OperatingSystemEvent(
            title=payload.appName,
            description=payload.description,
            event_start_time=event_start_time,
            event_end_time=event_end_time,
            processing_time=processing_time,
            publisher=payload.developer,
            process=payload.packageName,
            category=EventType.PHONE_OS
        )