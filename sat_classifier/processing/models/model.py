import os

import qgis.core as qcore
from ..qgis_extensions import described
import abc


class Model(qcore.QgsProcessingAlgorithm):
    MODEL_MODE = "MODEL_MODE"
    MODE_ENUM = ["Fit", "Predict"]
    LABELED_DATA_FOLDER = "LABELED_DATA"
    UNLABELED_DATA_FOLDER = "UNLABELED_DATA"
    INPUT_MODEL_FILE = "INPUT_MODEL_FILE"

    OUTPUT_MODEL_FILE = "MODEL_FILE"
    OUTPUT_DATA_FOLDER = "PREDICTIONS_FOLDER"

    user_inputs = {False}

    _group = "Models"
    _group_id = "models"
    _help_string = ""

    @property
    @abc.abstractmethod
    def _display_name(self) -> str:
        ...

    @abc.abstractmethod
    def fit(self, unlabeled_data: str, labeled_data: str):
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
                Model.LABELED_DATA_FOLDER,
                described(Model.LABELED_DATA_FOLDER),
                multiLine=False,
                optional=True
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterString(
                Model.UNLABELED_DATA_FOLDER,
                described(Model.UNLABELED_DATA_FOLDER),
                multiLine=False,
                optional=True
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterFolderDestination(
                Model.OUTPUT_DATA_FOLDER,
                described(Model.OUTPUT_DATA_FOLDER),
                optional=True,
                defaultValue=qcore.QgsProcessing.TEMPORARY_OUTPUT,
                createByDefault=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        predict = self.parameterAsEnum(parameters, Model.MODEL_MODE, context)
        if not predict:
            unlabeled_fld = self.parameterAsString(parameters, Model.UNLABELED_DATA_FOLDER, context)
            labeled_fld = self.parameterAsString(parameters, Model.LABELED_DATA_FOLDER, context)
            output_file = "/tmp/model.gz"

            self.fit(unlabeled_fld, labeled_fld)

            self.save(output_file)
            return {Model.OUTPUT_MODEL_FILE: output_file}
        else:
            input_data = self.parameterAsString(parameters, Model.UNLABELED_DATA_FOLDER, context)
            output_fld = self.parameterAsString(parameters, Model.OUTPUT_DATA_FOLDER, context)
            model = "/tmp/model.gz"

            self.load(model)
            os.makedirs(output_fld, exist_ok=True)
            self.predict(input_data, output_fld)
            return {Model.OUTPUT_DATA_FOLDER: output_fld}
