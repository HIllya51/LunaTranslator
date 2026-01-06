from qtsymbols import *
import functools, os, re
import gobject, math, NativeUtils
from myutils.config import (
    globalconfig,
    savehook_new_data,
    translatorsetting,
    _TR,
    tryreadconfig2,
    getcopyfrom,
    copyllmapi,
    dynamicapiname,
    dynamiclink,
)
from datetime import datetime
import requests
from myutils.utils import (
    getlangtgt,
    format_bytes,
    selectdebugfile,
    splittranslatortypes,
    translate_exits,
    getannotatedapiname,
    format_bytes,
)
from myutils.proxy import getproxy
from myutils.hwnd import subprochiderun
import json, sqlite3
from traceback import print_exc
from gui.usefulwidget import SuperCombo
from collections import Counter
from language import Languages
from myutils.wrapper import tryprint, threader
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getspinbox,
    AutoScaleImageButton,
    getboxlayout,
    VisLFormLayout,
    getIconButton,
    D_getcolorbutton,
    getcolorbutton,
    check_grid_append,
    CollapsibleBoxWithButton,
    getsimpleswitch,
    D_getIconButton,
    MyInputDialog,
    D_getsimpleswitch,
    request_delete_ok,
    createfoldgrid,
    getspinbox,
    ClickableLabel,
    automakegrid,
    FocusFontCombo,
    getsmalllabel,
    NQGroupBox,
    makescrollgrid,
    IconButton,
    PopupWidget,
    getsimplecombobox,
)
from gui.setting.display_text import GetFormForLineHeight
from gui.dynalang import LPushButton, LAction, LFormLayout, LDialog
from gui.setting.about import offlinelinks


def getallllms(l):
    _ = []
    for fanyi in l:
        is_gpt_like = globalconfig["fanyi"][fanyi].get("is_gpt_like", False)
        if is_gpt_like:
            _.append(fanyi)
    return _


def splitapillm(l):
    not_is_gpt_like = []
    is_gpt_likes = []
    for fanyi in l:
        is_gpt_like = globalconfig["fanyi"][fanyi].get("is_gpt_like", False)
        if is_gpt_like:
            is_gpt_likes.append(fanyi)
        else:
            not_is_gpt_like.append(fanyi)
    return is_gpt_likes, not_is_gpt_like


def loadvisinternal(copy):
    __vis = []
    __uid = []
    for _ in getallllms(globalconfig["fanyi"]):
        if copy:
            which = translate_exits(_, which=True)
            if which != 1:
                continue
        else:
            if not translate_exits(_):
                continue
        __vis.append(dynamicapiname(_))
        __uid.append(_)
    return __vis, __uid


class SpecialFont(PopupWidget):
    def __init__(self, apiuid, p):
        super().__init__(p)
        self.apiuid = apiuid
        box = QGridLayout(self)
        grid = []
        grid.append(
            [
                "",
                "跟随默认",
            ]
        )
        if "privatefont" not in globalconfig["fanyi"][apiuid]:
            globalconfig["fanyi"][apiuid]["privatefont"] = {}
        dd = globalconfig["fanyi"][apiuid]["privatefont"]
        for i in range(4):
            if i == 0:
                t = "字体"
                k = "fontfamily"
                w = QPushButton()

                def _f(dd, key, x):
                    dd[key] = x
                    self.resetfont()

                w = FocusFontCombo()
                w.setCurrentFont(QFont(dd.get(k, globalconfig["fonttype2"])))
                w.currentTextChanged.connect(functools.partial(_f, dd, k))
            elif i == 1:
                t = "大小"
                k = "fontsize"
                w = getspinbox(
                    1,
                    100,
                    dd,
                    k,
                    double=True,
                    default=globalconfig[k],
                    callback=self.resetfont,
                )
            elif i == 2:
                t = "加粗"
                k = "showbold"
                w = getsimpleswitch(
                    dd, k, default=globalconfig[k], callback=self.resetfont
                )
            elif i == 3:
                t = "间距"
                k = "lineheight"
                w = QWidget()
                GetFormForLineHeight(w, dd, self.resetfont)

            w.setEnabled(not dd.get(k + "_df", True))
            switch = D_getsimpleswitch(
                dd,
                k + "_df",
                callback=functools.partial(self.disableclear, w),
                default=True,
            )
            grid.append([getsmalllabel(t), switch, w])
        automakegrid(box, grid)

    def disableclear(self, w: QWidget, _):
        w.setEnabled(not _)
        self.resetfont()

    def resetfont(self, _=None):
        gobject.base.translation_ui.translate_text.setfontextra(self.apiuid)


