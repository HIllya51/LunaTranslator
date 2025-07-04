from qtsymbols import *
import functools, re
import NativeUtils
from myutils.config import globalconfig, static_data
from gobject import runtime_for_xp, runtime_bit_64, runtime_for_win10
from myutils.wrapper import threader
from myutils.utils import makehtml, getlanguse, dynamiclink
import requests, importlib
import gobject
import os
from traceback import print_exc
from gui.usefulwidget import (
    D_getsimpleswitch,
    makescrollgrid,
    createfoldgrid,
    SuperCombo,
    getIconButton,
    getsmalllabel,
    getboxlayout,
    MDLabel,
    NQGroupBox,
    VisLFormLayout,
    clearlayout,
    makeforms,
)
from language import UILanguages, Languages
from gui.dynalang import LLabel
from myutils.updater import versionchecktask


def createversionlabel(self):

    versionlabel = getsmalllabel()()
    versionlabel.setOpenExternalLinks(False)
    versionlabel.linkActivated.connect(
        lambda _: os.startfile(dynamiclink("/ChangeLog"))
    )
    versionlabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)

    gobject.base.connectsignal(
        gobject.base.versiontextsignal,
        functools.partial(versionlabelmaybesettext, versionlabel),
    )
    return versionlabel


def versionlabelmaybesettext(versionlabel: QLabel, x):
    x = '<a href="fuck">{}</a>'.format(x)
    versionlabel.setText(x)


def delayloadlinks(key):
    sources: "list[dict]" = static_data["aboutsource"][key]
    grid = []
    for source in sources:
        link = source.get("link")
        if link:
            grid.append(
                [
                    source.get("name", ""),
                    (makehtml(link, source.get("vis", None)), 2),
                    source.get("about", ""),
                ]
            )
            continue
        __grid = []
        function = source.get("function")
        if function:
            try:
                func = getattr(
                    importlib.import_module(function[0]),
                    function[1],
                )
                __grid.append([(func, 0)])
            except:
                print_exc()
        else:
            for link in source["links"]:
                __grid.append(
                    [
                        link["name"],
                        (makehtml(link["link"], link.get("vis", None)), 2),
                    ]
                    + ([link.get("about")] if link.get("about") else [])
                )

        grid.append([dict(title=source.get("name", None), type="grid", grid=__grid)])
    return grid


def offlinelinks(key):
    box = createfoldgrid(delayloadlinks(key), "资源下载")
    return box


def changeUIlanguage(_):
    languageChangeEvent = QEvent(QEvent.Type.LanguageChange)
    QApplication.sendEvent(QApplication.instance(), languageChangeEvent)
    try:
        gobject.base.textsource.setlang()
    except:
        pass


def validator(createproxyedit_check: QLabel, text):
    regExp = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$")
    mch = regExp.match(text)
    for _ in (1,):

        if not mch:
            break
        _1, _2, _3, _4, _p = [int(_) for _ in mch.groups()]
        if _p > 65535:
            break
        if any([_ > 255 for _ in [_1, _2, _3, _4]]):
            break
        globalconfig["proxy"] = text
        createproxyedit_check.hide()
        return
    if not createproxyedit_check.isVisible():
        createproxyedit_check.show()
    createproxyedit_check.setText("Invalid")


def proxyusage(self):
    hbox = QHBoxLayout()
    hbox.setContentsMargins(0, 0, 0, 0)
    w2 = QWidget()
    w2.setEnabled(globalconfig["useproxy"])
    switch1 = D_getsimpleswitch(globalconfig, "useproxy", callback=w2.setEnabled)()
    hbox.addWidget(switch1)
    hbox.addWidget(w2)
    hbox2 = QHBoxLayout(w2)
    hbox2.setContentsMargins(0, 0, 0, 0)
    hbox2.addWidget(QLabel())
    hbox2.addWidget(LLabel("使用系统代理"))

    w3 = QWidget()
    hbox3 = QHBoxLayout(w3)
    hbox3.setContentsMargins(0, 0, 0, 0)

    def __(x):
        x = not x
        w3.setVisible(x)
        if x:
            if hbox2.count() > 4:
                hbox2.takeAt(hbox2.count() - 1)
        else:
            hbox2.addStretch(0)

    switch2 = D_getsimpleswitch(globalconfig, "usesysproxy", callback=__)()
    hbox2.addWidget(switch2)
    hbox2.addWidget(w3)
    __(globalconfig["usesysproxy"])
    hbox3.addWidget(QLabel())
    hbox3.addWidget(LLabel("手动设置代理"))
    proxy = QLineEdit(globalconfig["proxy"])
    check = QLabel()
    hbox3.addWidget(proxy)
    hbox3.addWidget(check)
    validator(check, globalconfig["proxy"])
    proxy.textChanged.connect(functools.partial(validator, check))
    return hbox


