from qtsymbols import *
import os, functools, uuid
from traceback import print_exc
import qtawesome
from gui.dynalang import LAction, LMenu
from gui.gamemanager.v3 import dialog_savedgame_v3
from gui.gamemanager.legacy import dialog_savedgame_legacy
from gui.gamemanager.setting import dialog_setting_game, userlabelset
from myutils.utils import targetmod
from myutils.wrapper import Singleton, tryprint
from gui.specialwidget import lazyscrollflow
from functools import cmp_to_key
import windows
from myutils.config import (
    savehook_new_data,
    savegametaged,
    _TR,
    get_launchpath,
    globalconfig,
    extradatas,
)
from gui.usefulwidget import (
    saveposwindow,
    IconButton,
    getspinbox,
    SplitLine,
    getcolorbutton,
    threeswitch,
    getsimplecombobox,
    request_delete_ok,
    FQLineEdit,
    getIconButton,
    FocusCombo,
    MyInputDialog,
)
from gui.gamemanager.common import (
    getfonteditor,
    dialog_syssetting,
    loadrecentlist,
    tagitem,
    startgamecheck,
    loadvisinternal,
    opendirforgameuid,
    CreateShortcutForUid,
    calculatetagidx,
    getreflist,
    getpixfunction,
    addgamesingle,
    addgamebatch,
    addgamebatch_x,
)


@Singleton
class dialog_savedgame_integrated(saveposwindow):

    def selectlayout(self, type, init=False):
        if not init:
            self.syssettingbtn.setVisible(type != 0)
        try:
            globalconfig["gamemanager_integrated_internal_layout"] = type
            self.do_resize()
            klass = [
                dialog_savedgame_legacy,
                dialog_savedgame_v3,
                dialog_savedgame_new,
            ][type]
            _old = self.internallayout.takeAt(0).widget()
            _old.hide()
            _: dialog_savedgame_new = klass(self)
            self.internallayout.addWidget(_)
            _.directshow()
            _old.deleteLater()
            self.__internal = _
        except:
            print_exc()

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            flags=Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint,
            poslist=globalconfig["savegamedialoggeo"],
        )
        self.setWindowTitle("游戏管理")
        self.setWindowIcon(
            qtawesome.icon(globalconfig["toolbutton"]["buttons"]["gamepad_new"]["icon"])
        )
        w = QWidget()
        self.internallayout = QHBoxLayout(w)
        self.internallayout.setContentsMargins(0, 0, 0, 0)
        self.__internal = None
        self.internallayout.addWidget(QWidget())
        self.setCentralWidget(w)

        self.switch = threeswitch(
            self,
            icons=["fa.list", "fa.th-list", "fa.th"],
            Direction=QBoxLayout.Direction.TopToBottom,
        )
        self.syssettingbtn = IconButton(icon="fa.gear", parent=self, tips="界面设置")
        self.syssettingbtn.clicked.connect(lambda: dialog_syssetting(self.__internal))
        self.syssettingbtn.sizeChanged.connect(self.do_resize)
        self.switch.sizeChanged.connect(self.do_resize)
        self.show()
        self.switch.selectlayout(globalconfig["gamemanager_integrated_internal_layout"])
        self.switch.btnclicked.connect(self.selectlayout)
        self.selectlayout(globalconfig["gamemanager_integrated_internal_layout"], True)

    def showEvent(self, a0):
        self.__check()
        return super().showEvent(a0)

    def __check(self):
        if not (self.hasFocus() and self.underMouse()):
            self.syssettingbtn.hide()
            self.switch.hide()

    def resizeEvent(self, e: QResizeEvent):
        self.do_resize()

    def do_resize(self, _=None):
        if globalconfig["gamemanager_integrated_internal_layout"] in (2,):
            self.switch.setDirection(QBoxLayout.Direction.TopToBottom)
            self.switch.move(0, self.height() - self.switch.height())
            self.syssettingbtn.move(
                0, self.height() - self.switch.height() - self.syssettingbtn.height()
            )
        else:
            self.switch.setDirection(QBoxLayout.Direction.LeftToRight)
            x = self.width() - self.switch.width()
            self.switch.move(x, 0)
            x -= self.syssettingbtn.width()
            self.syssettingbtn.move(x, 0)

    def leaveEvent(self, a0):
        self.switch.hide()
        self.syssettingbtn.hide()
        return super().leaveEvent(a0)

    def enterEvent(self, a0):
        self.switch.show()
        self.syssettingbtn.show()
        return super().enterEvent(a0)


