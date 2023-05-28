import importlib.util
import sys
from pathlib import Path
from typing import Type

from qgis.core import QgsProcessingProvider, Qgis, QgsMessageLog


class Provider(QgsProcessingProvider):
    INPUT_DATA_FILES = {"__init__.py", "raster_loader.py"}
    MODEL_FILES = {"__init__.py", "model.py"}

    @staticmethod
    def load_folder(folder, predefined_files, package="minimal"):
        files = Path(folder).iterdir()
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

    @staticmethod
    def load_from_package(package, predefined_files):
        folder = Path(sys.modules[package].__file__).parent
        yield from Provider.load_folder(folder, predefined_files, package=package)

    def loadAlgorithms(self, *args, **kwargs):
        import minimal.sat_classifier.mct_processing.input_data
        import minimal.sat_classifier.mct_processing.models
        for cls in Provider.load_from_package("minimal.sat_classifier.mct_processing.input_data", Provider.INPUT_DATA_FILES):
            self.addAlgorithm(cls())
        for cls in Provider.load_from_package("minimal.sat_classifier.mct_processing.models", Provider.MODEL_FILES):
            self.addAlgorithm(cls())
        custom_packages = Path.home() / "qgis_mct"
        if custom_packages.is_dir():
            for d in custom_packages.iterdir():
                if d.is_dir():
                    QgsMessageLog.logMessage(f"Loading {d} extension")
                    try:
                        for cls in Provider.load_folder(d, predefined_files=set()):
                            self.addAlgorithm(cls())
                    except Exception as e:
                        QgsMessageLog.logMessage(f"Failed to load {d}:\n{e}")

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
