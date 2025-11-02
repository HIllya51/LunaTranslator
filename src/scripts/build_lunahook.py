import os, sys, re, shutil
import subprocess

rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
rootDir = os.path.abspath(os.path.join(rootDir, "../NativeImpl/LunaHook"))

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

os.chdir(rootDir)
if sys.argv[1] == "plugin":
    bits = sys.argv[2]
    with open("buildplugin.bat", "w") as ff:
        if bits == "32":
            ff.write(
                rf"""
cmake -DBUILD_CORE=OFF -DUSESYSQTPATH=1 -DBUILD_PLUGIN=ON ./CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ./build/plugin32
cmake --build ./build/plugin32 --config Release --target ALL_BUILD -j {os.cpu_count()}
"""
            )
        else:
            ff.write(
                rf"""
cmake -DBUILD_CORE=OFF -DUSESYSQTPATH=1 -DBUILD_PLUGIN=ON ./CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ./build/plugin64
cmake --build ./build/plugin64 --config Release --target ALL_BUILD -j {os.cpu_count()}
"""
            )
    os.system(f"cmd /c buildplugin.bat")
elif sys.argv[1] == "build":
    arch = sys.argv[2]
    core = int(sys.argv[3])
    target = sys.argv[4]

    archA = ("win32", "x64")[arch == "x64"]
    vsver = "Visual Studio 17 2022"
    Tool = "v141_xp" if target == "winxp" else f"host={arch}"
    config = (
        "-DWIN10ABOVE=ON"
        if target == "win10"
        else (" -DWINXP=ON " if target == "winxp" else "")
    )
    config += " -DBUILD_PLUGIN=OFF "
    if not core:
        config += " -DBUILD_GUI=ON "

    subprocess.run(
        f'cmake {config} ./CMakeLists.txt -G "{vsver}" -A {archA} -T {Tool} -B ./build/{arch}_{target}'
    )
    subprocess.run(
        f"cmake --build ./build/{arch}_{target} --config Release --target ALL_BUILD -j {os.cpu_count()}"
    )
