from dataclasses import dataclass
import datetime

from configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION

@dataclass
class Event:
    event_time: int
    ended_at: int

@dataclass
class OperatingSystemEvent(Event):
    category: str
    process: str
    publisher: str
    type: str

    def __repr__(self):
        return f"OS Activity: {self.process=}, {self.event_time=}, {self.type=}"
    
@dataclass
class BrowserEvent(Event):
    os_event_id: int = None
    website: str | None = None
    website_title: str | None = None

    def __repr__(self):
        return f"Browser Activity: {self.website=}, {self.os_event_id=}"
    

class PhoneMapper:
    def to_os_event(payload: dict):
        ended_at = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]
        return OperatingSystemEvent(
            process=payload.get('appName'),
            type="Phone",
            event_time=payload.get('usedAtTimestamp'),
            ended_at=ended_at
        )