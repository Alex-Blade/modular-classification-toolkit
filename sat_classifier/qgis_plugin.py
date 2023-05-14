from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.core import QgsApplication, QgsMessageLog

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
        #
        # self.dock_widget.vector_class_field.setLayer(self.dock_widget.train_vector.currentLayer())
        # self.dock_widget.vector_id_field.setLayer(self.dock_widget.train_vector.currentLayer())
        #

        #
        # self.dock_widget.train_vector.layerChanged[qcore.QgsMapLayer]\
        #     .connect(self.dock_widget.vector_class_field.setLayer)
        # self.dock_widget.train_vector.layerChanged[qcore.QgsMapLayer]\
        #     .connect(self.dock_widget.vector_id_field.setLayer)
        #
        # def push_event():
        #     QgsMessageLog.logMessage("Button Pressed")
        #     feedback = qcore.QgsProcessingFeedback(logFeedback=True)
        #     context = qcore.QgsProcessingContext()
        #     results = {}
        #     outputs = {}
        #
        #     # Labeled Tiff Loader
        #     alg_params = {
        #         'input_map': self.dock_widget.raster_map.currentLayer(),
        #         'training_data': self.dock_widget.train_vector.currentLayer(),
        #         'class_field': self.dock_widget.vector_class_field.currentField(),
        #         'id_field': self.dock_widget.vector_id_field.currentField(),
        #         'processed_bands': [],
        #         'Predicted': qcore.QgsProcessing.TEMPORARY_OUTPUT
        #     }
        #     outputs = processing.runAndLoadResults('yourplugin:FullPipeline', alg_params, context=context, feedback=feedback)
        #     QgsMessageLog.logMessage(str(outputs))
        # self.dock_widget.pushButton.clicked[bool].connect(push_event)

        if self.dock_widget is None:
            self.dock_widget = gui.EmptyDockWidget()
            from processing.tools.dataobjects import createContext
            processing_context = createContext()
            some = ParametersPanel(self.provider.algorithms()[1], self.iface, self.dock_widget.verticalLayout_6, processing_context)
            some.initWidgets()
            some = ParametersPanel(self.provider.algorithms()[-1], self.iface, self.dock_widget.verticalLayout_7, processing_context)
            some.initWidgets()
            self.dock_widget.finish()

        QgsMessageLog.logMessage(f"{[i.name() for i in self.provider.algorithms()]}")

        self.dock_widget.closingPlugin.connect(self.onClosePlugin)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.show()