def renameapi(qlabel: QLabel, apiuid, self, countnum, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    specialfont = LAction("字体设置", menu)
    delete = LAction("删除", menu)
    copy = LAction("复制", menu)
    astoppest = LAction("设为首选", menu)
    astoppest.setCheckable(True)
    usecache = LAction("使用翻译缓存", menu)
    usecache.setCheckable(True)
    useproxy = LAction("使用代理", menu)
    useproxy.setCheckable(True)
    astoppest.setChecked(globalconfig["toppest_translator"] == apiuid)
    menu.addAction(editname)
    menu.addAction(specialfont)
    menu.addAction(astoppest)
    which = translate_exits(apiuid, which=True)
    is_gpt_like = globalconfig["fanyi"][apiuid].get("is_gpt_like", False)
    if is_gpt_like:
        menu.addSeparator()
        menu.addAction(usecache)
        usecache.setChecked(globalconfig["fanyi"][apiuid].get("use_trans_cache", True))
        menu.addAction(copy)

    if which == 1 or "chatgpt-offline" == apiuid:
        menu.addAction(delete)
    if globalconfig["useproxy"] and globalconfig["fanyi"][apiuid].get("type") not in (
        "offline",
        "other",
        "pre",
    ):
        menu.addSeparator()
        menu.addAction(useproxy)
        useproxy.setChecked(globalconfig["fanyi"][apiuid].get("useproxy", True))
    pos = QCursor.pos()
    action = menu.exec(pos)
    if action == delete:
        selectllmcallback_2(self, countnum, apiuid, None)
    elif action == useproxy:
        globalconfig["fanyi"][apiuid]["useproxy"] = useproxy.isChecked()
    elif action == astoppest:
        globalconfig["toppest_translator"] = apiuid if action.isChecked() else None
        if action.isChecked():
            try:
                # 若已开启，则立即置顶
                globalconfig["fix_translate_rank_rank"].remove(apiuid)
                globalconfig["fix_translate_rank_rank"].insert(0, apiuid)
            except:
                pass

    elif action == usecache:
        globalconfig["fanyi"][apiuid]["use_trans_cache"] = usecache.isChecked()
    elif action == editname:
        before = dynamicapiname(apiuid)
        newname = MyInputDialog(self, "重命名", "名称", before)
        if not newname:
            return
        if newname == before:
            return
        globalconfig["fanyi"][apiuid]["name_self_set"] = newname
        qlabel.setText(newname)

    elif action == specialfont:
        SpecialFont(apiuid, self).display(pos)
    elif action == copy:
        selectllmcallback(self, countnum, apiuid)


def getrenameablellabel(uid, self, countnum):
    name = ClickableLabel(dynamicapiname(uid))
    fn = functools.partial(renameapi, name, uid, self, countnum)
    name.clicked.connect(fn)
    return name


def loadbutton(self, fanyi):
    which = translate_exits(fanyi, which=True)
    copyfrom = getcopyfrom(fanyi)
    if (copyfrom != fanyi) and (copyfrom in translatorsetting):
        if "args" in translatorsetting[copyfrom]:
            for k in translatorsetting[copyfrom]["args"]:
                if k not in translatorsetting[fanyi]["args"]:
                    translatorsetting[fanyi]["args"][k] = translatorsetting[copyfrom][
                        "args"
                    ][k]

            for k in list(translatorsetting[fanyi]["args"].keys()):
                if k not in translatorsetting[copyfrom]["args"]:
                    translatorsetting[fanyi]["args"].pop(k)
        if "argstype" in translatorsetting[copyfrom]:
            translatorsetting[fanyi]["argstype"] = translatorsetting[copyfrom][
                "argstype"
            ]
    items = autoinitdialog_items(translatorsetting[fanyi])
    if which == 0:
        aclass = "translator." + fanyi
    elif which == 1:
        aclass = "copyed." + fanyi
    else:
        return
    return autoinitdialog(
        self,
        translatorsetting[fanyi]["args"],
        dynamicapiname(fanyi),
        800,
        items,
        aclass,
        fanyi,
    )


def selectllmcallback(self, countnum: list, fanyi, newname=None):
    uid = copyllmapi(fanyi, newname=newname)

    layout: QGridLayout = getattr(self, "damoxinggridinternal")

    last = getIconButton(callback=functools.partial(loadbutton, self, uid))

    name = getrenameablellabel(uid, self, countnum)
    swc = getsimpleswitch(
        globalconfig["fanyi"][uid],
        "use",
        callback=functools.partial(gobject.base.prepare, uid),
    )
    color = getcolorbutton(
        self,
        globalconfig["fanyi"][uid],
        "color",
        callback=gobject.base.translation_ui.translate_text.setcolorstyle,
    )

    offset = 5 * (len(countnum) % 3)
    layout.addWidget(name, layout.rowCount() - 1 + (len(countnum) % 3 == 0), offset + 0)
    layout.addWidget(swc, layout.rowCount() - 1, offset + 1)
    layout.addWidget(color, layout.rowCount() - 1, offset + 2)
    layout.addWidget(last, layout.rowCount() - 1, offset + 3)
    if len(countnum) % 3 != 2:
        layout.addWidget(QLabel(), layout.rowCount() - 1, offset + 4)
    countnum.append(uid)
    self.__del_btn.show()


def selectllmcallback_2(self, countnum: list, fanyi, _=None):
    if not request_delete_ok(self, "99e3f96f-8659-457f-9e0b-52643f552889"):
        return
    _f2 = gobject.getconfig("copyed/{}.py".format(fanyi))
    try:
        os.remove(_f2)
    except:
        pass
    globalconfig["fanyi"][fanyi]["use"] = False
    try:
        gobject.base.translators.pop(fanyi)
    except:
        pass
    layout: QGridLayout = getattr(self, "damoxinggridinternal")
    if not layout:
        return
    if fanyi not in countnum:
        print(fanyi)
        return
    idx = countnum.index(fanyi)
    line = idx // 3
    off = line * 14 + (idx % 3) * 5
    do = 0
    i = 0
    while do < 4:

        w = layout.itemAt(off + i).widget()
        i += 1
        if isinstance(w, NQGroupBox):
            continue
        elif isinstance(w, QLabel) and w.text() == "":
            continue
        elif not w.isEnabled():
            continue
        w.setEnabled(False)
        do += 1

    if not loadvisinternal(True)[0]:
        self.__del_btn.hide()


def addordelete(delete, self, countnum):
    menu = QMenu(self)

    __vis, __uid = loadvisinternal(delete)
    if not __vis:
        return
    lang = getlangtgt()
    actions = {}
    for i in range(len(__vis)):
        if not delete:
            langs = globalconfig["fanyi"][__uid[i]].get("langs")
            if langs and (lang not in langs):
                continue
        _ = QAction(__vis[i], menu)
        actions[_] = __uid[i]
        menu.addAction(_)
    action = menu.exec(QCursor.pos())
    if action in actions:
        name = None
        if not delete:
            name = MyInputDialog(self, "复制接口", "命名为", action.text() + "_copy")
            if not name:
                return
        (selectllmcallback_2 if delete else selectllmcallback)(
            self, countnum, actions[action], name
        )


def btndeccallback(self, countnum):
    addordelete(True, self, countnum)


def btnpluscallback(self, countnum):
    addordelete(False, self, countnum)


def initsome11(self, l, save=False):
    grids: "list[list]" = []
    i = 0
    line = []
    countnum = []
    if save:
        self.__countnum = countnum
    lang = getlangtgt()
    for fanyi in l:
        langs = globalconfig["fanyi"][fanyi].get("langs")
        if langs and (lang not in langs):
            continue
        which = translate_exits(fanyi, which=True)
        if which is None:
            continue
        i += 1
        countnum.append(fanyi)
        if translatorsetting.get(fanyi):
            last = D_getIconButton(callback=functools.partial(loadbutton, self, fanyi))
        elif fanyi == "selfbuild":
            last = D_getIconButton(
                callback=lambda: selectdebugfile("selfbuild.py"),
                icon="fa.edit",
            )
        else:
            last = ""
        line += [
            functools.partial(getrenameablellabel, fanyi, self, countnum),
            D_getsimpleswitch(
                globalconfig["fanyi"][fanyi],
                "use",
                callback=functools.partial(gobject.base.prepare, fanyi),
            ),
            D_getcolorbutton(
                self,
                globalconfig["fanyi"][fanyi],
                "color",
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            ),
            last,
        ]

        if i % 3 == 0:
            grids.append(line)
            line = []
        else:
            line += [""]
    if len(line):
        grids.append(line)
    check_grid_append(grids)
    if len(grids) == 1:
        if i % 3 != 0:
            grids[-1].append(("", 5 * (3 - i % 3)))
    return grids


def initsome21(self, not_is_gpt_like):
    not_is_gpt_like = initsome11(self, not_is_gpt_like)
    not_is_gpt_like += [[(functools.partial(offlinelinks, "translate"), 0)]]
    grids = [
        [
            functools.partial(
                createfoldgrid,
                not_is_gpt_like,
                "过时的",
                globalconfig["foldstatus"]["ts"],
                "outdate",
            )
        ],
    ]
    return grids


def __create(download, keydir, key, check):
    combollama = SuperCombo()
    combollama.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def refresh_llama(combo: SuperCombo):
        llamacppdir = globalconfig["llama.cpp"].get(keydir, ".")
        if not llamacppdir:
            return
        with QSignalBlocker(combo) as _:
            combo.clear()
            for _dir, _, _fs in os.walk(llamacppdir):
                for _f in _fs:
                    if not check(_f):
                        continue
                    _ = os.path.relpath(os.path.join(_dir, _f), llamacppdir)
                    combo.addItem(_, internal=_)
            combo.setCurrentData(globalconfig["llama.cpp"].get(key))

    def getdir(combo):
        llamacppdir = globalconfig["llama.cpp"].get(keydir, ".")
        f = QFileDialog.getExistingDirectory(combo, directory=llamacppdir)
        if not f:
            return
        globalconfig["llama.cpp"].__setitem__(keydir, f)
        refresh_llama(combo)

    refresh_llama(combollama)
    combollama.currentIndexChanged.connect(
        lambda idx: globalconfig["llama.cpp"].__setitem__(
            key, combollama.getIndexData(idx)
        )
    )
    return (
        (
            getIconButton(
                callback=functools.partial(download, combollama),
                icon="fa.download",
            )
            if download
            else None
        ),
        combollama,
        getIconButton(
            callback=functools.partial(getdir, combollama),
            icon="fa.folder-open",
        ),
        getIconButton(
            callback=functools.partial(refresh_llama, combollama),
            icon="fa.refresh",
            tips="刷新",
        ),
    )


def context_to_slider(context):
    min_value = math.log(256)
    max_value = math.log(131072)
    return int(10000 * (math.log(context) - min_value) / (max_value - min_value))


def slider_to_context(value):
    min_value = math.log(256)
    max_value = math.log(131072)
    return int(math.exp(min_value + (value / 10000) * (max_value - min_value)))


def update_context_from_slider(value):
    context_length = slider_to_context(value)
    context_length = max(256, min(131072, context_length))
    context_length = round(context_length / 256) * 256
    return context_length


def update_slider_from_input(value):
    value = round(value / 256) * 256
    slider_value = context_to_slider(value)
    slider_value = max(0, min(10000, slider_value))
    return slider_value


def _c_slice_spin(
    keydefault,
    keyvalue,
    range0,
    range1,
    range20,
    range21,
    step,
    step2,
    default,
    defaulttext,
    f1=lambda x: x,
    f2=lambda x: x,
):
    w = QWidget()
    text = QLabel(defaulttext)
    stack = QStackedWidget()
    stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    stack.addWidget(w)
    stack.addWidget(text)

    def __(_=None):
        _df = globalconfig["llama.cpp"].get(keydefault, False)
        stack.setCurrentIndex(1 - _df)

    switch = getsimpleswitch(
        globalconfig["llama.cpp"], keydefault, callback=__, default=False
    )
    __()
    l2 = QHBoxLayout(w)
    context_length = QSlider()
    context_length.setOrientation(Qt.Orientation.Horizontal)
    context_length.setRange(range0, range1)
    context_length.setPageStep(step)
    context_length.setValue(f1(globalconfig["llama.cpp"].get(keyvalue, default)))
    context_length_input = QSpinBox()
    context_length_input.setRange(range20, range21)
    context_length_input.setSingleStep(step2)
    context_length_input.setValue(globalconfig["llama.cpp"].get(keyvalue, default))
    l2.setContentsMargins(0, 0, 0, 0)
    l2.addWidget(context_length)
    l2.addWidget(context_length_input)

    def __(v):
        with QSignalBlocker(context_length_input) as _:
            context_length_input.setValue(f2(v))
            globalconfig["llama.cpp"][keyvalue] = f2(v)

    def __2(v):
        with QSignalBlocker(context_length) as _:
            context_length.setValue(f1(v))
            globalconfig["llama.cpp"][keyvalue] = v

    context_length.valueChanged.connect(__)
    context_length_input.valueChanged.connect(__2)

    l = QHBoxLayout()
    l.setContentsMargins(0, 0, 0, 0)
    l.addWidget(switch)
    l.addWidget(stack)
    return l


def nglnum():
    l = QHBoxLayout()
    combo = getsimplecombobox(
        ["auto", "all", "number"],
        d=globalconfig["llama.cpp"],
        k="gpu-layers-which",
        internal=["auto", "all", "number"],
        default="auto",
    )
    l.addWidget(combo)
    stack = QStackedWidget()
    stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    stack.addWidget(QLabel())
    stack.addWidget(
        getspinbox(0, 200, globalconfig["llama.cpp"], "gpu-layers", default=200)
    )

    def cb(_):
        stack.setCurrentIndex(combo.getIndexData(_) == "number")

    combo.currentIndexChanged.connect(cb)
    stack.setCurrentIndex(combo.getCurrentData() == "number")
    l.addWidget(stack)
    return l


def mmapmlock():
    ll = getsmalllabel(
        "--mlock",
        "--mlock    force system to keep model in RAM rather than swapping or compressing",
    )()
    swith2 = getsimpleswitch(globalconfig["llama.cpp"], key="mlock", default=False)

    def ___(x):
        ll.setHidden(x)
        swith2.setHidden(x)

    swith = getsimpleswitch(
        globalconfig["llama.cpp"], key="mmap", default=True, callback=___
    )
    l = QHBoxLayout()
    l.setContentsMargins(0, 0, 0, 0)
    l.addWidget(swith)
    l.addWidget(QLabel())
    l.addWidget(ll)
    l.addWidget(swith2)
    if swith.isChecked():
        swith2.hide()
        ll.hide()
    return l


llamacppautoHandle = None


def __getfirstllamacpp(llamacppdir: str):
    for _dir, _, _fs in os.walk(llamacppdir):
        for _f in _fs:
            if _f.lower() == "llama-server.exe":
                return os.path.abspath(os.path.join(_dir, _f))


def __getfirstgguf(ggufdir: str):
    for _dir, _, _fs in os.walk(ggufdir):
        for _f in _fs:
            if _f.lower().endswith(".gguf"):
                return os.path.abspath(os.path.join(_dir, _f))


@threader
def autostartllamacpp(force=False):
    if (not force) and (not globalconfig["llama.cpp"].get("autolaunch", False)):
        return

    gobject.base.llamacppstatus.emit(1)
    loghandle = open(gobject.getcachedir("llama-server.log"), "a", encoding="utf8")

    class _scopeexits:
        def __del__(self):
            gobject.base.llamacppstatus.emit(0)
            loghandle.close()

    __scopeexits = _scopeexits()
    llamacppdir = globalconfig["llama.cpp"].get("llama-server.exe.dir", ".")
    llamaserver = os.path.abspath(
        os.path.join(llamacppdir, globalconfig["llama.cpp"].get("llama-server.exe", ""))
    )
    if not os.path.isfile(llamaserver):
        llamaserver = __getfirstllamacpp(llamacppdir)
        if not llamaserver:
            return
    ggufdir = globalconfig["llama.cpp"].get("models", ".")
    gguf = os.path.abspath(
        os.path.join(
            ggufdir,
            globalconfig["llama.cpp"].get("model", ""),
        )
    )
    if not os.path.isfile(gguf):
        gguf = __getfirstgguf(ggufdir)
        if not gguf:
            return

    cmd = '"{llamaserver}" --version'.format(llamaserver=llamaserver)
    proc = subprochiderun(cmd, cwd=os.path.dirname(llamaserver))
    version: "re.Match" = re.search(r"version: (\d+?)", proc.stderr)
    if not version:
        gobject.base.translation_ui.displayglobaltooltip.emit("llama-server not runnable")
        raise Exception()
    version = int(version.groups()[0])

    ctx = ""
    if globalconfig["llama.cpp"].get("ctx-size-use", False):
        ctx = "--ctx-size {}".format(globalconfig["llama.cpp"].get("ctx-size", 2048))
    parallel = ""
    if globalconfig["llama.cpp"].get("parallel-use", False):
        parallel = "--parallel {}".format(globalconfig["llama.cpp"].get("parallel", 1))
    fa = ""
    if version >= 6325:
        fa = globalconfig["llama.cpp"].get("flash-attn", "auto")
        if globalconfig["llama.cpp"].get("flash-attn", "auto") != "auto":
            fa = "--flash-attn {fa}".format(fa=fa)
    else:
        if globalconfig["llama.cpp"].get("flash-attn", "auto") == "on":
            fa = "-fa"
    ngl = globalconfig["llama.cpp"].get("gpu-layers-which", "auto")
    if ngl == "number":
        ngl = globalconfig["llama.cpp"].get("gpu-layers", 200)
    gobject.base.translation_ui.displayglobaltooltip.emit("loading llama.cpp")
    mmap = "--mmap"
    if not globalconfig["llama.cpp"].get("mmap", True):
        mmap = "--no-mmap"
        if globalconfig["llama.cpp"].get("mlock", False):
            mmap += " --mlock"
    cmd = '"{llamaserver}" -m "{gguf}" --host {host} --port {port} {ctx} {parallel} --gpu-layers {ngl} {mmap} --metrics'.format(
        mmap=mmap,
        ngl=ngl,
        fa=fa,
        ctx=ctx,
        parallel=parallel,
        llamaserver=llamaserver,
        gguf=gguf,
        host=globalconfig["llama.cpp"].get("host", "127.0.0.1"),
        port=globalconfig["llama.cpp"].get("port", 8080),
    )
    gobject.base.llamacppstdout.emit(cmd)
    print(cmd, file=loghandle, flush=True)
    env = None
    _env: str = globalconfig["llama.cpp"].get("environment")
    if _env:
        env = os.environ.copy()
        for _ in _env.split(";"):
            _s = _.split("=")
            if len(_s) != 2:
                continue
            if (not _s[0]) or (not _s[1]):
                return
            env[_s[0]] = _s[1]
    proc = subprochiderun(cmd, cwd=os.path.dirname(llamaserver), run=False, env=env)
    global llamacppautoHandle
    llamacppautoHandle = NativeUtils.AutoKillProcess(proc.pid)

    @threader
    def _():
        cnt = 0
        while True:
            l = proc.stderr.readline()
            if not l:
                break
            if l == "main: starting the main loop...\n":
                cnt += 1
            elif l == "srv  update_slots: all slots are idle\n":
                cnt += 1
            if cnt == 2:
                cnt += 1
                gobject.base.translation_ui.displayglobaltooltip.emit(
                    "llama.cpp loaded"
                )
                gobject.base.llamacppstatus.emit(2)
            gobject.base.llamacppstdout.emit(l[:-1])
            print(l, file=loghandle, flush=True, end="")

    _()

    proc.wait()
    gobject.base.translation_ui.displayglobaltooltip.emit("llama.cpp exit")


def __llamadownload(parent):
    try:
        c = QCursor.pos()
        res = requests.get(
            "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest",
            proxies=getproxy(),
        ).json()
        menu = QMenu(parent)
        for _ in res["assets"]:
            name = _["name"]
            if (not "win" in name) or ("arm" in name):
                continue
            browser_download_url = _["browser_download_url"]
            size = format_bytes(_["size"])
            action = QAction(name + "\t" + size, menu)
            action.setData(browser_download_url)
            menu.addAction(action)
        ret = menu.exec(c)
        if ret:
            os.startfile(ret.data())
    except:
        print_exc()
        os.startfile("https://github.com/ggml-org/llama.cpp/releases")


def __ggufdownload(parent, checked):
    parent["pathlayout"].layout().setRowVisible(2, checked)


class AdvancedTreeTable(QTreeWidget):
    def updatelangtext(self):
        self.setHeaderLabels(_TR(self.headers))
        for i, item in enumerate(self.langitem):
            item.setText(self.vislang(self.langitemlang[i]))

    def __init__(self):
        super().__init__()
        self.langitem: "list[QLabel]" = []
        self.langitemlang: "list[str]" = []
        self.setup_ui()

    def setup_ui(self):
        self.headers = [
            ("模型"),
            ("大小"),
            ("更新时间"),
        ]
        self.setHeaderLabels(_TR(self.headers))
        header = self.header()
        header.setSectionsClickable(True)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, self.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_header_menu)
        self.itemDoubleClicked.connect(self._itemDoubleClicked)
        self.populate_data()
        self.setSortingEnabled(False)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.sortIndicatorChanged.connect(self.changed)

    def changed(self, index, order: Qt.SortOrder):
        self.sortItems(index, order)

    def astimestm(self, input_value):
        if isinstance(input_value, str):
            try:
                dt = datetime.fromisoformat(input_value.replace("Z", "+00:00"))
            except ValueError:
                dt = datetime.strptime(input_value.split("T")[0], "%Y-%m-%d")
        elif isinstance(input_value, (int, float)):
            if input_value > 1e10:
                dt = datetime.fromtimestamp(input_value / 1000)
            else:
                dt = datetime.fromtimestamp(input_value)
        return dt

    def alightoday(self, input_value):
        return self.astimestm(input_value).strftime("%Y-%m-%d")

    def vislang(self, l):
        def replace_match(_: "re.Match"):
            return _TR(Languages.fromcode(_.group(0)).zhsname)

        return re.sub("[a-z]+", replace_match, l)

    def vissize(self, z):
        if isinstance(z, str):
            return z
        return format_bytes(z)

    def populate_data(self):
        llm_model_list = tryreadconfig2("llm_model_list.json")
        for line in llm_model_list:
            user = QTreeWidgetItem(self, [line.get("author", line["account"])])
            _ = QWidget()
            _l = QHBoxLayout(_)
            _l.setContentsMargins(0, 0, 0, 0)
            _l.setAlignment(Qt.AlignmentFlag.AlignRight)
            label = QLabel(self.vislang(line["lang"]))
            _l.addWidget(label)
            self.setItemWidget(user, 0, _)
            self.langitemlang.append(line["lang"])
            self.langitem.append(label)
            user.setExpanded(True)
            for repo in line["repos"]:
                r = QTreeWidgetItem(user, [repo["repo"]])
                repo["models"].sort(
                    key=lambda _: -self.astimestm(_["timestamp"]).timestamp()
                )
                for m in repo["models"]:
                    itm = QTreeWidgetItem(
                        r,
                        [
                            m["file"],
                            self.vissize(m["size"]),
                            self.alightoday(m["timestamp"]),
                        ],
                    )
                    itm.setData(
                        0,
                        Qt.ItemDataRole.UserRole + 20,
                        (line["account"], repo["repo"], m["file"]),
                    )

    def _itemDoubleClicked(self, item: QTreeWidgetItem):
        data = item.data(0, Qt.ItemDataRole.UserRole + 20)
        if not data:
            return
        menu = QMenu(self)
        action = LAction("下载_huggingface", menu)
        action2 = LAction("下载_hf-mirror", menu)
        menu.addAction(action)
        menu.addAction(action2)
        a = menu.exec(QCursor.pos())
        if a:
            u, r, m = data
            if a == action:
                os.startfile(
                    "https://huggingface.co/{}/{}/resolve/main/{}".format(u, r, m)
                )
            elif a == action2:
                os.startfile(
                    "https://hf-mirror.com/{}/{}/resolve/main/{}".format(u, r, m)
                )

    def show_header_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
        self._itemDoubleClicked(item)

    def hide_column(self):
        action = self.sender()
        col = action.data()
        self.setColumnHidden(col, True)


