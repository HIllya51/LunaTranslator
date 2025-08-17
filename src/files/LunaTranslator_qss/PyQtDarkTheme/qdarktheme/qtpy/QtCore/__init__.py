"""Module for QtCore."""
from qdarktheme.qtpy.qt_compat import QT_API, qt_import_error

if QT_API is None:
    raise qt_import_error
if QT_API == "PySide6":
    from PySide6.QtCore import *  # type: ignore  # noqa: F403
elif QT_API == "PyQt6":
    from PyQt6.QtCore import *  # type: ignore  # noqa: F403

    Slot = pyqtSlot  # noqa: F405
    Signal = pyqtSignal  # noqa: F405
elif QT_API == "PyQt5":
    from PyQt5.QtCore import *  # type: ignore  # noqa: F403

    Slot = pyqtSlot  # type: ignore  # noqa: F405
    Signal = pyqtSignal  # type: ignore  # noqa: F405
elif QT_API == "PySide2":
    from PySide2.QtCore import *  # type: ignore  # noqa: F403
