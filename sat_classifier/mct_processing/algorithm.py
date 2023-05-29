import qgis.core as qcore
import abc


class Algorithm(qcore.QgsProcessingAlgorithm):
    @property
    @abc.abstractmethod
    def user_inputs(self) -> set[str] | set[bool]:
        ...

    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def name_string(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def group_string(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def group_id(self) -> str:
        ...

    @abc.abstractmethod
    def initAlgorithm(self, config=None):
        ...

    @abc.abstractmethod
    def processAlgorithm(self, parameters, context, feedback):
        ...

    def createInstance(self):
        """
        Initialize the algorithm
        """
        return self.__class__()

    def displayName(self) -> str:
        """
        Name in GUI
        """
        return self.display_name

    def shortHelpString(self) -> str:
        """
        Basic description
        """
        try:
            return self.help_string
        except AttributeError:
            return ""

    def name(self) -> str:
        return self.name_string

    def group(self) -> str:
        return self.group_string

    def groupId(self) -> str:
        """
        Group in GUI
        """
        return self.group_id

    def tr(self, s: str) -> str:
        return s
