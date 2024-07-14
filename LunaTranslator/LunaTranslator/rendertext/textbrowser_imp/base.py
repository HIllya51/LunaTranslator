from qtsymbols import *
from myutils.config import globalconfig


class base(QLabel):
    def paintText(self, painter: QPainter):
        raise Exception

    def setShadow(self):
        pass

    def moveoffset(self):
        return self.config.get("width", 0), self.config.get("width", 0)

    def extraWH(self):
        return 2 * self.config.get("width", 0), 2 * self.config.get("width", 0)

    def init(self):
        pass

    @property
    def config(self):
        return globalconfig["rendertext"]["textbrowser"][self.typename].get("args", {})

    @property
    def basecolor(self):
        return self._basecolor

    def setColor(self, color: str):
        if color is None:
            self._basecolor = QColor()
        else:
            self._basecolor = QColor(color)

    def __init__(self, typename, parent):
        super().__init__(parent)
        self._basecolor = QColor()
        self.typename = typename
        self.movedy = 0
        self.movedx = 0
        self._pix = None
        self._m_text = ""

        self.init()

    def adjustSize(self):
        self._pix = None
        font = self.font()
        text = self.text()
        font_m = QFontMetrics(font)
        w, h = self.extraWH()
        self.resize(
            int(font_m.size(0, text).width() + w),
            int(font_m.height() + h),
        )
        self.setShadow()

    def move(self, x: int, y: int):
        self.movedx = 0
        self.movedy = 0
        dx, dy = self.moveoffset()
        text = self.text()
        isarabic = lambda char: (ord(char) >= 0x0600 and ord(char) <= 0x06E0)
        isfirstara = lambda text: len(text) and isarabic(text[0])
        isarabicx = any(isarabic(char) for char in text) and isfirstara(text)

        if isarabicx:
            self.movedx -= self.width()
            self.movedx += dx
        else:
            self.movedx -= dx
        self.movedy -= dy
        super().move(QPoint(int(x + self.movedx), int(y + self.movedy)))

    def y(self):
        y = super().y()
        return y - self.movedy

    def x(self):
        x = super().x()
        return x - self.movedx

    def pos(self) -> QPoint:
        return QPoint(self.x(), self.y())

    def clearShadow(self):
        self.setGraphicsEffect(None)

    def text(self):
        return self._m_text

    def setText(self, text):
        self._m_text = text

    def paintEvent(self, event):
        if not self._pix:
            rate = self.devicePixelRatioF()
            self._pix = QPixmap(self.size() * rate)
            self._pix.setDevicePixelRatio(rate)
            self._pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(self._pix)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.paintText(painter)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pix)
