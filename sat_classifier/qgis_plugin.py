from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.core import QgsApplication, QgsMessageLog
import qgis.core as core

from .processing.provider import Provider
from . import gui
from .gui.parameters_panel import ParametersPanel


class QGisPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.action = None
        self.dock_widget = None

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

    def run(self):
        QMessageBox.information(None, 'Minimal plugin', 'Do something useful here')

        panels = []
        if self.dock_widget is None:
            self.dock_widget = gui.EmptyDockWidget(self.provider, self.iface)
            self.dock_widget.finish()

        QgsMessageLog.logMessage(f"{[i.name() for i in self.provider.algorithms()]}")

        self.dock_widget.closingPlugin.connect(self.onClosePlugin)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.show()
