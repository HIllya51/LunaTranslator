import os, sys, re, json
import shutil, json
import subprocess, time
import urllib.request
from urllib.parse import urljoin

rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
else:
    rootDir = os.path.abspath(rootDir)
rootthisfiledir = rootDir
rootDir = os.path.abspath(os.path.join(rootDir, "../../py"))
if sys.argv[1] == "loadversion":
    os.chdir(rootDir)
    with open("../cpp/version.cmake", "r", encoding="utf8") as ff:
        pattern = r"set\(VERSION_MAJOR\s*(\d+)\s*\)\nset\(VERSION_MINOR\s*(\d+)\s*\)\nset\(VERSION_PATCH\s*(\d+)\s*\)"
        match = re.findall(pattern, ff.read())[0]
        version_major, version_minor, version_patch = match
        versionstring = f"v{version_major}.{version_minor}.{version_patch}"
        print("version=" + versionstring)
        exit()

print(sys.version)
print(__file__)
print(rootDir)

mylinks = {
    "ocr_models": {
        "ja.zip": "https://github.com/test123456654321/RESOURCES/releases/download/ocr_models/ja.zip",
    },
    "mecab_xp.zip": "https://github.com/HIllya51/mecab/releases/download/common/mecab_xp.zip",
    "mecab.zip": "https://github.com/HIllya51/mecab/releases/download/common/mecab.zip",
    "magpie.zip": "https://github.com/HIllya51/Magpie_CLI/releases/download/common/magpie.zip",
}


pluginDirs = ["DLL32", "DLL64", "Magpie"]
pluginDirs_1 = ["DLL32", "DLL64"]

vcltlFile = "https://github.com/Chuyu-Team/VC-LTL5/releases/download/v5.0.9/VC-LTL-5.0.9-Binary.7z"

brotliFile32 = "https://github.com/google/brotli/releases/latest/download/brotli-x86-windows-dynamic.zip"
brotliFile64 = "https://github.com/google/brotli/releases/latest/download/brotli-x64-windows-dynamic.zip"

localeEmulatorFile = "https://github.com/xupefei/Locale-Emulator/releases/download/v2.5.0.1/Locale.Emulator.2.5.0.1.zip"
ntleaFile = "https://github.com/zxyacb/ntlea/releases/download/0.46/ntleas046_x64.7z"
LocaleRe = "https://github.com/InWILL/Locale_Remulator/releases/download/v1.5.3-beta.1/Locale_Remulator.1.5.3-beta.1.zip"

curlFile32 = "https://curl.se/windows/dl-8.8.0_3/curl-8.8.0_3-win32-mingw.zip"
curlFile64 = "https://curl.se/windows/dl-8.8.0_3/curl-8.8.0_3-win64-mingw.zip"

availableLocales = ["cht", "en", "ja", "ko", "ru", "zh"]


def createPluginDirs(which):
    os.chdir(rootDir + "\\files")
    if not os.path.exists("plugins"):
        os.mkdir("plugins")
    os.chdir("plugins")
    for pluginDir in [pluginDirs_1, pluginDirs][which]:
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
    shutil.move("brotli32/brotlicommon.dll", f"{rootDir}/files/plugins/DLL32")
    shutil.move("brotli32/brotlidec.dll", f"{rootDir}/files/plugins/DLL32")
    shutil.move("brotli64/brotlicommon.dll", f"{rootDir}/files/plugins/DLL64")
    shutil.move("brotli64/brotlidec.dll", f"{rootDir}/files/plugins/DLL64")


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


def downloadmecab():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {mylinks['mecab.zip']}")
    subprocess.run(f"7z x mecab.zip -oALL")
    move_directory_contents("ALL/ALL", f"{rootDir}/files/plugins")


def downloadmecabxp():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {mylinks['mecab_xp.zip']}")
    subprocess.run(f"7z x mecab_xp.zip -oALL")
    move_directory_contents("ALL/ALL", f"{rootDir}/files/plugins")


def downloadmapie():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {mylinks['magpie.zip']}")
    subprocess.run(f"7z x magpie.zip -oALL")
    move_directory_contents("ALL/ALL", f"{rootDir}/files/plugins")


def downloadlr():

    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {LocaleRe}")
    base = LocaleRe.split("/")[-1]
    fn = os.path.splitext(base)[0]
    subprocess.run(f"7z x {base}")
    os.makedirs(
        rf"{rootDir}\files\plugins\Locale\Locale_Remulator",
        exist_ok=True,
    )

    for f in [
        "LRHookx64.dll",
        "LRHookx32.dll",
        # "LRConfig.xml",
        "LRProc.exe",
        "LRSubMenus.dll",
    ]:
        shutil.move(
            os.path.join(fn, f),
            rf"{rootDir}\files\plugins\Locale\Locale_Remulator",
        )


