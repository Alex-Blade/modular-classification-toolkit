from typing import Protocol
import qgis.core as qcore
import processing
from ..gui.event_bus import SubmitExecutionEvent


class PipelineExecutor(Protocol):
    @staticmethod
    def on_execution_submit(data: SubmitExecutionEvent):
        ...


class DefaultPipelineExecutor:
    @staticmethod
    def on_execution_submit(data: SubmitExecutionEvent):
        params = dict()
        feedback = qcore.QgsProcessingFeedback(logFeedback=True)
        context = data.panels[0].processing_context
        intermediate_result = {}
        for idx, panel in enumerate(data.panels):
            params.update(panel.createProcessingParameters())
            params.update(intermediate_result)
            func = processing.run
            kwargs = {"context": context, "feedback": feedback, "is_child_algorithm": True}
            if idx == len(data.panels) - 1:
                func = processing.runAndLoadResults
                kwargs.pop("is_child_algorithm")
            intermediate_result = func(f'yourplugin:{panel.algorithm().name()}', params, **kwargs)
