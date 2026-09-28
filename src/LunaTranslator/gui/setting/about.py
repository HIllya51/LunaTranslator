from qtsymbols import *
import functools, re
from myutils.config import globalconfig, static_data, _TR, dynamiclink
from myutils.wrapper import threader
from myutils.utils import makehtml, getlanguse, nowisdark
from gui.qevent import DarkLightChangedEvent
import requests, importlib
import gobject
import os, NativeUtils
from traceback import print_exc
from gui.usefulwidget import (
    D_getsimpleswitch,
    makegrid,
    makescrollgrid,
    createfoldgrid,
    SuperCombo,
    getsmalllabel,
    getboxlayout,
    LinkLabel,
    SClickableLabel,
    VisLFormLayout,
    tabadd_lazy,
)
from gui.setting.setting_year import yearsummary
from language import UILanguages, Languages
from myutils.updater import versionchecktask


def createversionlabel():

    versionlabel = LinkLabel()
    versionlabel.setOpenExternalLinks(False)
    versionlabel.linkActivated.connect(lambda _: os.startfile(dynamiclink("ChangeLog")))

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


def updatexx(self):
    return getboxlayout(
        [
            D_getsimpleswitch(
                globalconfig,
                "autoupdate",
                callback=lambda _: (
                    versionchecktask.put(_),
                    (
                        self.aboutlayout.layout().setRowVisible(2, False)
                        if not _
                        else ""
                    ),
                ),
                default=True,
            ),
            getsmalllabel(""),
            getsmalllabel("最新版本"),
            createversionlabel,
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
    if (val or text) and globalconfig.get("autoupdate", True):
        updatelayout.setRowVisible(2, True)


class MDLabel(LinkLabel):
    def setMD(self, md, static=True):
        self._md = md
        self.static = static
        self.updatelangtext()

    def __init__(self, md: str, static=False):
        super().__init__()
        self._md = md
        self.static = static
        self.setWordWrap(True)
        self.updatelangtext()

    def updatelangtext(self):
        self.setText(
            NativeUtils.Markdown2Html(self._md if self.static else _TR(self._md))
        )


class MDLabel1(MDLabel):
    def __init__(self, md):
        super().__init__(md, True)
        self.setOpenExternalLinks(False)
        self.linkActivated.connect(
            lambda link: gobject.base.aboutlinkclicked(link, self.window())
        )

    def setText(self, t):
        t = re.sub('<a href="WEIXIN".*?>(.*?)</a>', "\\1", t)
        super().setText(t)


def get_about_info():
    lang = getlanguse()
    t3 = "如果使用中遇到困难，可以查阅[使用说明](/)、观看[我的B站视频](https://space.bilibili.com/592120404/video)，也欢迎加入[QQ群](https://lunatranslator.org/Resource/QQGroup)。"
    t2 = "软件维护不易，如果您感觉该软件对你有帮助，欢迎通过[爱发电](https://afdian.com/a/HIllya51)，或[微信扫码](WEIXIN)赞助，您的支持将成为软件长期维护的助力，谢谢~"
    t5 = "如果使用中遇到困難，可以查閱[使用說明](/)、觀看[我的 B 站影片](https://space.bilibili.com/592120404/video)，也歡迎加入 [Discord](https://discord.com/invite/ErtDwVeAbhtB)／[QQ 群](https://lunatranslator.org/Resource/QQGroup)。"
    t6 = "如果使用中遇到困难，可以查阅[使用说明](/)，也欢迎加入[Discord](https://discord.com/invite/ErtDwVeAbB)。"
    t4 = "软件维护不易，如果您感觉该软件对你有帮助，欢迎通过[patreon](https://patreon.com/HIllya51)支持我，您的支持将成为软件长期维护的助力，谢谢~"
    if lang == Languages.Chinese:
        return "\n\n".join([t3, t2])

    elif lang == Languages.TradChinese:
        return "\n\n".join([t5, _TR(t4)])
    else:
        return _TR("\n\n".join([t6, t4]))


def _rgb_to_hsl(r, g, b):
    """r,g,b in [0,255] -> h in [0,360), s,l in [0,1]"""
    r /= 255.0
    g /= 255.0
    b /= 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    l = (mx + mn) / 2.0
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = (g - b) / d + (6 if g < b else 0)
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    h *= 60.0
    return h, s, l


def _hsl_to_rgb(h, s, l):
    """h in [0,360), s,l in [0,1] -> r,g,b in [0,255]"""
    if s == 0:
        v = int(round(l * 255))
        return v, v, v

    def hue2rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    hk = h / 360.0
    r = hue2rgb(p, q, hk + 1 / 3)
    g = hue2rgb(p, q, hk)
    b = hue2rgb(p, q, hk - 1 / 3)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def _hsl_invert_luminance(qimg: QImage) -> QImage:
    """HSL 只反转亮度（保留色相/饱和度）。灰阶像素（s=0）走快速路径——
    亮度反转等价于 255-r，避免整图纯 Python HSL 往返。"""
    qimg = qimg.convertToFormat(QImage.Format_RGB32)
    w, h = qimg.width(), qimg.height()
    out = QImage(w, h, QImage.Format_RGB32)
    src = memoryview(qimg.bits().asarray(w * h * 4))
    dst = memoryview(out.bits().asarray(w * h * 4))
    for i in range(0, w * h * 4, 4):
        b = src[i]
        g = src[i + 1]
        r = src[i + 2]
        mx = r if r >= g else g
        if b > mx:
            mx = b
        mn = r if r <= g else g
        if b < mn:
            mn = b
        if mx == mn:
            v = 255 - r
            dst[i] = v
            dst[i + 1] = v
            dst[i + 2] = v
        else:
            hh, ss, ll = _rgb_to_hsl(r, g, b)
            r2, g2, b2 = _hsl_to_rgb(hh, ss, 1.0 - ll)
            dst[i] = b2
            dst[i + 1] = g2
            dst[i + 2] = r2
        dst[i + 3] = 255
    return out


def load_scaled_pixmap_darkadapt(file_path: str, target_width: int, dpr: float, isdark=None):
    """暗色适配包装：黑暗模式下 HSL 反转亮度（二维码等黑白图不刺眼，
    彩色部分保留色相）。isdark 显式传入时以它为准（用于明暗切换事件）。"""
    img = load_scaled_pixmap(file_path, target_width, dpr)
    if nowisdark() if isdark is None else isdark:
        qimg = _hsl_invert_luminance(img.toImage())
        img = QPixmap.fromImage(qimg)
        img.setDevicePixelRatio(dpr)
    return img


def load_scaled_pixmap(
    file_path: str,
    target_width: int,
    device_pixel_ratio: float = 1.0,
) -> QPixmap:

    if file_path.endswith(".svg"):
        renderer = QSvgRenderer(file_path)
        physical_width = int(target_width * device_pixel_ratio)
        size = renderer.defaultSize()
        size.scale(physical_width, int(1e6), Qt.AspectRatioMode.KeepAspectRatio)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
        painter.end()

        pixmap.setDevicePixelRatio(device_pixel_ratio)
        return pixmap
    else:
        img = QPixmap.fromImage(QImage(file_path))
        img.setDevicePixelRatio(device_pixel_ratio)
        img = img.scaledToWidth(
            int(target_width * device_pixel_ratio),
            Qt.TransformationMode.SmoothTransformation,
        )
        return img


class aboutwidget(QWidget):
    """关于信息卡片（「如果使用中…」等内容）。"""

    def __init__(self, *a):
        super().__init__(*a)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("isCard", True)
        self.grid = QFormLayout(self)
        self.grid.setContentsMargins(16, 12, 16, 12)
        self.labels: "list[QWidget]" = []
        # (label, 路径, 宽度)：明暗切换事件到来时重新加载
        self._darkadapt_labels: "list[tuple[QLabel, str, int]]" = []
        self.mdlabel = MDLabel1("")
        self.grid.addRow(self.mdlabel)
        self.updatelangtext()

    def event(self, a0):
        # 明暗切换：暗色适配图片（如赞助二维码）随之翻转
        if isinstance(a0, DarkLightChangedEvent):
            for lb, path, w in self._darkadapt_labels:
                lb.setPixmap(load_scaled_pixmap_darkadapt(
                    path, w, self.devicePixelRatioF(), a0.isdark()))
        return super().event(a0)

    def createlabel(self, img: str, w, link=None, darkadapt=False):
        if link:
            lb = SClickableLabel()
            lb.clicked.connect(lambda: os.startfile(link))
        else:
            lb = QLabel()
        sp = lb.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        lb.setSizePolicy(sp)
        if darkadapt:
            lb.setPixmap(load_scaled_pixmap_darkadapt(
                img, w, self.devicePixelRatioF()))
            self._darkadapt_labels.append((lb, img, w))
        else:
            lb.setPixmap(load_scaled_pixmap(img, w, self.devicePixelRatioF()))
        self.labels.append(lb)
        self.grid.addRow(lb)

    def updatelangtext(self):
        self.mdlabel.setMD(get_about_info())
        lang = getlanguse()
        for _ in self.labels:
            _.deleteLater()
        self.labels.clear()
        self._darkadapt_labels.clear()
        if lang == Languages.Chinese:
            self.createlabel(
                "files/static/button-sponsorme.png",
                200,
                "https://afdian.com/a/HIllya51",
            )
            self.createlabel("files/static/zan.jpg", 300, darkadapt=True)
        elif lang == Languages.TradChinese:
            self.createlabel(
                "files/static/become_a_patron_4x1_black_logo_white_text_on_coral.svg",
                200,
                "https://patreon.com/HIllya51",
            )
        else:
            self.createlabel(
                "files/static/become_a_patron_4x1_black_logo_white_text_on_coral.svg",
                200,
                "https://patreon.com/HIllya51",
            )


class delayloadsvg(QSvgWidget):
    def __init__(self, img, url):
        super().__init__()
        self.url = url
        self._load(img)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, _: QMouseEvent):
        if _.button() == Qt.MouseButton.LeftButton:
            os.startfile(self.url)

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.Type.FontChange:
            self.loadh()
        return super().event(a0)

    def loadh(self):
        h = QFontMetricsF(self.font(), self).height()
        renderer = self.renderer()
        if renderer != None:
            size = renderer.defaultSize()
            self.setFixedSize(QSizeF(size.width() * h / size.height(), h).toSize())

    @threader
    def _load(self, link):
        self.load(requests.get(link).content)
        self.loadh()


def makelink(repo):
    if repo == "uchardet/uchardet":
        url = "https://gitlab.freedesktop.org/uchardet/uchardet"
        img = "https://img.shields.io/gitlab/license/uchardet%2Fuchardet?gitlab_url=https%3A%2F%2Fgitlab.freedesktop.org%2F"
    else:
        url = "https://github.com/" + repo
        img = "https://img.shields.io/github/license/" + repo

    return [
        functools.partial(delayloadsvg, img, url),
        functools.partial(
            LinkLabel,
            '<a href="{url}">{repo}</a>'.format(url=url, repo=repo),
        ),
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


def setTab_about(self: QWidget, basel):
    from gui.fluent.card import make_trailing_combo
    from gui.usefulwidget import makecardrow, makescrollgrid
    from gui.setting.display_ui import switch_darklight
    from gui.usefulwidget import getsimplecombobox
    from myutils.config import ui_settings as _uis

    # 与其他设置页同一条代码路径（makescrollgrid）——不手搓容器

    # 界面语言（不能抽出 combo 重挂——延迟加载会丢 item，必须用 widget 包裹布局）
    lang_holder = QWidget()
    lang_holder.setLayout(__delayloadlangs())
    lang_holder.layout().setContentsMargins(0, 0, 0, 0)

    # 应用主题
    darklight_combo = getsimplecombobox(
        ["跟随系统", "明亮", "黑暗"], _uis, "darklight2",
        callback=lambda _: (
            gobject.base.setcommonstylesheet(),
            switch_darklight(),
        ),
        default=0,
    )

    # 自动更新
    update_switch = D_getsimpleswitch(
        globalconfig, "autoupdate",
        callback=lambda _: versionchecktask.put(_),
        default=True,
    )()
    self.downloadprogress = QProgressBar(self)
    self.downloadprogress.setRange(0, 10000)
    self.downloadprogress.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    self.downloadprogress.setVisible(False)
    version_link = createversionlabel()

    # 自动更新进度回调
    gobject.base.connectsignal(
        gobject.base.progresssignal4,
        lambda text, val: _progresssignal4_card(
            self.downloadprogress, text, val),
    )

    # LICENSE 折叠（ExExpander，同 Gallery 强调色折叠面板的用法）
    from gui.fluent.expander import ExExpander
    from gui.fluent.card import make_card_contents
    from gui.fluent.icons import ICON_SETTINGS_DISPLAY_SOUND

    license_expander = ExExpander()
    license_expander.setObjectName("settingsLicenseExpander")

    # 同 Gallery：用 make_card_contents（不设 isCard——ExExpander 自己画卡片底色）
    license_header = make_card_contents(
        ICON_SETTINGS_DISPLAY_SOUND, "LICENSE", "查看许可证与引用的项目",
        None, license_expander)
    # 同 C++：HeaderButton 自带 16px 左内边距与 chevron 预留区，内容只留上下边距
    license_header.layout().setContentsMargins(0, 12, 0, 12)
    license_expander.setHeaderWidget(license_header)

    license_content = makegrid(
        (
            [
                makelink("HIllya51/LunaTranslator")[0],
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
            makelink("AuroraWright/owocr"),
            makelink("b1tg/win11-oneocr"),
            makelink("mity/md4c"),
            makelink("swigger/wechat-ocr"),
            makelink("rupeshk/MarkdownHighlighter"),
            makelink("sindresorhus/github-markdown-css"),
            makelink("gexgd0419/NaturalVoiceSAPIAdapter"),
            makelink("microsoft/PowerToys"),
            makelink("WaterJuice/WjCryptLib"),
            makelink("k2-fsa/sherpa-onnx"),
            makelink("chromium/chromium"),
            makelink("Neargye/magic_enum"),
            makelink("bbepis/XUnity.AutoTranslator"),
            makelink("uchardet/uchardet"),
            makelink("XHY-ChuJian/FluentUIStyle"),
        ),
    )
    license_expander.addContentWidget(license_content)
    license_expander.setExpanded(False)

    # 与其他设置页完全相同的排版路径（makescrollgrid）
    grid = [
        [(makecardrow("界面语言", lang_holder), 0)],
        [(makecardrow("应用主题", make_trailing_combo(darklight_combo)), 0)],
        [(makecardrow("自动更新", update_switch, version_link), 0)],
        # 下载进度条：显示时出现在卡片下方（隐藏时布局不占位）
        [(self.downloadprogress, 0)],
        [(aboutwidget(), 0)],
        [(license_expander, 0)],
    ]
    makescrollgrid(grid, basel)


def _progresssignal4_card(progressbar: QProgressBar, text, val):
    progressbar.setValue(val)
    progressbar.setFormat(text)
    progressbar.setVisible(bool(val or text))

