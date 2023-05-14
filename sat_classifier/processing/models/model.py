import os

import qgis.core as qcore
from ..qgis_extensions import described
import abc


class Model(qcore.QgsProcessingAlgorithm):
    MODEL_MODE = "MODEL_MODE"
    MODE_ENUM = ["Fit", "Predict"]
    INPUT_DATA_FOLDER = "INPUT_DATA_FOLDER"
    INPUT_DATA_IS_LABELED = "INPUT_DATA_IS_LABELED"
    INPUT_MODEL_FILE = "INPUT_MODEL_FILE"

    OUTPUT_MODEL_FILE = "OUTPUT_MODEL_FILE"
    OUTPUT_DATA_FOLDER = "OUTPUT_DATA_FOLDER"

    user_inputs = {False}

    _group = "Models"
    _group_id = "models"
    _help_string = ""

    @property
    @abc.abstractmethod
    def _display_name(self) -> str:
        ...

    @abc.abstractmethod
    def fit_labeled(self, data: str):
        ...

    @abc.abstractmethod
    def fit_unlabeled(self, data: str):
        ...

    @abc.abstractmethod
    def save(self, file: str):
        ...

    @abc.abstractmethod
    def load(self, file: str):
        ...

    @abc.abstractmethod
    def predict(self, data: str, output_folder: str):
        ...

    def tr(self, string) -> str:
        """
        Translation boilerplate
        """
        import sklearn.svm as sss
        return string

    def createInstance(self):
        """
        Initialize the algorithm
        """
        return self.__class__()

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

    def shortHelpString(self) -> str:
        """
        Basic description
        """
        return self._help_string

    def groupId(self) -> str:
        """
        Group in GUI
        """
        return self._group_id

    def initAlgorithm(self, config=None):
        self.addParameter(
            qcore.QgsProcessingParameterEnum(
                Model.MODEL_MODE,
                described(Model.MODEL_MODE),
                options=Model.MODE_ENUM,
                optional=False,
                allowMultiple=False
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterString(
                Model.INPUT_DATA_FOLDER,
                described(Model.INPUT_DATA_FOLDER),
                multiLine=False,
                optional=False
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterBoolean(
                Model.INPUT_DATA_IS_LABELED,
                described(Model.INPUT_DATA_IS_LABELED),
                optional=True
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterFile(
                Model.INPUT_MODEL_FILE,
                described(Model.INPUT_MODEL_FILE),
                optional=True
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterFileDestination(
                Model.OUTPUT_MODEL_FILE,
                described(Model.OUTPUT_MODEL_FILE),
                optional=True,
                defaultValue="/tmp/model.gz"
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterFolderDestination(
                Model.OUTPUT_DATA_FOLDER,
                described(Model.OUTPUT_DATA_FOLDER),
                optional=True,
                createByDefault=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        fit = self.parameterAsEnum(parameters, Model.MODEL_MODE, context)
        if fit == 0:
            fld = self.parameterAsString(parameters, Model.INPUT_DATA_FOLDER, context)
            output_file = self.parameterAsFile(parameters, Model.OUTPUT_MODEL_FILE, context)
            labeled = self.parameterAsBoolean(parameters, Model.INPUT_DATA_IS_LABELED, context)

            if labeled:
                self.fit_labeled(fld)
            else:
                self.fit_unlabeled(fld)

            self.save(output_file)
            return {Model.OUTPUT_MODEL_FILE: output_file}
        else:
            input_data = self.parameterAsString(parameters, Model.INPUT_DATA_FOLDER, context)
            output_fld = self.parameterAsString(parameters, Model.OUTPUT_DATA_FOLDER, context)
            model = self.parameterAsFile(parameters, Model.INPUT_MODEL_FILE, context)

            self.load(model)
            os.makedirs(output_fld, exist_ok=True)
            self.predict(input_data, output_fld)
            return {Model.OUTPUT_DATA_FOLDER: output_fld}