def modellist():
    tree = AdvancedTreeTable()
    tree.setMinimumHeight(400)
    return tree


def llamacppgrid():
    _0, _1, _2, _3 = __create(
        __llamadownload,
        "llama-server.exe.dir",
        "llama-server.exe",
        lambda f: f.lower() == "llama-server.exe",
    )
    obj = dict()
    _, _12, _22, _32 = __create(
        None,
        "models",
        "model",
        lambda f: f.lower().endswith(".gguf"),
    )
    _02 = IconButton(icon="fa.download", checkable=True, checkablechangecolor=False)
    _02.clicked.connect(functools.partial(__ggufdownload, obj))

    def _edit(k, df):
        edit = QLineEdit(globalconfig["llama.cpp"].get(k, df))
        edit.textChanged.connect(
            functools.partial(globalconfig["llama.cpp"].__setitem__, k)
        )
        return edit

    statusbtn = IconButton("fa.play", tips="启动")

    def _cb():
        if statusbtn.iconStr() == "fa.play":
            autostartllamacpp(force=True)
        else:
            global llamacppautoHandle
            llamacppautoHandle = None

    statusbtn.clicked.connect(_cb)

    def __status(status: int):
        statusbtn.setIconStr(("fa.play", "fa.spinner", "fa.stop")[status])
        statusbtn.setToolTip(("启动", "启动中", "停止")[status])

    gobject.base.connectsignal(gobject.base.llamacppstatus, __status)
    _loglable = QPlainTextEdit()
    _loglable.setReadOnly(True)
    gobject.base.connectsignal(
        gobject.base.llamacppstdout, lambda s: _loglable.appendPlainText(s)
    )
    logopenbtn = IconButton(
        "fa.terminal", tips="log", checkable=True, checkablechangecolor=False
    )
    form = VisLFormLayout()
    form.addRow(
        "伴随启动",
        getboxlayout(
            [
                getsimpleswitch(
                    globalconfig["llama.cpp"], key="autolaunch", default=False
                ),
                getsmalllabel(""),
                statusbtn,
                getsmalllabel(""),
                logopenbtn,
                "",
            ]
        ),
    )
    form.addRow(_loglable)
    form.setRowVisible(1, False)
    logopenbtn.clicked.connect(lambda c: form.setRowVisible(1, c))
    return [
        [(form, -1)],
        [
            dict(
                name="pathlayout",
                title="路径",
                parent=obj,
                hiderows=[2],
                grid=[
                    ["llama-server", _0, _1, _2, _3],
                    ["Model", _02, _12, _22, _32],
                    [modellist],
                ],
            ),
        ],
        [
            dict(
                title="网络",
                type="grid",
                grid=[
                    [
                        "--port",
                        D_getspinbox(
                            0, 65536, globalconfig["llama.cpp"], "port", default=8080
                        ),
                        "",
                        "--host",
                        functools.partial(_edit, "host", "127.0.0.1"),
                    ],
                ],
            ),
        ],
        [
            dict(
                title="参数",
                type="grid",
                grid=[
                    [
                        getsmalllabel(
                            "size of the prompt context (-c)",
                            "-c, --ctx-size N   size of the prompt context (default: 0, 0 = loaded from model)",
                        ),
                        _c_slice_spin(
                            "ctx-size-use",
                            "ctx-size",
                            0,
                            10000,
                            256,
                            131072,
                            1,
                            128,
                            2048,
                            "default: 0, 0 = loaded from model",
                            f1=update_slider_from_input,
                            f2=update_context_from_slider,
                        ),
                    ],
                    [
                        getsmalllabel(
                            "number of server slots (-np)",
                            "-np, --parallel N  number of server slots (default: -1, -1 = auto)",
                        ),
                        _c_slice_spin(
                            "parallel-use",
                            "parallel",
                            1,
                            32,
                            1,
                            32,
                            1,
                            1,
                            1,
                            "default: -1, -1 = auto",
                        ),
                    ],
                    [
                        getsmalllabel(
                            "set Flash Attention use (-fa)",
                            "-fa, --flash-attn [on|off|auto]    set Flash Attention use ('on', 'off', or 'auto', default: 'auto')",
                        ),
                        getsimplecombobox(
                            ["auto", "on", "off"],
                            globalconfig["llama.cpp"],
                            k="flash-attn",
                            internal=["auto", "on", "off"],
                            default="auto",
                        ),
                    ],
                    [
                        getsmalllabel(
                            "whether to memory-map model (--mmap)",
                            "--mmap, --no-mmap  whether to memory-map model (if disabled, slower load but may reduce pageouts if not using mlock) (default: enabled)",
                        ),
                        mmapmlock,
                    ],
                    [
                        getsmalllabel(
                            "max. number of layers to store in VRAM (-ngl)",
                            "-ngl, --gpu-layers, --n-gpu-layers N   max. number of layers to store in VRAM, either an exact number, 'auto', or 'all' (default: auto)",
                        ),
                        nglnum,
                    ],
                ],
            )
        ],
        [
            dict(
                title="环境变量",
                type="grid",
                grid=[
                    [
                        "key=val;...",
                        functools.partial(
                            _edit, "environment", "CUDA_VISIBLE_DEVICES="
                        ),
                    ]
                ],
            )
        ],
    ]


