from typing import Protocol
import qgis.core as qcore
import processing
from ..gui.event_bus import ExecutionProgressEvent, SubmitExecutionEvent, EventBus


class PipelineExecutor(Protocol):
    def on_execution_submit(self, data: SubmitExecutionEvent):
        ...


class DefaultPipelineExecutor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def on_execution_submit(self, data: SubmitExecutionEvent):
        params = dict()
        feedback = qcore.QgsProcessingFeedback(logFeedback=True)
        context = data.panels[0].processing_context
        intermediate_result = {}
        steps_count = len(data.panels)
        self.event_bus.publish(ExecutionProgressEvent.event_type, ExecutionProgressEvent(0, steps_count))
        for idx, panel in enumerate(data.panels):
            params.update(panel.createProcessingParameters())
            params.update(intermediate_result)
            func = processing.run
            kwargs = {"context": context, "feedback": feedback, "is_child_algorithm": True}
            if idx == len(data.panels) - 1:
                func = processing.runAndLoadResults
                kwargs.pop("is_child_algorithm")
            intermediate_result = func(f'mct:{panel.algorithm().name()}', params, **kwargs)
            self.event_bus.publish(ExecutionProgressEvent.event_type, ExecutionProgressEvent(idx + 1, steps_count))
