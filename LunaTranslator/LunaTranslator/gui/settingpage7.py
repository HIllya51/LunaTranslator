import functools, copy, os, gobject
from qtsymbols import *
from traceback import print_exc
from myutils.config import (
    globalconfig,
    postprocessconfig,
    static_data,
    savehook_new_data,
    _TR,
)
from gui.usefulwidget import (
    getcolorbutton,
    D_getcolorbutton,
    D_getsimpleswitch,
    makescrollgrid,
    getvboxwidget,
    makesubtab_lazy,
)
from gui.codeacceptdialog import codeacceptdialog
from gui.inputdialog import (
    postconfigdialog,
    autoinitdialog,
    autoinitdialog_items,
)
from myutils.utils import (
    selectdebugfile,
    checkpostlangmatch,
    loadpostsettingwindowmethod,
)
from myutils.post import POSTSOLVE


def savegameprocesstext():
    try:
        try:
            with open("./userconfig/mypost.py", "r", encoding="utf8") as ff:
                _mypost = ff.read()
            os.makedirs("./userconfig/posts", exist_ok=True)
            with open(
                "./userconfig/posts/{}.py".format(gobject.baseobject.textsource.uuname),
                "w",
                encoding="utf8",
            ) as ff:
                ff.write(_mypost)
        except:
            _mypost = None
        ranklist = []
        postargs = {}
        for postitem in globalconfig["postprocess_rank"]:
            if postitem not in postprocessconfig:
                continue
            if postprocessconfig[postitem]["use"]:
                ranklist.append(postitem)
                postargs[postitem] = copy.deepcopy(postprocessconfig[postitem])
        exepath = gobject.baseobject.textsource.pname
        savehook_new_data[exepath]["save_text_process_info"] = {
            "postprocessconfig": postargs,
            "rank": ranklist,
            "mypost": gobject.baseobject.textsource.uuname,
        }
        if savehook_new_data[exepath]["use_saved_text_process"] == False:
            savehook_new_data[exepath]["use_saved_text_process"] = True
    except:
        print_exc()


def delaysetcomparetext(self, s):
    try:
        self.__fromtext.setPlainText(s)
        self.__totext.setPlainText(POSTSOLVE(s))
    except:
        self.__fromtext_cache = s
        self.__totext_cache = POSTSOLVE(s)


def getcomparelayout(self):

    layout = QHBoxLayout()
    fromtext = QPlainTextEdit()
    totext = QPlainTextEdit()
    solvebutton = getcolorbutton(
        globalconfig,
        "",
        callback=lambda: totext.setPlainText(POSTSOLVE(fromtext.toPlainText())),
        icon="fa.chevron-right",
        constcolor="#FF69B4",
    )

    layout.addWidget(fromtext)
    layout.addWidget(solvebutton)
    layout.addWidget(totext)
    w = QWidget()
    w.setLayout(layout)
    self.__fromtext = fromtext
    self.__totext = totext
    try:
        fromtext.setPlainText(self.__fromtext_cache)
        totext.setPlainText(self.__totext_cache)
    except:
        pass
    return w


