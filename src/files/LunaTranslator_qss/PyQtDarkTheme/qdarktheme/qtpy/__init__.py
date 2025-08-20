"""Package applying Qt compat of PyQt6, PySide6, PyQt5 and PySide2."""
from qdarktheme.qtpy.qt_compat import QtImportError
from qdarktheme.qtpy.qt_version import __version__

try:
    from qdarktheme.qtpy import QtCore, QtGui, QtSvg, QtWidgets
except ImportError:
    pass