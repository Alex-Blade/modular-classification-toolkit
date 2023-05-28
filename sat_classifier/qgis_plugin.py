from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.core import QgsApplication, QgsMessageLog
import qgis.core as core

from .mct_processing.provider import Provider
from .mct_processing.pipeline_executor import PipelineExecutor, DefaultPipelineExecutor
from .gui.main_dock import MainDock
from .gui.event_bus import EventBus, SubmitExecutionEvent
import processing


class QGisPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider: core.QgsProcessingProvider = None
        self.action: QAction = None
        self.event_bus: EventBus = EventBus()
        self.dock_widget: MainDock = None
        self.pipeline_executor: PipelineExecutor = DefaultPipelineExecutor()
        self.event_bus.subscribe(SubmitExecutionEvent.event_type, self.pipeline_executor.on_execution_submit)

    def init_processing(self):
        """
        Initialize and register processing providers
        :return:
        """
        if not self.provider:
            self.provider = Provider()
            QgsApplication.processingRegistry().addProvider(self.provider)

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        self.event_bus.reset_bus()
        self.dock_widget.closingPlugin.disconnect(self.onClosePlugin)
        self.dock_widget.setParent(None)

    def initGui(self):
        """
        Initialize GUI elements
        :return:
        """
        self.action = QAction('Start MCT', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.init_processing()

    def unload(self):
        """
        Unload processing providers and GUI elements
        :return:
        """
        self.iface.removeToolBarIcon(self.action)
        if self.dock_widget is not None:
            self.dock_widget.close()
            self.dock_widget = None

        if self.action is not None:
            self.action.setParent(None)
            self.action = None

        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

    def run(self):
        if self.dock_widget is None or self.dock_widget.parent() is None:
            self.dock_widget = MainDock(self.iface, self.provider, self.event_bus)

        self.dock_widget.closingPlugin.connect(self.onClosePlugin)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.show()
