"""ExMessageBox —— WinUI3 ContentDialog 样式消息框
（ExWidgets/dialogs/exmessagebox.cpp 的移植）。

无边框圆角卡片 + 父窗口遮罩(Smoke) + 分层阴影；标题/正文/按钮布局与 C++ 版一致。
仅依赖 qtsymbols —— 可能在加载 C++ 环境之前被调用，不能引入复杂依赖。
"""

try:
    from PyQt5 import sip
except ImportError:
    from PyQt6 import sip

from qtsymbols import (
    QApplication,
    QCheckBox,
    QEvent,
    QColor,
    QDialog,
    QDialogButtonBox,
    QFont,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QPoint,
    QPushButton,
    QRect,
    QRectF,
    Qt,
    QVBoxLayout,
    QWidget,
)

# ---- WinUI 3 ContentDialog 设计常量 ----
_CORNER_RADIUS = 8
_PADDING = 16
_TITLE_CONTENT_GAP = 12
_CONTENT_BUTTON_GAP = 16
_BUTTON_SPACING = 8
_BUTTON_MARGIN_V = 12
_BUTTON_MIN_WIDTH = 120
_TITLE_FONT_PX = 20
_BODY_FONT_PX = 14
_INFORMATIVE_FONT_PX = 13
_SHADOW_MARGIN = 8

_DIALOG_MIN_WIDTH = 320
_DIALOG_MAX_WIDTH = 548


def _is_dark():
    return QApplication.palette().color(QPalette.Window).lightness() < 128


def _dialog_border_color(dark):
    return QColor(255, 255, 255, 20) if dark else QColor(0, 0, 0, 15)


