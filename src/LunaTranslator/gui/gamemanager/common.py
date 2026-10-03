from qtsymbols import *
from gui.fluent.messagebox import ExMessageBox
import os, functools
from traceback import print_exc
from myutils.wrapper import threader
from myutils.utils import find_or_create_uid, duplicateconfig
from myutils.hwnd import getExeIcon, getcurrexe
import gobject, NativeUtils, uuid, re
from myutils.localetools import localeswitchedrun
from myutils.config import (
    savehook_new_data,
    savegametaged,
    get_launchpath,
    _TR,
    extradatas,
    savehook_new_list,
    globalconfig,
)
from gui.usefulwidget import (
    getIconButton,
    SClickableLabel,
)


class tagitem(QFrame):
    # search game
    TYPE_SEARCH = 0
    TYPE_DEVELOPER = 1
    TYPE_TAG = 2
    TYPE_EXISTS = 4
    removesignal = pyqtSignal(tuple)
    labelclicked = pyqtSignal(tuple)

    @staticmethod
    def __init__(self, tag, removeable=True, _type=TYPE_SEARCH, refdata=None) -> None:
        super().__init__()
        if _type == tagitem.TYPE_SEARCH:
            border_color = "black"
        elif _type == tagitem.TYPE_DEVELOPER:
            border_color = "red"
        elif _type == tagitem.TYPE_TAG:
            border_color = "green"
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


def decode_scaled(src, by_max=None, by_height=None, by_width=None) -> QImage:
    """按目标尺寸直接解码（shrink-on-load，缩略路径共用核心）：全量
    解码再缩既慢又吃内存——9448px 实测全量 730ms/~213MB，按目标解码
    ~265ms/~0.4MB（Qt JPEG 走 DCT 缩放）。三种定尺寸方式（互斥）：
    by_max    长边不超过 by_max
    by_height 高度恰为 by_height（横向条带）
    by_width  宽度恰为 by_width（纵向条带）
    均仅缩小不放大；尺寸未知/无需缩时原样解码。返回 QImage（可跨
    线程；QPixmap 仅限 GUI 线程）。"""
    reader = QImageReader(src)
    sz = reader.size()
    if sz.isValid() and sz.width() > 0 and sz.height() > 0:
        w, h = sz.width(), sz.height()
        if by_max and max(w, h) > by_max:
            if w > h:
                reader.setScaledSize(QSize(by_max, max(1, by_max * h // w)))
            else:
                reader.setScaledSize(QSize(max(1, w * by_max // h), by_max))
        elif by_height and by_height < h:
            reader.setScaledSize(QSize(
                max(1, round(w * by_height / h)), by_height))
        elif by_width and by_width < w:
            reader.setScaledSize(QSize(
                by_width, max(1, round(h * by_width / w))))
    return reader.read()


def getcachedimage(src, small) -> QPixmap:
    """small=True 取缩略（≤400，按需解码不落盘）；False 原图全量
    （画廊轮播的查看器语义）。解码核心见 decode_scaled。"""
    src = extradatas["localedpath"].get(src, src)
    if not small:
        return QPixmap(src)
    img = decode_scaled(src, by_max=400)
    if img.isNull():
        return QPixmap()
    return QPixmap.fromImage(img)


def loadgridimage(uid) -> QImage:
    """网格项图标（工作线程调用）：currentmainimage -> 其余图片依次
    全量解码——网格项用完整分辨率（缩略图会糊）；大图解码在后台
    线程进行，不占 GUI 线程。无可用图返回 null，exe 图标兜底由 GUI
    线程回调做（widgets.ItemWidget.applyimage）。"""
    data = savehook_new_data.get(uid) or {}
    _all = data.get("imagepath_all", [])
    checks = [data.get("currentmainimage")]
    if data.get("currentmainimage") not in _all:
        checks += _all
    for _ in checks:
        if not _:
            continue
        src = extradatas["localedpath"].get(_, _)
        if not os.path.exists(src):
            continue
        img = QImage(src)
        if not img.isNull():
            return img
    return QImage()


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
    _pix: QPixmap = getExeIcon(get_launchpath(kk), False, cache=True, large=True)
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
    if not globalconfig.get("startgamenototop", True):
        # 最近游戏的 getreflist 返回哨兵 1（动态列表，启动后自然置顶），
        # 非列表/不在列表中时跳过手动置顶
        if isinstance(reflist, list) and gameuid in reflist:
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
        response = ExMessageBox.question(
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


def loadvisinternal(skipid=False, skipidid=None, recent=True, global_=True):
    __vis = []
    __uid = []
    for _ in savegametaged:
        if _ is None:
            if not global_:
                continue
            __vis.append("所有游戏")
            __uid.append(None)
        elif _ == 1:
            if not recent:
                continue
            __vis.append("最近游戏")
            __uid.append(1)
        else:
            __vis.append("[[{}]]".format(_["title"]))
            __uid.append(_["uid"])
        if skipid:
            if skipidid == __uid[-1]:
                __uid.pop(-1)
                __vis.pop(-1)
    return __vis, __uid


def calculatetagidx(tagid):
    i = 0
    for save in savegametaged:
        if save is None and tagid is None:
            return i
        elif save == 1 and tagid == 1:
            return i
        elif (
            (save not in (None, 1))
            and (tagid not in (None, 1))
            and save["uid"] == tagid
        ):
            return i
        i += 1

    return None


def loadrecentlist():
    data = gobject.base.somedatabase.all()
    datas = {}
    for uid, tms in data.items():
        tm = tms[-1][1]
        datas[uid] = tm
    ks = list(_ for _ in datas if _ in savehook_new_data and _ in savehook_new_list)
    ks.sort(key=lambda uid: -datas[uid])
    return ks[: globalconfig.get("recentgamelistnum", 10)]


def getreflist(reftagid):
    _idx = calculatetagidx(reftagid)
    if _idx is None:
        return None
    tag = savegametaged[_idx]
    if tag is None:
        return savehook_new_list
    if tag == 1:
        return 1
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


