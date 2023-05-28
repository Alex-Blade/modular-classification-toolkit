import abc

from PyQt5.QtWidgets import QWidget


class Tab(abc.ABC):
    @property
    @abc.abstractmethod
    def tab_to_add(self) -> QWidget:
        ...
