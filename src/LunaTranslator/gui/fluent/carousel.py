"""ExCarousel —— WinUI 3 风格图文轮播。

移植自 FluentUIStyle/ExWidgets/controls/excarousel.cpp：
- 图片页 CarouselImageSlide：KeepAspectRatioByExpanding 铺满裁切 + 底部
  渐变暗色横幅（标题/副标题），圆角剪裁
- 圆形导航按钮 CarouselNavButton（Segoe Fluent Icons Chevron）
- 圆点指示器 CarouselPips：当前点强调色、悬停放大、可点击跳页
- 切换动效：grab() 抓取两页快照在 CarouselViewport 中实体平移
  （QVariantAnimation + OutCubic；连续快翻自动缩短过渡时长）
- 自动播放 / 悬停暂停 / 首尾环绕 / 键盘左右 / 滚轮翻页
与 C++ 版差异：略去 QML 用途的 *Changed 属性信号，增加 clear()、
stopTransition()（无信号中断动画）与 setCurrentIndexImmediate()
（重建内容后直接就位不播动画）。
"""

from qtsymbols import (
    QApplication,
    QBrush,
    QColor,
    QEasingCurve,
    QEvent,
    QFont,
    QGraphicsOpacityEffect,
    QPalette,
    QPen,
    QPointF,
    QPixmap,
    QPoint,
    QPainter,
    QPainterPath,
    QRect,
    QRectF,
    QPropertyAnimation,
    QSize,
    QSizePolicy,
    Qt,
    QTimer,
    QToolButton,
    QVariantAnimation,
    QWidget,
    pyqtSignal,
)
from PyQt5.QtGui import QLinearGradient
from myutils.config import _TR

# ---- 常量（同 excarousel.cpp 匿名命名空间）----
_DEFAULT_WIDTH = 560
_DEFAULT_HEIGHT = 260
_MIN_WIDTH = 160
_MIN_HEIGHT = 96
_BUTTON_SIZE = 36
_BUTTON_MARGIN = 12
_PIPS_HEIGHT = 20
_PIPS_BOTTOM = 10
_PIP_SLOT_WIDTH = 16
_PIP_NORMAL_DIAMETER = 6.0
_PIP_HOVER_DIAMETER = 7.0
_PIP_SELECTED_DIAMETER = 8.0
_DEFAULT_INTERVAL = 4000
# 舒缓优雅的轮播滑动时长（550ms），对齐 ElaPromotionView 的动效呼吸感
_DEFAULT_DURATION = 550
_DEFAULT_CORNER_RADIUS = 8.0

_ICON_CHEVRON_LEFT = "\ue76b"    # ChevronLeft
_ICON_CHEVRON_RIGHT = "\ue76c"   # ChevronRight
_ICON_CHEVRON_UP = "\ue70e"      # ChevronUp
_ICON_CHEVRON_DOWN = "\ue70d"    # ChevronDown


def _wrap_index(index, count):
    if count <= 0:
        return 0
    m = index % count
    return m + count if m < 0 else m


def _resolve_accent_color(w):
    app = QApplication.instance()
    if app is not None:
        col = app.property("_q_accent_color")
        if isinstance(col, QColor) and col.isValid():
            return col
    if w is not None:
        hl = w.palette().color(QPalette.Active, QPalette.Highlight)
        if hl.isValid():
            return hl
    return QColor(0, 120, 215)


