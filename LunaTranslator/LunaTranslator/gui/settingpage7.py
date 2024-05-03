import functools

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QTextEdit,
    QHBoxLayout,
    QWidget,
    QMenu,
    QAction,
)
from PyQt5.QtCore import Qt, QPoint
from traceback import print_exc
from myutils.config import (
    globalconfig,
    postprocessconfig,
    static_data,
    _TR,
)
import functools, gobject
from gui.usefulwidget import getcolorbutton, getsimpleswitch
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
from myutils.config import savehook_new_data
import copy, os
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


def settab7direct(self):
    self.comparelayout = getcomparelayout(self)


def setTab7(self):
    self.tabadd_lazy(self.tab_widget, ("文本处理"), lambda: setTab7_lazy(self))


def getcomparelayout(self):

    layout = QHBoxLayout()
    fromtext = QTextEdit()
    totext = QTextEdit()
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

    def _(s):
        fromtext.setPlainText(s)
        totext.setPlainText(POSTSOLVE(fromtext.toPlainText()))

    self.showandsolvesig.connect(_)
    return w


def setTab7_lazy(self):
    grids = [[("预处理方法", 6), "", "", ("调整执行顺序", 6)]]
    if set(postprocessconfig.keys()) != set(globalconfig["postprocess_rank"]):
        globalconfig["postprocess_rank"] = list(postprocessconfig.keys())
    sortlist = globalconfig["postprocess_rank"]
    savelist = []
    savelay = []

    def changerank(item, up):

        ii = sortlist.index(item)
        if up and ii == 0:
            return
        if up == False and ii == len(sortlist) - 1:
            return
        headoffset = 1
        toexchangei = ii + (-1 if up else 1)
        sortlist[ii], sortlist[toexchangei] = sortlist[toexchangei], sortlist[ii]
        for i, ww in enumerate(savelist[ii + headoffset]):

            w1 = savelay[0].indexOf(ww)
            w2 = savelay[0].indexOf(savelist[toexchangei + headoffset][i])
            p1 = savelay[0].getItemPosition(w1)
            p2 = savelay[0].getItemPosition(w2)
            savelay[0].removeWidget(ww)
            savelay[0].removeWidget(savelist[toexchangei + headoffset][i])

            savelay[0].addWidget(savelist[toexchangei + headoffset][i], *p1)
            savelay[0].addWidget(ww, *p2)
        savelist[ii + headoffset], savelist[toexchangei + headoffset] = (
            savelist[toexchangei + headoffset],
            savelist[ii + headoffset],
        )

    for i, post in enumerate(sortlist):
        if post == "_11":
            config = getcolorbutton(
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
                config = getcolorbutton(
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
                config = getcolorbutton(
                    globalconfig,
                    "",
                    callback=callback,
                    icon="fa.gear",
                    constcolor="#FF69B4",
                )
            else:
                config = ""

        button_up = getcolorbutton(
            globalconfig,
            "",
            callback=functools.partial(changerank, post, True),
            icon="fa.arrow-up",
            constcolor="#FF69B4",
        )
        button_down = getcolorbutton(
            globalconfig,
            "",
            callback=functools.partial(changerank, post, False),
            icon="fa.arrow-down",
            constcolor="#FF69B4",
        )

        l = [
            ((postprocessconfig[post]["name"]), 6),
            getsimpleswitch(postprocessconfig[post], "use"),
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
                [((visname), 6), getsimpleswitch(globalconfig["transoptimi"], name)]
            )
            setting = loadpostsettingwindowmethod(name)

            def __(_f, _1, _2):
                return _f(_1)

            if setting:
                grids2[-1].append(
                    getcolorbutton(
                        globalconfig,
                        "",
                        callback=functools.partial(__, setting, self),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    )
                )

    def __():
        _w = self.makescroll(self.makegrid(grids, True, savelist, savelay))
        _w.setContextMenuPolicy(Qt.CustomContextMenu)

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
        return _w

    tab = self.makesubtab_lazy(
        ["文本预处理", "翻译优化"],
        [lambda: __(), lambda: self.makescroll(self.makegrid(grids2))],
    )

    return self.makevbox([tab, self.comparelayout])
