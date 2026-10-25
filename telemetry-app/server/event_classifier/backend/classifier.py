import joblib
import pandas as pd
import numpy as np

from ollama import chat
from server.processing_layer.enums import EventCategory
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from shared.configs import MODEL_PATH
from .enums import ClassificationRole
from typing import TYPE_CHECKING
from server.logs.logger import logger

if TYPE_CHECKING:
    from server.event_classifier.backend.pipeline import EnrichedEvent

class Classifier(ABC):
    def classify(self, event: "EnrichedEvent") -> tuple[float, EventCategory]:
        try:
            confidence, predicted_class = self._classify(event)
            logger.info(f'[{self.__class__.__name__}] Classified class={predicted_class} | {confidence=:.4f}')
            return confidence, predicted_class
        except:
            logger.error(f'[{self.__class__.__name__}] An error occured while classifying event.')
            
    @abstractmethod
    def _classify(self, event: "EnrichedEvent") -> tuple[float, EventCategory]:
        pass

class HardCodedClassifier(Classifier):
    activity_map = {
        "Steam.exe": EventCategory.GAMING,
        "Telegram.exe": EventCategory.SOCIAL_MEDIA,
        "Code.exe": EventCategory.STUDYING,
    }
    def _classify(self, event: "EnrichedEvent" = None) -> tuple[float, EventCategory] | None: # This currently works only with OS events
        class_ = HardCodedClassifier.activity_map.get(event.process)
        if class_:
            return (100, class_)
        else:
            return (0, None)

class MLClassifier(Classifier):
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        super().__init__()

    def _classify(self, event: "EnrichedEvent" = None) -> tuple[float, EventCategory]:
        X = pd.DataFrame([asdict(event)])
        confidences = self.model.predict_proba(X)

        confidence = np.max(confidences, axis=1)[0]
        predicted_class = self.model.classes_[np.argmax(confidences, axis=1)][0]
        return confidence, predicted_class

class LLMClassifier(Classifier):
    def _classify(self, event: "EnrichedEvent" = None) -> tuple[float, EventCategory]:
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