import os, sys, re, json
import shutil, json
import subprocess, time
import urllib.request
from urllib.parse import urljoin

rootDir = os.path.dirname(__file__)
if sys.argv[1] == "loadversion":
    os.chdir(rootDir)
    with open("plugins/CMakeLists.txt", "r", encoding="utf8") as ff:
        pattern = r"set\(VERSION_MAJOR\s*(\d+)\s*\)\nset\(VERSION_MINOR\s*(\d+)\s*\)\nset\(VERSION_PATCH\s*(\d+)\s*\)"
        match = re.findall(pattern, ff.read())[0]
        version_major, version_minor, version_patch = match
        versionstring = f"v{version_major}.{version_minor}.{version_patch}"
        print("version=" + versionstring)
        exit()

mylinks = {
    "LunaHook": "https://github.com/HIllya51/LunaHook/releases/latest/download/Release_English.zip",
    "ocr_models": {
        "ocr_models": {
            "ja.zip": "https://github.com/test123456654321/RESOURCES/releases/download/ocr_models/ja.zip",
        }
    },
    "mecab.zip": "https://github.com/HIllya51/RESOURCES/releases/download/common/mecab.zip",
    "ocr.zip": "https://github.com/HIllya51/RESOURCES/releases/download/common/ocr.zip",
    "magpie.zip": "https://github.com/HIllya51/RESOURCES/releases/download/common/magpie.zip",
    "stylesheets-main.zip": "https://github.com/HIllya51/RESOURCES/releases/download/common/stylesheets-main.zip",
}


pluginDirs = ["DLL32", "DLL64", "Locale_Remulator", "LunaHook", "Magpie", "NTLEAS"]

vcltlFile = "https://github.com/Chuyu-Team/VC-LTL5/releases/download/v5.0.9/VC-LTL-5.0.9-Binary.7z"

brotliFile32 = "https://github.com/google/brotli/releases/latest/download/brotli-x86-windows-dynamic.zip"
brotliFile64 = "https://github.com/google/brotli/releases/latest/download/brotli-x64-windows-dynamic.zip"

localeEmulatorFile = "https://github.com/xupefei/Locale-Emulator/releases/download/v2.5.0.1/Locale.Emulator.2.5.0.1.zip"
ntleaFile = "https://github.com/zxyacb/ntlea/releases/download/0.46/ntleas046_x64.7z"
LocaleRe = "https://github.com/InWILL/Locale_Remulator/releases/download/v1.5.3-beta.1/Locale_Remulator.1.5.3-beta.1.zip"

curlFile32 = "https://curl.se/windows/dl-8.8.0_3/curl-8.8.0_3-win32-mingw.zip"
curlFile64 = "https://curl.se/windows/dl-8.8.0_3/curl-8.8.0_3-win64-mingw.zip"

availableLocales = ["cht", "en", "ja", "ko", "ru", "zh"]




def createPluginDirs():
    os.chdir(rootDir + "\\LunaTranslator\\files")
    if not os.path.exists("plugins"):
        os.mkdir("plugins")
    os.chdir("plugins")
    for pluginDir in pluginDirs:
        if not os.path.exists(pluginDir):
            os.mkdir(pluginDir)


def installVCLTL():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {vcltlFile}")
    subprocess.run(f"7z x {vcltlFile.split('/')[-1]} -oVC-LTL5")
    os.chdir("VC-LTL5")
    subprocess.run("cmd /c Install.cmd")


def downloadBrotli():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {brotliFile32}")
    subprocess.run(f"curl -LO {brotliFile64}")
    subprocess.run(f"7z x {brotliFile32.split('/')[-1]} -obrotli32")
    subprocess.run(f"7z x {brotliFile64.split('/')[-1]} -obrotli64")
    shutil.move(
        "brotli32/brotlicommon.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL32"
    )
    shutil.move(
        "brotli32/brotlidec.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL32"
    )
    shutil.move(
        "brotli64/brotlicommon.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL64"
    )
    shutil.move(
        "brotli64/brotlidec.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL64"
    )


def downloadlr():

    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {LocaleRe}")
    subprocess.run(f"7z x {LocaleRe.split('/')[-1]} -oLR")
    os.makedirs(
        f"{rootDir}/LunaTranslator/files/plugins/Locale_Remulator",
        exist_ok=True,
    )
    for _dir, _, _fs in os.walk("LR"):
        for f in _fs:
            if f in ["LRHookx64.dll", "LRHookx32.dll"]:
                shutil.move(
                    os.path.join(_dir, f),
                    f"{rootDir}/LunaTranslator/files/plugins/Locale_Remulator",
                )


def move_directory_contents(source_dir, destination_dir):
    contents = os.listdir(source_dir)

    for item in contents:
        if item == ".git":
            continue
        item_path = os.path.join(source_dir, item)
        try:
            shutil.move(item_path, destination_dir)
        except:
            for k in os.listdir(item_path):
                shutil.move(
                    os.path.join(item_path, k), os.path.join(destination_dir, item)
                )


def downloadcommon():
    os.chdir(rootDir + "\\temp")
    downloadlr()
    subprocess.run(f"curl -LO {mylinks['mecab.zip']}")
    subprocess.run(f"7z x mecab.zip -oALL")
    subprocess.run(f"curl -LO {mylinks['ocr.zip']}")
    subprocess.run(f"7z x ocr.zip -oALL")
    subprocess.run(f"curl -LO {mylinks['magpie.zip']}")
    subprocess.run(f"7z x magpie.zip -oALL")

    move_directory_contents("ALL/ALL", f"{rootDir}/LunaTranslator/files/plugins")


