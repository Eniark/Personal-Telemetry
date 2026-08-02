from enum import Enum

class EventType(Enum):
    BROWSER = 'browser'
    OS = 'os'

class EventCategory:
    WORK = "work"
    STUDYING = "studying"
    GAMING = "gaming"
    SOCIAL_MEDIA = "social_media"
    MUSIC = "music"
    SHOPPING = "shopping"
    NEWS = "news"
    OTHER = "other"