from qgis.core import QgsProcessingAlgorithm
from dataclasses import dataclass

from .parameters_panel import ParametersPanel


@dataclass
class SubmitExecutionEvent:
    panels: list[ParametersPanel]
    event_type = "SubmitExecutionEvent"


@dataclass
class AlgorithmAddedEvent:
    pipeline_element_id: str
    event_type = "AlgorithmAddedEvent"


@dataclass
class AlgorithmRemovedEvent:
    pipeline_element_id: str
    event_type = "AlgorithmRemovedEvent"


@dataclass
class AlgorithmSelectedEvent:
    pipeline_element_id: str
    algo: QgsProcessingAlgorithm
    event_type = "AlgorithmSelectedEvent"


@dataclass
class UpdateConfigurationPageRequest:
    pipeline_element_id: str
    algo: QgsProcessingAlgorithm
    event_type = "UpdateConfigurationPageRequest"


class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)

    def publish(self, event_type, data=None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)
