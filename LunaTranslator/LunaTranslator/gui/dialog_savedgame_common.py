from qtsymbols import *
import os, functools
from traceback import print_exc
from myutils.wrapper import tryprint, threader, Singleton_close
from myutils.utils import str2rgba, find_or_create_uid, duplicateconfig
from myutils.hwnd import getExeIcon
import gobject, hashlib
from gui.inputdialog import autoinitdialog
from gui.dynalang import LFormLayout, LDialog
from myutils.localetools import localeswitchedrun
from myutils.config import (
    savehook_new_data,
    savegametaged,
    uid2gamepath,
    get_launchpath,
    _TR,
    savehook_new_list,
    globalconfig,
)
from gui.usefulwidget import (
    getIconButton,
    FocusCombo,
    getsimplecombobox,
    getspinbox,
    getcolorbutton,
    getsimpleswitch,
    FQLineEdit,
    getspinbox,
    selectcolor,
)


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
            self.bottommask.setStyleSheet(
                f'background-color: {str2rgba(globalconfig["dialog_savegame_layout"]["onselectcolor1"],globalconfig["dialog_savegame_layout"]["transparentselect"])};'
            )

            if self != ItemWidget.globallashfocus:
                ItemWidget.clearfocus()
            ItemWidget.globallashfocus = self
            self.focuschanged.emit(True, self.gameuid)
        except:
            print_exc()

    def mousePressEvent(self, ev) -> None:
        self.click()

    def focusOut(self):
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.focuschanged.emit(False, self.gameuid)

    def mouseDoubleClickEvent(self, e):
        self.doubleclicked.emit(self.gameuid)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.bottommask.resize(a0.size())
        self.maskshowfileexists.resize(a0.size())

    def __init__(self, gameuid, pixmap, file) -> None:
        super().__init__()
        self.itemw = globalconfig["dialog_savegame_layout"]["itemw"]
        self.itemh = globalconfig["dialog_savegame_layout"]["itemh"]
        # self.imgw = globalconfig["dialog_savegame_layout"]["imgw"]
        # self.imgh = globalconfig["dialog_savegame_layout"]["imgh"]
        # margin = (
        #     self.itemw - self.imgw
        # ) // 2  # globalconfig['dialog_savegame_layout']['margin']
        margin = globalconfig["dialog_savegame_layout"]["margin"]
        if globalconfig["showgametitle"]:
            textH = globalconfig["dialog_savegame_layout"]["textH"]
        else:
            textH = 0
        self.imgw = self.itemw - 2 * margin
        self.imgh = self.itemh - textH - 2 * margin
        #
        self.setFixedSize(QSize(self.itemw, self.itemh))
        # self.setFocusPolicy(Qt.StrongFocus)
        self.maskshowfileexists = QLabel(self)
        self.bottommask = QLabel(self)
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._img = IMGWidget(self.imgw, self.imgh, pixmap)
        _w = QWidget()
        _w.setStyleSheet("background-color: rgba(255,255,255, 0);")
        wrap = QVBoxLayout()
        _w.setLayout(wrap)
        _w.setFixedHeight(self.imgh + 2 * margin)
        wrap.setContentsMargins(margin, margin, margin, margin)
        wrap.addWidget(self._img)
        layout.addWidget(_w)
        layout.setSpacing(0)
        self._lb = QLabel()
        if globalconfig["showgametitle"]:
            self._lb.setText(file)
        self._lb.setWordWrap(True)
        self._lb.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self._lb.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._lb)
        self.setLayout(layout)
        self.gameuid = gameuid
        exists = os.path.exists(get_launchpath(gameuid))
        c = globalconfig["dialog_savegame_layout"][
            ("onfilenoexistscolor1", "backcolor1")[exists]
        ]
        c = str2rgba(
            c,
            globalconfig["dialog_savegame_layout"][
                ("transparentnotexits", "transparent")[exists]
            ],
        )
        self.maskshowfileexists.setStyleSheet(f"background-color:{c};")


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

    def setimg(self, pixmap):
        if type(pixmap) != QPixmap:
            pixmap = pixmap()

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

    def __init__(self, w, h, pixmap) -> None:
        super().__init__()
        self.setFixedSize(QSize(w, h))
        self.setScaledContents(True)
        self.setimg(pixmap)


class ClickableLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setClickable(True)

    def setClickable(self, clickable):
        self._clickable = clickable

    def mousePressEvent(self, event):
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    clicked = pyqtSignal()


class tagitem(QWidget):
    # website
    TYPE_GLOABL_LIKE = 3
    TYPE_GAME_LIKE = 1
    # search game
    TYPE_RAND = 0
    TYPE_DEVELOPER = 1
    TYPE_TAG = 2
    TYPE_USERTAG = 3
    TYPE_EXISTS = 4
    removesignal = pyqtSignal(tuple)
    labelclicked = pyqtSignal(tuple)

    def remove(self):
        self.hide()
        _lay = self.layout()
        _ws = []
        for i in range(_lay.count()):
            witem = _lay.itemAt(i)
            _ws.append(witem.widget())
        for w in _ws:
            _lay.removeWidget(w)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._type == tagitem.TYPE_RAND:
            border_color = Qt.GlobalColor.black
        elif self._type == tagitem.TYPE_DEVELOPER:
            border_color = Qt.GlobalColor.red
        elif self._type == tagitem.TYPE_TAG:
            border_color = Qt.GlobalColor.green
        elif self._type == tagitem.TYPE_USERTAG:
            border_color = Qt.GlobalColor.blue
        elif self._type == tagitem.TYPE_EXISTS:
            border_color = Qt.GlobalColor.yellow
        border_width = 1
        pen = QPen(border_color)
        pen.setWidth(border_width)
        painter.setPen(pen)
        painter.drawRect(self.rect())

    def __init__(self, tag, removeable=True, _type=TYPE_RAND, refdata=None) -> None:
        super().__init__()
        tagLayout = QHBoxLayout()
        tagLayout.setContentsMargins(0, 0, 0, 0)
        tagLayout.setSpacing(0)
        self._type = _type
        key = (tag, _type, refdata)
        self.setLayout(tagLayout)
        lb = ClickableLabel()
        lb.setStyleSheet("background: transparent;")
        lb.setText(tag)
        lb.clicked.connect(functools.partial(self.labelclicked.emit, key))
        tagLayout.addWidget(lb)
        if removeable:
            button = getIconButton(
                functools.partial(self.removesignal.emit, key), icon="fa.times"
            )
            tagLayout.addWidget(button)


class TagWidget(QWidget):
    tagschanged = pyqtSignal(tuple)  # ((tag,type,refdata),)
    linepressedenter = pyqtSignal(str)
    tagclicked = pyqtSignal(tuple)  # tag,type,refdata

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.lineEdit = FocusCombo()
        self.lineEdit.setLineEdit(FQLineEdit())

        self.lineEdit.lineEdit().returnPressed.connect(
            lambda: self.linepressedenter.emit(self.lineEdit.currentText())
        )

        self.lineEdit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )

        layout.addWidget(self.lineEdit)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.tag2widget = {}

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
        layout = self.layout()
        layout.insertWidget(layout.count() - 1, qw)
        self.tag2widget[key] = qw
        self.lineEdit.setFocus()

    def addTag(self, tag, _type, refdata=None, signal=True):
        self.__addTag((tag, _type, refdata))
        self.__calltagschanged(signal)

    @tryprint
    def __removeTag(self, key):
        _w = self.tag2widget[key]
        _w.remove()

        self.layout().removeWidget(_w)
        self.tag2widget.pop(key)

    def removeTag(self, key, signal=True):
        self.__removeTag(key)
        self.__calltagschanged(signal)

    def __calltagschanged(self, signal):
        if signal:
            self.tagschanged.emit(tuple(self.tag2widget.keys()))

    def clearTag(self, signal=True):
        for key in self.tag2widget.copy():
            self.__removeTag(key)
        self.__calltagschanged(signal)


