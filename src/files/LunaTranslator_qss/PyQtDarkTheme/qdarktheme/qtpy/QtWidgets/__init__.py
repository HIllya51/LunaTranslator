"""Module for QtWidgets."""

from collections.abc import Sequence

from qdarktheme.qtpy.qt_compat import QT_API

if QT_API == "PySide6":
    from PySide6.QtWidgets import *  # type: ignore  # noqa: F403
elif QT_API == "PyQt6":
    from PyQt6.QtWidgets import *  # type: ignore  # noqa: F403
elif QT_API == "PyQt5":
    from PyQt5.QtWidgets import *  # type: ignore # noqa: F403
elif QT_API == "PySide2":
    from PySide2.QtWidgets import *  # type: ignore  # noqa: F403


class Application(QApplication):  # type: ignore  # noqa: F405
    """Override QApplication."""

    def __init__(self, args = None) -> None:
        """Override QApplication method."""
        super().__init__(args)

    def exec(self) -> int:
        """Override QApplication method."""
        if hasattr(super(), "exec"):
            return super().exec()
        return super().exec_()

    def exit(self, returnCode = 0) -> None:  # noqa: N803
        """Override QApplication method."""
        return super().exit(returnCode)


QApplication = Application