def downloadLocaleEmulator():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {localeEmulatorFile}")
    subprocess.run(f"7z x {localeEmulatorFile.split('/')[-1]} -oLocaleEmulator")
    shutil.move(
        "LocaleEmulator/LoaderDll.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LoaderDll.dll",
    )
    shutil.move(
        "LocaleEmulator/LocaleEmulator.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LocaleEmulator.dll",
    )


def downloadNtlea():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {ntleaFile}")
    subprocess.run(f"7z x {ntleaFile.split('/')[-1]} -ontlea")
    shutil.move(
        "ntlea/x86/ntleai.dll",
        f"{rootDir}/LunaTranslator/files/plugins/NTLEAS/ntleai.dll",
    )
    shutil.move(
        "ntlea/x64/ntleak.dll",
        f"{rootDir}/LunaTranslator/files/plugins/NTLEAS/ntleak.dll",
    )


def downloadCurl():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {curlFile32}")
    subprocess.run(f"curl -LO {curlFile64}")
    subprocess.run(f"7z x {curlFile32.split('/')[-1]}")
    subprocess.run(f"7z x {curlFile64.split('/')[-1]}")
    outputDirName32 = curlFile32.split('/')[-1].replace(".zip", "")
    shutil.move(
        f"{outputDirName32}/bin/libcurl.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL32",
    )
    outputDirName64 = curlFile64.split('/')[-1].replace(".zip", "")
    shutil.move(
        f"{outputDirName64}/bin/libcurl-x64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL64",
    )


def downloadOCRModel():
    os.chdir(rootDir + "\\LunaTranslator\\files")
    if not os.path.exists("ocr"):
        os.mkdir("ocr")
    os.chdir("ocr")
    subprocess.run(f"curl -LO {mylinks['ocr_models']['ja.zip']}")
    subprocess.run(f"7z x ja.zip")
    os.remove(f"ja.zip")


def get_url_as_json(url):
    for i in range(10):
        try:
            response = urllib.request.urlopen(url)
            data = response.read().decode("utf-8")
            json_data = json.loads(data)
            return json_data
        except:
            time.sleep(3)


def buildLunaHook():

    os.chdir(rootDir + "\\temp")
    LunaHook_latest = mylinks["LunaHook"]
    subprocess.run(f"curl -LO {LunaHook_latest}")
    subprocess.run(f"7z x {LunaHook_latest.split('/')[-1]}")
    shutil.move(
        "Release_English/LunaHook32.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )
    shutil.move(
        "Release_English/LunaHost32.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )
    shutil.move(
        "Release_English/LunaHook64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )
    shutil.move(
        "Release_English/LunaHost64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )


def buildPlugins():
    os.chdir(rootDir + "\\plugins\\scripts")
    subprocess.run("python fetchwebview2.py")
    subprocess.run(
        f'cmake ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86 -DCMAKE_SYSTEM_VERSION=10.0.26621.0'
    )
    subprocess.run(
        f"cmake --build ../build/x86 --config Release --target ALL_BUILD -j 14"
    )
    subprocess.run(f"python copytarget.py 1")
    subprocess.run(
        f'cmake ../CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ../build/x64 -DCMAKE_SYSTEM_VERSION=10.0.26621.0'
    )
    subprocess.run(
        f"cmake --build ../build/x64 --config Release --target ALL_BUILD -j 14"
    )
    subprocess.run(f"python copytarget.py 0")


def downloadsomething():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {mylinks['stylesheets-main.zip']}")
    subprocess.run(f"7z x stylesheets-main.zip -oALL")
    move_directory_contents(
        "ALL/stylesheets-main", rootDir + "\\LunaTranslator\\files\\themes"
    )


def downloadbass():

    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO https://www.un4seen.com/files/bass24.zip")
    subprocess.run(f"7z x bass24.zip -oALL")
    shutil.move(
        "ALL/bass.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL32",
    )
    shutil.move(
        "ALL/x64/bass.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL64",
    )


if __name__ == "__main__":
    arch = sys.argv[1]
    version = sys.argv[2]
    os.chdir(rootDir)
    os.system("git submodule update --init --recursive")
    os.makedirs("temp", exist_ok=True)

    createPluginDirs()
    downloadsomething()
    downloadBrotli()
    downloadLocaleEmulator()
    downloadNtlea()
    downloadCurl()
    downloadOCRModel()
    downloadcommon()
    downloadbass()
    buildLunaHook()

    installVCLTL()
    buildPlugins()

    os.chdir(rootDir)

    if arch == "x86":
        py37Path = f"C:\\hostedtoolcache\\windows\\Python\\{version}\\x86\\python.exe"
    else:
        py37Path = f"C:\\hostedtoolcache\\windows\\Python\\{version}\\x64\\python.exe"

    os.chdir(rootDir + "\\LunaTranslator")

    subprocess.run(f"{py37Path} -m pip install --upgrade pip")
    subprocess.run(f"{py37Path} -m pip install -r requirements.txt")
    # 3.8之后会莫名其妙引用这个b东西，然后这个b东西会把一堆没用的东西导入进来
    shutil.rmtree(os.path.join(os.path.dirname(py37Path), "Lib\\test"))
    shutil.rmtree(os.path.join(os.path.dirname(py37Path), "Lib\\unittest"))
    # 放弃，3.8需要安装KB2533623才能运行，3.7用不着。
    subprocess.run(f"{py37Path} retrieval.py")
