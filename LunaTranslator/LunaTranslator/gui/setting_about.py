from qtsymbols import *
import platform, functools, sys
import winsharedutils, queue
from myutils.config import globalconfig, _TR, static_data, _TRL
from myutils.wrapper import threader, tryprint
from myutils.utils import makehtml
import requests, time
import shutil, gobject
from myutils.proxy import getproxy
from traceback import print_exc
import zipfile, os
import subprocess
from gui.usefulwidget import (
    D_getsimpleswitch,
    makescrollgrid,
    makesubtab_lazy,
)

versionchecktask = queue.Queue()


def getvesionmethod():
    try:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Proxy-Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        }
        res = requests.get(
            "https://api.github.com/repos/HIllya51/LunaTranslator/releases/latest",
            headers=headers,
            verify=False,
            proxies=getproxy(("github", "versioncheck")),
        ).json()
        # print(res)
        _version = res["tag_name"]
        return _version
    except:
        print_exc()
        return None


def doupdate():
    if not gobject.baseobject.update_avalable:
        return
    if platform.architecture()[0] == "64bit":
        bit = ""
        _6432 = "64"
    elif platform.architecture()[0] == "32bit":
        bit = "_x86"
        _6432 = "32"
    shutil.copy(
        rf".\files\plugins\shareddllproxy{_6432}.exe",
        gobject.getcachedir("Updater.exe"),
    )
    subprocess.Popen(rf".\cache\Updater.exe update .\cache\update\LunaTranslator{bit}")


def updatemethod_checkalready(size, savep):
    if not os.path.exists(savep):
        return False
    stats = os.stat(savep)
    if stats.st_size != size:
        return False
    return True


@tryprint
def updatemethod(_version, self):

    check_interrupt = lambda: not (
        globalconfig["autoupdate"] and versionchecktask.empty()
    )
    if platform.architecture()[0] == "64bit":
        bit = ""
    elif platform.architecture()[0] == "32bit":
        bit = "_x86"
    else:
        raise Exception
    url = "https://github.com/HIllya51/LunaTranslator/releases/download/{}/LunaTranslator{}.zip".format(
        _version, bit
    )

    savep = gobject.getcachedir("update/LunaTranslator{}.zip".format(bit))

    r2 = requests.get(
        url, stream=True, verify=False, proxies=getproxy(("github", "download"))
    )
    size = int(r2.headers["Content-Length"])
    if check_interrupt():
        return
    if updatemethod_checkalready(size, savep):
        return savep
    with open(savep, "wb") as file:
        sess = requests.session()
        r = sess.get(
            url, stream=True, verify=False, proxies=getproxy(("github", "download"))
        )
        file_size = 0
        for i in r.iter_content(chunk_size=1024):
            if check_interrupt():
                return
            if not i:
                continue
            file.write(i)
            thislen = len(i)
            file_size += thislen

            prg = int(10000 * file_size / size)
            prg100 = prg / 100
            sz = int(1000 * (int(size / 1024) / 1024)) / 1000
            self.progresssignal.emit(
                "总大小{} MB 进度 {:0.2f}% ".format(sz, prg100), prg
            )

    if check_interrupt():
        return
    if updatemethod_checkalready(size, savep):
        return savep


def uncompress(self, savep):
    self.progresssignal.emit("正在解压……", 10000)
    shutil.rmtree(gobject.getcachedir("update/LunaTranslator"))
    with zipfile.ZipFile(savep) as zipf:
        zipf.extractall(gobject.getcachedir("update"))


@threader
def versioncheckthread(self):
    versionchecktask.put(True)
    while True:
        x = versionchecktask.get()
        gobject.baseobject.update_avalable = False
        self.progresssignal.emit("……", 0)
        if not x:
            continue
        self.versiontextsignal.emit(_TR("获取中"))  # ,'',url,url))
        _version = getvesionmethod()

        if _version is None:
            sversion = _TR("获取失败")
        else:
            sversion = _version
        self.versiontextsignal.emit(sversion)
        version = winsharedutils.queryversion(sys.argv[0])
        need = (
            version
            and _version
            and version < tuple(int(_) for _ in _version[1:].split("."))
        )
        if not (need and globalconfig["autoupdate"]):
            continue
        savep = updatemethod(_version, self)
        if not savep:
            self.progresssignal.emit("自动更新失败，请手动更新", 0)
            continue

        uncompress(self, savep)
        gobject.baseobject.update_avalable = True
        self.progresssignal.emit("准备完毕，等待更新", 10000)


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


