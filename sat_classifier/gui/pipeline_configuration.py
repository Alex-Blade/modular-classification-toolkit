import random
import string

from PyQt5 import QtGui, QtWidgets, QtCore, Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QToolBox, QWidget
from qgis import gui
from qgis.core import QgsMessageLog, QgsProcessingProvider
import qgis.core as qcore

from .event_bus import EventBus, AlgorithmSelectedEvent, AlgorithmRemovedEvent, AlgorithmAddedEvent
from .parameters_panel import ParametersPanel
import processing
from processing.tools.dataobjects import createContext


REMOVE_PIXMAP = QPixmap("/home/user/code/minimal/x-square-svgrepo-com.svg")
REMOVE_ICON = QIcon(REMOVE_PIXMAP)

ADD_PIXMAP = QPixmap("/home/user/code/minimal/add-square-svgrepo-com.svg")
ADD_ICON = QIcon(ADD_PIXMAP)


class PipelineElement:
    def __init__(self, parent: QtWidgets.QWidget,
                 provider: QgsProcessingProvider,
                 event_bus: EventBus,
                 peid: str):
        self.parent = parent
        self.event_bus = event_bus
        self.pipeline_element_id = peid
        self.title = QtWidgets.QLabel(parent)
        self.hlayout = QtWidgets.QHBoxLayout()

        self.combo_box = QtWidgets.QComboBox(parent)
        self.remove = QtWidgets.QPushButton(parent)
        self.provider = provider

        self.hlayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        for alg in self.provider.algorithms():
            self.combo_box.addItem(alg.displayName(), {"name": alg.name()})
        self.hlayout.addWidget(self.combo_box)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.remove.sizePolicy().hasHeightForWidth())
        self.remove.setSizePolicy(size_policy)
        self.remove.setIcon(REMOVE_ICON)
        self.remove.setFlat(True)
        self.remove.clicked[bool].connect(self.on_remove)
        self.hlayout.addWidget(self.remove)

        self.title.setText(self.algorithm.group() or "Test")

        self.combo_box.currentTextChanged[str].connect(self.on_algo_selected)
        self.on_algo_selected()

    @property
    def algorithm(self):
        return self.provider.algorithm(self.combo_box.currentData()["name"])

    def add_to_layout(self, layout: QtWidgets.QBoxLayout):
        idx = layout.count() - 1
        layout.insertLayout(idx, self.hlayout)
        layout.insertWidget(idx, self.title)

    def on_algo_selected(self):
        algo = self.algorithm
        self.title.setText(algo.group())
        self.event_bus.publish(AlgorithmSelectedEvent.event_type, AlgorithmSelectedEvent(self.pipeline_element_id, algo))

    def on_remove(self):
        self.remove_children()
        self.event_bus.publish(AlgorithmRemovedEvent.event_type, AlgorithmRemovedEvent(self.pipeline_element_id))

    def remove_children(self):
        self.title.setParent(None)
        self.combo_box.setParent(None)
        self.hlayout.setParent(None)
        self.remove.setParent(None)
        del self.title
        del self.combo_box
        del self.hlayout
        del self.remove


class PipelineConfiguration:
    def __init__(self, parent, provider: QgsProcessingProvider, event_bus: EventBus):
        self.parent = parent
        self.provider = provider
        self.pipeline: list[PipelineElement] = []
        self.event_bus = event_bus

        # GUI Initialization
        self.config = QtWidgets.QWidget(self.parent)
        self.config.setObjectName("config")
        self.page_layout = QtWidgets.QVBoxLayout(self.config)
        self.page_layout.setObjectName("page_layout")
        self.scroll_area = QtWidgets.QScrollArea(self.config)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area_widget_contents = QtWidgets.QWidget(self.config)
        self.scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 409, 272))
        self.scroll_area_widget_contents.setObjectName("scroll_area_widget_contents")
        self.vertical_layout = QtWidgets.QVBoxLayout(self.scroll_area_widget_contents)
        self.vertical_layout.setObjectName("vertical_layout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacer_item)
        self.add_to_pipe = QtWidgets.QPushButton(self.scroll_area_widget_contents)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.add_to_pipe.sizePolicy().hasHeightForWidth())
        self.add_to_pipe.setSizePolicy(size_policy)
        self.add_to_pipe.setIcon(ADD_ICON)
        self.add_to_pipe.setFlat(True)
        self.add_to_pipe.setObjectName("add_to_pipe")
        self.horizontalLayout_2.addWidget(self.add_to_pipe)
        self.vertical_layout.addLayout(self.horizontalLayout_2)

        self.add_to_pipe.clicked[bool].connect(self.add_pipeline_element)
        spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vertical_layout.addItem(spacer_item)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.page_layout.addWidget(self.scroll_area)

        self.event_bus.subscribe(AlgorithmRemovedEvent.event_type, self.remove_pipeline_element)

    def remove_pipeline_element(self, data: AlgorithmRemovedEvent):
        self.pipeline = list(filter(lambda p: p.pipeline_element_id != data.pipeline_element_id, self.pipeline))

    def add_pipeline_element(self):
        ids = [pel.pipeline_element_id for pel in self.pipeline]
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        while rand in ids:
            rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        self.event_bus.publish(AlgorithmAddedEvent.event_type, AlgorithmAddedEvent(rand))
        pel = PipelineElement(self.scroll_area_widget_contents, self.provider, self.event_bus, rand)
        pel.add_to_layout(self.vertical_layout)
        self.pipeline.append(pel)

    @property
    def tab_to_add(self) -> QWidget:
        return self.config

    @property
    def tab_title(self) -> str:
        return "Configuration"
