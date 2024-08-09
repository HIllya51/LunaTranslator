import modulefinder, shutil, os, sys
import builtins, platform
import sys
from importanalysis import importanalysis

pyversion = platform.python_version()
pyversion2 = "".join(pyversion.split(".")[:2])
x86 = platform.architecture()[0] == "32bit"
if x86:
    downlevel = r"C:\Windows\SysWOW64\downlevel"

    runtime = r"..\build\LunaTranslator_x86\LunaTranslator\runtime"
    targetdir = r"..\build\LunaTranslator_x86"
    launch = r"..\plugins\builds\_x86"
    baddll = "DLL64"
    gooddll = "DLL32"

    webviewappendix = r"Lib\site-packages\webviewpy\platform\win32\x86\webview.dll"
else:
    baddll = "DLL32"
    gooddll = "DLL64"
    launch = r"..\plugins\builds\_x64"
    runtime = r"..\build\LunaTranslator\LunaTranslator\runtime"
    targetdir = r"..\build\LunaTranslator"
    downlevel = r"C:\Windows\system32\downlevel"

    webviewappendix = r"Lib\site-packages\webviewpy\platform\win32\x64\webview.dll"

py37Path = os.path.dirname(sys.executable)
print(py37Path)
py37Pathwebview = os.path.join(py37Path, webviewappendix)


def get_dependencies(filename):
    saveopen = builtins.open

    def __open(*arg, **kwarg):
        if len(arg) > 1:
            mode = arg[1]
        else:
            mode = ""
        if "b" not in mode:
            kwarg["encoding"] = "utf8"
        return saveopen(*arg, **kwarg)

    builtins.open = __open
    finder = modulefinder.ModuleFinder()

    finder.run_script(filename)

    dependencies = []
    for name, module in finder.modules.items():
        if module.__file__ is not None:
            dependencies.append(module.__file__)
    builtins.open = saveopen
    return dependencies


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


if os.path.exists(targetdir):
    shutil.rmtree(targetdir)
copycheck(os.path.join(launch, "LunaTranslator.exe"), targetdir)
copycheck(os.path.join(launch, "LunaTranslator_admin.exe"), targetdir)
copycheck(os.path.join(launch, "LunaTranslator_debug.exe"), targetdir)
copycheck("./LunaTranslator", targetdir)
copycheck(r".\files", targetdir)
try:
    shutil.rmtree(rf"{targetdir}\files\plugins\{baddll}")
except:
    pass
shutil.copy(r"..\LICENSE", targetdir)
shutil.copy(py37Pathwebview, rf"{targetdir}\files\plugins\{gooddll}")

all_dependencies = set()
for _d, _, _fs in os.walk("./LunaTranslator"):
    for f in _fs:
        if not f.endswith(".py"):
            continue
        base = os.path.basename(_d)
        if base in [
            "tts",
            "transoptimi",
            "translator",
            "scalemethod",
            "ocrengines",
            "winhttp",
            "libcurl",
            "network",
            "hiraparse",
            "cishu",
            "textoutput",
        ]:
            continue
        print(base, f)
        got = get_dependencies(os.path.join(_d, f))
        all_dependencies = all_dependencies.union(set(got))

for dependency in all_dependencies:
    if dependency.startswith("./"):
        continue
    if not dependency.startswith(py37Path):
        continue
    print(dependency)
    end = dependency[len(py37Path) + 1 :]
    if end.lower().startswith("lib"):
        end = end[4:]
        if end.lower().startswith("site-packages"):
            end = end[len("site-packages") + 1 :]
    elif end.lower().startswith("dlls"):
        end = end[5:]
    print(end)
    tgtreal = os.path.join(runtime, os.path.dirname(end))
    copycheck(dependency, tgtreal)


with open(os.path.join(runtime, f"python{pyversion2}._pth"), "w") as ff:
    ff.write("..\n.")

