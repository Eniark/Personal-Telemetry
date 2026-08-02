from ollama import chat
from .enums import EventCategory
from abc import ABC, abstractmethod
from .event import OperatingSystemEvent
class Classifier(ABC):
    @abstractmethod
    def classify(self, event: OperatingSystemEvent) -> EventCategory:
        pass

class HardCodedClassifier(Classifier):
    activity_map = {
        "Steam.exe": EventCategory.GAMING,
        "Telegram.exe": EventCategory.SOCIAL_MEDIA,
        "Code.exe": EventCategory.STUDYING,
    }
    def classify(self, event = None) -> EventCategory | None:
        return HardCodedClassifier.activity_map.get(event.process)


class MLClassifier(Classifier):
    def classify(self, event = None) -> EventCategory:
        pass


class LLMClassifier(Classifier):
    def classify(self, event = None) -> EventCategory:
        response = chat(
            model="qwen3:4b",
            messages=[
                {
                    "role": "user",
                    "content": "Categorize Chrome - Stack Overflow"
                }
            ]
        )

        print(response.message.content)