import os, shutil, sys


rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
rootDir=os.path.abspath(os.path.join(rootDir,'../../cpp/LunaHook'))

os.chdir(rootDir)
for f in os.listdir("../builds"):
    if os.path.isdir("../builds/" + f) == False:
        continue

    for dirname, _, fs in os.walk("../builds/" + f):
        if (
            dirname.endswith("translations")
            or dirname.endswith("translations")
            or dirname.endswith("imageformats")
            or dirname.endswith("iconengines")
            or dirname.endswith("bearer")
        ):
            shutil.rmtree(dirname)
            continue
        for ff in fs:
            path = os.path.join(dirname, ff)
            if ff in [
                "Qt5Svg.dll",
                "libEGL.dll",
                "libGLESv2.dll",
                "opengl32sw.dll",
                "D3Dcompiler_47.dll",
            ]:
                os.remove(path)
    targetdir = "../builds/" + f
    target = "../builds/" + f + ".zip"
    os.system(
        rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target} {targetdir}'
    )
