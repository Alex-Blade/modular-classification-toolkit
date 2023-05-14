import abc
import os
from pathlib import Path
from typing import Iterator, NamedTuple

import numpy as np
import qgis.core as qcore
from ..qgis_extensions import described


class Band(NamedTuple):
    arr: np.ndarray


class Label(NamedTuple):
    poly_id: int
    initial_value: str


ListOfBands = list[Label | Band]


class RasterLoader(qcore.QgsProcessingAlgorithm):
    _group = "Data Loaders"
    _group_id = "data_loaders"
    _help_string = ""

    user_inputs = {True}

    OUTPUT_FOLDER = "OUTPUT_FOLDER"
    CONFIG_MULTI_FILE_MODE = "multi_file"

    @property
    @abc.abstractmethod
    def _display_name(self) -> str:
        ...

    @abc.abstractmethod
    def init_parameters_single_input(self: qcore.QgsProcessingAlgorithm):
        ...

    @abc.abstractmethod
    def init_parameters_multi_input(self: qcore.QgsProcessingAlgorithm):
        ...

    @abc.abstractmethod
    def convert_to_numpy(self: qcore.QgsProcessingAlgorithm,
                         parameters: qcore.QgsProcessingParameters,
                         context: qcore.QgsProcessingContext,
                         feedback: qcore.QgsProcessingFeedback,
                         multi_file: bool) -> \
            Iterator[ListOfBands]:
        ...

    def __init__(self, _config=None):
        super().__init__()
        self._config: dict = _config

    def tr(self, string) -> str:
        """
        Translation boilerplate
        """
        return string

    def createInstance(self):
        """
        Initialize the algorithm
        """
        return self.__class__(self._config)

    def name(self) -> str:
        """
        Unique algorithm identifier
        """
        return self.__class__.__name__.lower()

    def displayName(self) -> str:
        """
        Name in GUI
        """
        return self._display_name

    def group(self) -> str:
        """
        Group name in GUI
        """
        return self._group

    def groupId(self) -> str:
        """
        Group in GUI
        """
        return self._group_id

    def shortHelpString(self) -> str:
        """
        Basic description
        """
        return self._help_string

    def initAlgorithm(self, config: dict = None):
        if config is None:
            config = {}
        if config.get(RasterLoader.CONFIG_MULTI_FILE_MODE, "no") == "no":
            self.init_parameters_single_input()
        else:
            self.init_parameters_multi_input()

        self.addParameter(
            qcore.QgsProcessingParameterFolderDestination(
                RasterLoader.OUTPUT_FOLDER,
                described(RasterLoader.OUTPUT_FOLDER)
            )
        )

        self._config = config

    def processAlgorithm(self, parameters, context, feedback) -> dict:
        multi_file = not (self._config.get(RasterLoader.CONFIG_MULTI_FILE_MODE, "no") == "no")
        folder = Path(self.parameterAsString(parameters, RasterLoader.OUTPUT_FOLDER, context))

        for idx, batch in enumerate(self.convert_to_numpy(parameters, context, feedback, multi_file=multi_file)):
            out = folder / (f"b{idx}" if multi_file else f"b0")
            os.makedirs(out, exist_ok=True)
            if (l := batch[-1]).__class__.__name__ == "Label":
                p = out / f"{l.initial_value}_{str(l.poly_id)}"
                np.savez_compressed(p, *[b.arr for b in batch[:-1]])
            elif batch[-1].__class__.__name__ == "Band":
                p = out / f"unlabeled"
                np.savez_compressed(p, *[b.arr for b in batch])
            else:
                feedback.reportError(f"Unknown object: {batch[-1]}, type: {type(batch[-1])}")
        feedback.pushDebugInfo(f"{RasterLoader.OUTPUT_FOLDER}: {folder}")
        return {RasterLoader.OUTPUT_FOLDER: str(folder)}
