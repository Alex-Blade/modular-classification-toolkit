import qgis.core
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget
import qgis.core as qcore

from .parameters_panel import ParametersPanel
from .event_bus import EventBus, AlgorithmSelectedEvent, AlgorithmRemovedEvent, AlgorithmAddedEvent, SubmitExecutionEvent, UpdateConfigurationPageRequest
from .tab import Tab


class AlgorithmConfiguration:
    def __init__(self, parent: QtWidgets.QWidget, iface, processing_context: qcore.QgsProcessingContext):
        self.parameters_page = QtWidgets.QWidget(parent)
        self.iface = iface
        self.processing_context = processing_context
        self.parameters_page.setGeometry(QtCore.QRect(0, 0, 411, 68))
        self.parameters_page.setObjectName("parameters_page")
        self.page_vertical_layout = QtWidgets.QVBoxLayout(self.parameters_page)
        self.page_vertical_layout.setObjectName("page_vertical_layout")
        self.parameter_panel: ParametersPanel = None

    def on_update(self, algo: qcore.QgsProcessingAlgorithm):
        if self.parameters_page is not None:
            self.clean_page()
        self.parameter_panel = ParametersPanel(algo, self.iface, self.page_vertical_layout, self.processing_context)
        self.parameter_panel.initWidgets()
        spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.page_vertical_layout.addItem(spacer_item)

    def clean_page(self):
        children = self.page_vertical_layout.children()
        for i in reversed(range(self.page_vertical_layout.count())):
            item = self.page_vertical_layout.itemAt(i)
            self.page_vertical_layout.removeItem(item)
            if item.widget():
                item.widget().setParent(None)

    def on_remove(self):
        self.clean_page()
        self.parameters_page.setParent(None)
        self.page_vertical_layout.setParent(None)
        del self.parameters_page
        del self.page_vertical_layout
        del self.parameter_panel


class PipelineExecution(Tab):
    def __init__(self, parent: QtWidgets.QWidget, iface, processing_context: qcore.QgsProcessingContext, event_bus: EventBus):
        self.parent = parent
        self.iface = iface
        self.processing_context = processing_context
        self.event_bus = event_bus
        self.execution_page = QtWidgets.QWidget(parent)
        self.execution_page.setObjectName("execution_page")
        self.toolbox_layout = QtWidgets.QVBoxLayout(self.execution_page)
        self.toolbox_layout.setObjectName("toolbox_layout")
        self.toolbox = QtWidgets.QToolBox(self.execution_page)
        self.toolbox.setObjectName("toolbox")
        self.pages = []
        self.page_layouts = []
        self.configurations: dict[str, AlgorithmConfiguration] = {}

        self.toolbox_layout.addWidget(self.toolbox)
        spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.toolbox_layout.addItem(spacer_item)
        self.classify_button = QtWidgets.QPushButton(self.execution_page)
        self.classify_button.setObjectName("classify_button")
        self.classify_button.setText("Classify")
        self.toolbox_layout.addWidget(self.classify_button)
        self.classify_button.clicked[bool].connect(self.on_classify)
        self.toolbox.setCurrentIndex(0)

        event_bus.subscribe(AlgorithmAddedEvent.event_type, self.on_algorithm_added)
        event_bus.subscribe(AlgorithmSelectedEvent.event_type, self.on_algorithm_selected)
        event_bus.subscribe(AlgorithmRemovedEvent.event_type, self.on_algorithm_removed)

    def on_algorithm_selected(self, data: AlgorithmSelectedEvent):
        conf = self.configurations[data.pipeline_element_id]
        idx = self.toolbox.indexOf(conf.parameters_page)
        self.toolbox.setItemText(idx, data.algo.displayName())
        conf.on_update(data.algo)

    def on_algorithm_added(self, data: AlgorithmAddedEvent):
        conf = AlgorithmConfiguration(self.toolbox, self.iface, self.processing_context)
        conf.parameters_page.setObjectName(f"params_page_{data.pipeline_element_id}")
        self.configurations[data.pipeline_element_id] = conf
        self.toolbox.addItem(conf.parameters_page, "Placeholder")

    def on_algorithm_removed(self, data: AlgorithmRemovedEvent):
        conf = self.configurations.pop(data.pipeline_element_id)
        idx = self.toolbox.indexOf(conf.parameters_page)
        self.toolbox.removeItem(idx)
        conf.on_remove()

    def on_classify(self):
        panels = []
        for conf in self.configurations.values():
            panels.append(conf.parameter_panel)
        self.event_bus.publish(SubmitExecutionEvent.event_type, SubmitExecutionEvent(panels))

    @property
    def tab_to_add(self) -> QWidget:
        return self.execution_page
