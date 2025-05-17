import os, sys, re, shutil
import subprocess

rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
rootDir = os.path.abspath(os.path.join(rootDir, "../cpp/LunaHook"))

if len(sys.argv) and sys.argv[1] == "merge":
    os.chdir(rootDir)
    os.mkdir("../build")
    os.mkdir("builds")

    shutil.copytree(
        f"build/64/Release",
        f"../build/Release",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        f"build/winxp/Release_winxp",
        f"../build/Release",
        dirs_exist_ok=True,
    )

    targetdir = f"../build/Release"
    target = f"builds/Release.zip"
    os.system(
        rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target} {targetdir}'
    )
    exit()

print(sys.version)
print(__file__)
print(rootDir)


def build_langx(bit, onlycore, win10above=False):
    config = f"-DBUILD_PLUGIN=OFF -DWINXP=OFF -DBUILD_GUI=ON " if not onlycore else ""
    if win10above:
        config += " -DWIN10ABOVE=ON "
    with open("do.bat", "w") as ff:
        if bit == "32":
            ff.write(
                rf"""
cmake {config} ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86
cmake --build ../build/x86 --config Release --target ALL_BUILD -j 14
"""
            )
        elif bit == "64":
            ff.write(
                rf"""
cmake {config} ../CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ../build/x64
cmake --build ../build/x64 --config Release --target ALL_BUILD -j 14
"""
            )
    os.system(f"cmd /c do.bat")


def build_langx_xp(core):
    flags = "" if core else " -DBUILD_GUI=ON "
    with open("do.bat", "w") as ff:
        ff.write(
            rf"""

cmake -DBUILD_PLUGIN=OFF -DWINXP=ON {flags} ../CMakeLists.txt -G "Visual Studio 16 2019" -A win32 -T v141_xp -B ../build/x86_xp
cmake --build ../build/x86_xp --config Release --target ALL_BUILD -j 14
"""
        )
    os.system(f"cmd /c do.bat")


os.chdir(os.path.join(rootDir, "scripts"))
if sys.argv[1] == "plugin":
    bits = sys.argv[2]
    with open("buildplugin.bat", "w") as ff:
        if bits == "32":
            ff.write(
                rf"""
cmake -DBUILD_CORE=OFF -DUSESYSQTPATH=1 -DBUILD_PLUGIN=ON ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/plugin32
cmake --build ../build/plugin32 --config Release --target ALL_BUILD -j 14
"""
            )
        else:
            ff.write(
                rf"""
cmake -DBUILD_CORE=OFF -DUSESYSQTPATH=1 -DBUILD_PLUGIN=ON ../CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ../build/plugin64
cmake --build ../build/plugin64 --config Release --target ALL_BUILD -j 14
"""
            )
    os.system(f"cmd /c buildplugin.bat")
elif sys.argv[1] == "build":
    bit = sys.argv[2]
    if bit == "winxp":
        build_langx_xp(False)
    elif bit == "winxp_core":
        build_langx_xp(True)
    else:
        onlycore = int(sys.argv[3]) if len(sys.argv) > 3 else False
        build_langx(bit, onlycore, len(sys.argv) > 4 and sys.argv[4] == "win10")
