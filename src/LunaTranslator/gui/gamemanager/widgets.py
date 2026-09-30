"""游戏管理通用控件（原 dialog.py 中的 imagehelper / ItemWidget）。

独立成模块以打破 v3 <-> dialog 的循环导入（v3 的网格页与 dialog 的
new 视图共用这些控件）。
"""

from qtsymbols import *
import os
from traceback import print_exc
from myutils.utils import targetmod
from myutils.config import savehook_new_data, extradatas, ui_settings, globalconfig, get_launchpath
from gui.gamemanager.common import getpixfunction


class imagehelper:
    def size(self):
        return QSizeF(self.p.width() - 2 * self.p.margin, self.p.imageheight)

    def height(self):
        return self.size().height()

    def width(self):
        return self.size().width()

    def rect(self):
        return QRectF(QPoint(0, 0), self.size())

    @property
    def imagewrapmode(self):
        return globalconfig.get("imagewrapmode", 0)

    def adaptsize(self, size: QSize):

        if self.imagewrapmode == 0:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r < max_r:
                new_w = self.width()
                new_h = new_w / r
            else:
                new_h = self.height()
                new_w = new_h * r
            return QSizeF(new_w, new_h)
        elif self.imagewrapmode == 1:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r > max_r:
                new_w = self.width()
                new_h = new_w / r
            else:
                new_h = self.height()
                new_w = new_h * r
            return QSizeF(new_w, new_h)
        elif self.imagewrapmode == 2:
            return QSizeF(self.size())
        elif self.imagewrapmode == 3:
            return QSizeF(size)

    def setimg(self):
        self._setimg(self._pixmap)

    def _setimg(self, pixmap: QPixmap):
        if pixmap.isNull():
            return
        if not (self.height() and self.width()):
            return
        if self.__last == (self.size(), self.imagewrapmode):
            return
        self.__last = (self.size(), self.imagewrapmode)
        rate = self.p.devicePixelRatioF()
        newpixmap = QPixmap((self.size() * rate).toSize())
        newpixmap.setDevicePixelRatio(rate)
        newpixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(newpixmap)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        rectf = self.getrect(pixmap.size())
        painter.drawPixmap(rectf, pixmap, QRectF(pixmap.rect()))
        painter.end()
        self.pixmap = newpixmap

    def getrect(self, size):
        size = self.adaptsize(size)
        rect = QRectF()
        rect.setX((self.width() - size.width()) / 2)
        rect.setY((self.height() - size.height()) / 2)
        rect.setSize(size)
        return rect

    def __init__(self, p: "ItemWidget", pixmap) -> None:
        self.p = p
        self._pixmap = pixmap
        self.__last = None
        self.pixmap = QPixmap()