def __showllamacpp(ref: "list[CollapsibleBoxWithButton]", checked):
    if ref[0].internalLayout.count() == 1:
        w = QWidget()
        ref[0].internalLayout.insertWidget(0, w)
        l = QHBoxLayout(w)
        margin = l.contentsMargins()
        margin.setBottom(0)
        l.setContentsMargins(margin)
        box = QGroupBox()
        box.setTitle("llama.cpp Launcher")
        l.addWidget(box)
        grid = QGridLayout(box)
        automakegrid(grid, llamacppgrid())
    else:
        ref[0].internalLayout.itemAt(0).widget().setVisible(checked)


def leftwidget(self, ref: "list[CollapsibleBoxWithButton]"):
    btn = IconButton("fa.plus", fix=False, tips="复制")
    btn.clicked.connect(functools.partial(btnpluscallback, self, self.__countnum))

    btn2 = IconButton("fa.minus", fix=False, tips="删除")
    btn2.clicked.connect(functools.partial(btndeccallback, self, self.__countnum))
    self.__del_btn = btn2
    if not loadvisinternal(True)[0]:
        btn2.hide()

    btn3 = IconButton(
        "fa.question",
        fix=False,
        tips="使用说明",
    )
    btn3.clicked.connect(
        lambda: os.startfile(dynamiclink("guochandamoxing.html", docs=True))
    )

    btn4 = AutoScaleImageButton(
        r"files\static\llama.cpp.light.png", r"files\static\llama.cpp.dark.png"
    )
    btn4.setToolTip("llama.cpp Launcher")
    btn4.clicked.connect(functools.partial(__showllamacpp, ref))
    return [btn3, btn, btn2, IconButton(none=True), btn4]