class CarouselImageSlide(QWidget):
    """图片轮播页：铺满绘制 + 底部图文渐变横幅。"""

    def __init__(self, pixmap, title="", subtitle="",
                 aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                 parent=None):
        super().__init__(parent)
        self._pixmap = pixmap
        self._title = title
        self._subtitle = subtitle
        self._aspectMode = aspectMode
        self._borderRadius = _DEFAULT_CORNER_RADIUS

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update()

    def setTitle(self, title):
        self._title = title
        self.update()

    def setSubtitle(self, subtitle):
        self._subtitle = subtitle
        self.update()

    def setBorderRadius(self, radius):
        if self._borderRadius == radius:
            return
        self._borderRadius = radius
        self.update()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
            | QPainter.RenderHint.TextAntialiasing
        )
        r = QRectF(self.rect())
        # 自身圆角剪裁（静态展示与快照生成时保持圆角）
        if self._borderRadius > 0:
            clip = QPainterPath()
            clip.addRoundedRect(r, self._borderRadius, self._borderRadius)
            painter.setClipPath(clip)

        if not self._pixmap.isNull():
            dpr = self.devicePixelRatioF()
            pw, ph = self._pixmap.width(), self._pixmap.height()
            tw, th = r.width() * dpr, r.height() * dpr
            if (self._aspectMode
                    == Qt.AspectRatioMode.KeepAspectRatioByExpanding):
                scale = max(tw / pw, th / ph)
                drawW, drawH = pw * scale / dpr, ph * scale / dpr
            elif self._aspectMode == Qt.AspectRatioMode.IgnoreAspectRatio:
                drawW, drawH = r.width(), r.height()
            else:  # KeepAspectRatio
                scale = min(tw / pw, th / ph)
                drawW, drawH = pw * scale / dpr, ph * scale / dpr
            drawX = r.left() + (r.width() - drawW) / 2.0
            drawY = r.top() + (r.height() - drawH) / 2.0
            painter.drawPixmap(
                QRectF(drawX, drawY, drawW, drawH),
                self._pixmap, QRectF(self._pixmap.rect()),
            )
        else:
            # 空图占位不填底（透明）——由所在卡片的底色透出
            pass

        # 底部图文渐变暗色遮罩
        if not (self._title or self._subtitle):
            return
        bannerHeight = 56 if not self._subtitle else 76
        bannerRect = QRectF(
            r.left(), r.bottom() - bannerHeight + 1, r.width(), bannerHeight)
        grad = QLinearGradient(bannerRect.topLeft(), bannerRect.bottomLeft())
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        grad.setColorAt(0.4, QColor(0, 0, 0, 110))
        grad.setColorAt(1.0, QColor(0, 0, 0, 175))
        painter.fillRect(bannerRect, QBrush(grad))

        painter.setPen(Qt.GlobalColor.white)
        textWidth = max(10, int(r.width()) - 40)
        bottom = int(r.bottom())
        if not self._subtitle:
            titleFont = QFont(self.font())
            titleFont.setBold(True)
            titleFont.setPixelSize(16)
            painter.setFont(titleFont)
            painter.drawText(
                QRect(20, bottom - 40, textWidth, 28),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                | Qt.TextFlag.TextSingleLine, self._title)
        else:
            titleFont = QFont(self.font())
            titleFont.setBold(True)
            titleFont.setPixelSize(16)
            painter.setFont(titleFont)
            painter.drawText(
                QRect(20, bottom - 56, textWidth, 24),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                | Qt.TextFlag.TextSingleLine, self._title)
            subFont = QFont(self.font())
            subFont.setPixelSize(12)
            painter.setFont(subFont)
            painter.setPen(QColor(240, 240, 240, 220))
            painter.drawText(
                QRect(20, bottom - 32, textWidth, 20),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                | Qt.TextFlag.TextSingleLine, self._subtitle)


class CarouselNavButton(QToolButton):
    """圆形浮动导航按钮（自绘，Chevron 箭头）。工具提示走 i18n：
    setToolTip 记原文并翻译，LanguageChange -> updatelangtext 刷新
    （由应用级事件过滤器驱动，同 LLabel）。"""

    _ARROW_GLYPHS = {
        Qt.ArrowType.LeftArrow: _ICON_CHEVRON_LEFT,
        Qt.ArrowType.RightArrow: _ICON_CHEVRON_RIGHT,
        Qt.ArrowType.UpArrow: _ICON_CHEVRON_UP,
        Qt.ArrowType.DownArrow: _ICON_CHEVRON_DOWN,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tr_tip = None
        self._hovered = False
        self._pressed = False

    def setToolTip(self, t):
        self._tr_tip = t
        super().setToolTip(_TR(t))

    def updatelangtext(self):
        if self._tr_tip is not None:
            super().setToolTip(_TR(self._tr_tip))

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        if self._pressed:
            r.adjust(1.0, 1.0, -1.0, -1.0)

        fill = QColor(self.palette().color(QPalette.Button))
        if self._pressed:
            alpha = 245
        elif self._hovered:
            alpha = 230
        else:
            alpha = 190
        fill.setAlpha(alpha)

        painter.setPen(QPen(self.palette().color(QPalette.Mid), 1.0))
        painter.setBrush(fill)
        painter.drawEllipse(r)

        font = QFont("Segoe Fluent Icons")
        font.setPixelSize(16)
        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.ButtonText))
        painter.drawText(
            r, Qt.AlignmentFlag.AlignCenter,
            CarouselNavButton._ARROW_GLYPHS.get(
                self.arrowType(), _ICON_CHEVRON_RIGHT),
        )

    def enterEvent(self, event):
        super().enterEvent(event)
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hovered = False
        self._pressed = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)


