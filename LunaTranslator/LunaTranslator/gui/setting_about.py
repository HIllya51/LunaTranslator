from qtsymbols import *
import platform, functools, sys, os
import winsharedutils, gobject
from myutils.config import globalconfig, _TR, static_data, _TRL
from myutils.wrapper import threader
from myutils.utils import makehtml, getimageformatlist
from myutils.githubupdate import updatemethod, getvesionmethod
from gui.usefulwidget import (
    D_getsimpleswitch,
    D_getsimplecombobox,
    makescrollgrid,
    makesubtab_lazy,
)

@threader
def getversion(self):
    version = winsharedutils.queryversion(sys.argv[0])
    if version is None:
        self.versiontextsignal.emit("unknown")
        return
    versionstring = f"v{version[0]}.{version[1]}.{version[2]}"
    self.versiontextsignal.emit(
        ("当前版本") + ":" + versionstring + "  " + ("最新版本") + ":" + ("获取中")
    )  # ,'',url,url))
    _version = getvesionmethod()

    if _version is None:
        sversion = _TR("获取失败")
    else:
        sversion = _version
    self.versiontextsignal.emit(
        (
            "{}:{}  {}  {}:{}".format(
                _TR("当前版本"),
                versionstring,
                platform.architecture()[0],
                _TR("最新版本"),
                sversion,
            )
        )
    )
    if _version is not None and version < tuple(
        int(_) for _ in _version[1:].split(".")
    ):
        if globalconfig["autoupdate"]:
            updatemethod(_version, self.progresssignal.emit)


def updateprogress(self, text, val):
    try:
        self.downloadprogress.setValue(val)
        self.downloadprogress.setFormat(text)
    except:
        self.downloadprogress_cache = val, text


def createdownloadprogress(self):

    self.downloadprogress = QProgressBar()

    self.downloadprogress.setRange(0, 10000)

    self.downloadprogress.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    try:
        val, text = self.downloadprogress_cache
        self.downloadprogress.setValue(val)
        self.downloadprogress.setFormat(text)
    except:
        pass
    return self.downloadprogress


def createversionlabel(self):

    self.versionlabel = QLabel()
    self.versionlabel.setOpenExternalLinks(True)
    self.versionlabel.setTextInteractionFlags(
        Qt.TextInteractionFlag.LinksAccessibleByMouse
    )
    try:
        self.versionlabel.setText(self.versionlabel_cache)
    except:
        pass
    return self.versionlabel


def versionlabelmaybesettext(self, x):
    try:
        self.versionlabel.setText(x)
    except:
        self.versionlabel_cache = x


def resourcegrid(self, l):
    titles = []
    makewidgetsfunctions = []
    for sourcetype in static_data["aboutsource"]:
        titles.append(sourcetype["name"])
        sources = sourcetype["sources"]
        grid = []
        for source in sources:
            name = source["name"]
            link = source["link"]
            if type(link) == list:
                for i, _link in enumerate(link):
                    grid.append(
                        [
                            (_TR(name) if i == 0 else "", 1, ""),
                            (makehtml(_link, True), 2, "link"),
                        ]
                    )
            else:
                if link[-8:] == "releases":
                    __ = False
                elif link[-1] == "/":
                    __ = False
                else:
                    __ = True
                grid.append([(_TR(name), 1, ""), (makehtml(link, __), 2, "link")])
        makewidgetsfunctions.append(functools.partial(makescrollgrid, grid))
    tab, dotab = makesubtab_lazy(_TRL(titles), makewidgetsfunctions, delay=True)
    l.addWidget(tab)
    dotab()


def createimageview(self):
    lb = QLabel()
    img = QPixmap.fromImage(QImage("./files/zan.jpg"))
    img.setDevicePixelRatio(self.devicePixelRatioF())
    img = img.scaled(
        600,
        600,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    lb.setPixmap(img)
    return lb


def setTab_aboutlazy(self, basel):
    webviews = ["IEFrame", "WebView2"]
    if gobject.testuseqwebengine():
        webviews.append("QWebEngine")
    grid2 = [
        [
            ("自动下载更新(需要连接github)", 5),
            (
                D_getsimpleswitch(
                    globalconfig, "autoupdate", callback=lambda x: getversion(self)
                ),
                1,
            ),
            ("", 10),
        ],
        [(functools.partial(createversionlabel, self), 10)],
        [(functools.partial(createdownloadprogress, self), 10)],
        [],
        [("网络请求_重启生效", -1)],
        [(D_getsimplecombobox(["winhttp", "libcurl"], globalconfig, "network"), 5)],
        [("网页显示", -1)],
        [
            (
                D_getsimplecombobox(
                    webviews,
                    globalconfig,
                    "usewebview",
                ),
                5,
            )
        ],
        [("截图保存格式", -1)],
        [(D_getsimplecombobox(getimageformatlist(), globalconfig, "imageformat"), 5)],
    ]

    shuominggrid = [
        [
            "项目网站",
            (makehtml("https://github.com/HIllya51/LunaTranslator"), 3, "link"),
        ],
        [
            "问题反馈",
            (makehtml("https://github.com/HIllya51/LunaTranslator/issues"), 3, "link"),
        ],
        [
            "使用说明",
            (
                makehtml("https://hillya51.github.io/LunaTranslator_tutorial/#/zh/"),
                3,
                "link",
            ),
        ],
    ]
    if globalconfig["languageuse"] == 0:
        shuominggrid += [
            [
                "交流群",
                (makehtml("https://qm.qq.com/q/qE32v9NYBO", show=912525396), 3, "link"),
            ],
            [],
            [("如果你感觉该软件对你有帮助，欢迎微信扫码赞助，谢谢~", -1)],
        ]

        shuominggrid += [[(functools.partial(createimageview, self), -1)]]
    else:
        shuominggrid += [
            [],
            [
                (
                    "If you feel that the software is helpful to you, ",
                    4,
                    "link",
                )
            ],
            [
                (
                    'welcome to become my <a href="https://patreon.com/HIllya51">sponsor. Thank you ~ ',
                    4,
                    "link",
                )
            ],
        ]

    tab, dotab = makesubtab_lazy(
        _TRL(["相关说明", "其他设置", "资源下载"]),
        [
            functools.partial(makescrollgrid, shuominggrid),
            functools.partial(makescrollgrid, grid2),
            functools.partial(resourcegrid, self),
        ],
        delay=True,
    )
    basel.addWidget(tab)
    dotab()