class ItemWidget(QWidget):
    focuschanged = pyqtSignal(bool, str)
    doubleclicked = pyqtSignal(str)
    droppedgame = pyqtSignal(str, str, bool)  # 拖动uid, 目标uid, 插到目标前
    globallashfocus = None

    @classmethod
    def clearfocus(cls):
        try:  # 可能已被删除
            if ItemWidget.globallashfocus:
                ItemWidget.globallashfocus.focusOut()
        except:
            pass
        ItemWidget.globallashfocus = None

    def click(self):
        try:
            self.isfucked = True
            self.update()
            if self != ItemWidget.globallashfocus:
                ItemWidget.clearfocus()
            ItemWidget.globallashfocus = self
            self.focuschanged.emit(True, self.gameuid)
        except:
            print_exc()

    def mousePressEvent(self, ev) -> None:
        self._presspos = ev.pos()
        self.click()

    def mouseMoveEvent(self, e) -> None:
        # 按住拖动超过阈值 -> 启动拖拽（acceptDrops=False 时 dropEvent 不会触发，
        # 拖拽启动本身由 gridpage 的 acceptDrops 状态控制——见 _apply_tag_filter）
        if e.buttons() & Qt.MouseButton.LeftButton and self.acceptDrops() and (
            e.pos() - getattr(self, "_presspos", e.pos())
        ).manhattanLength() >= QApplication.startDragDistance():
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText("lunamovegame:" + self.gameuid)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mouseMoveEvent(e)

    def dragEnterEvent(self, e) -> None:
        if e.mimeData().text().startswith("lunamovegame:"):
            e.acceptProposedAction()

    def dropEvent(self, e) -> None:
        txt = e.mimeData().text()
        if not txt.startswith("lunamovegame:"):
            return
        uid = txt.split(":", 1)[1]
        if uid == self.gameuid:
            return
        e.acceptProposedAction()
        # 按落点在目标中心的哪一侧决定插前/插后
        self.droppedgame.emit(uid, self.gameuid, e.pos().x() < self.width() / 2)

    def focusOut(self):
        self.isfucked = False
        self.update()
        self.focuschanged.emit(False, self.gameuid)

    def mouseDoubleClickEvent(self, e):
        self.doubleclicked.emit(self.gameuid)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resizeobjects()

    def resizeobjects(self):
        self._img.setimg()
        self.update()

    def event(self, e: QEvent):
        if e.type() == QEvent.Type.FontChange:
            self.resizeobjects()
        return super().event(e)

    def others(self):
        self.resizeobjects()

    def __init__(self, gameuid) -> None:
        super().__init__()
        self.isfucked = False
        self.setAcceptDrops(True)
        self.gameuid = gameuid

        for image in savehook_new_data[gameuid].get("imagepath_all", []):
            fr = extradatas["imagefrom"].get(image)
            if fr:
                targetmod.get(fr).dispatchdownloadtask(image)

        self._img = imagehelper(self, getpixfunction(gameuid))
        exists = os.path.exists(get_launchpath(gameuid))
        self.setObjectName("savegame_exists" + str(exists))
        self.setToolTip(savehook_new_data[gameuid]["title"])
        self.setAccessibleName(savehook_new_data[gameuid]["title"])

    @property
    def margin(self):
        return ui_settings["dialog_savegame_layout"].get("margin2", 6) + ui_settings[
            "dialog_savegame_layout"
        ].get("borderW", 1)

    @property
    def imageheight(self):
        layout = ui_settings["dialog_savegame_layout"].get("layout", "updown")
        if layout == "updown":
            return self.height() - self.margin * 2 - self.textareaheight
        if layout == "overlay":
            return self.height() - self.margin * 2

    @property
    def textcolor(self):
        return QColor(ui_settings["dialog_savegame_layout"].get("textColor", "#000000"))

    @property
    def textfont(self):
        font = QFont()
        fontstring = globalconfig.get("savegame_textfont1", "")
        if not fontstring:
            return font
        font.fromString(fontstring)
        return font

    @property
    def textareaheight(self):
        h = QFontMetricsF(self.textfont, self).height()
        h = ui_settings["dialog_savegame_layout"].get("textH2", 1) * h
        return h

    def paintEvent(self, a0):
        dialog_savegame_layout = ui_settings["dialog_savegame_layout"]
        hasFocus = (
            dialog_savegame_layout.get("onselectcolor2", "#40007fff")
            if self.isfucked
            else None
        )
        if self.objectName() == "savegame_existsFalse":
            background = dialog_savegame_layout.get("onfilenoexistscolor2", "#40acacac")
        else:
            background = dialog_savegame_layout.get("backcolor2", "#40ffffff")
        if self.isfucked:
            bordercolor = dialog_savegame_layout.get("borderColor2", "#ff000000")
        else:
            bordercolor = dialog_savegame_layout.get("borderColor", "#10000000")
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path_inner = self.get_inter_path()
        path_out = self.get_out_path()
        painter.fillPath(path_out.subtracted(path_inner), QColor(bordercolor))
        painter.fillPath(path_inner, QColor(hasFocus if hasFocus else background))

        content_path = self.get_shrunk_rounded_rect_path(
            QRectF(self.rect()), self.radius, self.margin
        )

        painter.setClipPath(content_path)
        painter.drawPixmap(self.margin, self.margin, self._img.pixmap)

        self.drawbottomtextareacolor(painter, content_path)
        self.drawtextinpath(painter, content_path)

    def drawtextinpath(self, painter: QPainter, path: QPainterPath):
        rect = path.boundingRect()
        cutter = QRectF(
            rect.left(),
            rect.bottom() - self.textareaheight,
            rect.width(),
            self.textareaheight,
        )
        text = savehook_new_data[self.gameuid]["title"]
        painter.setFont(self.textfont)
        pen = QPen()
        pen.setColor(self.textcolor)
        painter.setPen(pen)
        painter.drawText(
            cutter, Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap, text
        )

    def drawbottomtextareacolor(self, painter: QPainter, path: QPainterPath):
        rect = path.boundingRect()
        cutter = QRectF(
            rect.left(), rect.top(), rect.width(), rect.height() - self.textareaheight
        )
        cutter_path = QPainterPath()
        cutter_path.addRect(cutter)
        result_path = path.subtracted(cutter_path)
        painter.fillPath(
            result_path,
            QColor(
                ui_settings["dialog_savegame_layout"].get("textbackColor", "#ffffffff")
            ),
        )

    def get_out_path(self):
        dialog_savegame_layout = ui_settings["dialog_savegame_layout"]
        radius = dialog_savegame_layout.get("radius", 10)
        rect = QRectF(self.rect())
        path_outer = QPainterPath()
        path_outer.addRoundedRect(rect, radius, radius)
        return path_outer

    @property
    def radius(self):
        return ui_settings["dialog_savegame_layout"].get("radius", 10)

    def get_inter_path(self):
        dialog_savegame_layout = ui_settings["dialog_savegame_layout"]
        offset = dialog_savegame_layout.get("borderW", 1)
        radius = dialog_savegame_layout.get("radius", 10)
        return self.get_shrunk_rounded_rect_path(QRectF(self.rect()), radius, offset)

    def get_shrunk_rounded_rect_path(self, rect: QRectF, r, shrink_width):
        shrunk_rect = rect.adjusted(
            shrink_width, shrink_width, -shrink_width, -shrink_width
        )
        new_rx = max(0.0, r - shrink_width)
        new_ry = max(0.0, r - shrink_width)
        path = QPainterPath()
        if shrunk_rect.width() > 0 and shrunk_rect.height() > 0:
            path.addRoundedRect(shrunk_rect, new_rx, new_ry)
        return path


