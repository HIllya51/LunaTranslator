import os, shutil, sys


rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
rootDir=os.path.abspath(os.path.join(rootDir,'../../src/NativeImpl/LunaHook'))

os.chdir(rootDir)
os.chdir('./builds')
for f in os.listdir("."):
    if os.path.isdir("./" + f) == False:
        continue

    for dirname, _, fs in os.walk("./" + f):
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
    targetdir = "./" + f
    target = "./" + f + ".zip"
    os.system(
        rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target} {targetdir}'
    )
