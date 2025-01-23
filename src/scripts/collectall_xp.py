import shutil, os
import platform
import sys
os.system('python generate_xp_code.py')
os.system("git clone --depth 1 https://github.com/HIllya51/py3.4_pyqt5.5.1")
os.rename("py3.4_pyqt5.5.1/Python34", "runtime")

targetdir = r"build\LunaTranslator_x86_winxp"
launch = "../src/cpp/builds/_x86"
baddll = "DLL64"


def copycheck(src, tgt):
    print(src, tgt, os.path.exists(src))
    if not os.path.exists(src):
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
copycheck(os.path.join(launch, "LunaTranslator_debug.exe"), targetdir)
os.remove('./LunaTranslator/requests.py')
copycheck("./LunaTranslator", targetdir)
copycheck(r".\files", targetdir)
copycheck("runtime", targetdir + "/files")
try:
    shutil.rmtree(rf"{targetdir}\files\plugins\{baddll}")
except:
    pass
shutil.copy(r"..\LICENSE", targetdir)

target = os.path.basename(targetdir)
os.chdir(os.path.dirname(targetdir))
if os.path.exists(rf"{target}.zip"):
    os.remove(rf"{target}.zip")
os.system(rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target}.zip {target}')