class TagWidget(QWidget):
    tagschanged = pyqtSignal(tuple)  # ((tag,type,refdata),)
    linepressedenter = pyqtSignal(str)
    tagclicked = pyqtSignal(tuple)  # tag,type,refdata

    def __init__(self, parent=None, exfoucus=True):
        super().__init__(parent)
        tagitem.setstyles(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.lineEdit = FocusCombo()
        if exfoucus:
            self.lineEdit.setLineEdit(FQLineEdit())
            # FQLineEdit导致游戏管理页面里，点击编辑框后，下边界消失。
            # FQLineEdit仅用于和webview同一窗口内焦点缺失问题，所以既然用不到那就不要多此一举了
        else:
            self.lineEdit.setEditable(True)
        edit = self.lineEdit.lineEdit()
        action = QAction(edit)
        action.setIcon(qtawesome.icon("fa.search"))
        edit.addAction(action, QLineEdit.ActionPosition.LeadingPosition)
        edit.returnPressed.connect(
            lambda: self.linepressedenter.emit(self.lineEdit.currentText())
        )

        self.lineEdit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )
        self.tagtypes = ["usertags", "developers", "webtags", "usertags"]
        self.tagtypes_zh = ["全部", "开发商", "标签", "自定义"]
        self.tagtypes_1 = [
            tagitem.TYPE_SEARCH,
            tagitem.TYPE_DEVELOPER,
            tagitem.TYPE_TAG,
            tagitem.TYPE_USERTAG,
        ]
        layout.addWidget(self.lineEdit)

        def __(idx):
            t = self.lineEdit.currentText()
            self.lineEdit.clear()
            self.lineEdit.addItems(userlabelset(self.tagtypes[idx]))
            self.lineEdit.setCurrentText(t)

        self.typecombo = getsimplecombobox(self.tagtypes_zh, callback=__)
        layout.addWidget(self.typecombo)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.tag2widget = {}

        def callback(t):
            if not t:
                return
            self.addTag(t, self.tagtypes_1[self.typecombo.currentIndex()])
            self.lineEdit.clearEditText()

        self.linepressedenter.connect(callback)
        self.typecombo.currentIndexChanged.emit(0)

    def addTags(self, tags, signal=True):
        for key in tags:
            self.__addTag(key)
        self.__calltagschanged(signal)

    @tryprint
    def __addTag(self, key):
        tag, _type, refdata = key
        if not tag:
            return
        if key in self.tag2widget:
            return
        qw = tagitem(tag, _type=_type, refdata=refdata)
        qw.removesignal.connect(self.removeTag)
        qw.labelclicked.connect(self.tagclicked.emit)
        layout: QHBoxLayout = self.layout()
        layout.insertWidget(layout.count() - 2, qw)
        self.tag2widget[key] = qw
        self.lineEdit.setFocus()

    def addTag(self, tag, _type, refdata=None, signal=True):
        self.__addTag((tag, _type, refdata))
        self.__calltagschanged(signal)

    def __removeTag(self, key):
        _w = self.tag2widget[key]
        self.layout().removeWidget(_w)
        self.tag2widget.pop(key)

    def removeTag(self, key, signal=True):
        try:
            self.__removeTag(key)
            self.__calltagschanged(signal)
        except:
            pass

    def __calltagschanged(self, signal):
        if signal:
            self.tagschanged.emit(tuple(self.tag2widget.keys()))

    def clearTag(self, signal=True):
        for key in self.tag2widget.copy():
            try:
                self.__removeTag(key)
            except:
                pass
        self.__calltagschanged(signal)