def __llmfold(self):

    is_gpt_likes = initsome11(self, getallllms(globalconfig["fanyi"]), save=True)
    ref = []
    fold = createfoldgrid(
        is_gpt_likes,
        "大模型",
        globalconfig["foldstatus"]["ts"],
        "gpt",
        "damoxinggridinternal",
        self,
        leftwidget=functools.partial(leftwidget, self, ref),
    )
    ref.append(fold)
    return fold


def initsome2(self, mianfei, api):

    onlinegrid = initsome11(self, mianfei)
    api = initsome11(self, api)
    grids = [
        [
            functools.partial(
                __llmfold,
                self,
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                onlinegrid,
                "传统",
                globalconfig["foldstatus"]["ts"],
                "free",
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                api,
                "传统_API",
                globalconfig["foldstatus"]["ts"],
                "api",
                leftwidget=D_getIconButton(
                    fix=False,
                    icon="fa.question",
                    callback=lambda: os.startfile(
                        dynamiclink("useapis/tsapi.html", docs=True)
                    ),
                    tips="使用说明",
                ),
            )
        ],
    ]
    return grids


@tryprint
def sqlite2json2(self, sqlitefile, targetjson=None, existsmerge=False):
    try:
        with sqlite3.connect(sqlitefile, check_same_thread=False) as sql:
            ret = sql.execute("SELECT * FROM artificialtrans  ").fetchall()
            js_format2: "dict[str, dict|str]" = {}
            collect = []
            for _aret in ret:
                if len(_aret) == 4:
                    _id, source, mt, source_origin = _aret
                    if targetjson:
                        source = source_origin
                    js_format2[source] = mt
                elif len(_aret) == 3:
                    _id, source, mt = _aret
                    js_format2[source] = mt
                try:
                    mtjs = json.loads(mt)
                except:
                    mtjs = mt
                js_format2[source] = mtjs
                if isinstance(mtjs, dict):
                    collect.extend(list(mtjs.keys()))
    except:
        print_exc()
        QMessageBox.critical(self, _TR("错误"), _TR("所选文件格式错误！"))
        return
    _collect = []
    for _, __ in Counter(collect).most_common():
        if _ in globalconfig["fanyi"]:
            _collect.append(_)
    dialog = LDialog(self, Qt.WindowType.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle("导出翻译记录为json文件")
    dialog.resize(QSize(800, 10))
    formLayout = LFormLayout(dialog)  # 配置layout

    combo = SuperCombo()
    combo.addItems([getannotatedapiname(_) for _ in _collect], _collect)

    formLayout.addRow("首选翻译", combo)
    e = QLineEdit(sqlitefile[: -(len(".sqlite"))])

    bu = LPushButton("选择路径")

    def __selectsavepath():
        ff = QFileDialog.getSaveFileName(
            dialog, directory=sqlitefile[: -(len(".sqlite"))]
        )
        if ff[0] == "":
            return
        e.setText(ff[0])

    bu.clicked.connect(__selectsavepath)
    hori = QHBoxLayout()
    hori.addWidget(e)
    hori.addWidget(bu)

    if targetjson is None:
        formLayout.addRow("保存路径", hori)

    button = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)

    def __savefunction(target, existsmerge):
        transkirokuuse = combo.getIndexData(combo.currentIndex())
        for k in js_format2:
            if isinstance(js_format2[k], dict):
                js_format2[k] = js_format2[k].get(transkirokuuse, "")

        if target is None:
            target = e.text() + ".json"
        if existsmerge and os.path.exists(target):
            try:
                with open(target, "r", encoding="utf8") as ff:
                    existsjs = json.load(ff)
            except:
                existsjs = {}
            for k in existsjs:
                if k not in js_format2 or js_format2[k] == "":
                    js_format2[k] = existsjs[k]
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf8") as ff:
            ff.write(
                json.dumps(js_format2, ensure_ascii=False, sort_keys=False, indent=4)
            )
        try:
            gameuid = gobject.base.gameuid
            _path = savehook_new_data[gameuid].get("gamejsonfile", [])
        except:
            _path: list = translatorsetting["rengong"]["args"]["jsonfile"]
        ready = set()
        for _ in _path:
            if not os.path.isfile(_):
                continue
            try:
                with open(_, "r", encoding="utf8") as ff:
                    _js: dict = json.load(ff)
            except:
                continue
            if not isinstance(_js, dict):
                continue
            ready = ready.union(_js.keys())
        changed = False
        for _ in ready:
            if _ in js_format2:
                js_format2.pop(_)
                changed = True
        if changed:
            with open(target[:-5] + ".partial.json", "w", encoding="utf8") as ff:
                ff.write(
                    json.dumps(
                        js_format2, ensure_ascii=False, sort_keys=False, indent=4
                    )
                )
        dialog.close()

    button.accepted.connect(functools.partial(__savefunction, targetjson, existsmerge))
    button.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
    button.button(QDialogButtonBox.StandardButton.Cancel).setText(_TR("取消"))
    dialog.show()


