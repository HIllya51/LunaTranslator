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
from LunaSubProcess import LunaSubProcess
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
            res = requests.get(main_server, proxies=proxy)
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

            if runtime_for_win10:
                target = "win10"
            elif runtime_bit_64:
                target = "win7"
            else:
                target = "winxp"
            res = requests.get(
                "{main_server}/version".format(main_server=main_server),
                params={"arch": ("x86", "x64")[runtime_bit_64], "target": target},
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
    # uncompress已把更新包规范到固定目录，这里直接使用并校验完整，
    # 不能os.walk现找：退出瞬间若正在重新解压，会扫到解压了一半的残缺目录并当成更新源
    found = gobject.getcachedir("update/LunaTranslator")
    if not os.path.isfile(os.path.join(found, "LunaTranslator.exe")):
        return
    exe1 = gobject.getcachedir("update/Updater.exe")
    exe = os.path.abspath(exe1)
    shutil.copy(
        r".\files\LunaSubProcess{}.exe".format(("32", "64")[runtime_bit_64]),
        exe,
    )
    for dll in os.listdir(runtimedir):
        if not (dll.lower().startswith("vcruntime") or dll.lower().startswith("msvcp")):
            continue
        _ = os.path.join(runtimedir, dll)
        shutil.copy(_, gobject.getcachedir("update/" + dll))

    texts: "list[str]" = [
        _TR("错误"),
        _TR("成功"),
        _TR("更新失败"),
        _TR("更新成功"),
        _TR("部分文件或目录被以下进程占用，是否终止以下进程？"),
    ]
    text = "\n".join(texts).encode("utf8")
    b64 = base64.b64encode(text).decode()
    LunaSubProcess.update(exe1, gobject.base.istriggertoupdate, found, os.getpid(), b64)


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
        globalconfig.get("autoupdate", True) and versionchecktask.empty()
    )

    savep = gobject.getcachedir("update/" + url.split("/")[-1])
    if not savep.endswith(".zip"):
        savep += ".zip"
    if check_interrupt():
        return
    if updatemethod_checkalready(savep, sha256):
        return savep
    with open(savep, "wb") as file:
        r = requests.get(url, stream=True, proxies=getproxy())
        size = int(r.headers["Content-Length"])
        file_size = 0
        asize = format_bytes(size)
        for i in r.iter_content(chunk_size=1024 * 32):
            if check_interrupt():
                return
            if not i:
                continue
            file.write(i)
            file_size += len(i)
            prg = int(10000 * file_size / size)
            gobject.base.progresssignal4.emit(
                _TR("{}/{} _进度_{:0.2f}%").format(
                    format_bytes(file_size), asize, prg / 100
                ),
                prg,
            )

    if check_interrupt():
        return
    if updatemethod_checkalready(savep, sha256):
        return savep


def uncompress(savep):
    gobject.base.progresssignal4.emit(_TR("正在解压"), 10000)
    # 先解压到暂存目录，再整体换入到cache\update\LunaTranslator，
    # 保证该目录任何时刻要么不存在、要么是完整的，退出时不会被更新器拿到半个包
    tmpbase = gobject.getcachedir("update_tmp")
    shutil.rmtree(tmpbase, ignore_errors=True)
    with zipfile.ZipFile(savep) as zipf:
        zipf.extractall(tmpbase)
    found = None
    for _dir, _, _fs in os.walk(tmpbase):
        for _f in _fs:
            if _f.lower() == "lunatranslator.exe":
                found = _dir
    if not found:
        shutil.rmtree(tmpbase, ignore_errors=True)
        raise Exception("unexpected update package layout")
    target = gobject.getcachedir("update/LunaTranslator")
    shutil.rmtree(target, ignore_errors=True)
    os.rename(found, target)
    if os.path.abspath(found) != os.path.abspath(tmpbase):
        shutil.rmtree(tmpbase, ignore_errors=True)


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
        if not (need and globalconfig.get("autoupdate", True)):
            continue
        gobject.base.progresssignal4.emit("……", 0)
        savep = updatemethod(_version[1:])
        if not savep:
            gobject.base.progresssignal4.emit(_TR("自动更新失败，请手动更新"), 0)
            continue

        uncompress(savep)
        gobject.base.update_avalable = True
        gobject.base.progresssignal4.emit(_TR("准备完毕，将在退出后更新"), 10000)
