from qtsymbols import *
import os, functools
from traceback import print_exc
from myutils.wrapper import threader, Singleton
from myutils.utils import find_or_create_uid, duplicateconfig
from myutils.hwnd import getExeIcon, getcurrexe
import gobject, hashlib, NativeUtils, uuid, re
from gui.inputdialog import autoinitdialog
from gui.dynalang import LFormLayout, LDialog
from myutils.localetools import localeswitchedrun
from myutils.config import (
    savehook_new_data,
    savegametaged,
    uid2gamepath,
    get_launchpath,
    _TR,
    extradatas,
    savehook_new_list,
    globalconfig,
)
from gui.usefulwidget import (
    getIconButton,
    getsimplecombobox,
    getspinbox,
    getcolorbutton,
    getsimpleswitch,
    getspinbox,
    SClickableLabel,
    SplitLine,
)


def showcountgame(window: QMainWindow, num):
    if num:
        window.setWindowTitle("游戏管理__-__" + str(num))
    else:
        window.setWindowTitle("游戏管理")


class tagitem(QFrame):
    # search game
    TYPE_SEARCH = 0
    TYPE_DEVELOPER = 1
    TYPE_TAG = 2
    TYPE_USERTAG = 3
    TYPE_EXISTS = 4
    removesignal = pyqtSignal(tuple)
    labelclicked = pyqtSignal(tuple)

    @staticmethod
    def setstyles(parent: QWidget):
        parent.setStyleSheet(
            """
            tagitem#red {
                border: 1px solid red;
            }
            tagitem#black {
                border: 1px solid black;
            }
            tagitem#green {
                border: 1px solid green;
            }
            tagitem#blue {
                border: 1px solid blue;
            }
            tagitem#yellow {
                border: 1px solid yellow;
            }
        """
        )

    def __init__(self, tag, removeable=True, _type=TYPE_SEARCH, refdata=None) -> None:
        super().__init__()
        if _type == tagitem.TYPE_SEARCH:
            border_color = "black"
        elif _type == tagitem.TYPE_DEVELOPER:
            border_color = "red"
        elif _type == tagitem.TYPE_TAG:
            border_color = "green"
        elif _type == tagitem.TYPE_USERTAG:
            border_color = "blue"
        elif _type == tagitem.TYPE_EXISTS:
            border_color = "yellow"
        self.setObjectName(border_color)

        tagLayout = QHBoxLayout(self)
        tagLayout.setContentsMargins(0, 0, 0, 0)
        tagLayout.setSpacing(0)

        key = (tag, _type, refdata)
        lb = SClickableLabel()
        lb.setText(tag)
        lb.clicked.connect(functools.partial(self.labelclicked.emit, key))
        if removeable:
            button = getIconButton(
                functools.partial(self.removesignal.emit, key), icon="fa.times"
            )
            tagLayout.addWidget(button)
        tagLayout.addWidget(lb)


def opendirforgameuid(gameuid):
    f = get_launchpath(gameuid)
    f = os.path.dirname(f)
    if os.path.isdir(f):
        os.startfile(f)


def startgame(gameuid):
    try:
        if not gameuid:
            return
        game = get_launchpath(gameuid)
        if os.path.exists(game):
            mode = savehook_new_data[gameuid].get("onloadautochangemode2", 0)
            if mode > 0:
                _ = {1: "texthook", 2: "copy", 3: "ocr"}
                if globalconfig["sourcestatus2"][_[mode]]["use"] == False:
                    globalconfig["sourcestatus2"][_[mode]]["use"] = True

                    for k in globalconfig["sourcestatus2"]:
                        globalconfig["sourcestatus2"][k]["use"] = k == _[mode]
                        gobject.base.sourceswitchs.emit(k, k == _[mode])

                    gobject.base.starttextsource(use=_[mode], checked=True)

            threader(localeswitchedrun)(gameuid)
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


def getcachedimage(src, small) -> QPixmap:
    src = extradatas["localedpath"].get(src, src)
    if not small:
        return QPixmap(src)
    if not os.path.exists(src):
        return QPixmap()
    srcsave = gobject.getcachedir("icon3/{}.webp".format(__b64string(src)))
    _pix = QPixmap(srcsave)
    if not _pix.isNull():
        return _pix
    _pix = QPixmap(src)
    if _pix.isNull():
        return _pix
    __scaletosize(_pix, srcsave)
    return _pix


def getpixfunction(kk, small=False, iconfirst=False) -> QPixmap:
    key = ["currentmainimage", "currenticon"][iconfirst]
    checks = [savehook_new_data[kk].get(key)]
    _all = savehook_new_data[kk].get("imagepath_all", [])
    if (savehook_new_data[kk].get(key) not in _all) and (not iconfirst):
        checks += _all
    for _ in checks:
        pix = getcachedimage(_, small)
        if not pix.isNull():
            return pix
    _pix: QPixmap = getExeIcon(uid2gamepath[kk], False, cache=True, large=True)
    return _pix


def make_square_pixmap(pixmap: QPixmap):
    width = pixmap.width()
    height = pixmap.height()
    size = max(width, height)
    square_pixmap = QPixmap(size, size)
    square_pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(square_pixmap)
    x = (size - width) // 2
    y = (size - height) // 2
    painter.drawPixmap(x, y, pixmap)
    painter.end()
    return square_pixmap


def getpixfunctionAlign(kk, small=False, iconfirst=False):
    icon = getpixfunction(kk, small=small, iconfirst=iconfirst)
    if icon.width() != icon.height():
        icon = make_square_pixmap(icon)
    return icon


