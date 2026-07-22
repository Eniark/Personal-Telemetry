from dataclasses import dataclass
import datetime

from configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION

# FIXME: Add frozen=True and slots=True to @dataclass decorators for memory optimization and event immutability.
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
    # FIXME: os_event_id: int = None violates type safety. Use os_event_id: int | None = None
    os_event_id: int = None
    website: str | None = None
    website_title: str | None = None

    def __repr__(self):
        return f"Browser Activity: {self.website=}, {self.os_event_id=}"
    

class PhoneMapper:
    # FIXME: Add @staticmethod decorator or convert to a standalone function since this holds no state and lacks 'self'.
    def to_os_event(payload: dict):
        ended_at = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]

        # FIXME: Fragile payload extraction. payload.get('usedAtTimestamp') can return None, polluting the integer event_time field without validation.
        return OperatingSystemEvent(
            process=payload.get('appName'),
            type="Phone",
            event_time=payload.get('usedAtTimestamp'),
            ended_at=ended_at
        )