class imagehelper:
    def size(self):
        return QSizeF(self.p.width() - 2 * self.p.margin, self.p.imageheight)

    def height(self):
        return self.size().height()

    def width(self):
        return self.size().width()

    def rect(self):
        return QRectF(QPoint(0, 0), self.size())

    def adaptsize(self, size: QSize):

        if globalconfig["imagewrapmode"] == 0:
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
        elif globalconfig["imagewrapmode"] == 1:
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
        elif globalconfig["imagewrapmode"] == 2:
            return QSizeF(self.size())
        elif globalconfig["imagewrapmode"] == 3:
            return QSizeF(size)

    def setimg(self):
        self._setimg(self._pixmap)

    def _setimg(self, pixmap: QPixmap):
        if pixmap.isNull():
            return
        if not (self.height() and self.width()):
            return
        if self.__last == (self.size(), globalconfig["imagewrapmode"]):
            return
        self.__last = (self.size(), globalconfig["imagewrapmode"])
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
        self.click()

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
        self.gameuid = gameuid

        for image in savehook_new_data[gameuid].get("imagepath_all", []):
            fr = extradatas["imagefrom"].get(image)
            if fr:
                targetmod.get(fr).dispatchdownloadtask(image)

        self._img = imagehelper(self, getpixfunction(gameuid))
        exists = os.path.exists(get_launchpath(gameuid))
        self.setObjectName("savegame_exists" + str(exists))
        self.setToolTip(savehook_new_data[gameuid]["title"])

    @property
    def margin(self):
        return (
            globalconfig["dialog_savegame_layout"]["margin2"]
            + globalconfig["dialog_savegame_layout"]["borderW"]
        )

    @property
    def imageheight(self):
        if globalconfig["dialog_savegame_layout"]["layout"] == "updown":
            return self.height() - self.margin * 2 - self.textareaheight
        if globalconfig["dialog_savegame_layout"]["layout"] == "overlay":
            return self.height() - self.margin * 2

    @property
    def textcolor(self):
        return QColor(globalconfig["dialog_savegame_layout"]["textColor"])

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
        h = globalconfig["dialog_savegame_layout"]["textH2"] * h
        return h

    def paintEvent(self, a0):
        dialog_savegame_layout = globalconfig["dialog_savegame_layout"]
        hasFocus = dialog_savegame_layout["onselectcolor2"] if self.isfucked else None
        background = dialog_savegame_layout[
            (
                "backcolor2",
                "onfilenoexistscolor2",
            )[self.objectName() == "savegame_existsFalse"]
        ]
        bordercolor = dialog_savegame_layout[
            (
                "borderColor",
                "borderColor2",
            )[self.isfucked]
        ]
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
            result_path, QColor(globalconfig["dialog_savegame_layout"]["textbackColor"])
        )

    def get_out_path(self):
        dialog_savegame_layout = globalconfig["dialog_savegame_layout"]
        radius = dialog_savegame_layout["radius"]
        rect = QRectF(self.rect())
        path_outer = QPainterPath()
        path_outer.addRoundedRect(rect, radius, radius)
        return path_outer

    @property
    def radius(self):
        return globalconfig["dialog_savegame_layout"]["radius"]

    def get_inter_path(self):
        dialog_savegame_layout = globalconfig["dialog_savegame_layout"]
        offset = dialog_savegame_layout["borderW"]
        radius = dialog_savegame_layout["radius"]
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


