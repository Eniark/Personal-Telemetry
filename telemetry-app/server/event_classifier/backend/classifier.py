import joblib
import numpy as np

from ollama import chat
from server.processing_layer.enums import EventCategory
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from shared.configs import MODEL_PATH
from .enums import ClassificationRole

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.processing_layer.event import OperatingSystemEvent, Event

class Classifier(ABC):
    @abstractmethod
    def classify(self, event: "Event") -> tuple[float, EventCategory]:
        pass

class HardCodedClassifier(Classifier):
    activity_map = {
        "Steam.exe": EventCategory.GAMING,
        "Telegram.exe": EventCategory.SOCIAL_MEDIA,
        "Code.exe": EventCategory.STUDYING,
    }
    def classify(self, event: "OperatingSystemEvent" = None) -> tuple[float, EventCategory] | None: # This currently works only with OS events
        class_ = HardCodedClassifier.activity_map.get(event.process)
        if class_:
            return (100, class_)
        else:
            return (0, None)

class MLClassifier(Classifier):
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        super().__init__()

    def classify(self, event: "Event" = None) -> tuple[float, EventCategory]:
        confidences = self.model.predict_proba([[event]])

        confidence = np.max(confidences, axis=1)
        predicted_class = self.model.classes_[np.argmax(confidences, axis=1)]
        print(confidence, predicted_class)

class LLMClassifier(Classifier):
    def classify(self, event: "Event" = None) -> tuple[float, EventCategory]:
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


@dataclass(slots=True)
class Classification:
    classified_at: datetime
    classified_by: ClassificationRole
    class_: EventCategory
    classification_approved: bool = field(default=False, kw_only=True)
    confidence: float