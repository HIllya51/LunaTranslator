"""Module for Qt compat."""

import os
import sys


class QtImportError(ImportError):
    """Error raise if no bindings could be selected."""


qt_import_error = QtImportError(
    "Failed to import qt-binding. Check packages(pip list)."
    "\n\tAvailable Qt-binding packages: PySide6, PyQt6, PyQt5, PySide2."
)


# Qt6
_QT_API_PYSIDE6 = "PySide6"
_QT_API_PYQT6 = "PyQt6"
# Qt5
_QT_API_PYQT5 = "PyQt5"
_QT_API_PYSIDE2 = "PySide2"


_API_LIST = [_QT_API_PYSIDE6, _QT_API_PYQT6, _QT_API_PYQT5, _QT_API_PYSIDE2]


def _get_loaded_api():
    """Return which API is loaded.

    If this returns anything besides None,
    importing any other Qt-binding is unsafe.
    """
    for api in _API_LIST:
        if sys.modules.get("{}.QtCore".format(api)):
            return api
    return None


def _get_environ_api():
    """Return which API is specified in environ."""
    _qt_api_env = os.environ.get("QT_API")
    if _qt_api_env is not None:
        _qt_api_env = _qt_api_env.lower()

    _env_to_module = {
        "pyside6": _QT_API_PYSIDE6,
        "pyqt6": _QT_API_PYQT6,
        "pyqt5": _QT_API_PYQT5,
        "pyside2": _QT_API_PYSIDE2,
        None: None,
    }
    try:
        return _env_to_module[_qt_api_env]
    except KeyError:
        raise KeyError(
            "The environment variable QT_API has the unrecognized value "
            "{!r}. "
            "Valid values are {}".format(_qt_api_env, [k for k in _env_to_module if k is not None])
        ) from None


def _get_installed_api():
    """Return which API is installed."""
    # Fix [AttributeError: module 'importlib' has no attribute 'util']
    # See https://stackoverflow.com/a/39661116/13452582
    from importlib import util

    for api in _API_LIST:
        if util.find_spec(api) is not None:
            return api
    return None


QT_API = _get_loaded_api()
if QT_API is None:
    QT_API = _get_environ_api()
if QT_API is None:
    QT_API = _get_installed_api()
