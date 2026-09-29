"""FluentColorPicker —— WinUI3 CommunityToolkit ColorPicker 的移植。

移植自 FluentUIStyle/ExWidgets/color/{excolorpicker,colorgradientslider,
excolorpickerdialog}.cpp（仅 Box 色域形态）：
- 顶部当前色预览条（棋盘格底 + 当前色）
- 分段页签：光谱（Hue×Saturation 色域 + 明度滑条 + Alpha 滑条）、
  色板（Fluent 标准色）、滑条（RGB/HSV + Hex + 通道滑条）
- FluentColorDialog：标题 + 取色器 + 确定/取消 的对话框封装

渐变图全部用 QPainter 渐变生成（hue 色带的 6 段基色 RGB 线性插值与
HSV 色带一致，避免逐像素 Python 循环）。
"""

from qtsymbols import (
    Qt,
    QSize,
    QRectF,
    QPointF,
    QSizePolicy,
    QFont,
    pyqtSignal,
    QColor,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QWidget,
    QSlider,
    QDialog,
    QTabBar,
    QStackedWidget,
    QComboBox,
    QLineEdit,
    QSpinBox,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QRegularExpressionValidator,
    QRegularExpression,
    QStyle,
    QPoint,
    QToolButton,
    QBrush,
)

from PyQt5.QtWidgets import QStyleOptionSlider, QStyleOptionToolButton
from PyQt5.QtGui import QLinearGradient

from gui.dynalang import LLabel, LPushButton, LDialog
from gui.fluent.tabwidget import apply_segmented_tabbar_style
from gui.fluent.expander import _exp_card_background, _exp_card_border

# Segoe Fluent Icons：ChevronDown（ColorPickerButton 右端箭头）
_ICON_CHEVRON_DOWN = ""
_FLYOUT_WIDTH = 360
_CORNER_RADIUS = 8

# ---- 常量（同 excolorpicker.cpp 匿名命名空间）----
_CHANNEL_THICKNESS = 24
_ALPHA_THICKNESS = 22
_SHADE_STRIP_HEIGHT = 28
_SPECTRUM_HEIGHT = 240
_PALETTE_COLUMNS = 8
_CHECKER_SIZE = 4
_CHECKER_COLOR = QColor(0x19, 0x80, 0x80, 0x80)

# Segoe Fluent Icons 码点：InkingTool / Color / Equalizer
_ICON_SPECTRUM = ""
_ICON_PALETTE = ""
_ICON_SLIDERS = ""


