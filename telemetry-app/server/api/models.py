from pydantic import BaseModel


class PhoneEventSchema(BaseModel):
    id: int
    packageName: str
    appName: str
    description: str
    developer: str
    eventStartTime: int
    eventEndTime: int
    sentToApi: bool
    isVerified: bool
    isSystemEvent: bool

class BrowserEventSchema(BaseModel):
    url: str
    title: str
    eventStartTime: int # unix-style timestamp
    eventEndTime: int # unix-style timestamp

class OSEventSchema(BaseModel):
    executable: str
    title: str
    publisher: str | None
    category: str
    event_start_time: str
    event_end_time: str
    recent_windows: list
    browser_events: list[BrowserEventSchema]