def downloadLocaleEmulator():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {localeEmulatorFile}")
    subprocess.run(f"7z x {localeEmulatorFile.split('/')[-1]} -oLocaleEmulator")

    os.makedirs(
        rf"{rootDir}\files\plugins\Locale\Locale.Emulator",
        exist_ok=True,
    )
    p = subprocess.Popen("LocaleEmulator/LEInstaller.exe")
    while 1:
        if os.path.exists("LocaleEmulator/LECommonLibrary.dll"):
            break
        time.sleep(0.1)
    p.kill()

    for f in [
        "LoaderDll.dll",
        "LocaleEmulator.dll",
        "LEProc.exe",
        # "LEConfig.xml",
        "LECommonLibrary.dll",
    ]:
        shutil.move(
            os.path.join("LocaleEmulator", f),
            rf"{rootDir}\files\plugins\Locale\Locale.Emulator",
        )


def downloadNtlea():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {ntleaFile}")
    subprocess.run(f"7z x {ntleaFile.split('/')[-1]} -ontlea")

    os.makedirs(
        rf"{rootDir}\files\plugins\Locale\ntleas046_x64",
        exist_ok=True,
    )
    shutil.copytree("ntlea/x86", rf"{rootDir}\files\plugins\Locale\ntleas046_x64\x86")
    shutil.copytree("ntlea/x64", rf"{rootDir}\files\plugins\Locale\ntleas046_x64\x64")


def downloadCurl():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {curlFile32}")
    subprocess.run(f"curl -LO {curlFile64}")
    subprocess.run(f"7z x {curlFile32.split('/')[-1]}")
    subprocess.run(f"7z x {curlFile64.split('/')[-1]}")
    outputDirName32 = curlFile32.split("/")[-1].replace(".zip", "")
    shutil.move(
        f"{outputDirName32}/bin/libcurl.dll",
        f"{rootDir}/files/plugins/DLL32",
    )
    outputDirName64 = curlFile64.split("/")[-1].replace(".zip", "")
    shutil.move(
        f"{outputDirName64}/bin/libcurl-x64.dll",
        f"{rootDir}/files/plugins/DLL64",
    )


def downloadOCRModel():
    os.chdir(rootDir + "\\files")
    if not os.path.exists("ocrmodel"):
        os.mkdir("ocrmodel")
    os.chdir("ocrmodel")
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


def buildPlugins(arch):
    os.chdir(rootDir + "\\..\\cpp\\scripts")
    subprocess.run("python fetchwebview2.py")
    if arch == "x86":
        subprocess.run(
            f'cmake ../CMakeLists.txt -G "Visual Studio 17 2022" -A win32 -T host=x86 -B ../build/x86 -DCMAKE_SYSTEM_VERSION=10.0.26621.0'
        )
        subprocess.run(
            f"cmake --build ../build/x86 --config Release --target ALL_BUILD -j 14"
        )
    # subprocess.run(f"python copytarget.py 1")
    elif arch == "x64":
        subprocess.run(
            f'cmake ../CMakeLists.txt -G "Visual Studio 17 2022" -A x64 -T host=x64 -B ../build/x64 -DCMAKE_SYSTEM_VERSION=10.0.26621.0'
        )
        subprocess.run(
            f"cmake --build ../build/x64 --config Release --target ALL_BUILD -j 14"
        )
        # subprocess.run(f"python copytarget.py 0")
    elif arch == "xp":
        # url = "https://github.com/Chuyu-Team/YY-Thunks/releases/download/v1.0.7/YY-Thunks-1.0.7-Binary.zip"
        # os.system(rf"curl -SLo YY-Thunks-1.0.7-Binary.zip " + url)
        # os.system(rf"7z x -y YY-Thunks-1.0.7-Binary.zip -o../libs/YY-Thunks")
        with open("do.bat", "w") as ff:
            ff.write(
                rf"""

cmake -DWINXP=ON ../CMakeLists.txt -G "Visual Studio 16 2019" -A win32 -T v141_xp -B ../build/x86_xp
cmake --build ../build/x86_xp --config Release --target ALL_BUILD -j 14
"""
            )
        os.system(f"cmd /c do.bat")


def downloadbass():

    os.chdir(rootDir + "\\temp")
    for link in (
        "https://www.un4seen.com/files/bass24.zip",
        "https://www.un4seen.com/files/z/2/bass_spx24.zip",
        "https://www.un4seen.com/files/z/2/bass_aac24.zip",
        "https://www.un4seen.com/files/bassopus24.zip",
        "https://www.un4seen.com/files/bassenc24.zip",
        "https://www.un4seen.com/files/bassenc_mp324.zip",
        "https://www.un4seen.com/files/bassenc_opus24.zip",
    ):
        name = link.split("/")[-1]
        d = name.split(".")[0]
        subprocess.run("curl -LO " + link)
        subprocess.run(f"7z x {name} -o{d}")
        shutil.move(
            f"{d}/{d[:-2]}.dll",
            f"{rootDir}/files/plugins/DLL32",
        )
        shutil.move(
            f"{d}/x64/{d[:-2]}.dll",
            f"{rootDir}/files/plugins/DLL64",
        )


