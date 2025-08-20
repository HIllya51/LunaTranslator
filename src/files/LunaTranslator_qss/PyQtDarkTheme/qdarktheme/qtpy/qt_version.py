"""Module for detecting Qt version."""

from qdarktheme.qtpy.qt_compat import QT_API

__version__ = None
if QT_API == "PySide6":
    from PySide6.QtCore import qVersion  # type: ignore

    __version__ = qVersion()
elif QT_API == "PyQt6":
    from PyQt6.QtCore import qVersion  # type: ignore

    __version__ = qVersion()
elif QT_API == "PyQt5":
    from PyQt5.QtCore import qVersion  # type: ignore

    __version__ = qVersion()
elif QT_API == "PySide2":
    from PySide2.QtCore import qVersion  # type: ignore

    __version__ = qVersion()
