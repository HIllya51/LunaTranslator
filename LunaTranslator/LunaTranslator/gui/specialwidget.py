from PyQt5.QtWidgets import QWidget, QSizePolicy, QListWidget, QScrollArea
from PyQt5.QtGui import QMouseEvent, QPainter, QPen, QFont, QFontMetrics
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QSpacerItem,
    QWidgetItem,
)
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QLayout
from traceback import print_exc


class chartwidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        font = QFont("Arial", 10)
        fmetrics = QFontMetrics(font)

        fhall = fmetrics.height()
        self.font = font

        self.ymargin = int(fhall) + 10  # 20
        self.valuewidth = 10
        self.xtext = lambda x: str(x)
        self.ytext = lambda y: str(y)
        self.fmetrics = fmetrics
        self.scalelinelen = 5

    def setdata(self, data):
        data = sorted(data, key=lambda _: _[0])
        self.data = data

    def paintEvent(self, event):
        if self.data is None or len(self.data) == 0:
            return
        try:
            if len(self.data) == 1:
                self.data.insert(0, (0, 0))
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            pen = QPen(Qt.blue)
            pen.setWidth(2)
            painter.setPen(pen)

            painter.setFont(self.font)

            ymargin = self.ymargin

            xmargin = 0

            max_y = int(max(y for _, y in self.data))
            y_labels = [self.ytext(i * max_y / 5) for i in range(6)]

            x_labels = [self.xtext(x) for x, _ in self.data]
            for l in y_labels:
                xmargin = max(xmargin, self.fmetrics.width(l))

            xmargin = xmargin + self.scalelinelen

            width = (
                self.width()
                - xmargin
                - max(
                    self.fmetrics.width(x_labels[-1]) // 2,
                    self.fmetrics.width(self.ytext(self.data[-1][1])) // 2,
                )
            )

            height = self.height() - 2 * ymargin

            # 纵坐标
            for i, label in enumerate(y_labels):
                y = int(ymargin + height - i * (height / 5))
                painter.drawLine(xmargin - self.scalelinelen, y, xmargin, y)
                painter.drawText(
                    xmargin - self.scalelinelen - self.fmetrics.width(label),
                    y + 5,
                    label,
                )

            painter.drawLine(xmargin, ymargin, xmargin, ymargin + height)  # Y轴
            painter.drawLine(
                xmargin, ymargin + height, xmargin + width, ymargin + height
            )  # X轴

            # 计算数据点在绘图区域中的坐标
            x_scale = width / (len(self.data) - 1)
            y_scale = height / max(max(y for _, y in self.data), 1)

            points = []
            for i, (x, y) in enumerate(self.data):
                x_coord = xmargin + i * x_scale
                y_coord = ymargin + height - y * y_scale
                points.append((int(x_coord), int(y_coord)))

            # 绘制折线
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                painter.drawLine(x1, y1, x2, y2)

                if self.data[i + 1][1]:  #!=0
                    text = self.ytext(self.data[i + 1][1])
                    painter.drawText(
                        x2 - self.fmetrics.width(text) // 2, y2 - 10, text
                    )  # value

            for i, (x, y) in enumerate(points):
                painter.drawLine(x, ymargin + height, x, ymargin + height + 5)  # 刻度线
                painter.drawText(
                    x - self.fmetrics.width(x_labels[i]) // 2,
                    ymargin + height + 20,
                    x_labels[i],
                )  # 标签
        except:
            print_exc()


class ScrollFlow(QWidget):
    bgclicked = pyqtSignal()

    def resizeEvent(self, a0) -> None:
        self.qscrollarea.resize(self.size())
        return super().resizeEvent(a0)

    def __init__(self):
        super(ScrollFlow, self).__init__()

        class _QListWidget(QListWidget):
            def mousePressEvent(_, _2) -> None:
                self.bgclicked.emit()

        self.listWidget = _QListWidget(self)
        # self.listWidget.setFixedWidth(600)

        self.l = FlowLayout()

        self.listWidget.setLayout(self.l)

        self.qscrollarea = QScrollArea(self)
        self.qscrollarea.setWidgetResizable(True)
        self.qscrollarea.setWidget(self.listWidget)

    def addwidget(self, wid):
        self.l.addWidget(wid)

    def insertwidget(self, idx, wid):
        self.l.insertWidget(idx, wid)

    def removeidx(self, index):
        _ = self.l.takeAt(index)
        _.widget().hide()

    def setfocus(self, idx):
        self.widget(idx).setFocus()

    def widget(self, idx):
        idx = min(idx, len(self.l._item_list) - 1)
        idx = max(idx, 0)
        return self.l._item_list[idx].widget()


class FlowLayout(QLayout):
    heightChanged = pyqtSignal(int)

    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

        self._item_list = []

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def insertWidget(self, idx, widget):
        item = QWidgetItem(widget)
        widget.setParent(self.parentWidget())
        widget.adjustSize()
        widget.setVisible(True)
        self._item_list.insert(idx, item)

        self._do_layout(self.geometry(), False)

    def addItem(self, item):  # pylint: disable=invalid-name
        self._item_list.append(item)

    def addSpacing(self, size):  # pylint: disable=invalid-name
        self.addItem(QSpacerItem(size, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):  # pylint: disable=invalid-name,no-self-use
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):  # pylint: disable=invalid-name,no-self-use
        return True

    def heightForWidth(self, width):  # pylint: disable=invalid-name
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):  # pylint: disable=invalid-name
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):  # pylint: disable=invalid-name
        return self.minimumSize()

    def minimumSize(self):  # pylint: disable=invalid-name
        size = QSize()

        for item in self._item_list:
            minsize = item.minimumSize()
            extent = item.geometry().bottomRight()
            size = size.expandedTo(QSize(minsize.width(), extent.y()))

        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _do_layout(self, rect, test_only=False):
        m = self.contentsMargins()
        effective_rect = rect.adjusted(+m.left(), +m.top(), -m.right(), -m.bottom())
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._item_list:
            wid = item.widget()

            space_x = self.spacing()
            space_y = self.spacing()
            if wid is not None:
                space_x += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
                )
                space_y += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
                )

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                sz = item.sizeHint()
                item.setGeometry(QRect(QPoint(x, y), sz))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        new_height = y + line_height - rect.y()
        self.heightChanged.emit(new_height)
        return new_height