if __name__ == "__main__":
    os.chdir(rootDir)
    os.makedirs("temp", exist_ok=True)
    arch = sys.argv[2]
    if sys.argv[1] == "cpp":
        installVCLTL()
        buildPlugins(arch)
    elif sys.argv[1] == "pyrt":
        version = sys.argv[3]
        if arch == "x86":
            py37Path = (
                f"C:\\hostedtoolcache\\windows\\Python\\{version}\\x86\\python.exe"
            )
        else:
            py37Path = (
                f"C:\\hostedtoolcache\\windows\\Python\\{version}\\x64\\python.exe"
            )
        os.chdir(rootDir)
        subprocess.run(f"{py37Path} -m pip install --upgrade pip")
        subprocess.run(f"{py37Path} -m pip install -r requirements.txt")
        # 3.8之后会莫名其妙引用这个b东西，然后这个b东西会把一堆没用的东西导入进来
        shutil.rmtree(os.path.join(os.path.dirname(py37Path), "Lib\\test"))
        shutil.rmtree(os.path.join(os.path.dirname(py37Path), "Lib\\unittest"))
        # 放弃，3.8需要安装KB2533623才能运行，3.7用不着。
        subprocess.run(
            f"{py37Path} {os.path.join(rootthisfiledir,'collectpyruntime.py')}"
        )
    elif sys.argv[1] == "merge":
        createPluginDirs(0 if arch == "xp" else 1)
        downloadNtlea()
        downloadbass()
        os.chdir(rootDir)
        if arch == "xp":
            downloadmecabxp()
            shutil.copytree(
                f"{rootDir}/../build/cpp_xp",
                f"{rootDir}/../cpp/builds",
                dirs_exist_ok=True,
            )
            shutil.copytree(
                f"{rootDir}/../build/hook_xp",
                f"{rootDir}/files/plugins/LunaHook",
                dirs_exist_ok=True,
            )
            os.chdir(rootDir + "/../cpp/scripts")
            os.makedirs("../../py/files/plugins/DLL32", exist_ok=True)
            shutil.copy("../builds/_x86/shareddllproxy32.exe", "../../py/files/plugins")
            shutil.copy(
                "../builds/_x86/winsharedutils.dll", "../../py/files/plugins/DLL32"
            )
            os.chdir(rootDir)
            os.system(f"python {os.path.join(rootthisfiledir,'collectall_xp.py')}")
            exit()
        downloadmecab()
        downloadLocaleEmulator()
        downloadBrotli()
        downloadCurl()
        downloadOCRModel()
        downloadmapie()
        downloadlr()

        os.chdir(rootDir)
        shutil.copytree(
            f"{rootDir}/../build/hook_64",
            f"{rootDir}/files/plugins/LunaHook",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            f"{rootDir}/../build/hook_32",
            f"{rootDir}/files/plugins/LunaHook",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            f"{rootDir}/../build/cpp_x64",
            f"{rootDir}/../cpp/builds",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            f"{rootDir}/../build/cpp_x86",
            f"{rootDir}/../cpp/builds",
            dirs_exist_ok=True,
        )
        os.chdir(rootDir + "/../cpp/scripts")

        os.makedirs("../../py/files/plugins/DLL32", exist_ok=True)
        shutil.copy("../builds/_x86/shareddllproxy32.exe", "../../py/files/plugins")
        shutil.copy("../builds/_x86/winrtutils.dll", "../../py/files/plugins/DLL32")
        shutil.copy(
            "../builds/_x86/winsharedutils.dll", "../../py/files/plugins/DLL32"
        )
        shutil.copy("../builds/_x86/wcocr.dll", "../../py/files/plugins/DLL32")
        shutil.copy("../builds/_x86/LunaOCR.dll", "../../py/files/plugins/DLL32")
        os.makedirs("../../py/files/plugins/DLL64", exist_ok=True)
        shutil.copy("../builds/_x64/shareddllproxy64.exe", "../../py/files/plugins")
        shutil.copy("../builds/_x64/winrtutils.dll", "../../py/files/plugins/DLL64")
        shutil.copy(
            "../builds/_x64/winsharedutils.dll", "../../py/files/plugins/DLL64"
        )
        shutil.copy("../builds/_x64/wcocr.dll", "../../py/files/plugins/DLL64")
        shutil.copy("../builds/_x64/LunaOCR.dll", "../../py/files/plugins/DLL64")

        if arch == "x86":
            os.chdir(rootDir)
            os.system(f"python {os.path.join(rootthisfiledir,'collectall.py')} 32")
        else:
            os.chdir(rootDir)
            os.system(f"python {os.path.join(rootthisfiledir,'collectall.py')} 64")
