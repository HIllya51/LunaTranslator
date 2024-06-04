import os, sys, re
import shutil, json
import subprocess, time
import urllib.request


pluginDirs = ["DLL32", "DLL64", "Locale_Remulator", "LunaHook", "Magpie", "NTLEAS"]

vcltlFile = "https://github.com/Chuyu-Team/VC-LTL5/releases/download/v5.0.9/VC-LTL-5.0.9-Binary.7z"
vcltlFileName = "VC-LTL-5.0.9-Binary.7z"
brotliFile32 = "https://github.com/google/brotli/releases/latest/download/brotli-x86-windows-dynamic.zip"
brotliFileName32 = "brotli-x86-windows-dynamic.zip"
brotliFile64 = "https://github.com/google/brotli/releases/latest/download/brotli-x64-windows-dynamic.zip"
brotliFileName64 = "brotli-x64-windows-dynamic.zip"
localeEmulatorFile = "https://github.com/xupefei/Locale-Emulator/releases/download/v2.5.0.1/Locale.Emulator.2.5.0.1.zip"
localeEmulatorFileName = "Locale.Emulator.2.5.0.1.zip"
ntleaFile = "https://github.com/zxyacb/ntlea/releases/download/0.46/ntleas046_x64.7z"
ntleaFileName = "ntleas046_x64.7z"
curlFile32 = "https://curl.se/windows/dl-8.7.1_7/curl-8.7.1_7-win32-mingw.zip"
curlFileName32 = "curl-8.7.1_7-win32-mingw.zip"
curlFile64 = "https://curl.se/windows/dl-8.7.1_7/curl-8.7.1_7-win64-mingw.zip"
curlFileName64 = "curl-8.7.1_7-win64-mingw.zip"


ocrModelUrl = "https://github.com/HIllya51/RESOURCES/releases/download/ocr_models"
availableLocales = ["cht", "en", "ja", "ko", "ru", "zh"]


# rootDir = os.path.dirname(os.path.abspath(__file__))
# print(__file__)
# print(rootDir)
rootDir = os.path.dirname(__file__)


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
    subprocess.run(f"7z x {vcltlFileName} -oVC-LTL5")
    os.chdir("VC-LTL5")
    subprocess.run("cmd /c Install.cmd")


def downloadBrotli():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {brotliFile32}")
    subprocess.run(f"curl -LO {brotliFile64}")
    subprocess.run(f"7z x {brotliFileName32} -obrotli32")
    subprocess.run(f"7z x {brotliFileName64} -obrotli64")
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

    for ass in get_url_as_json(
        "https://api.github.com/repos/InWILL/Locale_Remulator/releases/latest"
    )["assets"]:
        if "browser_download_url" in ass:
            os.chdir(rootDir + "\\temp")
            subprocess.run(f"curl -LO {ass['browser_download_url']}")
            subprocess.run(f"7z x {ass['name']} -oLR")
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
    subprocess.run(
        f"curl -LO https://github.com/HIllya51/RESOURCES/releases/download/common/mecab.zip"
    )
    subprocess.run(f"7z x mecab.zip -oALL")
    subprocess.run(
        f"curl -LO https://github.com/HIllya51/RESOURCES/releases/download/common/ocr.zip"
    )
    subprocess.run(f"7z x ocr.zip -oALL")
    subprocess.run(
        f"curl -LO https://github.com/HIllya51/RESOURCES/releases/download/common/magpie.zip"
    )
    subprocess.run(f"7z x magpie.zip -oALL")

    move_directory_contents("ALL/ALL", f"{rootDir}/LunaTranslator/files/plugins")


def downloadLocaleEmulator():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {localeEmulatorFile}")
    subprocess.run(f"7z x {localeEmulatorFileName} -oLocaleEmulator")
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
    subprocess.run(f"7z x {ntleaFileName} -ontlea")
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
    subprocess.run(f"7z x {curlFileName32}")
    subprocess.run(f"7z x {curlFileName64}")
    outputDirName32 = curlFileName32.replace(".zip", "")
    shutil.move(
        f"{outputDirName32}/bin/libcurl.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL32",
    )
    outputDirName64 = curlFileName64.replace(".zip", "")
    shutil.move(
        f"{outputDirName64}/bin/libcurl-x64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL64",
    )


def downloadOCRModel(locale):
    if locale not in availableLocales:
        return
    os.chdir(rootDir + "\\LunaTranslator\\files")
    if not os.path.exists("ocr"):
        os.mkdir("ocr")
    os.chdir("ocr")
    subprocess.run(f"curl -LO {ocrModelUrl}/{locale}.zip")
    subprocess.run(f"7z x {locale}.zip")
    os.remove(f"{locale}.zip")


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
    for ass in get_url_as_json(
        "https://api.github.com/repos/HIllya51/LunaHook/releases/latest"
    )["assets"]:
        if ass["name"] == "Release_English.zip":
            os.chdir(rootDir + "\\temp")
            subprocess.run(f"curl -LO {ass['browser_download_url']}")
            subprocess.run(f"7z x Release_English.zip")
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
    subprocess.run(f"build32.bat")
    subprocess.run(f"build64.bat")


def downloadsomething():
    os.chdir(rootDir + "\\temp")
    os.system("git clone https://github.com/HIllya51/stylesheets")
    move_directory_contents("stylesheets", rootDir + "\\LunaTranslator\\files\\themes")


if __name__ == "__main__":
    if sys.argv[1] == "loadversion":
        os.chdir(rootDir)
        with open("plugins/CMakeLists.txt", "r", encoding="utf8") as ff:
            pattern = r"set\(VERSION_MAJOR\s*(\d+)\s*\)\nset\(VERSION_MINOR\s*(\d+)\s*\)\nset\(VERSION_PATCH\s*(\d+)\s*\)"
            match = re.findall(pattern, ff.read())[0]
            version_major, version_minor, version_patch = match
            versionstring = f"v{version_major}.{version_minor}.{version_patch}"
            print("version=" + versionstring)
            exit()
    arch = sys.argv[1]
    isdebug = len(sys.argv) > 2 and int(sys.argv[2])
    os.chdir(rootDir)
    os.system("git submodule update --init --recursive")
    os.makedirs("temp", exist_ok=True)

    createPluginDirs()
    downloadsomething()
    downloadBrotli()
    downloadLocaleEmulator()
    downloadNtlea()
    downloadCurl()
    downloadOCRModel("ja")
    downloadcommon()
    buildLunaHook()

    installVCLTL()
    buildPlugins()

    os.chdir(rootDir)

    if arch == "x86":
        py37Path = "C:\\hostedtoolcache\\windows\\Python\\3.7.9\\x86\\python.exe"
    else:
        py37Path = "C:\\hostedtoolcache\\windows\\Python\\3.7.9\\x64\\python.exe"

    os.chdir(rootDir + "\\LunaTranslator")

    subprocess.run(f"{py37Path} -m pip install --upgrade pip")
    subprocess.run(f"{py37Path} -m pip install -r requirements.txt")

    subprocess.run(f'{py37Path} retrieval.py {int(arch == "x86")}')