class dialog_savedgame_new(QSplitter):

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        addgamebatch_x(self.addgame, self.reflist, files)

    def clicked2(self):
        if not request_delete_ok(self, "bf4aa76a-41a5-4b07-a095-0c34c616ed2d"):
            return
        try:
            game = self.currentfocusuid
            idx2 = self.reflist.index(game)
            self.reflist.pop(idx2)

            idx2 = self.idxsave.index(game)
            self.flow.removeidx(idx2)
            self.idxsave.pop(idx2)
            ItemWidget.clearfocus()
            try:
                self.flow.widget(idx2).click()
            except:
                self.flow.widget(idx2 - 1).click()

        except:
            print_exc()

    def clicked4(self):
        opendirforgameuid(self.currentfocusuid)

    def addgame(self, uid):
        if uid not in self.idxsave:
            self.newline(uid, first=True)
        else:
            idx = self.idxsave.index(uid)
            self.idxsave.pop(idx)
            self.idxsave.insert(0, uid)
            self.flow.totop1(idx)

    def clicked3_batch(self):
        addgamebatch(self.addgame, self.reflist)

    def clicked3(self):
        addgamesingle(self, self.addgame, self.reflist)

    @property
    def reflistx(self):
        if self.reflist != 1:
            return self.reflist
        return loadrecentlist()

    def tagschanged(self, tags):
        self.currtags = tags
        newtags = tags
        self.idxsave.clear()
        ItemWidget.clearfocus()
        self.flow.hide()
        self.flow.deleteLater()
        self.flow = lazyscrollflow(self.keypressed)
        self.flow.setObjectName("NOBORDER")
        self.flow.bgclicked.connect(ItemWidget.clearfocus)
        self.flow.setsize(
            QSize(
                globalconfig["dialog_savegame_layout"]["itemw"],
                globalconfig["dialog_savegame_layout"]["itemh"],
            )
        )
        self.flow.setSpacing(globalconfig["dialog_savegame_layout"]["margin"])
        self.flowcontainer.addWidget(self.flow)
        idx = 0
        for k in self.reflistx:
            if newtags != self.currtags:
                break
            notshow = False
            webtags = [
                globalconfig["tagNameRemap"].get(tag, tag)
                for tag in savehook_new_data[k]["webtags"]
            ]
            for tag, _type, _ in tags:
                if _type == tagitem.TYPE_EXISTS:
                    if os.path.exists(get_launchpath(k)) == False:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_DEVELOPER:
                    if tag not in savehook_new_data[k]["developers"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_TAG:
                    if tag not in webtags:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_USERTAG:
                    if tag not in savehook_new_data[k]["usertags"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_SEARCH:
                    if (
                        tag not in webtags
                        and tag not in savehook_new_data[k]["usertags"]
                        and tag not in savehook_new_data[k]["title"]
                        and tag not in savehook_new_data[k]["developers"]
                    ):
                        notshow = True
                        break
            if notshow:
                continue
            self.newline(k, idx == 0)
            idx += 1
        self.flow.directshow()

    def showmenu(self, p):
        menu = QMenu(self)

        editname = LAction("修改列表名称", menu)
        addlist = LAction("创建列表", menu)
        dellist = LAction("删除列表", menu)

        startgame = LAction("开始游戏", menu)
        delgame = LAction("删除游戏", menu)
        opendir = LAction("打开目录", menu)
        createlnk = LAction("创建快捷方式", menu)
        gamesetting = LAction("游戏设置", menu)
        addgame = LAction("添加游戏", menu)
        batchadd = LAction("批量添加", menu)

        if self.currentfocusuid:
            lc = get_launchpath(self.currentfocusuid)
            exists = os.path.exists(lc)
            if exists:
                menu.addAction(startgame)
                menu.addAction(opendir)
                menu.addAction(createlnk)
            elif os.path.exists(os.path.dirname(lc)):
                menu.addAction(opendir)
            menu.addAction(gamesetting)
            if self.reftagid not in (1,):
                menu.addAction(delgame)
            menu.addSeparator()
            __vis, __uid = loadvisinternal(
                True, self.reftagid, recent=False, global_=False
            )
            if __uid:
                addtolist = LMenu("添加到列表", menu)
                menu.addMenu(addtolist)
                for _ in range(len(__vis)):
                    a = LAction(__vis[_], addtolist)
                    a.setData(__uid[_])
                    addtolist.addAction(a)
        else:
            if self.reftagid not in (None, 1):
                menu.addAction(editname)
            menu.addAction(addlist)
            if self.reftagid not in (None, 1):
                menu.addAction(dellist)
            menu.addSeparator()
            if self.reftagid not in (1,):
                menu.addAction(addgame)
                menu.addAction(batchadd)
            menu.addSeparator()
        action = menu.exec(self.mapToGlobal(p))
        if action == startgame:
            startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
        elif action == gamesetting:
            self.showsettingdialog()
        elif action == createlnk:
            CreateShortcutForUid(self.currentfocusuid)
        elif action == delgame:
            self.clicked2()
        elif action == opendir:
            self.clicked4()
        elif action == addgame:
            self.clicked3()
        elif action == batchadd:
            self.clicked3_batch()

        elif action == editname or action == addlist:

            def cb(title):
                if not title:
                    return
                i = calculatetagidx(self.reftagid)
                if action == addlist:
                    tag = {
                        "title": title,
                        "games": [],
                        "uid": str(uuid.uuid4()),
                        "opened": True,
                    }
                    savegametaged.insert(i, tag)
                    globalconfig["currvislistuid"] = tag["uid"]
                    self.loadcombo(False)
                    self.refresh_curr()
                elif action == editname:

                    savegametaged[i]["title"] = title
                    self.loadcombo(False)

            __ = (
                savegametaged[calculatetagidx(self.reftagid)]["title"]
                if action == editname
                else ""
            )
            cb(
                MyInputDialog(
                    self,
                    "修改列表名称" if action == editname else "创建列表",
                    "名称",
                    __,
                )
            )

        elif action == dellist:
            if request_delete_ok(self, "90063a5b-1e96-4688-ac1c-ee3c1ba5d275"):
                i = calculatetagidx(self.reftagid)
                savegametaged.pop(i)
                self.loadcombo(False)
                self.refresh_curr()

        elif action:  # addtolist
            __uid = action.data()
            if __uid:
                self.addtolistcallback(__uid, self.currentfocusuid)

    def refresh_curr(self):

        self.reftagid = self.vislistcombo.getIndexData(self.vislistcombo.currentIndex())
        self.reflist = getreflist(self.reftagid)
        self.tagschanged(self.currtags)

    def directshow(self):
        self.flow.directshow()

    def resetcurrvislist(self, uid):
        self.reftagid = uid
        self.reflist = getreflist(uid)
        self.tagschanged(self.currtags)
        self.vislistcombo.setFocus()

    def loadcombo(self, init):
        vis, uid = loadvisinternal()
        if not init:
            w = self.__layout.itemAt(0).widget()
            self.__layout.removeWidget(w)
            w.hide()
            w.deleteLater()
        self.vislistcombo = getsimplecombobox(
            vis,
            globalconfig,
            "currvislistuid",
            self.resetcurrvislist,
            internal=uid,
        )
        self.__layout.insertWidget(0, self.vislistcombo)

    def callexists(self, _):
        if _:
            self.tagswidget.addTag(_TR("存在"), tagitem.TYPE_EXISTS)
        else:
            self.tagswidget.removeTag((_TR("存在"), tagitem.TYPE_EXISTS, None))

    def callchange(self, _=None):
        self.flow.setsize(
            QSize(
                globalconfig["dialog_savegame_layout"]["itemw"],
                globalconfig["dialog_savegame_layout"]["itemh"],
            )
        )
        self.flow.setSpacing(globalconfig["dialog_savegame_layout"]["margin"])
        self.flow.resizeandshow()
        for _ in self.flow.widgets:
            if not isinstance(_, ItemWidget):
                continue
            _.others()

    def createsettings(self, formLayout: QFormLayout):

        for i, (key, name) in enumerate(
            [
                ("itemw", "宽度"),
                ("itemh", "高度"),
                ("margin", "边距_inter"),
                ("margin2", "边距_intra"),
                ("radius", "圆角"),
                ("borderW", "边框宽度"),
            ]
        ):
            minv = 0 if i >= 2 else 32
            spin = getspinbox(minv, 1000, globalconfig["dialog_savegame_layout"], key)
            formLayout.addRow(name, spin)
            if "radius" == key:
                spin.valueChanged.connect(self.callchange)
            elif "borderW" == key:
                spin.valueChanged.connect(
                    lambda _: (self.callchange(), self.callchange())
                )
            else:
                spin.valueChanged.connect(self.callchange)

        formLayout.addRow(
            "缩放",
            getsimplecombobox(
                ["填充", "适应", "拉伸", "居中"],
                globalconfig,
                "imagewrapmode",
                callback=self.callchange,
            ),
        )

        formLayout.addRow(SplitLine())
        for key, name in [
            ("backcolor2", "颜色"),
            ("onselectcolor2", "颜色_选中时"),
            ("onfilenoexistscolor2", "游戏不存在时颜色"),
            ("borderColor", "边框颜色"),
            ("borderColor2", "边框颜色_选中时"),
        ]:
            formLayout.addRow(
                name,
                getcolorbutton(
                    self,
                    globalconfig["dialog_savegame_layout"],
                    key,
                    callback=self.callchange,
                    alpha=True,
                ),
            )
        formLayout.addRow(SplitLine())
        formLayout.addRow(
            "文字区_高度",
            getspinbox(
                0,
                1000,
                globalconfig["dialog_savegame_layout"],
                "textH2",
                callback=self.callchange,
                double=False,
            ),
        )
        formLayout.addRow(
            "文字区_布局",
            getsimplecombobox(
                ["上下", "悬浮"],
                globalconfig["dialog_savegame_layout"],
                "layout",
                callback=self.callchange,
                internal=["updown", "overlay"],
            ),
        )
        formLayout.addRow(
            "字体",
            getfonteditor(
                d=globalconfig,
                k="savegame_textfont1",
                callback=lambda _: self.callchange(),
            ),
        )
        formLayout.addRow(
            "颜色_文字",
            getcolorbutton(
                self,
                globalconfig["dialog_savegame_layout"],
                "textColor",
                callback=self.callchange,
            ),
        )
        formLayout.addRow(
            "颜色_文字区",
            getcolorbutton(
                self,
                globalconfig["dialog_savegame_layout"],
                "textbackColor",
                callback=self.callchange,
                alpha=True,
            ),
        )

    reference = None

    def sortgamecallback(self):
        if self.reflist == 1:
            return
        menu = QMenu(self)
        sortbytime = LAction("按添加时间排序", menu)
        sortbytime.setIcon(qtawesome.icon("fa.sort-numeric-asc"))
        menu.addAction(sortbytime)
        sortbytimede = LAction("按添加时间排序_降序", menu)
        sortbytimede.setIcon(qtawesome.icon("fa.sort-numeric-desc"))
        menu.addAction(sortbytimede)
        sortbyname = LAction("按名称排序", menu)
        sortbyname.setIcon(qtawesome.icon("fa.sort-alpha-asc"))
        menu.addAction(sortbyname)
        sortbynamedesc = LAction("按名称排序_降序", menu)
        sortbynamedesc.setIcon(qtawesome.icon("fa.sort-alpha-desc"))
        menu.addAction(sortbynamedesc)
        action = menu.exec(QCursor.pos())

        def unsafetrygettime(uid: str):
            __ = savehook_new_data[uid]
            t = __.get("createtime")
            if not t:
                try:
                    t = float(uid.split("_")[0])
                except:
                    t = 0
            return t

        if action in (sortbytime, sortbytimede):
            self.reflist.sort(key=unsafetrygettime, reverse=action != sortbytimede)
            self.tagschanged(self.currtags)
        elif action in (sortbyname, sortbynamedesc):
            paircmp = lambda a, b: windows.StrCmpLogicalW(
                savehook_new_data[a]["title"], savehook_new_data[b]["title"]
            )
            self.reflist.sort(
                key=cmp_to_key(paircmp),
                reverse=action == sortbynamedesc,
            )
            self.tagschanged(self.currtags)

    def event(self, e: QEvent):
        if e.type() == QEvent.Type.FontChange:
            self.topw.setFixedHeight(self.topw.sizeHint().height())
        return super().event(e)

    def createHandle(self):
        class MySplitterHandle(QSplitterHandle):
            def paintEvent(self1, event):
                if self1.underMouse():
                    super().paintEvent(event)
                else:
                    pass

        return MySplitterHandle(self.orientation(), self)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        dialog_savedgame_new.reference = self
        self.setObjectName("NOBORDER")
        self.setOrientation(Qt.Orientation.Vertical)
        self.setHandleWidth(1)
        _w = QWidget()
        self.topw = _w
        layout = QHBoxLayout(_w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setAcceptDrops(True)
        self.__layout = layout
        self.loadcombo(True)
        self.reftagid = self.vislistcombo.getIndexData(self.vislistcombo.currentIndex())
        self.reflist = getreflist(self.reftagid)

        self.tagswidget = TagWidget(self, exfoucus=False)

        self.currtags = tuple()
        self.tagswidget.tagschanged.connect(self.tagschanged)
        layout.addWidget(self.tagswidget)
        layout.addWidget(
            getIconButton(
                icon="fa.sort-amount-asc", callback=self.sortgamecallback, tips="排序"
            )
        )
        self.addWidget(_w)
        __ = QWidget()
        self.flowcontainer = QHBoxLayout(__)
        self.flowcontainer.setContentsMargins(0, 0, 0, 0)
        self.flow = QWidget()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        self.addWidget(__)
        self.savebutton = []

        self.idxsave = []
        self.activategamenum = 1
        self.itemfocuschanged(False, None)
        if globalconfig["hide_not_exists"]:
            self.tagswidget.addTag(_TR("存在"), tagitem.TYPE_EXISTS)
        else:
            self.tagschanged(tuple())
        self.installEventFilter(self)

        def __(_):
            globalconfig["dialogsplit"] = self.sizes()

        if "dialogsplit" in globalconfig:
            self.setSizes(globalconfig["dialogsplit"])
        self.splitterMoved.connect(__)

    def eventFilter(self, obj, _):
        try:
            if obj == self:
                dialog_setting_game.reference.raise_()
        except:
            pass
        return False

    def addtolistcallback(self, uid, gameuid):
        if gameuid not in getreflist(uid):
            getreflist(uid).insert(0, gameuid)
        else:
            idx = getreflist(uid).index(gameuid)
            getreflist(uid).insert(0, getreflist(uid).pop(idx))

    def keypressed(self, e: QKeyEvent):
        if self.currentfocusuid:

            if e.key() == Qt.Key.Key_Return:
                startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
            elif e.key() == Qt.Key.Key_Delete:
                self.clicked2()
            elif e.key() in (
                Qt.Key.Key_Left,
                Qt.Key.Key_Right,
                Qt.Key.Key_Down,
                Qt.Key.Key_Up,
            ):
                offset = self.flow.calc_last_next_line_offset(
                    self.idxsave.index(self.currentfocusuid),
                    e.key() in (Qt.Key.Key_Up, Qt.Key.Key_Left),
                    shu=e.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down),
                )
                if e.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.moverank(offset)
                else:
                    self.movefocus(offset)

    def movefocus(self, dx):
        game = self.currentfocusuid
        idx1 = self.idxsave.index(game)
        idx2 = (idx1 + dx) % len(self.idxsave)

        self.flow.enableidx(idx2)
        self.flow.ensureWidgetVisible(self.flow.widget(idx2))

        try:
            self.flow.widget(idx2).click()
        except:
            pass

    def moverank(self, dx):
        if self.reflist == 1:
            return
        game = self.currentfocusuid

        idx1 = self.idxsave.index(game)
        idx2 = (idx1 + dx) % len(self.idxsave)
        game2 = self.idxsave[idx2]
        self.idxsave.insert(idx2, self.idxsave.pop(idx1))
        self.flow.switchidx(idx1, idx2)

        self.flow.ensureWidgetVisible(self.flow.widget(idx2))
        idx1 = self.reflist.index(game)
        idx2 = self.reflist.index(game2)
        self.reflist.insert(idx2, self.reflist.pop(idx1))

    def showsettingdialog(self):
        try:
            dialog_setting_game(self.parent(), self.currentfocusuid)
        except:
            print_exc()

    def itemfocuschanged(self, b, k):

        if b:
            self.currentfocusuid = k
        else:
            self.currentfocusuid = None

        for _btn, exists in self.savebutton:
            _able1 = b and (
                (not exists)
                or (self.currentfocusuid)
                and (os.path.exists(get_launchpath(self.currentfocusuid)))
            )
            _btn.setEnabled(_able1)

    def getagameitem(self, k, focus):
        gameitem = ItemWidget(k)
        gameitem.doubleclicked.connect(
            functools.partial(startgamecheck, self, getreflist(self.reftagid))
        )
        gameitem.focuschanged.connect(self.itemfocuschanged)
        if focus:
            gameitem.click()
            self.flow.setFocus()
        return gameitem

    def newline(self, k, first=False):

        if first:
            self.idxsave.insert(0, k)
            self.flow.insertwidget(0, functools.partial(self.getagameitem, k, True))
        else:
            self.idxsave.append(k)
            self.flow.addwidget(functools.partial(self.getagameitem, k, False))
