import os

import qgis.core as qcore
from ..qgis_extensions import described
from ..algorithm import Algorithm
import abc


class Model(Algorithm):
    MODEL_MODE = "MODEL_MODE"
    MODE_ENUM = ["Fit", "Predict"]
    LABELED_DATA_FOLDER = "LABELED_DATA"
    UNLABELED_DATA_FOLDER = "UNLABELED_DATA"
    INPUT_MODEL_FILE = "INPUT_MODEL_FILE"

    OUTPUT_DATA_FOLDER = "PREDICTIONS_FOLDER"

    group_string = "Models"
    group_id = "models"

    @property
    def OUTPUT_MODEL_FILE(self):
        return f"{self.__class__.__name__}_MODEL_FILE"

    @property
    @abc.abstractmethod
    def model_parameters(self) -> set[str] | set[bool]:
        ...

    @property
    def user_inputs(self) -> set[str] | set[bool]:
        return {Model.MODEL_MODE} | self.model_parameters

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

    def add_custom_parameters(self):
        ...

    def tr(self, string) -> str:
        """
        Translation boilerplate
        """
        import sklearn.svm as sss
        return string

    def initAlgorithm(self, config=None):
        self.add_custom_parameters()

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

        self.addParameter(
            qcore.QgsProcessingParameterFileDestination(
                self.OUTPUT_MODEL_FILE,
                description=described(self.OUTPUT_MODEL_FILE),
                optional=True,
                defaultValue=qcore.QgsProcessing.TEMPORARY_OUTPUT,
                createByDefault=False,
                fileFilter="(*.gz)"
            )
        )

    def processAlgorithm(self, parameters, context, feedback: qcore.QgsProcessingFeedback):
        predict = self.parameterAsEnum(parameters, Model.MODEL_MODE, context)
        if not predict:
            unlabeled_fld = self.parameterAsString(parameters, Model.UNLABELED_DATA_FOLDER, context)
            labeled_fld = self.parameterAsString(parameters, Model.LABELED_DATA_FOLDER, context)
            output_file = self.parameterAsFile(parameters, self.OUTPUT_MODEL_FILE, context)

            self.fit(unlabeled_fld, labeled_fld)

            self.save(output_file)
            return {self.OUTPUT_MODEL_FILE: output_file}
        else:
            input_data = self.parameterAsString(parameters, Model.UNLABELED_DATA_FOLDER, context)
            output_fld = self.parameterAsString(parameters, Model.OUTPUT_DATA_FOLDER, context)
            model = self.parameterAsFile(parameters, self.OUTPUT_MODEL_FILE, context)

            self.load(model)
            os.makedirs(output_fld, exist_ok=True)
            self.predict(input_data, output_fld)
            return {Model.OUTPUT_DATA_FOLDER: output_fld}
