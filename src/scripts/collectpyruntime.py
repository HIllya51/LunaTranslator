import os
import modulefinder, shutil, os, sys
import builtins, platform
import sys

target = sys.argv[1]
rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
else:
    rootDir = os.path.abspath(rootDir)
rootthisfiledir = rootDir
rootDir = os.path.abspath(os.path.join(rootDir, "../../src"))
pyversion = platform.python_version()
pyversion2 = "".join(pyversion.split(".")[:2])
x86 = platform.architecture()[0] == "32bit"
runtime = r"pyrt\runtime"
if x86:
    downlevel = r"C:\Windows\SysWOW64\downlevel"
else:
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
got = get_dependencies('keeprefs.py')
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
copycheck(os.path.join(py37Path, "DLLs/libffi-8.dll"), runtime)

try:
    from PyQt5 import QtCore

    qtver = "Qt5"
except:
    qtver = "Qt6"

pyqtdir = os.path.join(py37Path, f"Lib/site-packages/Py{qtver}")
pyqtbindir = os.path.join(pyqtdir, f"{qtver}/bin")
pyqtplgdir = os.path.join(pyqtdir, f"{qtver}/plugins")

targetpyqtdir = os.path.join(runtime, f"Py{qtver}")
targetpyqtbindir = os.path.join(targetpyqtdir, f"{qtver}/bin")
targetpyqtplgdir = os.path.join(targetpyqtdir, f"{qtver}/plugins")


if target == "win7":
    copycheck(rf"{downlevel}\ucrtbase.dll", runtime)

    copycheck(os.path.join(pyqtbindir, f"vcruntime140.dll"), runtime)
    copycheck(os.path.join(pyqtbindir, f"vcruntime140_1.dll"), runtime)
    copycheck(os.path.join(pyqtbindir, f"msvcp140.dll"), runtime)
    copycheck(os.path.join(pyqtbindir, f"msvcp140_1.dll"), runtime)

for _ in os.listdir(pyqtdir):
    if _.startswith("sip"):
        copycheck(os.path.join(pyqtdir, _), targetpyqtdir)

copycheck(os.path.join(pyqtbindir, f"{qtver}Core.dll"), targetpyqtbindir)
copycheck(os.path.join(pyqtbindir, f"{qtver}Svg.dll"), targetpyqtbindir)
copycheck(os.path.join(pyqtbindir, f"{qtver}SvgWidgets.dll"), targetpyqtbindir)
copycheck(os.path.join(pyqtdir, f"QtSvg.pyd"), targetpyqtdir)
copycheck(os.path.join(pyqtbindir, f"{qtver}Gui.dll"), targetpyqtbindir)

copycheck(os.path.join(pyqtbindir, f"{qtver}Widgets.dll"), targetpyqtbindir)

copycheck(os.path.join(pyqtplgdir, f"iconengines"), targetpyqtplgdir)
copycheck(os.path.join(pyqtplgdir, f"imageformats"), targetpyqtplgdir)
copycheck(
    os.path.join(pyqtplgdir, f"platforms/qwindows.dll"),
    os.path.join(targetpyqtplgdir, f"platforms"),
)

copycheck(
    os.path.join(pyqtplgdir, f"styles/qmodernwindowsstyle.dll"),
    os.path.join(targetpyqtplgdir, f"styles"),
)
copycheck(
    os.path.join(pyqtplgdir, f"styles/qwindowsvistastyle.dll"),
    os.path.join(targetpyqtplgdir, f"styles"),
)
