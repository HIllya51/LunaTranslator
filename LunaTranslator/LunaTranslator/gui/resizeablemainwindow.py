from PyQt5 import QtCore, QtWidgets


class SideGrip(QtWidgets.QWidget):
    def __init__(self, parent, edge):
        QtWidgets.QWidget.__init__(self, parent)
        if edge == QtCore.Qt.LeftEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == QtCore.Qt.TopEdge:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == QtCore.Qt.RightEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None


class Mainw(QtWidgets.QMainWindow):
    _gripSize = 8

    def __init__(self, x):
        QtWidgets.QMainWindow.__init__(self, x)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.sideGrips = [
            SideGrip(self, QtCore.Qt.LeftEdge),
            SideGrip(self, QtCore.Qt.TopEdge),
            SideGrip(self, QtCore.Qt.RightEdge),
            SideGrip(self, QtCore.Qt.BottomEdge),
        ]
        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QtWidgets.QSizeGrip(self) for i in range(4)]
        for s in self.cornerGrips:
            s.setStyleSheet(""" background-color: transparent;  """)

    @property
    def gripSize(self):
        return self._gripSize

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(
            self.gripSize, self.gripSize, -self.gripSize, -self.gripSize
        )

        # top left
        self.cornerGrips[0].setGeometry(
            QtCore.QRect(outRect.topLeft(), inRect.topLeft())
        )
        # top right
        self.cornerGrips[1].setGeometry(
            QtCore.QRect(outRect.topRight(), inRect.topRight()).normalized()
        )
        # bottom right
        self.cornerGrips[2].setGeometry(
            QtCore.QRect(inRect.bottomRight(), outRect.bottomRight())
        )
        # bottom left
        self.cornerGrips[3].setGeometry(
            QtCore.QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized()
        )

        # left edge
        self.sideGrips[0].setGeometry(0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(), inRect.top(), self.gripSize, inRect.height()
        )
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(), inRect.width(), self.gripSize
        )

    def resizeEvent(self, event):
        QtWidgets.QMainWindow.resizeEvent(self, event)
        self.updateGrips()


# app = QtWidgets.QApplication([])
# m = Mainw()
# m.show()
# m.resize(240, 160)
# app.exec_()
