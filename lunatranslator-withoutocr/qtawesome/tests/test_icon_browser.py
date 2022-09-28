"""
Tests for QtAwesome Icon Browser.
"""

# Third party imports
from qtpy import QtCore, QtWidgets
import pytest

# Local imports
from qtawesome.icon_browser import IconBrowser
from qtawesome.styles import DEFAULT_DARK_PALETTE


@pytest.fixture
def browser(qtbot):
    browser = IconBrowser()
    browser._updateStyle(DEFAULT_DARK_PALETTE)
    qtbot.add_widget(browser)
    browser.show()
    return browser


def test_browser_init(browser):
    """
    Ensure the browser opens without error
    """
    def close():
        browser.close()

    timer = QtCore.QTimer()
    timer.timeout.connect(close)
    timer.setSingleShot(2000)
    timer.start()


def test_copy(qtbot, browser):
    """
    Ensure the copy UX works
    """
    clipboard = QtWidgets.QApplication.instance().clipboard()

    clipboard.setText('')

    assert clipboard.text() == ""

    # Enter a search term and press enter
    qtbot.keyClicks(browser._lineEdit, 'google')
    qtbot.keyPress(browser._lineEdit, QtCore.Qt.Key_Enter)

    # TODO: Figure out how to do this via a qtbot.mouseClick call
    # Select the first item in the list
    model = browser._listView.model()
    selectionModel = browser._listView.selectionModel()
    selectionModel.setCurrentIndex(model.index(0, 0), QtCore.QItemSelectionModel.ClearAndSelect)

    # Click the copy button
    qtbot.mouseClick(browser._copyButton, QtCore.Qt.LeftButton)

    assert "google" in clipboard.text()


def test_filter(qtbot, browser):
    """
    Ensure the filter UX works
    """
    initRowCount = browser._listView.model().rowCount()
    assert initRowCount > 0

    # Enter a search term
    qtbot.keyClicks(browser._lineEdit, 'google')

    # Press Enter to perform the filter
    qtbot.keyPress(browser._lineEdit, QtCore.Qt.Key_Enter)

    filteredRowCount = browser._listView.model().rowCount()
    assert initRowCount > filteredRowCount


if __name__ == "__main__":
    pytest.main()