copycheck(os.path.join(py37Path, "python3.dll"), runtime)
copycheck(os.path.join(py37Path, f"python{pyversion2}.dll"), runtime)
copycheck(os.path.join(py37Path, "Dlls/sqlite3.dll"), runtime)

copycheck(os.path.join(py37Path, "Lib/encodings"), runtime)
copycheck(os.path.join(py37Path, "DLLs/libffi-7.dll"), runtime)


copycheck(rf"{downlevel}\ucrtbase.dll", runtime)
copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/vcruntime140.dll"),
    os.path.join(runtime),
)
copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/vcruntime140_1.dll"),
    os.path.join(runtime),
)
copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/msvcp140.dll"),
    os.path.join(runtime),
)
copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/msvcp140_1.dll"),
    os.path.join(runtime),
)


for _ in os.listdir(os.path.join(py37Path, "Lib/site-packages/PyQt5")):
    if _.startswith("sip"):
        copycheck(
            os.path.join(py37Path, "Lib/site-packages/PyQt5", _),
            os.path.join(runtime, "PyQt5"),
        )

copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/Qt5Core.dll"),
    os.path.join(runtime, "PyQt5/Qt5/bin"),
)
copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/Qt5Svg.dll"),
    os.path.join(runtime, "PyQt5/Qt5/bin"),
)
copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/Qt5Gui.dll"),
    os.path.join(runtime, "PyQt5/Qt5/bin"),
)

copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/bin/Qt5Widgets.dll"),
    os.path.join(runtime, "PyQt5/Qt5/bin"),
)

copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/plugins/iconengines"),
    os.path.join(runtime, "PyQt5/Qt5/plugins"),
)
copycheck(
    os.path.join(py37Path, "Lib/site-packages/PyQt5/Qt5/plugins/imageformats"),
    os.path.join(runtime, "PyQt5/Qt5/plugins"),
)
copycheck(
    os.path.join(
        py37Path, "Lib/site-packages/PyQt5/Qt5/plugins/platforms/qwindows.dll"
    ),
    os.path.join(runtime, "PyQt5/Qt5/plugins/platforms"),
)
copycheck(
    os.path.join(
        py37Path, "Lib/site-packages/PyQt5/Qt5/plugins/styles/qwindowsvistastyle.dll"
    ),
    os.path.join(runtime, "PyQt5/Qt5/plugins/styles"),
)

collect = []
for _dir, _, fs in os.walk(targetdir):
    for f in fs:
        collect.append(os.path.join(_dir, f))
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
            if _dll.lower().startswith("api-ms-win-core"):
                # 其实对于api-ms-win-core-winrt-XXX实际上是到ComBase.dll之类的，不过此项目中不包含这些
                _target = "kernel32.dll"
            elif _dll.lower().startswith("api-ms-win-crt"):
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

target = os.path.basename(targetdir)
if os.path.exists(rf"{targetdir}\..\{target}.zip"):
    os.remove(rf"{targetdir}\..\{target}.zip")
if os.path.exists(rf"{targetdir}\..\{target}.7z"):
    os.remove(rf"{targetdir}\..\{target}.7z")
os.system(
    rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {targetdir}\..\{target}.zip {targetdir}'
)
if 0:
    os.system(
        rf'"C:\Program Files\7-Zip\7z.exe" a -m0=LZMA2 -mx9 {targetdir}\..\{target}.7z {targetdir}'
    )
    with open(r"C:\Program Files\7-Zip\7z.sfx", "rb") as ff:
        sfx = ff.read()

    config = """
    ;!@Install@!UTF-8!


    ;!@InstallEnd@!
    """
    with open(rf"{targetdir}\..\{target}.7z", "rb") as ff:
        data = ff.read()

    with open(rf"{targetdir}\..\{target}.exe", "wb") as ff:
        ff.write(sfx)
        ff.write(config.encode("utf8"))
        ff.write(data)
