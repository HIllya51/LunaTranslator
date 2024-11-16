import os, sys, re, shutil
import subprocess

rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
rootDir = os.path.abspath(os.path.join(rootDir, "../../cpp/LunaHook"))
if len(sys.argv) and sys.argv[1] == "loadversion":
    os.chdir(rootDir)
    with open("CMakeLists.txt", "r", encoding="utf8") as ff:
        pattern = r"set\(VERSION_MAJOR\s*(\d+)\s*\)\nset\(VERSION_MINOR\s*(\d+)\s*\)\nset\(VERSION_PATCH\s*(\d+)\s*\)"
        match = re.findall(pattern, ff.read())[0]
        version_major, version_minor, version_patch = match
        versionstring = f"v{version_major}.{version_minor}.{version_patch}"
        print("version=" + versionstring)
        exit()
if len(sys.argv) and sys.argv[1] == "merge":
    os.chdir(rootDir)
    os.mkdir("../build")
    os.mkdir("builds")
    language = ["Chinese", "English", "Russian", "TradChinese"]
    for lang in language:
        shutil.copytree(
            f"build/{lang}_64/Release_{lang}",
            f"../build/Release_{lang}",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            f"build/{lang}_winxp/Release_{lang}_winxp",
            f"../build/Release_{lang}",
            dirs_exist_ok=True,
        )

        targetdir = f"../build/Release_{lang}"
        target = f"builds/Release_{lang}.zip"
        os.system(
            rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target} {targetdir}'
        )
    exit()

print(sys.version)
print(__file__)
print(rootDir)


def build_langx(lang, bit, onlycore):
    config = (
        f"-DBUILD_PLUGIN=OFF -DWINXP=OFF -DLANGUAGE={lang} -DBUILD_GUI=ON -DBUILD_CLI=ON"
        if not onlycore
        else ""
    )
    with open("do.bat", "w") as ff:
        if bit == "32":
            ff.write(
                rf"""
cmake {config} ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86_{lang}
cmake --build ../build/x86_{lang} --config Release --target ALL_BUILD -j 14
"""
            )
        elif bit == "64":
            ff.write(
                rf"""
cmake {config} ../CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ../build/x64_{lang}
cmake --build ../build/x64_{lang} --config Release --target ALL_BUILD -j 14
"""
            )
    os.system(f"cmd /c do.bat")


def build_langx_xp(lang, core):
    url = "https://github.com/Chuyu-Team/YY-Thunks/releases/download/v1.0.7/YY-Thunks-1.0.7-Binary.zip"
    os.system(rf"curl -SLo YY-Thunks-1.0.7-Binary.zip " + url)
    os.system(rf"7z x -y YY-Thunks-1.0.7-Binary.zip -o../../libs/YY-Thunks")
    os.system("dir")
    flags = "" if core else " -DBUILD_GUI=ON -DBUILD_CLI=ON "
    with open("do.bat", "w") as ff:
        ff.write(
            rf"""

cmake -DBUILD_PLUGIN=OFF -DWINXP=ON -DLANGUAGE={lang} {flags} ../CMakeLists.txt -G "Visual Studio 16 2019" -A win32 -T v141_xp -B ../build/x86_{lang}_xp
cmake --build ../build/x86_{lang}_xp --config Release --target ALL_BUILD -j 14
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
    lang = sys.argv[2]
    bit = sys.argv[3]
    if bit == "winxp":
        build_langx_xp(lang, False)
    elif bit == "winxp_core":
        build_langx_xp(lang, True)
    else:
        onlycore = int(sys.argv[4]) if len(sys.argv) >= 5 else False
        build_langx(lang, bit, onlycore)
