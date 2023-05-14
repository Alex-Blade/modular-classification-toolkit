import os

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from qgis import gui

from . import simple_widget


class DockWidget(QtWidgets.QDockWidget, simple_widget.Ui_DockWidget):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(DockWidget, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


class EmptyDockWidget(QtWidgets.QDockWidget):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(EmptyDockWidget, self).__init__(parent)
        self.setObjectName("DockWidget")
        self.resize(451, 362)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.prepare_model_1 = QtWidgets.QWidget()
        self.prepare_model_1.setObjectName("prepare_model_1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.prepare_model_1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.di_frame_1 = QtWidgets.QVBoxLayout()
        self.di_frame_1.setObjectName("di_frame_1")
        self.verticalLayout_2.addLayout(self.di_frame_1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabWidget.addTab(self.prepare_model_1, "")
        self.prepare_model_2 = QtWidgets.QWidget()
        self.prepare_model_2.setObjectName("prepare_model_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.prepare_model_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.di_frame_2 = QtWidgets.QVBoxLayout()
        self.di_frame_2.setObjectName("di_frame_2")
        self.verticalLayout_3.addLayout(self.di_frame_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.tabWidget.addTab(self.prepare_model_2, "")
        self.predict = QtWidgets.QWidget()
        self.predict.setObjectName("predict")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.predict)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.toolBox = QtWidgets.QToolBox(self.predict)
        self.toolBox.setObjectName("toolBox")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 411, 68))
        self.page_3.setObjectName("page_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.page_3)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.toolBox.addItem(self.page_3, "")
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setGeometry(QtCore.QRect(0, 0, 411, 68))
        self.page_4.setObjectName("page_4")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.page_4)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.toolBox.addItem(self.page_4, "")
        self.verticalLayout_4.addWidget(self.toolBox)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.label_3 = QtWidgets.QLabel(self.predict)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.tabWidget.addTab(self.predict, "")
        self.config = QtWidgets.QWidget()
        self.config.setObjectName("config")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.config)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(self.config)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.data_importer_1 = QtWidgets.QComboBox(self.config)
        self.data_importer_1.setObjectName("data_importer_1")
        self.verticalLayout.addWidget(self.data_importer_1)
        self.label = QtWidgets.QLabel(self.config)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.data_importer_2 = QtWidgets.QComboBox(self.config)
        self.data_importer_2.setObjectName("data_importer_2")
        self.verticalLayout.addWidget(self.data_importer_2)
        self.label_6 = QtWidgets.QLabel(self.config)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.model_1 = QtWidgets.QComboBox(self.config)
        self.model_1.setObjectName("model_1")
        self.verticalLayout.addWidget(self.model_1)
        self.label_2 = QtWidgets.QLabel(self.config)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.model_2 = QtWidgets.QComboBox(self.config)
        self.model_2.setObjectName("model_2")
        self.verticalLayout.addWidget(self.model_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.tabWidget.addTab(self.config, "")

    def finish(self):
        self.translate_ui()
        self.horizontalLayout.addWidget(self.tabWidget)
        self.setWidget(self.dockWidgetContents)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("DockWidget", "DockWidget"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.prepare_model_1), _translate("DockWidget", "Data Importer #1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.prepare_model_2), _translate("DockWidget", "Data Importer #2"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("DockWidget", "Model #1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_4), _translate("DockWidget", "Model #2"))
        self.label_3.setText(_translate("DockWidget", "There will be something"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.predict), _translate("DockWidget", "Classify"))
        self.label_5.setText(_translate("DockWidget", "Data Importer #1"))
        self.label.setText(_translate("DockWidget", "Data Importer #2"))
        self.label_6.setText(_translate("DockWidget", "Model #1"))
        self.label_2.setText(_translate("DockWidget", "Model #2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.config), _translate("DockWidget", "Configuration"))

    def messageBar(self):
        return self._messageBar

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
