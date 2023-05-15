import importlib.util
import sys
from pathlib import Path
from typing import Type

from .input_data import raster_loader
from .models import model

from qgis.core import QgsProcessingProvider
from .renderer import Renderer
from .pipelines.full_pipeline import FullPipeline


class Provider(QgsProcessingProvider):
    INPUT_DATA_FILES = {"__init__.py", "raster_loader.py"}
    MODEL_FILES = {"__init__.py", "model.py"}

    @staticmethod
    def load_folder(package, predefined_files):
        files = Path(sys.modules[package].__file__).parent.iterdir()
        files = list(filter(lambda f: f.is_file() and f.name not in predefined_files, files))
        for file in files:
            module = f"{package}.{file.name.replace('.', '_')}"
            spec = importlib.util.spec_from_file_location(module, str(file))
            foo = importlib.util.module_from_spec(spec)
            sys.modules[module] = foo
            spec.loader.exec_module(foo)
            for cls_name in getattr(foo, "__all__"):
                cls: Type = getattr(foo, str(cls_name))
                yield cls

    def loadAlgorithms(self, *args, **kwargs):
        for cls in Provider.load_folder("minimal.sat_classifier.processing.input_data", Provider.INPUT_DATA_FILES):
            self.addAlgorithm(cls())
        for cls in Provider.load_folder("minimal.sat_classifier.processing.models", Provider.MODEL_FILES):
            self.addAlgorithm(cls())
        self.addAlgorithm(Renderer())
        # self.addAlgorithm(FullPipeline())

    def id(self, *args, **kwargs):
        """The ID of your plugin, used for identifying the provider.

        This string should be a unique, short, character only string,
        eg "qgis" or "gdal". This string should not be localised.
        """
        return 'yourplugin'

    def name(self, *args, **kwargs):
        """The human friendly name of your plugin in Processing.

        This string should be as short as possible (e.g. "Lastools", not
        "Lastools version 1.0.1 64-bit") and localised.
        """
        return self.tr('Your plugin')

    def icon(self):
        """Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)
