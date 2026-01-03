import NativeUtils, queue, hashlib, threading
from myutils.config import globalconfig, static_data, _TR
from gobject import runtime_for_xp, runtime_bit_64, runtime_for_win10, runtimedir
from myutils.wrapper import threader, tryprint, trypass
from myutils.hwnd import getcurrexe
from myutils.utils import format_bytes
import requests, base64
import shutil, gobject
from myutils.proxy import getproxy
import zipfile, os
import subprocess
from traceback import print_exc

versionchecktask = queue.Queue()


@threader
def testdocconnect():
    wait = threading.Event()
    results = []
    proxy = getproxy()
    for i, main_server in enumerate(static_data["docs_server"]):

        @threader
        @trypass
        def __(i, main_server, proxy):
            res = requests.get(main_server, verify=False, proxies=proxy)
            if res.status_code == 200:
                results.append((i, res))
                wait.set()

        __(i, main_server, proxy)
    wait.wait()
    gobject.serverindex2 = results[0][0]


def tryqueryfromhost():
    wait = threading.Event()
    results = []
    proxy = getproxy()
    for i, main_server in enumerate(static_data["main_server"]):

        @threader
        @trypass
        def __(i, main_server, proxy):

            if runtime_for_xp:
                target = "winxp"
            elif runtime_for_win10:
                target = "win10"
            else:
                target = "win7"
            res = requests.get(
                "{main_server}/version".format(main_server=main_server),
                params={"arch": ("x86", "x64")[runtime_bit_64], "target": target},
                verify=False,
                proxies=proxy,
            )
            res = res.json()
            results.append((i, res))
            wait.set()

        __(i, main_server, proxy)
        if proxy.get("https"):
            __(i, main_server, None)
    wait.wait()
    gobject.serverindex = results[0][0]
    return results[0][1]


def trygetupdate():
    try:
        result = tryqueryfromhost()
        version, link, sha256 = result["version"], result["link"], result["sha256"]
        return version, link, sha256
    except:
        print_exc()
        return None


def doupdate():
    if not gobject.base.update_avalable:
        return
    exe1 = gobject.getcachedir("update/Updater.exe")
    exe = os.path.abspath(exe1)
    shutil.copy(
        r".\files\shareddllproxy{}.exe".format(("32", "64")[runtime_bit_64]),
        exe,
    )
    for dll in os.listdir(runtimedir):
        if not (dll.lower().startswith("vcruntime") or dll.lower().startswith("msvcp")):
            continue
        _ = os.path.join(runtimedir, dll)
        shutil.copy(_, gobject.getcachedir("update/" + dll))

    for _dir, _, _fs in os.walk(r".\cache\update"):
        for _f in _fs:
            if _f.lower() == "lunatranslator.exe":
                found = _dir

    texts: "list[str]" = [
        _TR("错误"),
        _TR("成功"),
        _TR("更新失败"),
        _TR("更新成功"),
        _TR("部分文件或目录被以下进程占用，是否终止以下进程？"),
    ]
    text = "\n".join(texts).encode("utf8")
    b64 = base64.b64encode(text).decode()
    subprocess.Popen(
        r"{} update {} {} {} {}".format(
            exe1, int(gobject.base.istriggertoupdate), found, os.getpid(), b64
        )
    )


def updatemethod_checkalready(savep, sha256):
    if not os.path.exists(savep):
        return False
    if not sha256:
        return True
    with open(savep, "rb") as ff:
        newsha256 = hashlib.sha256(ff.read()).hexdigest()
        return newsha256 == sha256


@tryprint
def updatemethod(urls: "tuple[str, str]"):
    url, sha256 = urls
    check_interrupt = lambda: not (
        globalconfig["autoupdate"] and versionchecktask.empty()
    )

    savep = gobject.getcachedir("update/" + url.split("/")[-1])
    if not savep.endswith(".zip"):
        savep += ".zip"
    if check_interrupt():
        return
    if updatemethod_checkalready(savep, sha256):
        return savep
    with open(savep, "wb") as file:
        r = requests.get(url, stream=True, verify=False, proxies=getproxy())
        size = int(r.headers["Content-Length"])
        file_size = 0
        asize = format_bytes(size)
        for i in r.iter_content(chunk_size=1024 * 32):
            if check_interrupt():
                return
            if not i:
                continue
            file.write(i)
            thislen = len(i)
            file_size += thislen

            prg = int(10000 * file_size / size)
            prg100 = prg / 100
            gobject.base.progresssignal4.emit(
                _TR("总大小_{} _进度_{:0.2f}%").format(asize, prg100),
                prg,
            )

    if check_interrupt():
        return
    if updatemethod_checkalready(savep, sha256):
        return savep


def uncompress(savep):
    gobject.base.progresssignal4.emit(_TR("正在解压"), 10000)
    shutil.rmtree(gobject.getcachedir("update/LunaTranslator/"))
    with zipfile.ZipFile(savep) as zipf:
        zipf.extractall(gobject.getcachedir("update"))


@threader
def versioncheckthread():
    testdocconnect()
    versionchecktask.put(True)
    while True:
        x = versionchecktask.get()
        gobject.base.update_avalable = False
        gobject.base.progresssignal4.emit("", 0)
        if not x:
            continue
        gobject.base.versiontextsignal.emit("获取中")  # ,'',url,url))
        _version = trygetupdate()

        if _version is None:
            sversion = "获取失败"
        else:
            sversion = _version[0]
        gobject.base.versiontextsignal.emit(sversion)
        version = NativeUtils.QueryVersion(getcurrexe())
        need = (
            (not getcurrexe().endswith("python.exe"))
            and version
            and _version
            and version < tuple(int(_) for _ in _version[0][1:].split("."))
        )
        if need or not globalconfig["autoupdate"]:
            gobject.base.showupdatebtn.emit()
        if not (need and globalconfig["autoupdate"]):
            continue
        gobject.base.progresssignal4.emit("……", 0)
        savep = updatemethod(_version[1:])
        if not savep:
            gobject.base.progresssignal4.emit(_TR("自动更新失败，请手动更新"), 0)
            continue

        uncompress(savep)
        gobject.base.update_avalable = True
        gobject.base.progresssignal4.emit(_TR("准备完毕，等待更新"), 10000)
        gobject.base.showtraymessage(
            sversion,
            _TR("准备完毕，等待更新") + "\n" + _TR("点击消息后退出并开始更新"),
            gobject.base.triggertoupdate,
        )
