from qtsymbols import *
import os, functools, uuid
from traceback import print_exc
import qtawesome
from gui.inputdialog import autoinitdialog
from gui.dynalang import LAction
from gui.gamemanager.v3 import dialog_savedgame_v3
from gui.gamemanager.legacy import dialog_savedgame_legacy
from gui.gamemanager.setting import dialog_setting_game, userlabelset
from myutils.utils import targetmod
from myutils.wrapper import Singleton, tryprint
from gui.specialwidget import lazyscrollflow
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
    threeswitch,
    getsimplecombobox,
    FQLineEdit,
    FocusCombo,
)
from gui.gamemanager.common import (
    dialog_syssetting,
    tagitem,
    startgamecheck,
    loadvisinternal,
    getalistname,
    opendirforgameuid,
    CreateShortcutForUid,
    calculatetagidx,
    getreflist,
    getpixfunction,
    showcountgame,
    addgamesingle,
    addgamebatch,
    addgamebatch_x,
)


@Singleton
class dialog_savedgame_integrated(saveposwindow):

    def selectlayout(self, type):
        self.syssettingbtn.setVisible(type != 0)
        try:
            globalconfig["gamemanager_integrated_internal_layout"] = type
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
        self.setWindowIcon(
            qtawesome.icon(globalconfig["toolbutton"]["buttons"]["gamepad_new"]["icon"])
        )
        w = QWidget()
        self.internallayout = QHBoxLayout(w)
        self.internallayout.setContentsMargins(0, 0, 0, 0)
        self.__internal = None
        self.internallayout.addWidget(QWidget())
        self.setCentralWidget(w)

        self.switch = threeswitch(self, icons=["fa.list", "fa.th-list", "fa.th"])
        self.switch.btnclicked.connect(self.selectlayout)
        self.syssettingbtn = IconButton(icon="fa.gear", parent=self)
        self.syssettingbtn.clicked.connect(self.syssetting)
        self.syssettingbtn.sizeChanged.connect(self.do_resize)
        self.switch.sizeChanged.connect(self.do_resize)
        self.show()
        self.switch.selectlayout(globalconfig["gamemanager_integrated_internal_layout"])

    def syssetting(self):
        dialog_syssetting(
            self.__internal,
            type_=globalconfig["gamemanager_integrated_internal_layout"],
        )

    def resizeEvent(self, e: QResizeEvent):
        self.do_resize()

    def do_resize(self, _=None):
        x = self.width() - self.switch.width()
        self.switch.move(x, 0)
        x -= self.syssettingbtn.width()
        self.syssettingbtn.move(x, 0)