def CreateShortcutForUid(gameuid):
    icon = getpixfunctionAlign(gameuid, small=True, iconfirst=True)
    path = gobject.getcachedir("shutcuticon/{}.ico".format(uuid.uuid4()))
    icon.save(path)
    NativeUtils.CreateShortcut(
        re.sub(r'[/\\?%*:|"<>]', " ", savehook_new_data[gameuid]["title"]),
        getcurrexe(),
        "--Exec {}".format(gameuid),
        path,
    )


def startgamecheck(self: QWidget, reflist: list, gameuid):
    if not gameuid:
        return
    if not os.path.exists(get_launchpath(gameuid)):
        return
    if globalconfig["startgamenototop"] == False:
        idx = reflist.index(gameuid)
        reflist.insert(0, reflist.pop(idx))
    self.window().close()
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
            "?",
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


def addgamebatch_x(callback, targetlist, paths):
    for path in paths:
        if not os.path.isfile(path):
            continue
        path = os.path.normpath(path)
        uid = find_or_create_uid(targetlist, path)
        if uid in targetlist:
            targetlist.pop(targetlist.index(uid))
        targetlist.insert(0, uid)
        callback(uid)


def addgamebatch(callback, targetlist):
    res = QFileDialog.getExistingDirectory(
        options=QFileDialog.Option.DontResolveSymlinks
    )
    if not res:
        return
    paths = []
    for _dir, _, _fs in os.walk(res):
        for _f in _fs:
            path = os.path.normpath(os.path.abspath(os.path.join(_dir, _f)))
            if path.lower().endswith(".exe") == False:
                continue
            paths.append(path)
    addgamebatch_x(callback, targetlist, paths)


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
            __d,
            title,
            600,
            [
                {
                    "type": "combo",
                    "name": "目标列表",
                    "k": "k",
                    "list": __vis,
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(__wrap, callback, __d, __uid),
                },
            ],
            exec_=True,
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


def getfonteditor(d: dict, k: str, callback=None):
    lay = QHBoxLayout()
    lay.setContentsMargins(0, 0, 0, 0)
    e = QLineEdit(d.get(k, ""))
    e.setReadOnly(True)
    icons = ("fa.font", "fa.undo")
    bu = getIconButton(icon=icons[0], tips="选择字体")
    clear = getIconButton(icon=icons[1], tips="还原")

    def __selectfont(d: dict, k: str, callback, e: QLineEdit):
        f = QFont()
        text = e.text()
        if text:
            f.fromString(text)
        font, ok = QFontDialog.getFont(f, e)
        if ok:
            _s = font.toString()
            d[k] = _s
            callback(_s)
            e.setText(_s)

    _cb = functools.partial(__selectfont, d, k, callback, e)

    bu.clicked.connect(_cb)
    lay.addWidget(e)
    lay.addWidget(bu)

    def __(d: dict, k: str, _cb, _e: QLineEdit):
        d[k] = ""
        _cb("")
        _e.setText("")

    clear.clicked.connect(functools.partial(__, d, k, callback, e))
    lay.addWidget(clear)
    return lay


@Singleton
class dialog_syssetting(LDialog):

    def closeEvent(self, e):
        self.parent().callchange()

    def __init__(self, parent, type_=1) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("其他设置")
        formLayout = LFormLayout(self)

        formLayout.addRow(
            "隐藏不存在的游戏",
            getsimpleswitch(
                globalconfig, "hide_not_exists", callback=self.parent().callexists
            ),
        )

        formLayout.addRow(
            "启动游戏不修改顺序",
            getsimpleswitch(globalconfig, "startgamenototop"),
        )

        formLayout.addRow(SplitLine())
        if type_ == 2:
            for i, (key, name) in enumerate(
                [
                    ("itemw", "宽度"),
                    ("itemh", "高度"),
                    ("margin", "边距_intra"),
                    ("margin2", "边距_inter"),
                    ("radius", "圆角"),
                    ("radius2", "圆角_2"),
                    ("textH", "文字区高度"),
                ]
            ):
                minv = 0 if i >= 2 else 32
                spin = getspinbox(
                    minv, 1000, globalconfig["dialog_savegame_layout"], key
                )
                formLayout.addRow(name, spin)
                if "radius" == key:
                    spin.valueChanged.connect(lambda _: self.parent().setstyle())
                else:
                    spin.valueChanged.connect(lambda _: self.parent().callchange())
            formLayout.addRow(
                "字体",
                getfonteditor(
                    d=globalconfig,
                    k="savegame_textfont1",
                    callback=lambda _: self.parent().setstyle(),
                ),
            )
            formLayout.addRow(
                "缩放",
                getsimplecombobox(
                    ["填充", "适应", "拉伸", "居中"],
                    globalconfig,
                    "imagewrapmode",
                    callback=lambda _: self.parent().callchange(),
                ),
            )

        elif type_ == 1:
            for key, name in [
                ("listitemheight", "高度"),
            ]:
                spin = getspinbox(10, 1000, globalconfig["dialog_savegame_layout"], key)
                formLayout.addRow(name, spin)
                spin.valueChanged.connect(lambda _: self.parent().callchange())
            formLayout.addRow(
                "字体",
                getfonteditor(
                    d=globalconfig,
                    k="savegame_textfont2",
                    callback=lambda _: self.parent().setstyle(),
                ),
            )

        formLayout.addRow(SplitLine())
        for key, name in [
            ("backcolor2", "颜色"),
            ("onselectcolor2", "选中时颜色"),
            ("onfilenoexistscolor2", "游戏不存在时颜色"),
        ]:
            formLayout.addRow(
                name,
                getcolorbutton(
                    self,
                    globalconfig["dialog_savegame_layout"],
                    key,
                    callback=lambda _: self.parent().setstyle(),
                    alpha=True,
                ),
            )
        self.show()
