"""Module for QtSvg."""
from qdarktheme.qtpy.qt_compat import QT_API, qt_import_error

if QT_API is None:
    raise qt_import_error
if QT_API == "PySide6":
    from PySide6.QtSvg import *  # type: ignore  # noqa: F403
elif QT_API == "PyQt6":
    from PyQt6.QtSvg import *  # type: ignore  # noqa: F403
elif QT_API == "PyQt5":
    from PyQt5.QtSvg import *  # type: ignore  # noqa: F403
elif QT_API == "PySide2":
    from PySide2.QtSvg import *  # type: ignore  # noqa: F403