def opendirforgameuid(gameuid):
    f = get_launchpath(gameuid)
    f = os.path.dirname(f)
    if os.path.exists(f) and os.path.isdir(f):
        os.startfile(f)


@threader
def startgame(gameuid):
    try:
        game = get_launchpath(gameuid)
        if os.path.exists(game):
            mode = savehook_new_data[gameuid]["onloadautochangemode2"]
            if mode > 0:
                _ = {1: "texthook", 2: "copy", 3: "ocr"}
                if globalconfig["sourcestatus2"][_[mode]]["use"] == False:
                    globalconfig["sourcestatus2"][_[mode]]["use"] = True

                    for k in globalconfig["sourcestatus2"]:
                        globalconfig["sourcestatus2"][k]["use"] = k == _[mode]
                        try:
                            getattr(gobject.baseobject.settin_ui, "sourceswitchs")[
                                k
                            ].setChecked(k == _[mode])
                        except:
                            pass

                    gobject.baseobject.starttextsource(use=_[mode], checked=True)

            localeswitchedrun(gameuid)

    except:
        print_exc()


def __b64string(a: str):
    return hashlib.md5(a.encode("utf8")).hexdigest()


def __scaletosize(_pix: QPixmap, tgt):

    if max(_pix.width(), _pix.height()) > 400:

        if _pix.width() > _pix.height():
            sz = QSize(400, 400 * _pix.height() // _pix.width())
        else:
            sz = QSize(400, _pix.width() * 400 // _pix.height())
        _pix = _pix.scaled(
            sz,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    _pix.save(tgt)


def getcachedimage(src, small):
    if not small:
        _pix = QPixmap(src)
        if _pix.isNull():
            return None
        return _pix
    if not os.path.exists(src):
        return None
    src2 = gobject.getcachedir(f"icon2/{__b64string(src)}.jpg")
    _pix = QPixmap(src2)
    if not _pix.isNull():
        return _pix
    _pix = QPixmap(src)
    if _pix.isNull():
        return None
    __scaletosize(_pix, src2)
    return _pix


def getpixfunction(kk, small=False):
    if (
        savehook_new_data[kk]["currentmainimage"]
        in savehook_new_data[kk]["imagepath_all"]
    ):
        src = savehook_new_data[kk]["currentmainimage"]
        pix = getcachedimage(src, small)
        if pix:
            return pix
    for _ in savehook_new_data[kk]["imagepath_all"]:
        pix = getcachedimage(_, small)
        if pix:
            return pix
    _pix = getExeIcon(uid2gamepath[kk], False, cache=True)
    return _pix


def startgamecheck(self, reflist, gameuid):
    if not gameuid:
        return
    if not os.path.exists(get_launchpath(gameuid)):
        return
    if globalconfig["startgamenototop"] == False:
        idx = reflist.index(gameuid)
        reflist.insert(0, reflist.pop(idx))
    self.parent().parent().close()
    startgame(gameuid)


def addgamesingle(parent, callback, targetlist):
    f = QFileDialog.getOpenFileName(options=QFileDialog.Option.DontResolveSymlinks)

    res = f[0]
    if res == "":
        return
    res = os.path.normpath(res)
    uid = find_or_create_uid(targetlist, res)
    if uid in targetlist:
        idx = targetlist.index(uid)
        response = QMessageBox.question(
            parent,
            "",
            _TR("游戏已存在，是否重复添加？"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if response == QMessageBox.StandardButton.No:
            if idx == 0:
                return
            targetlist.pop(idx)
        else:
            uid = duplicateconfig(uid)
    targetlist.insert(0, uid)
    callback(uid)


def addgamebatch(callback, targetlist):
    res = QFileDialog.getExistingDirectory(
        options=QFileDialog.Option.DontResolveSymlinks
    )
    if res == "":
        return
    for _dir, _, _fs in os.walk(res):
        for _f in _fs:
            path = os.path.normpath(os.path.abspath(os.path.join(_dir, _f)))
            if path.lower().endswith(".exe") == False:
                continue
            uid = find_or_create_uid(targetlist, path)
            if uid in targetlist:
                targetlist.pop(targetlist.index(uid))
            targetlist.insert(0, uid)
            callback(uid)


def loadvisinternal(skipid=False, skipidid=None):
    __vis = []
    __uid = []
    for _ in savegametaged:
        if _ is None:
            __vis.append("GLOBAL")
            __uid.append(None)
        else:
            __vis.append(_["title"])
            __uid.append(_["uid"])
        if skipid:
            if skipidid == __uid[-1]:
                __uid.pop(-1)
                __vis.pop(-1)
    return __vis, __uid


def getalistname(parent, callback, skipid=False, skipidid=None, title="添加到列表"):
    __d = {"k": 0}
    __vis, __uid = loadvisinternal(skipid, skipidid)

    def __wrap(callback, __d, __uid):
        if len(__uid) == 0:
            return

        uid = __uid[__d["k"]]
        callback(uid)

    if len(__uid) > 1:
        autoinitdialog(
            parent,
            title,
            600,
            [
                {
                    "type": "combo",
                    "name": "目标列表",
                    "d": __d,
                    "k": "k",
                    "list": __vis,
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(__wrap, callback, __d, __uid),
                },
            ],
        )
    elif len(__uid):

        callback(__uid[0])


def calculatetagidx(tagid):
    i = 0
    for save in savegametaged:
        if save is None and tagid is None:
            return i
        elif save and tagid and save["uid"] == tagid:
            return i
        i += 1

    return None


def getreflist(reftagid):
    _idx = calculatetagidx(reftagid)
    if _idx is None:
        return None
    tag = savegametaged[_idx]
    if tag is None:
        return savehook_new_list
    return tag["games"]


@Singleton_close
class dialog_syssetting(LDialog):

    def __init__(self, parent, type_=1) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("其他设置")
        formLayout = LFormLayout(self)

        formLayout.addRow(
            "隐藏不存在的游戏",
            getsimpleswitch(globalconfig, "hide_not_exists"),
        )
        if type_ == 1:
            for key, name in [
                ("itemw", "宽度"),
                ("itemh", "高度"),
                # ("imgw", "图片宽度"),
                # ("imgh", "图片高度"),
                ("margin", "边距"),
                ("textH", "文字区高度"),
            ]:
                formLayout.addRow(
                    name,
                    getspinbox(0, 1000, globalconfig["dialog_savegame_layout"], key),
                )
        elif type_ == 2:
            for key, name in [
                ("listitemheight", "文字区高度"),
                ("listitemwidth", "高度"),
            ]:
                formLayout.addRow(
                    name,
                    getspinbox(0, 1000, globalconfig["dialog_savegame_layout"], key),
                )

        for key, key2, name in [
            ("backcolor1", "transparent", "颜色"),
            ("onselectcolor1", "transparentselect", "选中时颜色"),
            ("onfilenoexistscolor1", "transparentnotexits", "游戏不存在时颜色"),
        ]:
            formLayout.addRow(
                name,
                getcolorbutton(
                    globalconfig["dialog_savegame_layout"],
                    key,
                    callback=functools.partial(
                        selectcolor,
                        self,
                        globalconfig["dialog_savegame_layout"],
                        key,
                        None,
                        self,
                        key,
                    ),
                    name=key,
                    parent=self,
                ),
            )
            formLayout.addRow(
                name + "_" + "不透明度",
                getspinbox(0, 100, globalconfig["dialog_savegame_layout"], key2),
            )
        if type_ == 1:
            formLayout.addRow(
                "缩放",
                getsimplecombobox(
                    ["填充", "适应", "拉伸", "居中"],
                    globalconfig,
                    "imagewrapmode",
                ),
            )
        formLayout.addRow(
            "启动游戏不修改顺序",
            getsimpleswitch(globalconfig, "startgamenototop"),
        )

        if type_ == 1:
            formLayout.addRow(
                "显示标题",
                getsimpleswitch(globalconfig, "showgametitle"),
            )
        self.show()