class CarouselPips(QWidget):
    """圆点指示器：当前=强调色、悬停放大、点击跳页。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._count = 0
        self._current = 0
        self._hoverIndex = -1

    def setCount(self, value):
        if self._count == value:
            return
        self._count = max(0, value)
        self.updateGeometry()
        self.update()

    def setCurrent(self, value):
        if self._current == value:
            return
        self._current = value
        self.update()

    def sizeHint(self):
        if self._count <= 0:
            return QSize(0, _PIPS_HEIGHT)
        return QSize(self._count * _PIP_SLOT_WIDTH, _PIPS_HEIGHT)

    def indexAt(self, pos):
        if self._count <= 0:
            return -1
        totalWidth = self._count * _PIP_SLOT_WIDTH
        startX = (self.width() - totalWidth) // 2
        if pos.x() < startX or pos.x() >= startX + totalWidth:
            return -1
        if pos.y() < 0 or pos.y() > self.height():
            return -1
        idx = (pos.x() - startX) // _PIP_SLOT_WIDTH
        if 0 <= idx < self._count:
            return idx
        return -1

    def mouseMoveEvent(self, event):
        idx = self.indexAt(event.pos())
        if idx != self._hoverIndex:
            self._hoverIndex = idx
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self._hoverIndex != -1:
            self._hoverIndex = -1
            self.update()
        super().leaveEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (
            QEvent.Type.PaletteChange,
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.StyleChange,
        ):
            self.update()

    def paintEvent(self, _):
        if self._count <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 动态跟随当前主题强调色（联动全局与调色板）
        accent = _resolve_accent_color(self)
        isDark = self.palette().color(QPalette.Window).lightness() < 128

        totalWidth = self._count * _PIP_SLOT_WIDTH
        startX = (self.width() - totalWidth) / 2.0
        centerY = self.height() / 2.0

        for i in range(self._count):
            selected = i == self._current
            hovered = i == self._hoverIndex
            if selected:
                diameter = _PIP_SELECTED_DIAMETER
            elif hovered:
                diameter = _PIP_HOVER_DIAMETER
            else:
                diameter = _PIP_NORMAL_DIAMETER
            radius = diameter / 2.0
            cx = startX + i * _PIP_SLOT_WIDTH + (_PIP_SLOT_WIDTH / 2.0)

            if selected:
                dotColor = accent
            elif hovered:
                dotColor = (QColor(255, 255, 255, 220) if isDark
                            else QColor(0, 0, 0, 180))
            else:
                dotColor = (QColor(255, 255, 255, 120) if isDark
                            else QColor(0, 0, 0, 95))

            painter.setPen(Qt.PenStyle.NoPen)
            # 柔和微弱底层投影：任何明暗背景图上圆点轮廓都清晰
            painter.setBrush(QColor(0, 0, 0, 40))
            painter.drawEllipse(QPointF(cx, centerY + 0.5), radius, radius)
            # WinUI 3 原生标准正圆 Pip 点（不变长为胶囊）
            painter.setBrush(dotColor)
            painter.drawEllipse(QPointF(cx, centerY), radius, radius)


class CarouselViewport(QWidget):
    """视口：圆角剪裁 + 切换动画（双快照实体平移）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._borderRadius = _DEFAULT_CORNER_RADIUS
        self._clipPath = QPainterPath()
        self._animating = False
        self._progress = 0.0
        self._direction = 1
        self._fromPix = QPixmap()
        self._toPix = QPixmap()

    def setBorderRadius(self, radius):
        if self._borderRadius == radius:
            return
        self._borderRadius = radius
        self._updateClipPath()
        self.update()

    def borderRadius(self):
        return self._borderRadius

    def startTransition(self, fromPix, toPix, direction):
        self._fromPix = fromPix
        self._toPix = toPix
        self._direction = direction
        self._progress = 0.0
        self._animating = True
        self.update()

    def setTransitionProgress(self, progress):
        self._progress = progress
        self.update()

    def endTransition(self):
        self._animating = False
        self._fromPix = QPixmap()
        self._toPix = QPixmap()
        self._progress = 0.0
        self.update()

    def isAnimating(self):
        return self._animating

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._updateClipPath()
        r = self.rect()
        for child in self.children():
            if isinstance(child, QWidget):
                child.resize(r.size())

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        # 预计算好的圆角路径，避免每帧重建 QPainterPath
        if not self._clipPath.isEmpty():
            painter.setClipPath(self._clipPath)

        if self._animating and not self._fromPix.isNull() \
                and not self._toPix.isNull():
            offset = self._progress * self.width()
            # 实体物理平移（无半透明重影）：离开页自 0 滑出，进入页滑入
            painter.drawPixmap(
                QPointF(-self._direction * offset, 0), self._fromPix)
            painter.drawPixmap(
                QPointF(self._direction * (self.width() - offset), 0),
                self._toPix)
        # 闲置态不填底色（透明）——由所在卡片的底色透出（画廊内容卡）

    def _updateClipPath(self):
        self._clipPath = QPainterPath()
        if self._borderRadius > 0 and self.width() > 0 and self.height() > 0:
            self._clipPath.addRoundedRect(
                QRectF(self.rect()), self._borderRadius, self._borderRadius)


