from PyQt5 import QtCore, QtGui, QtWidgets
from qgis import core
from qgis import gui
from processing.gui.AlgorithmDialog import AlgorithmDialog


def generate_dynamic_parameters(parent: QtWidgets.QWidget, *algorithms: core.QgsProcessingAlgorithm):
    core.QgsMessageLog.logMessage(f"Algorithms: {algorithms}")
    dlgs = []
    for alg in algorithms:
        dlg = alg.createCustomParametersWidget(parent)
        if not dlg:
            dlg = AlgorithmDialog(alg, parent=parent, in_place=True)
        dlgs.append(dlg)
    return dlgs
