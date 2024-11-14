from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from qtsymbols import *
import os, functools, uuid
from traceback import print_exc
import gobject, qtawesome
from gui.dynalang import LPushButton, LAction
from gui.dialog_savedgame_v3 import dialog_savedgame_v3
from gui.dialog_savedgame_legacy import dialog_savedgame_legacy
from gui.dialog_savedgame_setting import dialog_setting_game, userlabelset
from myutils.wrapper import Singleton_close
from gui.specialwidget import lazyscrollflow
from myutils.utils import str2rgba
from myutils.config import (
    savehook_new_data,
    savegametaged,
    _TR,
    get_launchpath,
    globalconfig,
)
from gui.usefulwidget import (
    saveposwindow,
    getboxlayout,
    MySwitch,
    Prompt_dialog,
    getsimplecombobox,
)
from gui.dialog_savedgame_common import (
    ItemWidget,
    dialog_syssetting,
    tagitem,
    TagWidget,
    startgamecheck,
    loadvisinternal,
    getalistname,
    opendirforgameuid,
    calculatetagidx,
    getreflist,
    getpixfunction,
    showcountgame,
    addgamesingle,
    addgamebatch,
    addgamebatch_x,
)


@Singleton_close
class dialog_savedgame_integrated(saveposwindow):

    def selectlayout(self, type):
        try:
            globalconfig["gamemanager_integrated_internal_layout"] = type
            klass = [
                dialog_savedgame_new,
                dialog_savedgame_v3,
                dialog_savedgame_legacy,
            ][type]

            [self.layout1btn, self.layout2btn, self.layout3btn][(type) % 3].setEnabled(
                False
            )
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 1) % 3
            ].setEnabled(False)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 2) % 3
            ].setEnabled(False)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 1) % 3
            ].setChecked(False)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 2) % 3
            ].setChecked(False)
            _old = self.internallayout.takeAt(0).widget()
            _old.hide()
            _ = klass(self)
            self.internallayout.addWidget(_)
            _.directshow()
            _old.deleteLater()
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 1) % 3
            ].setEnabled(True)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 2) % 3
            ].setEnabled(True)
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
        w, self.internallayout = getboxlayout(
            [], margin0=True, makewidget=True, both=True
        )

        self.internallayout.addWidget(QWidget())
        self.setCentralWidget(w)
        self.layout1btn = MySwitch(self, icon="fa.th")
        self.layout2btn = MySwitch(self, icon="fa.th-list")
        self.layout3btn = MySwitch(self, icon="fa.list")
        self.layout1btn.clicked.connect(functools.partial(self.selectlayout, 0))
        self.layout2btn.clicked.connect(functools.partial(self.selectlayout, 1))
        self.layout3btn.clicked.connect(functools.partial(self.selectlayout, 2))
        self.layout1btn.setFixedSize(QSize(20, 20))
        self.layout2btn.setFixedSize(QSize(20, 20))
        self.layout3btn.setFixedSize(QSize(20, 20))
        self.show()
        self.selectlayout(globalconfig["gamemanager_integrated_internal_layout"])

    def resizeEvent(self, e: QResizeEvent):
        self.layout1btn.move(e.size().width() - self.layout1btn.width(), 0)
        self.layout2btn.move(
            e.size().width() - self.layout2btn.width() - self.layout1btn.width(), 0
        )
        self.layout3btn.move(
            e.size().width()
            - self.layout3btn.width()
            - self.layout2btn.width()
            - self.layout1btn.width(),
            0,
        )


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
        self.formLayout.insertWidget(self.formLayout.count() - 1, self.flow)
        idx = 0
        for k in self.reflist:
            if newtags != self.currtags:
                break
            notshow = False
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
                    if tag not in savehook_new_data[k]["webtags"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_USERTAG:
                    if tag not in savehook_new_data[k]["usertags"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_RAND:
                    if (
                        tag not in savehook_new_data[k]["webtags"]
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

        editname = LAction(("修改列表名称"))
        addlist = LAction(("创建列表"))
        dellist = LAction(("删除列表"))

        startgame = LAction(("开始游戏"))
        delgame = LAction(("删除游戏"))
        opendir = LAction(("打开目录"))
        addtolist = LAction(("添加到列表"))
        gamesetting = LAction(("游戏设置"))
        addgame = LAction(("添加游戏"))
        batchadd = LAction(("批量添加"))
        othersetting = LAction(("其他设置"))

        if self.currentfocusuid:
            exists = os.path.exists(get_launchpath(self.currentfocusuid))
            if exists:
                menu.addAction(startgame)
            if exists:
                menu.addAction(opendir)
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
            menu.addAction(othersetting)
        action = menu.exec(self.mapToGlobal(p))
        if action == startgame:
            startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
        elif action == gamesetting:
            self.showsettingdialog()
        elif action == addtolist:
            self.addtolist()
        elif action == delgame:
            self.clicked2()
        elif action == opendir:
            self.clicked4()
        elif action == addgame:
            self.clicked3()
        elif action == batchadd:
            self.clicked3_batch()
        elif action == othersetting:
            dialog_syssetting(self)

        elif action == editname or action == addlist:
            _dia = Prompt_dialog(
                self,
                "修改列表名称" if action == editname else "创建列表",
                "",
                [
                    [
                        "名称",
                        (
                            savegametaged[calculatetagidx(self.reftagid)]["title"]
                            if action == editname
                            else ""
                        ),
                    ],
                ],
            )

            if _dia.exec():

                title = _dia.text[0].text()
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
        elif action == dellist:
            i = calculatetagidx(self.reftagid)
            savegametaged.pop(i)
            self.loadcombo(False)
            self.resetcurrvislist(globalconfig["currvislistuid"])

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
        self.__layout.insertWidget(
            0,
            getsimplecombobox(
                vis,
                globalconfig,
                "currvislistuid",
                self.resetcurrvislist,
                internal=uid,
                static=True,
            ),
        )

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
        for exits in [True, False]:
            c = globalconfig["dialog_savegame_layout"][
                ("onfilenoexistscolor1", "backcolor1")[exits]
            ]
            c = str2rgba(
                c,
                globalconfig["dialog_savegame_layout"][
                    ("transparentnotexits", "transparent")[exits]
                ],
            )

            style += "#savegame_exists{}{{background-color:{};}}".format(exits, c)
        style += "#savegame_onselectcolor1{{background-color: {};}}".format(
            str2rgba(
                globalconfig["dialog_savegame_layout"]["onselectcolor1"],
                globalconfig["dialog_savegame_layout"]["transparentselect"],
            )
        )
        self.setStyleSheet(style)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._parent = parent
        self.setstyle()
        gobject.global_dialog_savedgame_new = self
        formLayout = QVBoxLayout()
        layout = QHBoxLayout()
        self.setAcceptDrops(True)
        layout.setContentsMargins(0, 0, 0, 0)
        self.__layout = layout
        self.loadcombo(True)
        self.reflist = getreflist(globalconfig["currvislistuid"])
        self.reftagid = globalconfig["currvislistuid"]

        def callback(t):
            if not t:
                return
            labelset = userlabelset()
            if t in labelset:
                tp = tagitem.TYPE_USERTAG
            else:
                tp = tagitem.TYPE_RAND
            self.tagswidget.addTag(t, tp)

            self.tagswidget.lineEdit.clear()
            self.tagswidget.lineEdit.addItems(labelset)
            self.tagswidget.lineEdit.clearEditText()

        self.tagswidget = TagWidget(self, exfoucus=False)
        self.tagswidget.lineEdit.addItems(userlabelset())
        self.tagswidget.lineEdit.setCurrentText("")
        self.tagswidget.linepressedenter.connect(callback)
        self.currtags = tuple()
        self.tagswidget.tagschanged.connect(self.tagschanged)
        _ = QLabel()
        _.setFixedWidth(60)
        layout.addWidget(self.tagswidget)
        layout.addWidget(_)
        formLayout.addLayout(layout)
        self.flow = QWidget()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        formLayout.addWidget(self.flow)
        self.formLayout = formLayout
        buttonlayout = QHBoxLayout()
        self.buttonlayout = buttonlayout
        self.savebutton = []
        self.simplebutton(
            "开始游戏",
            True,
            lambda: startgamecheck(
                self, getreflist(self.reftagid), self.currentfocusuid
            ),
            True,
        )
        self.simplebutton("游戏设置", True, self.showsettingdialog, False)
        self.simplebutton("删除游戏", True, self.clicked2, False)
        self.simplebutton("打开目录", True, self.clicked4, True)

        self.simplebutton("添加到列表", True, self.addtolist, False)
        # if globalconfig["startgamenototop"]:
        self.simplebutton("左移", True, functools.partial(self.moverank, -1), False)
        self.simplebutton("右移", True, functools.partial(self.moverank, 1), False)
        self.simplebutton("添加游戏", False, self.clicked3, 1)
        self.simplebutton("批量添加", False, self.clicked3_batch, 1)
        self.simplebutton("其他设置", False, lambda: dialog_syssetting(self), False)
        formLayout.addLayout(buttonlayout)
        self.idxsave = []
        self.setLayout(formLayout)
        self.activategamenum = 1
        self.itemfocuschanged(False, None)
        if globalconfig["hide_not_exists"]:
            self.tagswidget.addTag(_TR("存在"), tagitem.TYPE_EXISTS)
        else:
            self.tagschanged(tuple())

        class WindowEventFilter(QObject):
            def eventFilter(__, obj, event):
                try:
                    if obj == self:
                        gobject.global_dialog_setting_game.raise_()
                except:
                    pass
                return False

        self.__filter = WindowEventFilter()  # keep ref
        self.installEventFilter(self.__filter)

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

    def moverank(self, dx):
        game = self.currentfocusuid

        idx1 = self.idxsave.index(game)
        idx2 = (idx1 + dx) % len(self.idxsave)
        game2 = self.idxsave[idx2]
        self.idxsave.insert(idx2, self.idxsave.pop(idx1))
        self.flow.switchidx(idx1, idx2)

        idx1 = self.reflist.index(game)
        idx2 = self.reflist.index(game2)
        self.reflist.insert(idx2, self.reflist.pop(idx1))

    def showsettingdialog(self):
        try:
            dialog_setting_game(self.parent(), self.currentfocusuid)
        except:
            print_exc()

    def simplebutton(self, text, save, callback, exists):
        button5 = LPushButton(text)
        button5.setMinimumWidth(10)
        if save:
            self.savebutton.append((button5, exists))
        button5.clicked.connect(callback)
        button5.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.buttonlayout.addWidget(button5)
        return button5

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
        gameitem = ItemWidget(
            k, functools.partial(getpixfunction, k), savehook_new_data[k]["title"]
        )
        gameitem.doubleclicked.connect(
            functools.partial(startgamecheck, self, getreflist(self.reftagid))
        )
        gameitem.focuschanged.connect(self.itemfocuschanged)
        if focus:
            gameitem.click()
        return gameitem

    def newline(self, k, first=False):

        itemw = globalconfig["dialog_savegame_layout"]["itemw"]
        itemh = globalconfig["dialog_savegame_layout"]["itemh"]

        if first:
            self.idxsave.insert(0, k)
            self.flow.insertwidget(
                0, (functools.partial(self.getagameitem, k, True), QSize(itemw, itemh))
            )
        else:
            self.idxsave.append(k)
            self.flow.addwidget(
                (functools.partial(self.getagameitem, k, False), QSize(itemw, itemh))
            )