def sqlite2json(self):
    f = QFileDialog.getOpenFileName(directory="translation_record", filter="*.sqlite")
    if f[0] == "":
        return

    sqlite2json2(self, f[0])


def createbtnexport(self):

    bt = LPushButton("导出翻译记录为json文件")
    bt.clicked.connect(lambda x: sqlite2json(self))
    return bt


def setTabTwo_lazy(self, basel: QVBoxLayout):

    res = splittranslatortypes()

    _, not_is_gpt_like = splitapillm(res.offline)
    offlinegrid = initsome21(self, not_is_gpt_like)
    _, not_is_gpt_like = splitapillm(res.api)
    online_reg_grid = initsome2(self, res.free, not_is_gpt_like)
    prets = initsome11(self, res.pre)
    prets += [[(functools.partial(createbtnexport, self), 0)]]
    pretransgrid = [
        [dict(type="grid", title="预翻译", grid=prets)],
        [dict(type="grid", title="其他", grid=initsome11(self, res.other))],
    ]
    pretransgrid += offlinegrid
    pretransgrid = [
        [
            functools.partial(
                createfoldgrid,
                pretransgrid,
                "其他",
                globalconfig["foldstatus"]["ts"],
                "special",
            )
        ],
    ]
    online_reg_grid += pretransgrid
    savelay = []
    makescrollgrid(online_reg_grid, basel, savelay=savelay)
