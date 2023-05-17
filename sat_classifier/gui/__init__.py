import os
from functools import partial

from PyQt5 import QtGui, QtWidgets, QtCore, Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from qgis import gui
from qgis.core import QgsMessageLog, QgsProcessingProvider
import qgis.core as core

from . import simple_widget
from .parameters_panel import ParametersPanel
import processing
from processing.tools.dataobjects import createContext


# import pydevd_pycharm
#
# pydevd_pycharm.settrace('127.0.0.1', port=12345, stdoutToServer=True, stderrToServer=True)
#

import faulthandler
faulthandler.enable()


class DockWidget(QtWidgets.QDockWidget, simple_widget.Ui_DockWidget):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(DockWidget, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


class PipelineElement:
    def __init__(self, parent: QtWidgets.QWidget, page_parent: QtWidgets.QWidget, provider: QgsProcessingProvider):
        self.parent = parent
        self.config_title = QtWidgets.QLabel(parent)
        self.config_hlayout = QtWidgets.QHBoxLayout()

        self.config_combobox = QtWidgets.QComboBox(parent)
        self.remove = QtWidgets.QPushButton(parent)

        self.parameters_page = QtWidgets.QWidget(page_parent)
        self.parameters_page.setGeometry(QtCore.QRect(0, 0, 411, 68))
        self.parameters_page.setObjectName("parameters_page")
        self.page_vertical_layout = QtWidgets.QVBoxLayout(self.parameters_page)  # QtWidgets.QVBoxLayout()
        self.page_vertical_layout.setObjectName("page_vertical_layout")
        # self.parameters_page.setLayout(self.page_vertical_layout)
        self.provider = provider
        self.parameter_panel: ParametersPanel = None

    @property
    def algorithm(self):
        return self.provider.algorithm(self.config_combobox.currentText())

    def initialize(self, remove_slot, iface, processing_context):
        self.config_hlayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.config_combobox.addItems([alg.name() for alg in self.provider.algorithms()])
        self.config_hlayout.addWidget(self.config_combobox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.remove.sizePolicy().hasHeightForWidth())
        self.remove.setSizePolicy(sizePolicy)
        self.remove.setText("-")
        remove_slot = partial(remove_slot, self)
        self.remove.clicked[bool].connect(remove_slot)
        self.config_hlayout.addWidget(self.remove)
        self.config_title.setText(self.algorithm.group() or "Test")
        selected_slot = partial(self.on_algo_selected, iface, processing_context)
        self.config_combobox.currentTextChanged[str].connect(selected_slot)
        selected_slot()

    def add_to_layout(self, layout: QtWidgets.QBoxLayout):
        idx = layout.count() - 1
        layout.insertLayout(idx, self.config_hlayout)
        layout.insertWidget(idx, self.config_title)

    def clean_page(self):
        children = self.page_vertical_layout.children()
        for i in reversed(range(self.page_vertical_layout.count())):
            item = self.page_vertical_layout.itemAt(i)
            self.page_vertical_layout.removeItem(item)
            if item.widget():
                item.widget().setParent(None)
        QgsMessageLog.logMessage(f"Cleaned: {self.page_vertical_layout.count()} {self.page_vertical_layout.children()}")

    def on_algo_selected(self, iface, processing_context):
        QgsMessageLog.logMessage(f"on algo selected: {self.algorithm.name()}")
        self.clean_page()
        algo = self.algorithm
        self.config_title.setText(algo.group())
        self.parameter_panel = ParametersPanel(algo, iface, self.page_vertical_layout, processing_context)
        self.parameter_panel.initWidgets()
        spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.page_vertical_layout.addItem(spacer_item)

    def remove_children(self):
        self.config_title.setParent(None)
        self.config_combobox.setParent(None)
        self.config_hlayout.setParent(None)
        self.clean_page()
        self.parameters_page.setParent(None)
        self.remove.setParent(None)
        del self.config_title
        del self.config_combobox
        del self.config_hlayout
        del self.parameters_page
        del self.remove


class EmptyDockWidget(QtWidgets.QDockWidget):
    closingPlugin = pyqtSignal()

    def __init__(self, provider: QgsProcessingProvider, iface):
        super(EmptyDockWidget, self).__init__(None)
        self.iface = iface
        self.processing_context = createContext()
        self.provider = provider
        self.setObjectName("DockWidget")
        self.resize(451, 362)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.predict = QtWidgets.QWidget(self.dockWidgetContents)
        self.predict.setObjectName("predict")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.predict)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.toolBox = QtWidgets.QToolBox(self.predict)
        self.toolBox.setObjectName("toolBox")
        self.pages = []
        self.page_layouts = []

        self.verticalLayout_4.addWidget(self.toolBox)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.pushButton = QtWidgets.QPushButton(self.predict)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_4.addWidget(self.pushButton)
        self.pushButton.clicked[bool].connect(self.push_button)

        self.tabWidget.addTab(self.predict, "")

        self.config = QtWidgets.QWidget(self.dockWidgetContents)
        self.config.setObjectName("config")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.config)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.config)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget(self.config)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 409, 272))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.add_to_pipe = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_to_pipe.sizePolicy().hasHeightForWidth())
        self.add_to_pipe.setSizePolicy(sizePolicy)
        self.add_to_pipe.setIconSize(QtCore.QSize(16, 16))
        self.add_to_pipe.setFlat(False)
        self.add_to_pipe.setObjectName("add_to_pipe")
        self.horizontalLayout_2.addWidget(self.add_to_pipe)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.pipeline: list[PipelineElement] = []
        self.add_to_pipe.clicked[bool].connect(self.add_pipeline_element)
        self.spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.config, "")
        self.tabWidget.currentChanged[int].connect(self.current_changed)

    def current_changed(self):
        QgsMessageLog.logMessage("Current state has changed")

    def remove_pipeline_element(self, pel: PipelineElement):
        index = self.pipeline.index(pel)
        self.toolBox.removeItem(index)
        pel.remove_children()
        self.pipeline.pop(index)

    def add_pipeline_element(self):
        pel = PipelineElement(self.scrollAreaWidgetContents, self.predict, self.provider)
        pel.initialize(self.remove_pipeline_element, self.iface, self.processing_context)
        i = self.verticalLayout_2.itemAt(self.verticalLayout_2.count() - 1)
        QgsMessageLog.logMessage(f"Object: {i.__class__.__name__}")
        pel.add_to_layout(self.verticalLayout_2)
        self.pipeline.append(pel)
        pel.parameters_page.setObjectName("Test")
        self.toolBox.addItem(pel.parameters_page, "Placeholder 2")

    def finish(self):
        self.translate_ui()
        self.horizontalLayout.addWidget(self.tabWidget)
        self.setWidget(self.dockWidgetContents)
        self.tabWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("DockWidget", "DockWidget"))
        self.pushButton.setText(_translate("DockWidget", "Classify"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.predict), _translate("DockWidget", "Classify"))
        self.add_to_pipe.setText(_translate("DockWidget", "+"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.config), _translate("DockWidget", "Configuration"))

    def push_button(self):
        QgsMessageLog.logMessage("message")
        params = dict()
        feedback = core.QgsProcessingFeedback(logFeedback=True)
        context = self.processing_context
        for idx, pel in enumerate(self.pipeline):
            panel = pel.parameter_panel
            params.update(panel.createProcessingParameters())
            func = processing.run
            kwargs = {"context": context, "feedback": feedback, "is_child_algorithm": True}
            if idx == len(self.pipeline) - 1:
                func = processing.runAndLoadResults
                kwargs.pop("is_child_algorithm")
            params.update(func(f'yourplugin:{pel.config_combobox.currentText()}', params, **kwargs))

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
