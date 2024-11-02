import os
import modulefinder, shutil, os, sys
import builtins, platform
import sys

pyversion = platform.python_version()
pyversion2 = "".join(pyversion.split(".")[:2])
x86 = platform.architecture()[0] == "32bit"
runtime = r"pyrt\runtime"
if x86:
    webviewpath = r"webviewpy\platform\win32\x86"
    downlevel = r"C:\Windows\SysWOW64\downlevel"
else:
    webviewpath = r"webviewpy\platform\win32\x64"
    downlevel = r"C:\Windows\system32\downlevel"
py37Path = os.path.dirname(sys.executable)
print(py37Path)


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
    os.path.join(py37Path, "Lib/site-packages", webviewpath, "webview.dll"),
    os.path.join(runtime, webviewpath),
)

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
