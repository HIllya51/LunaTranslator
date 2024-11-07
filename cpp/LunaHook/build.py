import os, sys, re, shutil
import subprocess

rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
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
    bits = [32, 64]
    for lang in language:
        for bit in bits:
            shutil.copytree(
                f"build/{lang}_{bit}/Release_{lang}",
                f"../build/Release_{lang}",
                dirs_exist_ok=True,
            )

        targetdir = f"../build/Release_{lang}"
        target = f"builds/Release_{lang}.zip"
        os.system(
            rf'"C:\Program Files\7-Zip\7z.exe" a -m0=Deflate -mx9 {target} {targetdir}'
        )
    exit()
vcltlFile = "https://github.com/Chuyu-Team/VC-LTL5/releases/download/v5.0.9/VC-LTL-5.0.9-Binary.7z"
vcltlFileName = "VC-LTL-5.0.9-Binary.7z"


print(sys.version)
print(__file__)
print(rootDir)


def installVCLTL():
    os.chdir(rootDir)
    if os.path.exists("temp"):
        return  # already installed
    os.makedirs(rootDir + "\\temp", exist_ok=True)
    subprocess.run(f"curl -Lo temp\\{vcltlFileName} {vcltlFile}")
    subprocess.run(f"7z x temp\\{vcltlFileName} -otemp\\VC-LTL5")
    subprocess.run("cmd /c temp\\VC-LTL5\\Install.cmd")


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


def build_langx_xp(lang):
    url = "https://github.com/Chuyu-Team/YY-Thunks/releases/download/v1.0.7/YY-Thunks-1.0.7-Binary.zip"
    target = "YY-Thunks/objs/X86/YY_Thunks_for_WinXP.obj"
    if os.path.exists(target) == False:
        os.system(rf"curl -SLo YY-Thunks-1.0.7-Binary.zip " + url)
        os.system(rf"7z x -y YY-Thunks-1.0.7-Binary.zip -o../YY-Thunks")
    os.system("dir")
    with open("do.bat", "w") as ff:
        ff.write(
            rf"""

cmake -DBUILD_PLUGIN=OFF -DWINXP=ON -DLANGUAGE={lang} -DBUILD_GUI=ON -DBUILD_CLI=ON ../CMakeLists.txt -G "Visual Studio 16 2019" -A win32 -T v141_xp -B ../build/x86_{lang}_xp
cmake --build ../build/x86_{lang}_xp --config Release --target ALL_BUILD -j 14
call dobuildxp.bat
"""
        )
    os.system(f"cmd /c do.bat")


# installVCLTL()
os.chdir(os.path.join(rootDir, "scripts"))
if sys.argv[1] == "plg32":
    os.system(f"cmd /c buildplugin32.bat")
elif sys.argv[1] == "plg64":
    os.system(f"cmd /c buildplugin64.bat")
elif sys.argv[1] == "build":
    lang = sys.argv[2]
    bit = sys.argv[3]
    if bit == "winxp":
        build_langx_xp(lang)
    else:
        onlycore = int(sys.argv[4]) if len(sys.argv) >= 5 else False
        build_langx(lang, bit, onlycore)