def updatexx(self):
    return getboxlayout(
        [
            D_getsimpleswitch(
                globalconfig,
                "autoupdate",
                callback=lambda _: (
                    versionchecktask.put(_),
                    (
                        self.aboutlayout.layout().setRowVisible(3, False)
                        if not _
                        else ""
                    ),
                ),
            ),
            getsmalllabel(""),
            getsmalllabel("最新版本"),
            functools.partial(createversionlabel, self),
            "",
        ]
    )


def progress___(self):

    downloadprogress = QProgressBar(self)
    downloadprogress.setRange(0, 10000)
    downloadprogress.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    self.downloadprogress = downloadprogress
    return downloadprogress


def _progresssignal4(
    updatelayout: VisLFormLayout, downloadprogress: QProgressBar, text, val
):
    downloadprogress.setValue(val)
    downloadprogress.setFormat(text)
    if (val or text) and globalconfig["autoupdate"]:
        updatelayout.setRowVisible(3, True)


class MDLabel1(MDLabel):
    def __init__(self, md, static=False):
        super().__init__(md, static)
        self.setOpenExternalLinks(False)
        self.linkActivated.connect(self._linkActivated)

    def setText(self, t):
        t = re.sub("<a(.*?)>", '<a\\1 style="color: #E91E63;">', t)
        super().setText(t)

    def _linkActivated(self, link: str):
        if link == "/":
            link = dynamiclink("/", docs=True)
        os.startfile(link)


class aboutwidget(NQGroupBox):
    def __init__(self, *a):
        super().__init__(*a)
        self.grid = QFormLayout(self)
        self.lastlang = None
        self.lastlangcomp = {Languages.Chinese: 1, Languages.TradChinese: 2, None: -1}
        self.updatelangtext()

    def createimageview(self):
        lb = QLabel()
        img = QPixmap.fromImage(QImage("files/static/zan.jpg"))
        img.setDevicePixelRatio(self.devicePixelRatioF())
        img = img.scaled(
            500,
            500,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        lb.setPixmap(img)
        return lb

    def updatelangtext(self):
        if self.lastlangcomp.get(self.lastlang, 0) == self.lastlangcomp.get(
            getlanguse(), 0
        ):
            return
        self.lastlan = getlanguse()
        clearlayout(self.grid)
        t2 = "软件维护不易，如果您感觉该软件对你有帮助，欢迎微信扫码赞助，您的支持将成为软件长期维护的助力，谢谢~"
        t3 = "如果使用中遇到困难，可以查阅[使用说明](/)、观看[我的B站视频](https://space.bilibili.com/592120404/video)，也欢迎加入[QQ群963119821](https://qm.qq.com/q/I5rr3uEpi2)、发起[issue](https://github.com/HIllya51/LunaTranslator/issues)来与我交流。"
        t4 = "软件维护不易，如果您感觉该软件对你有帮助，欢迎成为我的[sponsor](https://patreon.com/HIllya51)，您的支持将成为软件长期维护的助力，谢谢~"
        t7 = "軟體維護不易，如果您感覺該軟體對你有幫助，歡迎微信掃碼贊助，或成為我的[sponsor](https://patreon.com/HIllya51)，您的支持將成為軟體長期維護的助力，謝謝~"
        t5 = "如果使用中遇到困難，可以查閱[使用說明](/)、觀看[我的B站影片](https://space.bilibili.com/592120404/video)，也歡迎加入[Discord](https://discord.com/invite/ErtDwVeAbhtB)/[QQ群96311982](https://qm.qq.com/q/I5rr3uEpi2)、發起[issue](https://github.com/HIllya51/LunaTranslator/issues)來與我交流。"
        t6 = "如果使用中遇到困难，可以查阅[使用说明](/)，也欢迎加入[Discord](https://discord.com/invite/ErtDwVeAbB)、发起[issue](https://github.com/HIllya51/LunaTranslator/issues)来与我交流。"
        if getlanguse() == Languages.Chinese:
            shuominggrid = [
                [functools.partial(MDLabel1, "\n\n".join([t3, t2]), static=True)],
                [self.createimageview],
            ]

        elif getlanguse() == Languages.TradChinese:
            shuominggrid = [
                [functools.partial(MDLabel1, "\n\n".join([t5, t7]), static=True)],
                [self.createimageview],
            ]
        else:
            shuominggrid = [[functools.partial(MDLabel1, "\n\n".join([t6, t4]))]]

        makeforms(self.grid, shuominggrid)


class delayloadsvg(QSvgWidget):
    def __init__(self, REPO):
        super().__init__()
        self.REPO = REPO
        link = "https://img.shields.io/github/license/" + REPO
        self._load(link)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, _: QMouseEvent):
        if _.button() == Qt.MouseButton.LeftButton:
            os.startfile("https://github.com/{repo}".format(repo=self.REPO))

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.Type.FontChange:
            self.loadh()
        return super().event(a0)

    def loadh(self):
        h = QFontMetricsF(self.font()).height()
        renderer = self.renderer()
        if renderer != None:
            size = renderer.defaultSize()
            self.setFixedSize(QSizeF(size.width() * h / size.height(), h).toSize())

    @threader
    def _load(self, link):
        self.load(requests.get(link).content)
        self.loadh()


