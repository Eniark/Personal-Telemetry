from .classifier import Classifier
from .event_feature_extractor import EventFeatureExtractor

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.processing_layer.event import Event

class ClassifierPipeline:
    def __init__(self, preprocessor: EventFeatureExtractor, classifier:Classifier):
        self.preprocessor = preprocessor
        self.classifier = classifier

    def enrich_and_predict(self, event: "Event") -> "Event":
        enriched_features = self.preprocessor.get_enriched_features(event)
        print(enriched_features)
        # classify the event here