def _paint_checkerboard(painter, rect):
    y = rect.top()
    while y < rect.bottom():
        x = rect.left()
        while x < rect.right():
            if ((x // _CHECKER_SIZE) + (y // _CHECKER_SIZE)) % 2:
                painter.fillRect(x, y, _CHECKER_SIZE, _CHECKER_SIZE, _CHECKER_COLOR)
            x += _CHECKER_SIZE
        y += _CHECKER_SIZE


def _fluent_palette_colors():
    """Fluent 标准色板（对齐 WinUI3 FluentColorPalette）。"""
    table = (
        (0xFFB900, 0xD13438, 0xE3008C, 0x8E8CD8, 0x0099BC, 0x00CC6A, 0x567C73, 0x69797E),
        (0xFF8C00, 0xFF4343, 0xBF0077, 0x6B69D6, 0x2D7D9A, 0x10893E, 0x486860, 0x4A5459),
        (0xF7630C, 0xE74856, 0xC239B3, 0x8764B8, 0x00B7C3, 0x7A7574, 0x498205, 0x647C64),
        (0xCA5010, 0xE81123, 0x9A0089, 0x744DA9, 0x038387, 0x5D5A58, 0x107C10, 0x525E54),
        (0xDA3B01, 0xEA005E, 0x0078D4, 0xB146C2, 0x00B294, 0x68768A, 0x767676, 0x847545),
        (0xEF6950, 0xC30052, 0x0063B1, 0x881798, 0x018574, 0x515C6B, 0x4C4A48, 0x7E735F),
    )
    return [QColor.fromRgb(rgb) for row in table for rgb in row]


# ============================================================================
# 渐变图生成（对齐 WinUI3 ColorPickerRenderingHelpers，QPainter 渐变实现）
# ============================================================================


def _build_hue_saturation_image(width, height):
    image = QImage(max(1, width), max(1, height), QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    p = QPainter(image)
    hue = QLinearGradient(0, 0, width, 0)
    for i in range(7):
        hue.setColorAt(i / 6.0, QColor.fromHsvF((i % 6) / 6.0, 1.0, 1.0))
    p.fillRect(image.rect(), hue)
    # 纵向向白渐隐 = 饱和度 1→0
    fade = QLinearGradient(0, 0, 0, height)
    fade.setColorAt(0.0, QColor(255, 255, 255, 0))
    fade.setColorAt(1.0, QColor(255, 255, 255, 255))
    p.fillRect(image.rect(), fade)
    p.end()
    return image


def _build_third_dimension_image(hue, saturation, width, height):
    image = QImage(max(1, width), max(1, height), QImage.Format_RGB32)
    p = QPainter(image)
    grad = QLinearGradient(0, 0, 0, height)
    grad.setColorAt(0.0, QColor.fromHsvF(hue, saturation, 1.0))
    grad.setColorAt(1.0, QColor(0, 0, 0))
    p.fillRect(image.rect(), grad)
    p.end()
    return image


def _build_channel_image(width, height, channel, base):
    """RGB 通道横向渐变（channel 0/1/2 = R/G/B，其余通道取 base）。"""
    image = QImage(max(1, width), max(1, height), QImage.Format_RGB32)
    p = QPainter(image)
    lo, hi = QColor(base), QColor(base)
    if channel == 0:
        lo.setRed(0)
        hi.setRed(255)
    elif channel == 1:
        lo.setGreen(0)
        hi.setGreen(255)
    else:
        lo.setBlue(0)
        hi.setBlue(255)
    grad = QLinearGradient(0, 0, width, 0)
    grad.setColorAt(0.0, lo)
    grad.setColorAt(1.0, hi)
    p.fillRect(image.rect(), grad)
    p.end()
    return image


def _build_hsv_channel_image(width, height, channel, h, s, v):
    image = QImage(max(1, width), max(1, height), QImage.Format_RGB32)
    p = QPainter(image)
    grad = QLinearGradient(0, 0, width, 0)
    if channel == 0:  # H：色带
        for i in range(7):
            grad.setColorAt(i / 6.0, QColor.fromHsvF((i % 6) / 6.0, s, v))
    elif channel == 1:  # S：去饱和→全饱和
        grad.setColorAt(0.0, QColor.fromHsvF(h, 0.0, v))
        grad.setColorAt(1.0, QColor.fromHsvF(h, 1.0, v))
    else:  # V：明度→黑
        grad.setColorAt(0.0, QColor.fromHsvF(h, s, v))
        grad.setColorAt(1.0, QColor(0, 0, 0))
    p.fillRect(image.rect(), grad)
    p.end()
    return image


def _build_alpha_channel_image(width, height, base, horizontal=True):
    image = QImage(max(1, width), max(1, height), QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    p = QPainter(image)
    _paint_checkerboard(p, image.rect())
    r, g, b = base.red(), base.green(), base.blue()
    grad = (QLinearGradient(0, 0, width, 0) if horizontal
            else QLinearGradient(0, 0, 0, height))
    if horizontal:
        grad.setColorAt(0.0, QColor(r, g, b, 0))
        grad.setColorAt(1.0, QColor(r, g, b, 255))
    else:
        grad.setColorAt(0.0, QColor(r, g, b, 255))
        grad.setColorAt(1.0, QColor(r, g, b, 0))
    p.fillRect(image.rect(), grad)
    p.end()
    return image


# ============================================================================
# 渐变滑条（colorgradientslider.cpp 移植：自绘 groove 渐变 + 样式画手柄）
# ============================================================================


class _GradientSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setRange(0, 255)
        self._builder = None
        self._cached = QImage()

    def set_image_builder(self, builder):
        self._builder = builder
        self._cached = QImage()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        opt = QStyleOptionSlider()
        opt.initFrom(self)
        opt.orientation = self.orientation()
        opt.minimum = self.minimum()
        opt.maximum = self.maximum()
        opt.sliderPosition = self.sliderPosition()
        opt.sliderValue = self.value()
        opt.singleStep = self.singleStep()
        opt.pageStep = self.pageStep()
        opt.upsideDown = (self.invertedAppearance()
                          != (self.orientation() == Qt.Vertical))

        groove = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        if groove.isEmpty():
            super().paintEvent(event)
            return

        thickness = 10.0
        if self.orientation() == Qt.Horizontal:
            gr = QRectF(groove.left() + 2, groove.center().y() - thickness / 2,
                        groove.width() - 4, thickness)
        else:
            gr = QRectF(groove.center().x() - thickness / 2, groove.top() + 2,
                        thickness, groove.height() - 4)
        if gr.isEmpty():
            super().paintEvent(event)
            return

        if self._builder is not None:
            if self._cached.isNull() or self._cached.size() != gr.size().toSize():
                self._cached = self._builder(gr.size().toSize())
            p.save()
            path = QPainterPath()
            path.addRoundedRect(gr, thickness / 2, thickness / 2)
            p.setClipPath(path)
            p.drawImage(gr.topLeft(), self._cached)
            p.restore()

        opt.subControls = QStyle.SC_SliderHandle
        self.style().drawComplexControl(QStyle.CC_Slider, opt, p, self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._cached = QImage()


# ============================================================================
# 当前色预览条（AccentShadeStripWidget 移植）
# ============================================================================


class _ShadeStrip(QWidget):
    colorActivated = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(_SHADE_STRIP_HEIGHT)
        self._color = QColor()

    def set_color(self, color):
        if self._color == color:
            return
        self._color = QColor(color)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cell = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(cell, 4, 4)
        p.setClipPath(path)
        _paint_checkerboard(p, self.rect())
        p.setPen(Qt.NoPen)
        p.setBrush(self._color)
        p.drawRoundedRect(cell, 4, 4)

    def mousePressEvent(self, _):
        self.colorActivated.emit(QColor(self._color))


# ============================================================================
# Hue×Saturation 色域（Box 形态）
# ============================================================================


class _HueSatMap(QWidget):
    hueSaturationChanged = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(_SPECTRUM_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._hue = 0.0
        self._sat = 1.0
        self._image = QImage()
        self._dragging = False

    def hue(self):
        return self._hue

    def saturation(self):
        return self._sat

    def set_hue_saturation(self, hue, saturation):
        hue = max(0.0, min(1.0, hue))
        saturation = max(0.0, min(1.0, saturation))
        if abs(self._hue - hue) < 1e-6 and abs(self._sat - saturation) < 1e-6:
            return
        self._hue = hue
        self._sat = saturation
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        if self._image.isNull() or self._image.size() != r.size():
            self._image = _build_hue_saturation_image(r.width(), r.height())
        path = QPainterPath()
        path.addRoundedRect(QRectF(r), 6, 6)
        p.setClipPath(path)
        p.drawImage(r, self._image)
        p.setPen(QPen(self.palette().color(QPalette_Mid), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(r), 6, 6)
        marker = self._marker_position(r)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(Qt.black, 1))
        p.drawEllipse(marker, 8, 8)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._image = QImage()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        self._dragging = True
        self.grabMouse()
        self._update_from_pos(event.pos())

    def mouseMoveEvent(self, event):
        if not self._dragging or not (event.buttons() & Qt.LeftButton):
            return
        self._update_from_pos(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton or not self._dragging:
            return
        self._dragging = False
        if self.mouseGrabber() is self:
            self.releaseMouse()

    def _marker_position(self, area):
        return QPointF(area.left() + self._hue * area.width(),
                       area.top() + (1.0 - self._sat) * area.height())

    def _update_from_pos(self, pos):
        area = self.rect().adjusted(0, 0, -1, -1)
        hue = max(0.0, min(1.0, (pos.x() - area.left()) / max(1.0, area.width())))
        sat = max(0.0, min(1.0, 1.0 - (pos.y() - area.top()) / max(1.0, area.height())))
        if abs(self._hue - hue) < 1e-6 and abs(self._sat - sat) < 1e-6:
            return
        self._hue = hue
        self._sat = sat
        self.update()
        self.hueSaturationChanged.emit(self._hue, self._sat)


# ============================================================================
# 色板网格（PaletteWidget 移植）
# ============================================================================


class _PaletteGrid(QWidget):
    colorSelected = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._colors = []
        self._selected = QColor()

    def set_colors(self, colors):
        self._colors = list(colors)
        self.update()

    def set_selected_color(self, color):
        self._selected = QColor(color)
        self.update()

    def paintEvent(self, _):
        if not self._colors:
            return
        rects = self._build_rects(self.rect())
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for i, cell in enumerate(rects):
            if i >= len(self._colors):
                break
            p.setPen(Qt.NoPen)
            p.setBrush(self._colors[i])
            selected = self._colors[i] == self._selected
            p.drawRoundedRect(QRectF(cell), 2 if selected else 3, 2 if selected else 3)
            if selected:
                p.setPen(QPen(self.palette().color(QPalette_Highlight), 2))
                p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(QRectF(cell).adjusted(1, 1, -1, -1), 1, 1)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or not self._colors:
            return
        for i, cell in enumerate(self._build_rects(self.rect())):
            if cell.contains(event.pos()):
                self._selected = self._colors[i]
                self.update()
                self.colorSelected.emit(QColor(self._selected))
                break

    def _build_rects(self, area):
        if not self._colors or area.width() <= 0 or area.height() <= 0:
            return []
        cols = min(_PALETTE_COLUMNS, len(self._colors))
        rows = (len(self._colors) + cols - 1) // cols
        gap = 3
        cell = max(1, min((area.width() - (cols - 1) * gap) // cols,
                          (area.height() - (rows - 1) * gap) // rows))
        rects = []
        for i in range(len(self._colors)):
            rects.append(QRectF(area.left() + (i % cols) * (cell + gap),
                                area.top() + (i // cols) * (cell + gap),
                                cell, cell))
        return rects


# 调色板角色（qtsymbols 未导出 QPalette，经 QColor/pen 取色时按明暗取灰）
from qtsymbols import QPalette  # noqa: E402

QPalette_Mid = QPalette.ColorRole.Mid if not hasattr(QPalette, "Mid") else QPalette.Mid
QPalette_Highlight = (QPalette.ColorRole.Highlight if not hasattr(QPalette, "Highlight")
                      else QPalette.Highlight)


# ============================================================================
# 取色器本体
# ============================================================================


class FluentColorPicker(QWidget):
    """WinUI3 CommunityToolkit ColorPicker（嵌入形态）。"""

    colorChanged = pyqtSignal(QColor)

    _RGBA, _HSVA = 0, 1

    def __init__(self, parent=None, popup=False):
        super().__init__(parent)
        self._color = QColor(0x94, 0x4E, 0x9B)
        self._alpha_enabled = True
        self._representation = FluentColorPicker._RGBA
        self._updating = False
        self._popup_mode = popup
        self._h, self._s, self._v, self._a = self._color.getHsvF()

        if popup:
            # 飞层形态（ColorPickerButton 弹出）：无边框弹层 + 自绘圆角卡
            self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setFixedWidth(_FLYOUT_WIDTH)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10) if popup else root.setContentsMargins(12, 8, 12, 12)
        root.setSpacing(8)

        # 当前色预览条
        self._shade = _ShadeStrip()
        root.addWidget(self._shade)

        # 分段页签（图标 + tooltip）
        self._tabbar = QTabBar(self)
        self._tabbar.setAttribute(Qt.WA_StyledBackground, True)
        self._tabbar.setDrawBase(False)
        apply_segmented_tabbar_style(self._tabbar)
        # 同 gallery 取色器：页签扩展三等分铺满整行
        # （apply_segmented_tabbar_style 默认紧凑排布，其他场景用）
        self._tabbar.setExpanding(True)
        iconfont = QFont("Segoe Fluent Icons")
        iconfont.setPixelSize(14)
        self._tabbar.setFont(iconfont)
        from myutils.config import _TR
        for glyph, tip in ((_ICON_SPECTRUM, "光谱"), (_ICON_PALETTE, "色板"),
                           (_ICON_SLIDERS, "滑条")):
            self._tabbar.addTab(glyph)
            self._tabbar.setTabToolTip(self._tabbar.count() - 1, _TR(tip))
        root.addWidget(self._tabbar)

        self._stack = QStackedWidget(self)
        root.addWidget(self._stack, 1)

        self._setup_spectrum_page()
        self._setup_palette_page()
        self._setup_sliders_page()
        self._setup_connections()
        self._apply_color(self._color, False, True)
        self._tabbar.setCurrentIndex(0)
        self._stack.setCurrentIndex(0)

    # ---- UI ----
    def _setup_spectrum_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 5, 0, 0)
        lay.setSpacing(6)
        row = QHBoxLayout()
        row.setSpacing(8)
        self._third = _GradientSlider(Qt.Vertical)
        self._third.setFixedWidth(_CHANNEL_THICKNESS)
        self._map = _HueSatMap()
        self._specalpha = _GradientSlider(Qt.Vertical)
        self._specalpha.setFixedWidth(_CHANNEL_THICKNESS)
        row.addWidget(self._third)
        row.addWidget(self._map, 1)
        row.addWidget(self._specalpha)
        lay.addLayout(row)
        self._stack.addWidget(page)

    def _setup_palette_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        self._palette = _PaletteGrid()
        self._palette.set_colors(_fluent_palette_colors())
        lay.addWidget(self._palette, 1)
        self._stack.addWidget(page)

    def _add_channel_row(self, page, lay, label, height):
        row = QHBoxLayout()
        row.setSpacing(6)
        labelw = QLabel(label, page)
        labelw.setFixedWidth(16)
        labelw.setAlignment(Qt.AlignCenter)
        row.addWidget(labelw)
        spin = QSpinBox(page)
        spin.setRange(0, 255)
        spin.setFixedWidth(56)
        spin.setButtonSymbols(QSpinBox.NoButtons)
        row.addWidget(spin)
        slider = _GradientSlider(Qt.Horizontal, page)
        slider.setFixedHeight(height)
        row.addWidget(slider, 1)
        lay.addLayout(row)
        return labelw, spin, slider

    def _setup_sliders_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        header = QHBoxLayout()
        self._repcombo = QComboBox(page)
        self._repcombo.addItem("RGB", FluentColorPicker._RGBA)
        self._repcombo.addItem("HSV", FluentColorPicker._HSVA)
        self._repcombo.setCurrentIndex(0)
        self._repcombo.setFixedWidth(80)
        header.addWidget(self._repcombo)
        self._hexedit = QLineEdit(page)
        self._hexedit.setPlaceholderText("944E9B")
        self._hexedit.setMaxLength(8)
        self._hexedit.setValidator(QRegularExpressionValidator(
            QRegularExpression("[0-9A-Fa-f]{6,8}"), self._hexedit))
        header.addWidget(self._hexedit, 1)
        lay.addLayout(header)

        self._labels, self._spins, self._sliders = [], [], []
        for text, height in (("R", _CHANNEL_THICKNESS), ("G", _CHANNEL_THICKNESS),
                             ("B", _CHANNEL_THICKNESS), ("A", _ALPHA_THICKNESS)):
            labelw, spin, slider = self._add_channel_row(page, lay, text, height)
            self._labels.append(labelw)
            self._spins.append(spin)
            self._sliders.append(slider)
        lay.addStretch()
        self._stack.addWidget(page)

    # ---- 连接 ----
    def _setup_connections(self):
        self._shade.colorActivated.connect(self._on_shade)
        self._tabbar.currentChanged.connect(self._stack.setCurrentIndex)
        self._map.hueSaturationChanged.connect(lambda *_: self._update_from_spectrum())
        self._third.valueChanged.connect(lambda _: self._update_from_spectrum())
        self._specalpha.valueChanged.connect(self._update_alpha)
        self._palette.colorSelected.connect(self._on_palette)

        for i in range(3):
            self._spins[i].valueChanged.connect(lambda _: self._update_from_rgb())
        for i in range(3):
            self._sliders[i].valueChanged.connect(self._make_slider_sync(i))
        self._spins[3].valueChanged.connect(self._update_alpha)
        self._sliders[3].valueChanged.connect(self._make_slider_sync(3))
        self._hexedit.editingFinished.connect(self._on_hex)
        self._repcombo.currentIndexChanged.connect(self._on_rep_changed)

    def _make_slider_sync(self, index):
        def __(value):
            if self._updating:
                return
            self._spins[index].setValue(value)
        return __

    # ---- 公共 API ----
    def paintEvent(self, event):
        if not self._popup_mode:
            super().paintEvent(event)
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        bounds = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(bounds, _CORNER_RADIUS, _CORNER_RADIUS)
        p.fillPath(path, _exp_card_background(self.palette()))
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(_exp_card_border(self.palette()), 1))
        p.drawPath(path)

    def isPopupMode(self):
        return self._popup_mode

    def showPopup(self, anchor):
        """在 anchor（颜色按钮）上方弹出飞层。"""
        if not self._popup_mode or anchor is None:
            return
        self.adjustSize()
        topleft = anchor.mapToGlobal(QPoint(0, 0))
        self.move(topleft.x() - 6, topleft.y() - self.height())
        self.show()
        self.raise_()
        self.activateWindow()

    def color(self):
        c = QColor(self._color.toRgb())
        if not self._alpha_enabled:
            c.setAlpha(255)
        return c

    def setColor(self, color):
        if not color.isValid():
            return
        self._apply_color(color, True, True)

    def isAlphaEnabled(self):
        return self._alpha_enabled

    def setAlphaEnabled(self, enabled):
        if self._alpha_enabled == enabled:
            return
        self._alpha_enabled = enabled
        self._specalpha.setVisible(enabled)
        self._labels[3].setVisible(enabled)
        self._spins[3].setVisible(enabled)
        self._sliders[3].setVisible(enabled)
        if not enabled and self._color.alpha() != 255:
            self._color.setAlpha(255)
            self._a = 1.0
        self._apply_color(self._color, True, True)

    # ---- 内部同步 ----
    def _on_shade(self, color):
        self._apply_color(color, True, True)

    def _on_palette(self, color):
        self._apply_color(color, True, True)

    def _on_hex(self):
        from myutils.config import _TR  # noqa: F401
        digits = self._hexedit.text().strip()
        if digits.startswith("#"):
            digits = digits[1:]
        parsed = QColor()
        if len(digits) == 8:
            try:
                parsed = QColor.fromRgba(int(digits, 16))
            except ValueError:
                pass
        elif len(digits) == 6:
            parsed = QColor("#" + digits)
        if parsed.isValid():
            self._apply_color(parsed, True, True)

    def _on_rep_changed(self, idx):
        self._representation = self._repcombo.itemData(idx)
        self._sync_rgb()

    def _hex_text(self):
        if self._alpha_enabled:
            return self._color.name(QColor.HexArgb)[1:].upper()
        return self._color.name(QColor.HexRgb).upper()

    def _sync_spectrum(self):
        self._map.set_hue_saturation(self._h, self._s)
        self._third.set_image_builder(
            lambda sz: _build_third_dimension_image(self._h, self._s, sz.width(), sz.height()))
        self._third.blockSignals(True)
        self._third.setValue(round(self._v * 255))
        self._third.blockSignals(False)
        self._specalpha.set_image_builder(
            lambda sz: _build_alpha_channel_image(
                sz.width(), sz.height(),
                QColor.fromHsvF(self._h, self._s, self._v, 1.0), False))
        self._specalpha.blockSignals(True)
        self._specalpha.setValue(round(self._a * 255))
        self._specalpha.blockSignals(False)

    def _sync_rgb(self):
        if not self._spins:
            return
        is_hsv = self._representation == FluentColorPicker._HSVA
        for w in self._spins + self._sliders:
            w.blockSignals(True)
        try:
            if is_hsv:
                names = ("H", "S", "V")
                ranges = ((0, 359), (0, 100), (0, 100))
                values = (round(self._h * 359), round(self._s * 100), round(self._v * 100))
            else:
                names = ("R", "G", "B")
                ranges = ((0, 255), (0, 255), (0, 255))
                values = (self._color.red(), self._color.green(), self._color.blue())
            for i in range(3):
                self._labels[i].setText(names[i])
                self._spins[i].setRange(*ranges[i])
                self._sliders[i].setRange(*ranges[i])
                self._spins[i].setValue(values[i])
                self._sliders[i].setValue(values[i])
            if is_hsv:
                builders = (
                    lambda sz: _build_hsv_channel_image(sz.width(), sz.height(), 0, self._h, self._s, self._v),
                    lambda sz: _build_hsv_channel_image(sz.width(), sz.height(), 1, self._h, self._s, self._v),
                    lambda sz: _build_hsv_channel_image(sz.width(), sz.height(), 2, self._h, self._s, self._v),
                )
            else:
                builders = (
                    lambda sz: _build_channel_image(sz.width(), sz.height(), 0, QColor(0, self._color.green(), self._color.blue())),
                    lambda sz: _build_channel_image(sz.width(), sz.height(), 1, QColor(self._color.red(), 0, self._color.blue())),
                    lambda sz: _build_channel_image(sz.width(), sz.height(), 2, QColor(self._color.red(), self._color.green(), 0)),
                )
            for i in range(3):
                self._sliders[i].set_image_builder(builders[i])
            self._sync_alpha()
        finally:
            for w in self._spins + self._sliders:
                w.blockSignals(False)

    def _sync_alpha(self):
        if not self._spins:
            return
        self._spins[3].blockSignals(True)
        self._spins[3].setValue(self._color.alpha())
        self._spins[3].blockSignals(False)
        self._sliders[3].set_image_builder(
            lambda sz: _build_alpha_channel_image(
                sz.width(), sz.height(),
                QColor(self._color.red(), self._color.green(), self._color.blue(), 255), True))
        self._sliders[3].blockSignals(True)
        self._sliders[3].setValue(self._color.alpha())
        self._sliders[3].blockSignals(False)

    def _apply_color(self, color, emit, update_inputs):
        normalized = QColor(color)
        if not self._alpha_enabled:
            normalized.setAlpha(255)
        if not normalized.isValid():
            return
        self._updating = True
        try:
            self._color = normalized
            self._h, self._s, self._v, self._a = self._color.getHsvF()
            self._sync_spectrum()
            if update_inputs:
                self._sync_rgb()
                self._hexedit.setText(self._hex_text())
                self._palette.set_selected_color(self._color)
            self._shade.set_color(self._color)
        finally:
            self._updating = False
        if emit:
            self.colorChanged.emit(self.color())

    def _update_from_spectrum(self):
        if self._updating:
            return
        self._h = self._map.hue()
        self._s = self._map.saturation()
        self._v = self._third.value() / 255.0
        alpha = self._a if self._alpha_enabled else 1.0
        self._apply_color(QColor.fromHsvF(self._h, self._s, self._v, alpha), True, True)

    def _update_from_rgb(self):
        if self._updating or len(self._spins) < 4:
            return
        if self._representation == FluentColorPicker._HSVA:
            color = QColor.fromHsvF(
                self._spins[0].value() / 359.0,
                self._spins[1].value() / 100.0,
                self._spins[2].value() / 100.0,
                (self._spins[3].value() / 255.0) if self._alpha_enabled else 1.0)
        else:
            color = QColor(self._spins[0].value(), self._spins[1].value(),
                           self._spins[2].value(),
                           self._spins[3].value() if self._alpha_enabled else 255)
        self._apply_color(color, True, True)

    def _update_alpha(self, alpha):
        if self._updating or not self._alpha_enabled:
            return
        self._updating = True
        try:
            self._color.setAlpha(alpha)
            self._a = alpha / 255.0
            self._hexedit.setText(self._hex_text())
            self._shade.set_color(self._color)
        finally:
            self._updating = False
        self.colorChanged.emit(self.color())


# ============================================================================
# 对话框封装（excolorpickerdialog.cpp 移植）
# ============================================================================


class FluentColorDialog(LDialog):
    colorChanged = pyqtSignal(QColor)
    colorSelected = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._finishing = False
        self._initial = QColor()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QVBoxLayout()
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(16)
        self._title_label = QLabel(self)
        self._title_label.setWordWrap(True)
        titlefont = self._title_label.font()
        titlefont.setPixelSize(20)
        titlefont.setWeight(QFont.DemiBold)
        self._title_label.setFont(titlefont)
        body.addWidget(self._title_label)

        self._picker = FluentColorPicker(self)
        self._picker.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._picker.layout().setContentsMargins(0, 0, 0, 0)
        body.addWidget(self._picker, 1)
        root.addLayout(body, 1)

        footer = QWidget(self)
        buttons = QHBoxLayout(footer)
        buttons.setContentsMargins(16, 16, 16, 16)
        buttons.setSpacing(8)
        self._accept = LPushButton("确定")
        self._accept.setProperty("accent", True)
        self._accept.setDefault(True)
        self._cancel = LPushButton("取消")
        self._cancel.setAutoDefault(True)
        for btn in (self._accept, self._cancel):
            btn.setMinimumSize(120, 40)
            btn.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            buttons.addWidget(btn, 1)
        root.addWidget(footer)

        self.windowTitleChanged.connect(self._title_label.setText)
        self._picker.colorChanged.connect(self.colorChanged)
        self._accept.clicked.connect(self.accept)
        self._cancel.clicked.connect(self.reject)
        self.setWindowTitle("编辑颜色")
        self._initial = self.color()

    def sizeHint(self):
        return super().sizeHint().expandedTo(QSize(480, 0))

    def colorPicker(self):
        return self._picker

    def color(self):
        return self._picker.color()

    def setColor(self, color):
        if not color.isValid():
            return
        self._picker.setColor(color)
        if not self.isVisible():
            self._initial = self.color()

    def setAlphaEnabled(self, enabled):
        self._picker.setAlphaEnabled(enabled)

    def isAlphaEnabled(self):
        return self._picker.isAlphaEnabled()

    def setVisible(self, visible):
        if visible and not self.isVisible():
            self._initial = self.color()
        super().setVisible(visible)

    def done(self, result):
        # 提交未完成的文本编辑（hex/spin 的 editingFinished 依赖失焦）
        if self._finishing:
            return
        self._finishing = True
        focused = self.focusWidget()
        if focused is not None:
            focused.clearFocus()
        if result != QDialog.DialogCode.Accepted:
            self._picker.setColor(self._initial)
        selected = self.color()
        super().done(result)
        if result == QDialog.DialogCode.Accepted:
            self.colorSelected.emit(selected)
        self._finishing = False


# ============================================================================
# ColorPickerButton（excolorpickerbutton.cpp 移植）：
# 内容显示当前颜色的色块，点击弹出取色器飞层，选色实时生效
# ============================================================================


class ColorPickerButton(QToolButton):
    """带 Flyout 的颜色选择按钮（CommunityToolkit ColorPickerButton）。"""

    selectedColorChanged = pyqtSignal(QColor)

    _CONTENT_HMARGIN = 8
    _CONTENT_ITEM_HMARGIN = 5
    _SWATCH_VMARGIN = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._picker = None
        self._color = QColor(Qt.blue)
        self._pressed = False
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setPopupMode(QToolButton.InstantPopup)
        self.setFixedSize(68, 32)
        self.clicked.connect(self._show_picker)

    # ---- 颜色 ----
    def selectedColor(self):
        if self._picker is not None:
            return self._picker.color()
        return QColor(self._color)

    def setSelectedColor(self, color):
        if not color.isValid():
            return
        if self._picker is not None:
            if self._picker.color() == color:
                return
            self._picker.setColor(color)
            self._color = QColor(self._picker.color())
        else:
            if self._color == color:
                return
            self._color = QColor(color)
        self.update()
        self.selectedColorChanged.emit(QColor(self._color))

    def colorPicker(self):
        return self._picker

    def setAlphaEnabled(self, enabled):
        """飞层取色器的 Alpha 通道（在首次弹出前调用）。"""
        self._alpha_enabled = bool(enabled)
        if self._picker is not None:
            self._picker.setAlphaEnabled(enabled)

    # ---- 弹层 ----
    def _ensure_picker(self):
        if self._picker is not None:
            return
        self._picker = FluentColorPicker(self, popup=True)
        if getattr(self, "_alpha_enabled", True) is False:
            self._picker.setAlphaEnabled(False)
        self._picker.setColor(self._color)
        self._picker.colorChanged.connect(self._on_picker_changed)

    def _on_picker_changed(self, _):
        color = self._picker.color()
        if self._color == color:
            return
        self._color = QColor(color)
        self.update()
        self.selectedColorChanged.emit(QColor(color))

    def _show_picker(self):
        self._ensure_picker()
        self._picker.showPopup(self)

    # ---- 绘制 ----
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        option = QStyleOptionToolButton()
        option.initFrom(self)
        option.text = ""
        option.arrowType = Qt.NoArrow
        option.features = QStyleOptionToolButton.None_
        # drawComplexControl 是 QStyle/QStylePainter 的接口（QPainter 没有）
        self.style().drawComplexControl(QStyle.CC_ToolButton, option, p, self)

        arrow_width = self.style().pixelMetric(
            QStyle.PM_MenuButtonIndicator, option, self)
        arrow_area = QRectF(self.width() - arrow_width - 2, 0,
                            arrow_width, self.height())
        swatch = QRectF(self.rect()).adjusted(
            self._CONTENT_HMARGIN, self._SWATCH_VMARGIN,
            -self._CONTENT_HMARGIN, -self._SWATCH_VMARGIN)
        swatch.setRight(arrow_area.left() - self._CONTENT_ITEM_HMARGIN)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._color))
        p.drawRoundedRect(swatch, 3, 3)

        arrowfont = QFont("Segoe Fluent Icons")
        arrowfont.setPixelSize(11)
        p.setFont(arrowfont)
        arrowcolor = self.palette().color(
            QPalette.Disabled if not self.isEnabled() else QPalette.Active,
            QPalette.ButtonText)
        p.setPen(arrowcolor)
        if self._pressed:
            arrow_area.setTop(arrow_area.top() + 2)
        p.drawText(arrow_area, Qt.AlignCenter, _ICON_CHEVRON_DOWN)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._pressed:
            self._pressed = False
            self.update()
        super().mouseReleaseEvent(event)
