from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.core import QgsApplication, QgsMessageLog
import qgis.core as core

from .processing.provider import Provider
from .gui.main_dock import MainDock
from .gui.event_bus import EventBus, SubmitExecutionEvent
import processing


class QGisPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.action = None
        self.event_bus = EventBus()
        self.dock_widget = None
        self.event_bus.subscribe(SubmitExecutionEvent.event_type, QGisPlugin.on_execution_submit)

    def init_processing(self):
        """
        Initialize and register processing providers
        :return:
        """
        self.provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        self.dock_widget.closingPlugin.disconnect(self.onClosePlugin)

    def initGui(self):
        """
        Initialize GUI elements
        :return:
        """
        self.action = QAction('Go!', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.init_processing()

    def unload(self):
        """
        Unload processing providers and GUI elements
        :return:
        """
        self.iface.removeToolBarIcon(self.action)
        QgsApplication.processingRegistry().removeProvider(self.provider)
        if self.dock_widget is not None:
            self.dock_widget.close()
        del self.action
        del self.provider

    @staticmethod
    def on_execution_submit(data: SubmitExecutionEvent):
        QgsMessageLog.logMessage("message")
        params = dict()
        feedback = core.QgsProcessingFeedback(logFeedback=True)
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

    def run(self):
        QMessageBox.information(None, 'Minimal plugin', 'Do something useful here')
        if self.dock_widget is None:
            self.dock_widget = MainDock(self.iface, self.provider, self.event_bus)

        QgsMessageLog.logMessage(f"{[i.name() for i in self.provider.algorithms()]}")

        self.dock_widget.closingPlugin.connect(self.onClosePlugin)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.show()