def wraplink(text: str):
    link = "https://github.com/HIllya51/LunaTranslator/releases"
    if text.startswith("v"):

        link = f"https://github.com/HIllya51/LunaTranslator/releases/tag/{text}"
    return makehtml(
        link,
        show=text,
    )


def createversionlabel(self):

    self.versionlabel = QLabel()
    self.versionlabel.setOpenExternalLinks(True)
    self.versionlabel.setTextInteractionFlags(
        Qt.TextInteractionFlag.LinksAccessibleByMouse
    )
    try:
        self.versionlabel.setText(
            wraplink(
                self.versionlabel_cache,
            )
        )
    except:
        pass
    return self.versionlabel


def versionlabelmaybesettext(self, x):
    try:
        self.versionlabel.setText(wraplink(x))
    except:
        self.versionlabel_cache = x


def solvelinkitems(grid, source):
    name = source["name"]
    link = source["link"]

    if link[-8:] == "releases":
        __ = False
    elif link[-1] == "/":
        __ = False
    else:
        __ = True
    grid.append([(_TR(name), 1, ""), (makehtml(link, __), 2, "link")])


def resourcegrid(self, l):
    titles = []
    makewidgetsfunctions = []
    for sourcetype in static_data["aboutsource"]:
        titles.append(sourcetype["name"])
        sources = sourcetype["sources"]
        grid = []
        for source in sources:
            _type = source.get("type", "link")
            if _type == "link":
                solvelinkitems(grid, source)
            elif _type == "group":
                __grid = []
                for link in source["links"]:
                    solvelinkitems(__grid, link)
                grid.append(
                    [
                        (
                            dict(
                                title=source.get("name", None), type="grid", grid=__grid
                            ),
                            0,
                            "group",
                        )
                    ]
                )
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

    resourcegrid(self, basel)


def setTab_update(self, basel):
    version = winsharedutils.queryversion(sys.argv[0])
    if version is None:
        versionstring = "unknown"
    else:
        versionstring = (
            f"v{version[0]}.{version[1]}.{version[2]}  {platform.architecture()[0]}"
        )
    grid2 = [
        [
            "自动更新",
            D_getsimpleswitch(
                globalconfig, "autoupdate", callback=versionchecktask.put
            ),
        ],
        [
            "当前版本",
            versionstring,
        ],
        [
            "最新版本",
            functools.partial(createversionlabel, self),
        ],
        [functools.partial(createdownloadprogress, self)],
    ]

    shuominggrid = [
        ["项目网站", makehtml("https://github.com/HIllya51/LunaTranslator")],
        [
            "问题反馈",
            makehtml("https://github.com/HIllya51/LunaTranslator/issues"),
        ],
        [
            "使用说明",
            makehtml("https://hillya51.github.io/LunaTranslator_tutorial/#/zh/"),
        ],
    ]
    if globalconfig["languageuse"] == 0:
        shuominggrid += [
            [],
            [
                "交流群",
                makehtml("https://qm.qq.com/q/qE32v9NYBO", show=912525396),
            ],
            [],
            ["如果你感觉该软件对你有帮助，欢迎微信扫码赞助，谢谢~"],
        ]

        shuominggrid += [[functools.partial(createimageview, self)]]
    else:
        shuominggrid += [
            [],
            [
                "If you feel that the software is helpful to you, ",
            ],
            [
                'welcome to become my <a href="https://patreon.com/HIllya51">sponsor. Thank you ~ ',
            ],
        ]
    makescrollgrid(
        [
            [
                (
                    dict(
                        Stretch=False,
                        grid=grid2,
                    ),
                    0,
                    "group",
                )
            ],
            [
                (
                    dict(
                        grid=shuominggrid,
                    ),
                    0,
                    "group",
                )
            ],
        ],
        basel,
    )