def makelink(repo):
    return [
        functools.partial(delayloadsvg, repo),
        '<a href="https://github.com/{repo}">{repo}</a>'.format(repo=repo),
    ]


class __delayloadlangs(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.como = SuperCombo(static=True)
        self.como.addItem(Languages.fromcode(globalconfig["languageuse2"]).nativename)
        # Qt6的脑残fontmerging机制导致变得很慢。
        QTimer.singleShot(0, self.delayload)
        self.addWidget(self.como)

    def delayload(self):
        self.como.clear()
        inner, vis = [_.code for _ in UILanguages], [_.nativename for _ in UILanguages]
        self.como.addItems(vis, inner)
        self.como.setCurrentData(globalconfig["languageuse2"])
        self.como.currentIndexChanged.connect(
            lambda _: (
                globalconfig.__setitem__("languageuse2", self.como.getCurrentData()),
                changeUIlanguage(0),
            )
        )


def setTab_about(self, basel):

    makescrollgrid(
        [
            [
                dict(
                    name="aboutlayout",
                    parent=self,
                    hiderows=[2, 3],
                    grid=[
                        ["UI语言", __delayloadlangs],
                        ["使用代理", functools.partial(proxyusage, self)],
                        ["自动更新", functools.partial(updatexx, self)],
                        [functools.partial(progress___, self)],
                    ],
                ),
            ],
            [aboutwidget],
            [
                functools.partial(
                    createfoldgrid,
                    [
                        [
                            functools.partial(
                                delayloadsvg,
                                "HIllya51/LunaTranslator",
                            ),
                            functools.partial(
                                MDLabel,
                                "[LunaTranslator](https://github.com/HIllya51/LunaTranslator)使用[GPLv3](https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE)许可证。",
                            ),
                        ],
                        [("引用的项目", -1)],
                        makelink("opencv/opencv"),
                        makelink("microsoft/onnxruntime"),
                        makelink("Artikash/Textractor"),
                        makelink("RapidAI/RapidOcrOnnx"),
                        makelink("PaddlePaddle/PaddleOCR"),
                        makelink("Blinue/Magpie"),
                        makelink("nanokina/ebyroid"),
                        makelink("xupefei/Locale-Emulator"),
                        makelink("InWILL/Locale_Remulator"),
                        makelink("zxyacb/ntlea"),
                        makelink("Chuyu-Team/YY-Thunks"),
                        makelink("Chuyu-Team/VC-LTL5"),
                        makelink("uyjulian/AtlasTranslate"),
                        makelink("ilius/pyglossary"),
                        makelink("ikegami-yukino/mecab"),
                        makelink("AngusJohnson/Clipper2"),
                        makelink("rapidfuzz/rapidfuzz-cpp"),
                        makelink("TsudaKageyu/minhook"),
                        makelink("lobehub/lobe-icons"),
                        makelink("kokke/tiny-AES-c"),
                        makelink("TPN-Team/OCR"),
                        makelink("AuroraWright/owocr"),
                        makelink("b1tg/win11-oneocr"),
                        makelink("mity/md4c"),
                        makelink("swigger/wechat-ocr"),
                        makelink("rupeshk/MarkdownHighlighter"),
                        makelink("sindresorhus/github-markdown-css"),
                        makelink("gexgd0419/NaturalVoiceSAPIAdapter"),
                        makelink("microsoft/PowerToys"),
                    ],
                    "LICENSE",
                )
            ],
        ],
        basel,
    )

    gobject.base.connectsignal(
        gobject.base.progresssignal4,
        functools.partial(
            _progresssignal4, self.aboutlayout.layout(), self.downloadprogress
        ),
    )
    gobject.base.connectsignal(
        gobject.base.showupdatebtn,
        lambda: self.aboutlayout.layout().setRowVisible(2, True),
    )
