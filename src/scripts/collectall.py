import shutil, os
import platform
import sys
from importanalysis import importanalysis

x86 = platform.architecture()[0] == "32bit"
if sys.argv[1] == "32":
    targetdir = r"build\LunaTranslator_x86"
    launch = "../src/cpp/builds/_x86"
    baddll = "DLL64"
    pyrt = "../build/pyrt_x86/runtime"
    downlevel = r"C:\Windows\SysWOW64\downlevel"
else:
    baddll = "DLL32"
    launch = "../src/cpp/builds/_x64"
    targetdir = r"build\LunaTranslator"
    pyrt = "../build/pyrt_x64/runtime"
    downlevel = r"C:\Windows\system32\downlevel"


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


copycheck(os.path.join(launch, "LunaTranslator.exe"), targetdir)
copycheck(os.path.join(launch, "LunaTranslator_admin.exe"), targetdir)
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
try:
    shutil.rmtree(rf"{targetdir}\files\plugins\{baddll}")
except:
    pass
shutil.copy(r"..\LICENSE", targetdir)

collect = []
for _dir, _, fs in os.walk(targetdir):
    for f in fs:
        collect.append(os.path.join(_dir, f))

collectapisets = set()
for f in collect:
    if f.endswith(".pyc") or f.endswith("Thumbs.db"):
        os.remove(f)
    elif f.endswith(".exe") or f.endswith(".pyd") or f.endswith(".dll"):
        if f.endswith("Magpie.Core.exe"):
            continue
        print(f)
        imports = importanalysis(f)
        print(f, imports)
        if len(imports) == 0:
            continue
        with open(f, "rb") as ff:
            bs = bytearray(ff.read())
        for _dll, offset in imports:
            low = _dll.lower()
            if low in (
                "api-ms-win-core-synch-l1-2-0.dll",
                "api-ms-win-core-winrt-string-l1-1-0.dll",
                "api-ms-win-core-winrt-l1-1-0.dll",
                "api-ms-win-core-path-l1-1-0.dll",
            ):
                continue
            elif low=='api-ms-win-core-com-l1-1-0.dll':
                _target='Ole32.dll'
            elif low == "api-ms-win-core-shlwapi-legacy-l1-1-0.dll":
                _target = "Shlwapi.dll"
            elif low in ("api-ms-win-eventing-provider-l1-1-0.dll", "api-ms-win-security-base-l1-1-0.dll"):
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
#         for _dll, _ in imports:
#             collectapisets.add(_dll)
# for api in collectapisets:
#     copycheck(rf"{downlevel}\{api}", targetdir + "/files/runtime")
target = os.path.basename(targetdir)
os.chdir(os.path.dirname(targetdir))
if os.path.exists(rf"{target}.zip"):
    os.remove(rf"{target}.zip")
if os.path.exists(rf"{target}.7z"):
    os.remove(rf"{target}.7z")
os.system(rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target}.zip {target}')
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