class ExCarousel(QWidget):
    """WinUI 3 风格图文轮播（addSlide/addPixmap 构建内容）。"""

    currentIndexChanged = pyqtSignal(int)
    slideClicked = pyqtSignal(int)

    # NavigationButtonTrigger
    AlwaysVisible = 0
    OnHover = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("exCarousel")
        self._slides = []
        self._currentIndex = -1
        self._pendingIndex = -1
        self._pendingDirection = 1
        self._autoPlay = True
        self._interval = _DEFAULT_INTERVAL
        self._wrap = True
        self._showNavigationButtons = True
        self._showIndicators = True
        self._animationDuration = _DEFAULT_DURATION
        self._pauseOnHover = True
        self._hovered = False
        self._animating = False
        self._borderRadius = _DEFAULT_CORNER_RADIUS
        self._navTrigger = ExCarousel.AlwaysVisible
        self._anim = None

        self.viewport = CarouselViewport(self)
        self.viewport.setObjectName("exCarouselViewport")
        self.viewport.setBorderRadius(self._borderRadius)
        self.viewport.installEventFilter(self)

        self.prevButton = CarouselNavButton(self)
        self.prevButton.setObjectName("exCarouselPrev")
        self.prevButton.setArrowType(Qt.ArrowType.LeftArrow)
        self.prevButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prevButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.prevButton.setFixedSize(_BUTTON_SIZE, _BUTTON_SIZE)
        self.prevButton.setToolTip("上一张")
        self._prevEffect = QGraphicsOpacityEffect(self.prevButton)
        self.prevButton.setGraphicsEffect(self._prevEffect)

        self.nextButton = CarouselNavButton(self)
        self.nextButton.setObjectName("exCarouselNext")
        self.nextButton.setArrowType(Qt.ArrowType.RightArrow)
        self.nextButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.nextButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.nextButton.setFixedSize(_BUTTON_SIZE, _BUTTON_SIZE)
        self.nextButton.setToolTip("下一张")
        self._nextEffect = QGraphicsOpacityEffect(self.nextButton)
        self.nextButton.setGraphicsEffect(self._nextEffect)

        self.pips = CarouselPips(self)
        self.pips.setObjectName("exCarouselIndicators")
        self.pips.installEventFilter(self)

        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.CoarseTimer)
        self._timer.timeout.connect(self.next)
        self.prevButton.clicked.connect(self.previous)
        self.nextButton.clicked.connect(self.next)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._updateChromeVisibility()

    # ---- 内容 ----
    def addSlide(self, widget):
        self.insertSlide(len(self._slides), widget)
        return len(self._slides) - 1

    def addPixmap(self, pixmap, title="", subtitle="",
                 aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding):
        slide = CarouselImageSlide(pixmap, title, subtitle, aspectMode,
                                   self.viewport)
        slide.setBorderRadius(self._borderRadius)
        return self.addSlide(slide)

    def addImage(self, filePath, title="", subtitle="",
                 aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding):
        return self.addPixmap(QPixmap(filePath), title, subtitle, aspectMode)

    def insertSlide(self, index, widget):
        if widget is None:
            return
        index = max(0, min(index, len(self._slides)))
        widget.setParent(self.viewport)
        widget.installEventFilter(self)
        if isinstance(widget, CarouselImageSlide):
            widget.setBorderRadius(self._borderRadius)
        self._slides.insert(index, widget)
        if self._currentIndex < 0:
            self._currentIndex = 0
        elif index <= self._currentIndex:
            self._currentIndex += 1
        self._placeIdle()
        self._restartTimer()

    def removeSlide(self, index):
        taken = self.takeSlide(index)
        if taken is not None:
            taken.deleteLater()

    def removeSlideWidget(self, widget):
        """按引用移除一页（延迟加载发现失效图时丢弃）。"""
        try:
            index = self._slides.index(widget)
        except ValueError:
            return
        self.removeSlide(index)

    def slideAt(self, index):
        if 0 <= index < len(self._slides):
            return self._slides[index]
        return None

    def takeSlide(self, index):
        if not 0 <= index < len(self._slides):
            return None
        widget = self._slides.pop(index)
        widget.removeEventFilter(self)
        widget.setParent(None)
        if not self._slides:
            self._currentIndex = -1
        elif self._currentIndex >= len(self._slides):
            self._currentIndex = len(self._slides) - 1
        elif index < self._currentIndex:
            self._currentIndex -= 1
        self._placeIdle()
        self._restartTimer()
        return widget

    def clear(self):
        """清空全部页（切换内容时重建；先中断动画防悬空索引）。"""
        self.stopTransition()
        for slide in self._slides:
            slide.removeEventFilter(self)
            slide.deleteLater()
        self._slides = []
        self._currentIndex = -1
        self._placeIdle()
        self._restartTimer()

    def count(self):
        return len(self._slides)

    def currentIndex(self):
        return self._currentIndex

    def setCurrentIndex(self, index):
        if not self._slides:
            return
        if self._wrap:
            bounded = _wrap_index(index, len(self._slides))
        else:
            bounded = max(0, min(index, len(self._slides) - 1))
        direction = 1 if bounded >= self._currentIndex else -1
        if self._wrap and self._currentIndex == len(self._slides) - 1 \
                and bounded == 0:
            direction = 1
        elif self._wrap and self._currentIndex == 0 \
                and bounded == len(self._slides) - 1:
            direction = -1
        self._goTo(bounded, direction)

    def setCurrentIndexImmediate(self, index):
        """直接就位到 index（不播切换动画）——内容重建/初次定位用。"""
        if not self._slides:
            return
        if self._wrap:
            index = _wrap_index(index, len(self._slides))
        else:
            index = max(0, min(index, len(self._slides) - 1))
        self.stopTransition()
        if index == self._currentIndex:
            self._placeIdle()
            return
        self._currentIndex = index
        self._placeIdle()
        self.currentIndexChanged.emit(self._currentIndex)
        self._restartTimer()

    def stopTransition(self):
        """中断进行中的切换动画（重建/重排内容前调用；不发 currentIndexChanged）。"""
        if self._anim is not None:
            anim, self._anim = self._anim, None
            # 先断开 finished 再 stop，避免 _finishAnimation 携旧索引
            # 二次改写状态/发信号
            anim.finished.disconnect()
            anim.stop()
            anim.deleteLater()
        self._animating = False
        self._pendingIndex = -1
        self.viewport.endTransition()

    def next(self):
        if len(self._slides) < 2:
            return
        index = self._nextIndex(self._currentIndex, 1)
        if index == self._currentIndex:
            return
        self._goTo(index, 1)

    def previous(self):
        if len(self._slides) < 2:
            return
        index = self._nextIndex(self._currentIndex, -1)
        if index == self._currentIndex:
            return
        self._goTo(index, -1)

    # ---- 选项 ----
    def setAutoPlay(self, enabled):
        if self._autoPlay == enabled:
            return
        self._autoPlay = enabled
        self._restartTimer()

    def setInterval(self, msec):
        msec = max(200, msec)
        if self._interval == msec:
            return
        self._interval = msec
        self._restartTimer()

    def setWrap(self, wrap):
        if self._wrap == wrap:
            return
        self._wrap = wrap
        self._updateChromeVisibility()
        self._restartTimer()

    def setShowNavigationButtons(self, show):
        if self._showNavigationButtons == show:
            return
        self._showNavigationButtons = show
        self._updateChromeVisibility()

    def setShowIndicators(self, show):
        if self._showIndicators == show:
            return
        self._showIndicators = show
        self._updateChromeVisibility()

    def setAnimationDuration(self, msec):
        self._animationDuration = max(0, msec)

    def setPauseOnHover(self, pause):
        if self._pauseOnHover == pause:
            return
        self._pauseOnHover = pause
        self._restartTimer()

    def setBorderRadius(self, radius):
        radius = max(0.0, radius)
        if self._borderRadius == radius:
            return
        self._borderRadius = radius
        self.viewport.setBorderRadius(radius)
        for slide in self._slides:
            if isinstance(slide, CarouselImageSlide):
                slide.setBorderRadius(radius)

    def setNavigationButtonTrigger(self, trigger):
        if self._navTrigger == trigger:
            return
        self._navTrigger = trigger
        self._updateChromeVisibility()

    # ---- 内部 ----
    def _relayoutChrome(self):
        r = self.rect()
        self.viewport.setGeometry(r)
        self.prevButton.move(
            r.left() + _BUTTON_MARGIN, r.center().y() - _BUTTON_SIZE // 2)
        self.nextButton.move(
            r.right() - _BUTTON_MARGIN - _BUTTON_SIZE + 1,
            r.center().y() - _BUTTON_SIZE // 2)
        hint = self.pips.sizeHint()
        self.pips.setGeometry(
            (r.width() - hint.width()) // 2,
            r.bottom() - _PIPS_BOTTOM - _PIPS_HEIGHT + 1,
            max(hint.width(), 1), _PIPS_HEIGHT)
        self.prevButton.raise_()
        self.nextButton.raise_()
        self.pips.raise_()

    def _placeIdle(self):
        self._relayoutChrome()
        vr = self.viewport.rect()
        for i, slide in enumerate(self._slides):
            slide.setGeometry(vr)
            slide.setVisible((not self._animating) and i == self._currentIndex)
        self.pips.setCount(len(self._slides))
        self.pips.setCurrent(self._currentIndex)
        self._updateChromeVisibility()

    def _nextIndex(self, frm, direction):
        if not self._slides:
            return -1
        candidate = frm + direction
        if self._wrap:
            return _wrap_index(candidate, len(self._slides))
        return max(0, min(candidate, len(self._slides) - 1))

    def _goTo(self, index, direction, overrideDuration=-1):
        if not self._slides:
            return
        if self._wrap:
            index = _wrap_index(index, len(self._slides))
        else:
            index = max(0, min(index, len(self._slides) - 1))
        if index == self._currentIndex and not self._animating:
            return
        if self._animating:
            self._pendingIndex = index
            self._pendingDirection = direction
            return
        dur = overrideDuration if overrideDuration >= 0 else self._animationDuration
        if (self._currentIndex < 0 or dur <= 0 or not self.isVisible()
                or self.viewport.width() <= 0 or self.viewport.height() <= 0):
            self._currentIndex = index
            self._placeIdle()
            self.currentIndexChanged.emit(self._currentIndex)
            self._restartTimer()
            return
        if direction == 0:
            direction = 1 if index >= self._currentIndex else -1
        if self._wrap and self._currentIndex == len(self._slides) - 1 \
                and index == 0:
            direction = 1
        elif self._wrap and self._currentIndex == 0 \
                and index == len(self._slides) - 1:
            direction = -1

        src = self._slides[self._currentIndex]
        dst = self._slides[index]
        vpSize = self.viewport.size()
        # grab() 抓取实际屏幕映射，自动对齐高 DPI 物理与逻辑尺寸
        src.setGeometry(QRect(QPoint(0, 0), vpSize))
        src.show()
        fromPix = src.grab(QRect(QPoint(0, 0), vpSize))
        dst.setGeometry(QRect(QPoint(0, 0), vpSize))
        dst.show()
        toPix = dst.grab(QRect(QPoint(0, 0), vpSize))
        src.hide()
        dst.hide()

        self.viewport.startTransition(fromPix, toPix, direction)
        self._animating = True
        self.prevButton.raise_()
        self.nextButton.raise_()
        self.pips.raise_()

        anim = QVariantAnimation(self)
        anim.setDuration(dur)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        # 与 ElaPromotionView 一致的 OutCubic 三次缓出阻尼曲线
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.valueChanged.connect(
            lambda v: self.viewport.setTransitionProgress(float(v)))

        def _finished(_anim=anim, _index=index):
            _anim.deleteLater()
            self._finishAnimation(_index)

        anim.finished.connect(_finished)
        self._anim = anim
        anim.start()

    def _finishAnimation(self, index):
        self._anim = None
        self._animating = False
        self.viewport.endTransition()
        if not self._slides:  # 动画期间被 clear()
            self._currentIndex = -1
            self._placeIdle()
            return
        index = max(0, min(index, len(self._slides) - 1))
        self._currentIndex = index
        self._placeIdle()
        self.currentIndexChanged.emit(self._currentIndex)

        if self._pendingIndex >= 0 and self._pendingIndex != self._currentIndex:
            nxt = self._pendingIndex
            direction = self._pendingDirection
            self._pendingIndex = -1
            # 快速连续翻页时缩短过渡时长，体验更跟手
            self._goTo(nxt, direction, min(self._animationDuration, 180))
            return
        self._pendingIndex = -1
        self._restartTimer()

    def _timerShouldRun(self):
        return (self._autoPlay and len(self._slides) > 1 and self.isVisible()
                and not (self._pauseOnHover and self._hovered)
                and not self._animating)

    def _restartTimer(self):
        self._timer.stop()
        if self._timerShouldRun():
            self._timer.start(self._interval)

    def _stopTimer(self):
        self._timer.stop()

    def _animateButtonsOpacity(self, targetOpacity):
        for button, effect in (
            (self.prevButton, self._prevEffect),
            (self.nextButton, self._nextEffect),
        ):
            anim = QPropertyAnimation(effect, b"opacity", button)
            anim.setDuration(160)
            anim.setStartValue(effect.opacity())
            anim.setEndValue(targetOpacity)
            anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _updateChromeVisibility(self):
        hasSlides = len(self._slides) > 1
        self.prevButton.setVisible(self._showNavigationButtons and hasSlides)
        self.nextButton.setVisible(self._showNavigationButtons and hasSlides)
        self.pips.setVisible(self._showIndicators and hasSlides)

        if self._navTrigger == ExCarousel.OnHover:
            target = 1.0 if self._hovered else 0.0
            self._prevEffect.setOpacity(target)
            self._nextEffect.setOpacity(target)
        else:
            self._prevEffect.setOpacity(1.0)
            self._nextEffect.setOpacity(1.0)

        self.prevButton.setEnabled(self._wrap or self._currentIndex > 0)
        self.nextButton.setEnabled(
            self._wrap or self._currentIndex < len(self._slides) - 1)

    # ---- 事件 ----
    def sizeHint(self):
        return QSize(_DEFAULT_WIDTH, _DEFAULT_HEIGHT)

    def minimumSizeHint(self):
        return QSize(_MIN_WIDTH, _MIN_HEIGHT)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._hovered = True
        self._restartTimer()
        if self._navTrigger == ExCarousel.OnHover:
            self._animateButtonsOpacity(1.0)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hovered = False
        self._restartTimer()
        if self._navTrigger == ExCarousel.OnHover:
            self._animateButtonsOpacity(0.0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._animating:
            self._finishAnimation(self._currentIndex)
        else:
            self._placeIdle()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._stopTimer()

    def showEvent(self, event):
        super().showEvent(event)
        self._placeIdle()
        self._restartTimer()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (
            QEvent.Type.PaletteChange,
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.StyleChange,
        ):
            self.prevButton.update()
            self.nextButton.update()
            self.pips.update()
            self.viewport.update()
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.previous()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Right:
            self.next()
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            delta = event.angleDelta().x()
        if delta > 0:
            self.previous()
        elif delta < 0:
            self.next()
        event.accept()

    def eventFilter(self, watched, event):
        if watched is self.pips and \
                event.type() == QEvent.Type.MouseButtonRelease:
            index = self.pips.indexAt(event.pos())
            if index >= 0:
                self.setCurrentIndex(index)
            return True
        if event.type() == QEvent.Type.MouseButtonRelease:
            for i, slide in enumerate(self._slides):
                if watched is slide and i == self._currentIndex:
                    self.slideClicked.emit(i)
                    break
        return super().eventFilter(watched, event)
