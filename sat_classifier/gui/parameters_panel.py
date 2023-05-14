from PyQt5 import QtWidgets
from processing.gui.wrappers import WidgetWrapperFactory, WidgetWrapper
import qgis.core
from qgis._core import QgsProject, QgsProcessingParameterDefinition, QgsProcessingOutputLayerDefinition, QgsMessageLog
from qgis._gui import QgsProcessingContextGenerator, QgsProcessingParameterWidgetContext, \
    QgsProcessingParametersGenerator, QgsProcessingHiddenWidgetWrapper, QgsGui, QgsProcessingGui


class ContextGenerator(QgsProcessingContextGenerator):
    def __init__(self, context):
        super().__init__()
        self.processing_context = context

    def processingContext(self):
        return self.processing_context


class ParametersPanel:
    def __init__(self, _algorithm, iface, parent, processing_context):
        self.parent = parent
        self.in_place = False
        self._algorithm = _algorithm
        self.wrappers = {}
        self.extra_parameters = {}
        self.processing_context = processing_context
        self.context_generator = ContextGenerator(processing_context)
        self.widget_context = QgsProcessingParameterWidgetContext()
        self.widget_context.setProject(QgsProject.instance())
        if iface is not None:
            self.widget_context.setMapCanvas(iface.mapCanvas())
            self.widget_context.setBrowserModel(iface.browserModel())
            self.widget_context.setActiveLayer(iface.activeLayer())

    def createProcessingParameters(self, flags=QgsProcessingParametersGenerator.Flags()):
        include_default = not (flags & QgsProcessingParametersGenerator.Flag.SkipDefaultValueParameters)
        parameters = {}
        for p, v in self.extra_parameters.items():
            parameters[p] = v

        for param in self.algorithm().parameterDefinitions():
            if param.flags() & QgsProcessingParameterDefinition.FlagHidden:
                continue
            if not param.isDestination():
                try:
                    wrapper = self.wrappers[param.name()]
                except KeyError:
                    continue

                # For compatibility with 3.x API, we need to check whether the wrapper is
                # the deprecated WidgetWrapper class. If not, it's the newer
                # QgsAbstractProcessingParameterWidgetWrapper class
                # TODO QGIS 4.0 - remove
                if issubclass(wrapper.__class__, WidgetWrapper):
                    widget = wrapper.widget
                else:
                    widget = wrapper.wrappedWidget()

                if not isinstance(wrapper, QgsProcessingHiddenWidgetWrapper) and widget is None:
                    continue

                value = wrapper.parameterValue()
                if param.defaultValue() != value or include_default:
                    parameters[param.name()] = value
            else:
                if self.in_place and param.name() == 'OUTPUT':
                    parameters[param.name()] = 'memory:'
                    continue

                try:
                    wrapper = self.wrappers[param.name()]
                except KeyError:
                    continue

                widget = wrapper.wrappedWidget()
                value = wrapper.parameterValue()

                dest_project = None
                if wrapper.customProperties().get('OPEN_AFTER_RUNNING'):
                    dest_project = QgsProject.instance()

                if value and isinstance(value, QgsProcessingOutputLayerDefinition):
                    value.destinationProject = dest_project
                if value and (param.defaultValue() != value or include_default):
                    parameters[param.name()] = value

                    context = qcore.QgsProcessingContext()
                    ok, error = param.isSupportedOutputValue(value, context)
                    if not ok:
                        raise ValueError("SomeError")

        return self.algorithm().preprocessParameters(parameters)

    def initWidgets(self):
        user_inputs = getattr(self.algorithm(), "user_inputs", {True})
        for p in self.algorithm().parameterDefinitions():
            if True not in user_inputs and not p.name() not in user_inputs:
                continue
            if p.isDestination():
                continue
            ww = WidgetWrapperFactory.create_wrapper_from_class(p, "a")
            ww.setWidgetContext(self.widget_context)
            ww.registerProcessingContextGenerator(self.context_generator)
            ww.registerProcessingParametersGenerator(self)
            self.parent.addWidget(ww.label)
            self.parent.addWidget(ww.widget)
            self.wrappers[p.name()] = ww
        for p in self.algorithm().destinationParameterDefinitions():
            wrapper = QgsGui.processingGuiRegistry().createParameterWidgetWrapper(p, QgsProcessingGui.Standard)
            wrapper.setWidgetContext(self.widget_context)
            wrapper.registerProcessingContextGenerator(self.context_generator)
            self.wrappers[p.name()] = wrapper

            label = wrapper.createWrappedLabel()
            if label is not None:
                label = QtWidgets.QLabel()
                label.setObjectName("label")
                label.setText(p.name())

            widget = wrapper.createWrappedWidget(self.processing_context)
            self.parent.addWidget(label)
            self.parent.addWidget(widget)

        for wrapper in list(self.wrappers.values()):
            QgsMessageLog.logMessage(f"{wrapper}")
            wrapper.postInitialize(list(self.wrappers.values()))

    def algorithm(self):
        return self._algorithm
