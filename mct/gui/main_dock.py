from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

import qgis.core as qcore
from processing.tools.dataobjects import createContext

from .event_bus import EventBus
from .pipeline_configuration import PipelineConfiguration
from .pipeline_execution import PipelineExecution
from .tab import Tab


class MainDock(QtWidgets.QDockWidget):
    closingPlugin = pyqtSignal()

    def __init__(self, iface, provider: qcore.QgsProcessingProvider, event_bus: EventBus):
        super(MainDock, self).__init__(None)
        self.setWindowTitle("Modular Classification Toolkit")
        self.iface = iface
        self.event_bus = event_bus
        self.processing_context = createContext()
        self.provider = provider
        self.setObjectName("MainDock")
        self.resize(451, 362)
        self.dock_widget_contents = QtWidgets.QWidget()
        self.dock_widget_contents.setObjectName("dock_widget_contents")
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.dock_widget_contents)
        self.horizontal_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontal_layout.setObjectName("horizontal_layout")
        self.tab_widget = QtWidgets.QTabWidget(self.dock_widget_contents)
        self.tab_widget.setObjectName("tab_widget")

        self.configuration_page: Tab = PipelineConfiguration(self.dock_widget_contents, self.provider, self.event_bus)
        self.tab_widget.addTab(self.configuration_page.tab_to_add, self.configuration_page.tab_title)

        self.execution_page: Tab = PipelineExecution(self.dock_widget_contents, self.iface, self.processing_context, self.event_bus)
        self.tab_widget.addTab(self.execution_page.tab_to_add, self.execution_page.tab_title)

        self.horizontal_layout.addWidget(self.tab_widget)
        self.setWidget(self.dock_widget_contents)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
