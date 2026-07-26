from pydantic import BaseModel


class PhoneEventSchema(BaseModel):
    id: int
    packageName: str
    appName: str
    description: str
    event_time: int
    sentToApi: bool
    isVerified: bool
    isSystemEvent: bool

class OSEventSchema(BaseModel):
    process: str
    title: str
    publisher: str
    category: str
    event_time: str


class BrowserEventSchema(BaseModel):
    website: str
    title: str
    eventTime: int # unix-style timestamp
    ended_at: int # unix-style timestamp