def setTab7_lazy(self, basel):
    grids = [[("预处理方法", 6), "", "", ("调整执行顺序", 6)]]
    if set(postprocessconfig.keys()) != set(globalconfig["postprocess_rank"]):
        globalconfig["postprocess_rank"] = list(postprocessconfig.keys())
    sortlist = globalconfig["postprocess_rank"]
    savelist = []
    savelay = []

    def changerank(item, up):

        idx = sortlist.index(item)
        idx2 = idx + (-1 if up else 1)
        if idx2 < 0 or idx2 >= len(sortlist):
            return
        headoffset = 1
        idx2 = idx + (-1 if up else 1)
        sortlist[idx], sortlist[idx2] = sortlist[idx2], sortlist[idx]
        for i, ww in enumerate(savelist[idx + headoffset]):

            w1 = savelay[0].indexOf(ww)
            w2 = savelay[0].indexOf(savelist[idx2 + headoffset][i])
            p1 = savelay[0].getItemPosition(w1)
            p2 = savelay[0].getItemPosition(w2)
            savelay[0].removeWidget(ww)
            savelay[0].removeWidget(savelist[idx2 + headoffset][i])

            savelay[0].addWidget(savelist[idx2 + headoffset][i], *p1)
            savelay[0].addWidget(ww, *p2)
        savelist[idx + headoffset], savelist[idx2 + headoffset] = (
            savelist[idx2 + headoffset],
            savelist[idx + headoffset],
        )

    for i, post in enumerate(sortlist):
        if post == "_11":
            config = D_getcolorbutton(
                globalconfig,
                "",
                callback=lambda: selectdebugfile("./userconfig/mypost.py"),
                icon="fa.gear",
                constcolor="#FF69B4",
            )
        else:
            if post not in postprocessconfig:
                continue
            if post == "_remove_chaos":
                config = D_getcolorbutton(
                    globalconfig,
                    "",
                    icon="fa.gear",
                    constcolor="#FF69B4",
                    callback=lambda: codeacceptdialog(self),
                )
            elif "args" in postprocessconfig[post]:
                if isinstance(list(postprocessconfig[post]["args"].values())[0], dict):
                    callback = functools.partial(
                        postconfigdialog,
                        self,
                        postprocessconfig[post]["args"],
                        postprocessconfig[post]["name"],
                    )
                else:
                    items = autoinitdialog_items(postprocessconfig[post])
                    callback = functools.partial(
                        autoinitdialog,
                        self,
                        postprocessconfig[post]["name"],
                        600,
                        items,
                    )
                config = D_getcolorbutton(
                    globalconfig,
                    "",
                    callback=callback,
                    icon="fa.gear",
                    constcolor="#FF69B4",
                )
            else:
                config = ""

        button_up = D_getcolorbutton(
            globalconfig,
            "",
            callback=functools.partial(changerank, post, True),
            icon="fa.arrow-up",
            constcolor="#FF69B4",
        )
        button_down = D_getcolorbutton(
            globalconfig,
            "",
            callback=functools.partial(changerank, post, False),
            icon="fa.arrow-down",
            constcolor="#FF69B4",
        )

        l = [
            ((postprocessconfig[post]["name"]), 6),
            D_getsimpleswitch(postprocessconfig[post], "use"),
            config,
            button_up,
            button_down,
        ]
        grids.append(l)
    grids2 = []
    for item in static_data["transoptimi"]:
        name = item["name"]
        visname = item["visname"]
        if checkpostlangmatch(name):
            grids2.append(
                [((visname), 6), D_getsimpleswitch(globalconfig["transoptimi"], name)]
            )
            setting = loadpostsettingwindowmethod(name)

            def __(_f, _1, _2):
                return _f(_1)

            if setting:
                grids2[-1].append(
                    D_getcolorbutton(
                        globalconfig,
                        "",
                        callback=functools.partial(__, setting, self),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    )
                )
    grids2 += [[("", 12)]]

    def ___(lay):
        vboxw, vbox = getvboxwidget()
        lay.addWidget(vboxw)
        _w = makescrollgrid(grids, vbox, True, savelist, savelay)
        _w.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        def showmenu(p: QPoint):

            try:
                gobject.baseobject.textsource.pname  # 检查是否为texthook

                menu = QMenu(_w)
                save = QAction(_TR("保存当前游戏的文本处理流程"))
                menu.addAction(save)
                action = menu.exec(_w.cursor().pos())
                if action == save:
                    savegameprocesstext()
            except:
                pass

        _w.customContextMenuRequested.connect(showmenu)

        vbox.addWidget(getcomparelayout(self))

    tab, dotab = makesubtab_lazy(
        ["文本预处理", "翻译优化"],
        [___, functools.partial(makescrollgrid, grids2)],
        delay=True,
    )
    basel.addWidget(tab)
    dotab()
