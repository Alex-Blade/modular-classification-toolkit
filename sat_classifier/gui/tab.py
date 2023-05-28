from typing import Protocol

from PyQt5.QtWidgets import QWidget


class Tab(Protocol):
    @property
    def tab_to_add(self) -> QWidget:
        ...

    @property
    def tab_title(self) -> str:
        ...