class ExMessageBox(QMessageBox):
    """使用 QMessageBox 模仿 WinUI3 的 ContentDialog 样式。"""

    def __init__(self, *args):
        if len(args) <= 1:
            # ExMessageBox(parent)
            QMessageBox.__init__(self, args[0] if args else None)
        else:
            # ExMessageBox(icon, title, text, buttons, parent)
            icon, title, text = args[0], args[1], args[2]
            buttons = (
                args[3] if len(args) > 3 else QMessageBox.StandardButton.NoButton
            )
            parent = args[4] if len(args) > 4 else None
            QMessageBox.__init__(self, icon, title, text, buttons, parent)
        self._card = None
        self._overlay = None
        self._overlayparent = None
        self._buttonarea = None
        self._customcontent = None
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    # ---- 自定义内容 ----
    def setContentWidget(self, widget):
        self._customcontent = widget

    # ---- 布局重构（同 C++ resetLayout） ----
    def _resetlayout(self):
        iconlabel = self.findChild(QLabel, "qt_msgboxex_icon_label")
        textlabel = self.findChild(QLabel, "qt_msgbox_label")
        infolabel = self.findChild(QLabel, "qt_msgbox_informativelabel")
        buttonbox = self.findChild(QDialogButtonBox, "qt_msgbox_buttonbox")
        if textlabel is None or buttonbox is None:
            return
        if self._card is not None:
            return

        # 删掉 QMessageBox 原布局（同 C++ delete q->layout()：仅删布局、不动控件；
        # 不能用 QWidget().setLayout(oldlay) —— 那会把子控件一并过继给临时控件再被 GC）
        oldlay = self.layout()
        if oldlay is not None:
            sip.delete(oldlay)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN, _SHADOW_MARGIN
        )
        outer.setSpacing(0)
        card = QWidget(self)
        card.setObjectName("FluentMessageBoxCard")
        outer.addWidget(card)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(_PADDING, _PADDING, _PADDING, 0)
        inner.setSpacing(0)

        if not self.windowTitle():
            self.setWindowTitle(QApplication.applicationName())
        titlelabel = QLabel(self.windowTitle(), card)
        titlelabel.setObjectName("FluentMessageBoxTitle")
        titlelabel.setWordWrap(True)
        titlefont = titlelabel.font()
        titlefont.setPixelSize(_TITLE_FONT_PX)
        titlefont.setWeight(QFont.DemiBold)
        titlelabel.setFont(titlefont)
        inner.addWidget(titlelabel)
        inner.addSpacing(_TITLE_CONTENT_GAP)

        textfont = textlabel.font()
        textfont.setPixelSize(_BODY_FONT_PX)
        textlabel.setFont(textfont)
        textlabel.setWordWrap(True)

        hasicon = False
        if iconlabel is not None:
            pix = iconlabel.pixmap()
            hasicon = pix is not None and not pix.isNull()
        if hasicon:
            contentrow = QHBoxLayout()
            contentrow.setSpacing(12)
            contentrow.addWidget(iconlabel, 0, Qt.AlignmentFlag.AlignVCenter)
            contentrow.addWidget(textlabel, 1)
            inner.addLayout(contentrow)
        else:
            inner.addWidget(textlabel)
            if iconlabel is not None:
                iconlabel.hide()
        if iconlabel is not None:
            iconlabel.setParent(card)
        textlabel.setParent(card)

        if infolabel is not None:
            infofont = infolabel.font()
            infofont.setPixelSize(_INFORMATIVE_FONT_PX)
            infolabel.setFont(infofont)
            infolabel.setContentsMargins(0, 7, 0, 0)
            infolabel.setParent(card)
            inner.addWidget(infolabel)

        for checkbox in self.findChildren(QCheckBox):
            checkbox.setContentsMargins(0, 7, 0, 0)
            checkbox.setParent(card)
            inner.addWidget(checkbox)
            break

        if self._customcontent is not None:
            self._customcontent.setParent(card)
            inner.addWidget(self._customcontent)

        inner.addSpacing(_CONTENT_BUTTON_GAP)

        buttonarea = QHBoxLayout()
        buttonarea.setSpacing(_BUTTON_SPACING)
        buttonarea.setContentsMargins(0, _BUTTON_MARGIN_V, 0, _BUTTON_MARGIN_V)
        buttonarea.addStretch()
        buttonbox.setParent(card)
        for pb in buttonbox.buttons():
            if isinstance(pb, QPushButton):
                pb.setDefault(False)
                pb.setMinimumWidth(_BUTTON_MIN_WIDTH)
        # QDialogButtonBox 内部布局不居中，取出按钮强制布局
        if buttonbox.layout() is not None:
            boxlayout = buttonbox.layout()
            while True:
                item = boxlayout.takeAt(0)
                if item is None:
                    break
                w = item.widget()
                if w is not None:
                    buttonarea.addWidget(w, 0, Qt.AlignmentFlag.AlignVCenter)
        buttonarea.addStretch()
        buttonbox.hide()
        inner.addLayout(buttonarea)

        self._card = card
        self._buttonarea = buttonarea
        self.setMinimumWidth(_DIALOG_MIN_WIDTH + 2 * _SHADOW_MARGIN)
        self.setMaximumWidth(_DIALOG_MAX_WIDTH + 2 * _SHADOW_MARGIN)

    # ---- 遮罩 ----
    def _showoverlay(self):
        top = self.parentWidget()
        if top is None:
            top = QApplication.activeWindow()
        if top is None:
            return
        while top.parentWidget() is not None:
            top = top.parentWidget()
        if self._overlay is None:
            self._overlay = QWidget(top)
            self._overlay.setObjectName("ExMessageBoxOverlay")
            self._overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            # WinUI 3 SmokeFillColorDefault: #4D000000
            self._overlay.setStyleSheet("background-color: rgba(0, 0, 0, 77);")
            self._overlayparent = top
            top.installEventFilter(self)
        self._overlay.setGeometry(top.rect())
        self._overlay.show()
        self._overlay.raise_()

    def _hideoverlay(self):
        if self._overlay is not None:
            if self._overlayparent is not None:
                self._overlayparent.removeEventFilter(self)
                self._overlayparent = None
            self._overlay.hide()
            self._overlay.deleteLater()
            self._overlay = None

    # ---- 对话框行为 ----
    def exec(self):
        self._showoverlay()
        result = QDialog.exec(self)
        self._hideoverlay()
        return result

    def setVisible(self, visible):
        if visible:
            self._resetlayout()
            self._showoverlay()
        else:
            self._hideoverlay()
        QMessageBox.setVisible(self, visible)

    def paintEvent(self, _):
        if self._card is None or self._buttonarea is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cardrect = QRect(self.rect()).adjusted(
            _SHADOW_MARGIN, _SHADOW_MARGIN, -_SHADOW_MARGIN, -_SHADOW_MARGIN
        )
        dark = _is_dark()

        # 分层阴影
        painter.setPen(Qt.PenStyle.NoPen)
        layers = 4
        for i in range(layers, 0, -1):
            expand = i * 1.5
            alpha = (6 + (layers - i) * 4) if dark else (3 + (layers - i) * 2)
            sr = QRectF(cardrect).adjusted(-expand, -expand + 1, expand, expand + 1)
            sp = QPainterPath()
            sp.addRoundedRect(sr, _CORNER_RADIUS + expand, _CORNER_RADIUS + expand)
            painter.setBrush(QColor(0, 0, 0, alpha))
            painter.drawPath(sp)

        # 卡片底色：按钮区上方 base/白，下方 window（同 C++）
        path = QPainterPath()
        path.addRoundedRect(QRectF(cardrect), _CORNER_RADIUS, _CORNER_RADIUS)
        painter.setClipPath(path)
        mapped = self._buttonarea.geometry().translated(
            self._card.mapTo(self, QPoint(0, 0))
        )
        splity = mapped.top()
        toparea = QRect(cardrect)
        toparea.setBottom(splity)
        painter.fillRect(
            toparea,
            self.palette().color(QPalette.Base) if dark else QColor(Qt.GlobalColor.white),
        )
        bottomarea = QRect(cardrect)
        bottomarea.setTop(splity)
        painter.fillRect(bottomarea, self.palette().color(QPalette.Window))
        painter.setClipping(False)
        painter.setPen(QPen(_dialog_border_color(dark), 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            QRectF(cardrect).adjusted(0.5, 0.5, -0.5, -0.5),
            _CORNER_RADIUS,
            _CORNER_RADIUS,
        )

    def showEvent(self, event):
        # 拦截 QMessageBox 的 showEvent，避免其强制触发内部的 updateSize()
        QDialog.showEvent(self, event)

    def resizeEvent(self, event):
        QDialog.resizeEvent(self, event)

    def event(self, e):
        # 拦截 QMessageBox 的 event，避免其在 LayoutRequest 时强制触发 updateSize()
        if e.type() == QEvent.LayoutRequest:
            return QDialog.event(self, e)
        return QMessageBox.event(self, e)

    def eventFilter(self, watched, event):
        if self._overlay is not None and event.type() == QEvent.Resize:
            self._overlay.setGeometry(watched.rect())
        return QMessageBox.eventFilter(self, watched, event)

    # ---- 静态便捷接口（与 QMessageBox 同名同参） ----
    @staticmethod
    def information(parent, title, text, buttons=None, defaultButton=None):
        box = ExMessageBox(
            QMessageBox.Icon.Information, title, text,
            buttons if buttons is not None else QMessageBox.StandardButton.Ok,
            parent,
        )
        if defaultButton is not None:
            box.setDefaultButton(defaultButton)
        return QMessageBox.StandardButton(box.exec())

    @staticmethod
    def warning(parent, title, text, buttons=None, defaultButton=None):
        box = ExMessageBox(
            QMessageBox.Icon.Warning, title, text,
            buttons if buttons is not None else QMessageBox.StandardButton.Ok,
            parent,
        )
        if defaultButton is not None:
            box.setDefaultButton(defaultButton)
        return QMessageBox.StandardButton(box.exec())

    @staticmethod
    def critical(parent, title, text, buttons=None, defaultButton=None):
        box = ExMessageBox(
            QMessageBox.Icon.Critical, title, text,
            buttons if buttons is not None else QMessageBox.StandardButton.Ok,
            parent,
        )
        if defaultButton is not None:
            box.setDefaultButton(defaultButton)
        return QMessageBox.StandardButton(box.exec())

    @staticmethod
    def question(parent, title, text, buttons=None, defaultButton=None):
        box = ExMessageBox(
            QMessageBox.Icon.Question, title, text,
            buttons
            if buttons is not None
            else (
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ),
            parent,
        )
        if defaultButton is not None:
            box.setDefaultButton(defaultButton)
        return QMessageBox.StandardButton(box.exec())