class TagWidget(QWidget):
    tagschanged = pyqtSignal(tuple)  # ((tag,type,refdata),)
    linepressedenter = pyqtSignal(str)
    tagclicked = pyqtSignal(tuple)  # tag,type,refdata

    def __init__(self, parent=None, exfoucus=True):
        super().__init__(parent)
        tagitem.setstyles(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lineEdit = FocusCombo()
        if exfoucus:
            self.lineEdit.setLineEdit(FQLineEdit())
            # FQLineEdit导致游戏管理页面里，点击编辑框后，下边界消失。
            # FQLineEdit仅用于和webview同一窗口内焦点缺失问题，所以既然用不到那就不要多此一举了
        else:
            self.lineEdit.setEditable(True)
        self.lineEdit.lineEdit().returnPressed.connect(
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


class IMGWidget(QLabel):

    def adaptsize(self, size: QSize):

        if globalconfig["imagewrapmode"] == 0:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r < max_r:
                new_w = self.width()
                new_h = int(new_w / r)
            else:
                new_h = self.height()
                new_w = int(new_h * r)
            return QSize(new_w, new_h)
        elif globalconfig["imagewrapmode"] == 1:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r > max_r:
                new_w = self.width()
                new_h = int(new_w / r)
            else:
                new_h = self.height()
                new_w = int(new_h * r)
            return QSize(new_w, new_h)
        elif globalconfig["imagewrapmode"] == 2:
            return self.size()
        elif globalconfig["imagewrapmode"] == 3:
            return size

    def setimg(self, pixmap: QPixmap):
        if pixmap.isNull():
            return
        if not (self.height() and self.width()):
            return
        if self.__last == (self.size(), globalconfig["imagewrapmode"]):
            return
        self.__last = (self.size(), globalconfig["imagewrapmode"])
        rate = self.devicePixelRatioF()
        newpixmap = QPixmap(self.size() * rate)
        newpixmap.setDevicePixelRatio(rate)
        newpixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(newpixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(self.getrect(pixmap.size()), pixmap)
        painter.end()
        self.setPixmap(newpixmap)

    def getrect(self, size):
        size = self.adaptsize(size)
        rect = QRect()
        rect.setX(int((self.width() - size.width()) / 2))
        rect.setY(int((self.height() - size.height()) / 2))
        rect.setSize(size)
        return rect

    def resizeEvent(self, a0):
        self.setimg(self._pixmap)
        return super().resizeEvent(a0)

    def __init__(self, p, pixmap) -> None:
        super().__init__(p)
        self.setScaledContents(True)
        if type(pixmap) != QPixmap:
            pixmap = pixmap()
        self._pixmap = pixmap
        self.__last = None

    def switch(self):
        self.setimg(self._pixmap)


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
            self.bottommask.show()
            if self != ItemWidget.globallashfocus:
                ItemWidget.clearfocus()
            ItemWidget.globallashfocus = self
            self.focuschanged.emit(True, self.gameuid)
        except:
            print_exc()

    def mousePressEvent(self, ev) -> None:
        self.click()

    def focusOut(self):
        self.bottommask.hide()
        self.focuschanged.emit(False, self.gameuid)

    def mouseDoubleClickEvent(self, e):
        self.doubleclicked.emit(self.gameuid)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.bottommask.resize(a0.size())
        self.maskshowfileexists.resize(a0.size())

    def others(self):
        self.l.setContentsMargins(
            *([globalconfig["dialog_savegame_layout"]["margin2"]] * 4)
        )

        if self._img._pixmap.isNull():
            pass
        else:
            self._lb.setFixedHeight(globalconfig["dialog_savegame_layout"]["textH"])
            self._img.switch()

    def __init__(self, gameuid) -> None:
        super().__init__()
        self.gameuid = gameuid
        self.maskshowfileexists = QLabel(self)
        self.l = QVBoxLayout(self)
        self.l.setSpacing(0)
        self.l.setContentsMargins(
            *([globalconfig["dialog_savegame_layout"]["margin2"]] * 4)
        )
        for image in savehook_new_data[gameuid].get("imagepath_all", []):
            fr = extradatas["imagefrom"].get(image)
            if fr:
                targetmod.get(fr).dispatchdownloadtask(image)

        self._img = IMGWidget(self, getpixfunction(gameuid))
        self._lb = QLabel(self)
        if self._img._pixmap.isNull():
            self.l.addStretch(1)
        else:
            self._lb.setFixedHeight(globalconfig["dialog_savegame_layout"]["textH"])
            self.l.addWidget(self._img)
        self._lb.setText(savehook_new_data[gameuid]["title"])
        self._lb.setWordWrap(True)
        self._lb.setObjectName("savegame_textfont1")
        self._lb.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.l.addWidget(self._lb)
        exists = os.path.exists(get_launchpath(gameuid))
        self.maskshowfileexists.setObjectName("savegame_exists" + str(exists))
        if not exists:
            self.maskshowfileexists.raise_()
        self.bottommask = QLabel(self)
        self.bottommask.hide()
        self.bottommask.setObjectName("savegame_onselectcolor1")


class dialog_savedgame_new(QWidget):

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        addgamebatch_x(self.addgame, self.reflist, files)

    def clicked2(self):
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

            showcountgame(self._parent, len(self.idxsave))
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
        showcountgame(self._parent, len(self.idxsave))

    def clicked3_batch(self):
        addgamebatch(self.addgame, self.reflist)

    def clicked3(self):
        addgamesingle(self, self.addgame, self.reflist)

    def tagschanged(self, tags):
        self.currtags = tags
        newtags = tags
        self.idxsave.clear()
        ItemWidget.clearfocus()
        self.formLayout.removeWidget(self.flow)
        self.flow.hide()
        self.flow.deleteLater()
        self.flow = lazyscrollflow()
        self.flow.bgclicked.connect(ItemWidget.clearfocus)
        self.flow.setsize(
            QSize(
                globalconfig["dialog_savegame_layout"]["itemw"],
                globalconfig["dialog_savegame_layout"]["itemh"],
            )
        )
        self.flow.setSpacing(globalconfig["dialog_savegame_layout"]["margin"])
        self.formLayout.insertWidget(self.formLayout.count(), self.flow)
        idx = 0
        for k in self.reflist:
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

        showcountgame(self._parent, idx)
        self.flow.directshow()

    def showmenu(self, p):
        menu = QMenu(self)

        editname = LAction("修改列表名称", menu)
        addlist = LAction("创建列表", menu)
        dellist = LAction("删除列表", menu)

        startgame = LAction("开始游戏", menu)
        delgame = LAction("删除游戏", menu)
        opendir = LAction("打开目录", menu)
        addtolist = LAction("添加到列表", menu)
        createlnk = LAction("创建快捷方式", menu)
        gamesetting = LAction("游戏设置", menu)
        addgame = LAction("添加游戏", menu)
        batchadd = LAction("批量添加", menu)

        if self.currentfocusuid:
            exists = os.path.exists(get_launchpath(self.currentfocusuid))
            if exists:
                menu.addAction(startgame)
                menu.addAction(opendir)
                menu.addAction(createlnk)
            menu.addAction(gamesetting)
            menu.addAction(delgame)
            menu.addSeparator()
            menu.addAction(addtolist)
        else:
            if self.reftagid:
                menu.addAction(editname)
            menu.addAction(addlist)
            if self.reftagid:
                menu.addAction(dellist)
            menu.addSeparator()
            menu.addAction(addgame)
            menu.addAction(batchadd)
            menu.addSeparator()
        action = menu.exec(self.mapToGlobal(p))
        if action == startgame:
            startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
        elif action == gamesetting:
            self.showsettingdialog()
        elif action == addtolist:
            self.addtolist()
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
            __d = {
                "k": (
                    savegametaged[calculatetagidx(self.reftagid)]["title"]
                    if action == editname
                    else ""
                )
            }

            def cb(__d):
                title = __d["k"]
                if title != "":
                    i = calculatetagidx(self.reftagid)
                    if action == addlist:
                        tag = {
                            "title": title,
                            "games": [],
                            "uid": str(uuid.uuid4()),
                            "opened": True,
                        }
                        savegametaged.insert(i, tag)
                        self.loadcombo(False)
                    elif action == editname:

                        savegametaged[i]["title"] = title
                        self.loadcombo(False)

            autoinitdialog(
                self,
                __d,
                "修改列表名称" if action == editname else "创建列表",
                600,
                [
                    {
                        "type": "lineedit",
                        "name": "名称",
                        "k": "k",
                    },
                    {
                        "type": "okcancel",
                        "callback": functools.partial(cb, __d),
                    },
                ],
                exec_=True,
            )
        elif action == dellist:
            i = calculatetagidx(self.reftagid)
            savegametaged.pop(i)
            self.loadcombo(False)
            self.reftagid = self.vislistcombo.getIndexData(
                self.vislistcombo.currentIndex()
            )
            self.reflist = getreflist(self.reftagid)

    def directshow(self):
        self.flow.directshow()

    def resetcurrvislist(self, uid):
        self.reftagid = uid
        self.reflist = getreflist(uid)
        self.tagschanged(self.currtags)

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
            static=True,
        )
        self.__layout.insertWidget(0, self.vislistcombo)

    def callexists(self, _):
        if _:
            self.tagswidget.addTag(_TR("存在"), tagitem.TYPE_EXISTS)
        else:
            self.tagswidget.removeTag((_TR("存在"), tagitem.TYPE_EXISTS, None))

    def callchange(self):
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

    def setstyle(self):
        key = "savegame_textfont1"
        fontstring = globalconfig.get(key, "")
        _style = """background-color: rgba(255,255,255, 0);"""
        if fontstring:
            _f = QFont()
            _f.fromString(fontstring)
            _style += "font-size:{}pt;".format(_f.pointSize())
            _style += 'font-family:"{}";'.format(_f.family())
        style = "#{}{{ {} }}".format(key, _style)

        style += "#savegame_existsTrue{{background-color:{};}}".format(
            globalconfig["dialog_savegame_layout"]["backcolor2"]
        )
        style += "#savegame_existsFalse{{background-color:{};}}".format(
            globalconfig["dialog_savegame_layout"]["onfilenoexistscolor2"]
        )
        style += "#savegame_onselectcolor1{{background-color: {};}}".format(
            globalconfig["dialog_savegame_layout"]["onselectcolor2"]
        )
        self.setStyleSheet(style)

    reference = None

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        self.setstyle()
        dialog_savedgame_new.reference = self
        formLayout = QVBoxLayout(self)
        layout = QHBoxLayout()
        self.setAcceptDrops(True)
        layout.setContentsMargins(0, 0, 0, 0)
        self.__layout = layout
        self.loadcombo(True)
        self.reftagid = self.vislistcombo.getIndexData(self.vislistcombo.currentIndex())
        self.reflist = getreflist(self.reftagid)

        self.tagswidget = TagWidget(self, exfoucus=False)

        self.currtags = tuple()
        self.tagswidget.tagschanged.connect(self.tagschanged)
        self.___ = threeswitch(self, [None, None, None, None])
        self.___.setStyleSheet("background:transparent")
        layout.addWidget(self.tagswidget)
        layout.addWidget(self.___)
        formLayout.addLayout(layout)
        self.flow = QWidget()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        formLayout.addWidget(self.flow)
        self.formLayout = formLayout
        self.savebutton = []

        self.idxsave = []
        self.activategamenum = 1
        self.itemfocuschanged(False, None)
        if globalconfig["hide_not_exists"]:
            self.tagswidget.addTag(_TR("存在"), tagitem.TYPE_EXISTS)
        else:
            self.tagschanged(tuple())
        self.installEventFilter(self)

    def eventFilter(self, obj, _):
        try:
            if obj == self:
                dialog_setting_game.reference.raise_()
        except:
            pass
        return False

    def addtolist(self):
        getalistname(
            self,
            lambda x: self.addtolistcallback(x, self.currentfocusuid),
            True,
            self.reftagid,
        )

    def addtolistcallback(self, uid, gameuid):
        if gameuid not in getreflist(uid):
            getreflist(uid).insert(0, gameuid)
        else:
            idx = getreflist(uid).index(gameuid)
            getreflist(uid).insert(0, getreflist(uid).pop(idx))

    def keyPressEvent(self, e: QKeyEvent):
        if self.currentfocusuid:
            if e.key() == Qt.Key.Key_Return:
                startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
            elif e.key() == Qt.Key.Key_Delete:
                self.clicked2()
            elif e.key() == Qt.Key.Key_Left:
                if e.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.moverank(-1)
                else:
                    self.movefocus(-1)
            elif e.key() == Qt.Key.Key_Right:
                if e.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.moverank(1)
                else:
                    self.movefocus(1)
        super().keyPressEvent(e)

    def movefocus(self, dx):
        game = self.currentfocusuid

        idx1 = self.idxsave.index(game)
        idx2 = (idx1 + dx) % len(self.idxsave)

        if idx1 == 0 and dx == -1:
            self.flow.verticalScrollBar().setValue(
                self.flow.verticalScrollBar().maximum()
            )
        else:
            try:
                self.flow.ensureWidgetVisible(self.flow.widget(idx2))
            except:
                pass
        try:
            self.flow.widget(idx2).click()
        except:
            pass

    def moverank(self, dx):
        game = self.currentfocusuid

        idx1 = self.idxsave.index(game)
        idx2 = (idx1 + dx) % len(self.idxsave)
        game2 = self.idxsave[idx2]
        self.idxsave.insert(idx2, self.idxsave.pop(idx1))
        self.flow.switchidx(idx1, idx2)

        try:
            self.flow.ensureWidgetVisible(self.flow.widget(idx2))
        except:
            pass
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
        return gameitem

    def newline(self, k, first=False):

        if first:
            self.idxsave.insert(0, k)
            self.flow.insertwidget(0, functools.partial(self.getagameitem, k, True))
        else:
            self.idxsave.append(k)
            self.flow.addwidget(functools.partial(self.getagameitem, k, False))
