import shutil, os, base64
import sys, re, json
from importanalysis import importanalysis
import urllib.request
import urllib.error


def get_json(url: str, headers=None):
    if headers is None:
        headers = {}

    # 设置默认的User-Agent（很多API需要）
    headers.setdefault("User-Agent", "Mozilla/5.0")

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        # 读取响应内容
        data = response.read()
        # 解码为字符串
        text = data.decode("utf-8")
        # 解析JSON
        return json.loads(text)


arch = sys.argv[1]
target = sys.argv[2]
if target != "win10":
    os.system(f"python scripts/generate_xp_code.py {target}")
if target == "winxp":
    os.system("git clone --depth 1 https://github.com/HIllya51/py3.4_pyqt5.5.1")
    os.rename("py3.4_pyqt5.5.1/Python34", "runtime")
    pyrt = "runtime"
else:
    pyrt = f"pyrt/runtime"
launch = f"NativeImpl/builds/_{arch}_{target}"
targetdir = rf"build\LunaTranslator_{arch}_{target}"

if arch == "x86":
    baddll = "DLL64"
else:
    baddll = "DLL32"

os.makedirs(targetdir, exist_ok=True)


def copycheck(src, tgt):
    print(src, tgt, os.path.exists(src))
    if not os.path.exists(src):
        return
    if src.lower().endswith("_ssl.pyd"):
        return
    if not os.path.exists(tgt):
        os.makedirs(tgt, exist_ok=True)
    if os.path.isdir(src):
        tgt = os.path.join(tgt, os.path.basename(src))
        if os.path.exists(tgt):
            shutil.rmtree(tgt)
        shutil.copytree(src, tgt)
        return
    shutil.copy(src, tgt)


# copycheck(os.path.join(launch, "LunaTranslator.exe"), targetdir)
# copycheck(os.path.join(launch, "LunaTranslator_admin.exe"), targetdir)
with open(os.path.join(targetdir, "LunaTranslator_debug.bat"), "w") as ff:
    ff.write(
        r""".\LunaTranslator.exe
pause"""
    )
# copycheck(os.path.join(launch, "LunaTranslator_admin.exe"), targetdir)
# copycheck(os.path.join(launch, "LunaTranslator_debug.exe"), targetdir)
copycheck("./LunaTranslator", targetdir)
copycheck(r".\files", targetdir)
copycheck(pyrt, targetdir + "/files")
if target == "win10":
    runtimedir = "runtime3.13-64"
elif target == "winxp":
    runtimedir = "runtime3.4-32"
elif arch == "x64":
    runtimedir = "runtime3.7-64"
else:
    runtimedir = "runtime3.7-32"
os.rename(targetdir + "/files/runtime", targetdir + "/files/" + runtimedir)
try:
    shutil.rmtree(rf"{targetdir}\files\{baddll}")
except:
    pass

os.makedirs("LICENSES")
shutil.copy(
    r"..\LICENSE", os.path.join(targetdir, "LICENSES", "LICENSE.LunaTranslator")
)
with open("LunaTranslator/gui/setting/about.py", "r", encoding="utf8") as ff:
    for _ in re.findall(r'makelink\(".*?"\)', ff.read()):
        _js: dict[str, str] = get_json(
            rf"https://api.github.com/repos/{_[10:-1]}/license"
        )
        content = _js.get("content")
        if content:
            content = base64.b64encode(content.encode()).decode()
            with open(
                os.path.join(targetdir, "LICENSES", "LICENSE." + _.replace("/", ".")),
                "w",
                encoding="utf8 ",
            ) as ff:
                ff.write(content)
collect = []
for _dir, _, fs in os.walk(targetdir):
    for f in fs:
        collect.append(os.path.join(_dir, f))
if target in ("win10", "winxp"):
    collect.clear()
for f in collect:
    if f.endswith(".pyc") or f.endswith("Thumbs.db"):
        os.remove(f)
    elif f.endswith(".exe") or f.endswith(".pyd") or f.endswith(".dll"):
        if f.endswith("Magpie.Core.exe"):
            continue
        print(f)
        imports = importanalysis(f)["imports"]
        print(f, imports)
        if len(imports) == 0:
            continue
        with open(f, "rb") as ff:
            bs = bytearray(ff.read())
        for _dll, offset in imports:
            low = _dll.lower()
            if low in (
                # "api-ms-win-core-synch-l1-2-0.dll",
                "api-ms-win-core-winrt-string-l1-1-0.dll",
                "api-ms-win-core-winrt-l1-1-0.dll",
                "api-ms-win-core-path-l1-1-0.dll",
            ):
                continue
            elif low == "api-ms-win-core-com-l1-1-0.dll":
                _target = "Ole32.dll"
            elif low == "api-ms-win-core-shlwapi-legacy-l1-1-0.dll":
                _target = "Shlwapi.dll"
            elif low in (
                "api-ms-win-eventing-provider-l1-1-0.dll",
                "api-ms-win-security-base-l1-1-0.dll",
            ):
                _target = "Advapi32.dll"
            elif low in ("api-ms-win-ntuser-sysparams-l1-1-0.dll",):
                _target = "User32.dll"
            elif low.startswith("api-ms-win-core"):
                # 其实对于api-ms-win-core-winrt-XXX实际上是到ComBase.dll之类的，不过此项目中不包含这些
                _target = "Kernel32.dll"
            elif low.startswith("api-ms-win-crt"):
                _target = "ucrtbase.dll"
            else:
                continue
            _dll = _dll.encode()
            _target = _target.encode()
            # print(len(bs))
            bs[offset : offset + len(_dll)] = _target + b"\0" * (
                len(_dll) - len(_target)
            )
            # print(len(bs))
        with open(f, "wb") as ff:
            ff.write(bs)


os.system(f"python scripts/createsigexe.py {arch} {target} {targetdir}")
copycheck(f"{launch}/LunaTranslator.exe", targetdir)
copycheck(f"{launch}/LunaTranslator_admin.exe", targetdir)


target = os.path.basename(targetdir)
os.chdir(os.path.dirname(targetdir))
if os.path.exists(rf"{target}.zip"):
    os.remove(rf"{target}.zip")
if os.path.exists(rf"{target}.7z"):
    os.remove(rf"{target}.7z")

if 0:
    os.system(
        rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target}.zip {target}'
    )
if 0:
    os.system(rf'"C:\Program Files\7-Zip\7z.exe" a -m0=LZMA2 -mx9 {target}.7z {target}')
    with open(r"C:\Program Files\7-Zip\7z.sfx", "rb") as ff:
        sfx = ff.read()

    config = """
    ;!@Install@!UTF-8!


    ;!@InstallEnd@!
    """
    with open(rf"{target}.7z", "rb") as ff:
        data = ff.read()

    with open(rf"{target}.exe", "wb") as ff:
        ff.write(sfx)
        ff.write(config.encode("utf8"))
        ff.write(data)
