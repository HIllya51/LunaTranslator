import argparse
import os
import shutil,json
import subprocess
import requests
py37Path32 = os.path.join(
    os.environ["LOCALAPPDATA"], "Programs\\Python\\Python37-32\\python.exe"
)
py37Path64 = os.path.join(
    os.environ["LOCALAPPDATA"], "Programs\\Python\\Python37\\python.exe"
)
msbuildPath = "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise\\MSBuild\\Current\\Bin\\MSBuild.exe"
vcvars32Path = "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise\\VC\\Auxiliary\\Build\\vcvars32.bat"
vcvars64Path = "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise\\VC\\Auxiliary\\Build\\vcvars64.bat"

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


prebuiltcommon="https://github.com/HIllya51/LunaTranslator_extra_build/releases/download/common/ALL.zip"

rootDir = os.path.dirname(__file__)


def createPluginDirs():
    os.chdir(rootDir + "\\LunaTranslator\\files")
    if not os.path.exists("plugins"):
        os.mkdir("plugins")
    os.chdir("plugins")
    for pluginDir in pluginDirs:
        if not os.path.exists(pluginDir):
            os.mkdir(pluginDir)


def installDependencies(arch):
    os.chdir(rootDir)
    if arch=='x86':
        subprocess.run(f"{py37Path32} -m pip install --upgrade pip")
    else:
        subprocess.run(f"{py37Path64} -m pip install --upgrade pip")

    os.chdir(rootDir + "\\LunaTranslator")
    if arch=='x86':
        subprocess.run(f"{py37Path32} -m pip install -r requirements.txt")
    else:
        subprocess.run(f"{py37Path64} -m pip install -r requirements.txt")


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


def downloadcommon():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"curl -LO {prebuiltcommon}")
    subprocess.run(f"7z x ALL.zip -oALL")
        
    def move_directory_contents(source_dir, destination_dir):
        contents = os.listdir(source_dir)

        for item in contents:
            item_path = os.path.join(source_dir, item)
            try:
                shutil.move(item_path, destination_dir)
            except:
                for k in os.listdir(item_path):
                    shutil.move(os.path.join(item_path,k), os.path.join(destination_dir,item))

    move_directory_contents(
        "ALL/ALL", f"{rootDir}/LunaTranslator/files/plugins"
    )

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



def buildLunaHook():
    for ass in requests.get('https://api.github.com/repos/HIllya51/LunaHook/releases/latest').json()['assets']:
        if ass['name']=='Release_English.zip':
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


def buildLunaTranslator(arch):
    os.chdir(rootDir + "\\LunaTranslator")
    if arch=='x86':
        subprocess.run(
            f"{py37Path32} -m nuitka --standalone --assume-yes-for-downloads --windows-disable-console --plugin-enable=pyqt5 --output-dir=..\\build\\x86 LunaTranslator\\LunaTranslator_main.py --windows-icon-from-ico=..\\plugins\\exec\\luna.ico"
        )
        subprocess.run(f"cmd /c pack32.cmd")
    else:
        subprocess.run(
            f"{py37Path64} -m nuitka --standalone --assume-yes-for-downloads --windows-disable-console --plugin-enable=pyqt5 --output-dir=..\\build\\x64 LunaTranslator\\LunaTranslator_main.py --windows-icon-from-ico=..\\plugins\\exec\\luna.ico"
        )
        subprocess.run(f"cmd /c pack64.cmd")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-download",
        action="store_true",
        default=False,
        help="Skip download steps",
    )
    parser.add_argument(
        "--skip-python-dependencies",
        action="store_true",
        default=False,
        help="Skip Python dependencies installation",
    )
    parser.add_argument(
        "--skip-vc-ltl",
        action="store_true",
        default=False,
        help="Skip VC-LTL installation",
    )
    parser.add_argument(
        "--skip-build", action="store_true", default=False, help="Skip build steps"
    )
    parser.add_argument(
        "--clean-temp",
        action="store_true",
        default=False,
        help="Clean temp directory before building",
    )
    parser.add_argument(
        "--clean-plugins",
        action="store_true",
        default=False,
        help="Clean plugins directory before building",
    )
    parser.add_argument(
        "--github-actions",
        action="store_true",
        default=False,
        help="Specify if running in a GitHub Actions environment",
    )
    parser.add_argument(
        "--arch",
    )

    args = parser.parse_args()

    os.chdir(rootDir)
    if args.clean_temp:
        os.system('powershell.exe -Command "Remove-Item -Path .\\temp -Recurse -Force"')
    if not os.path.exists("temp"):
        os.mkdir("temp")
    if args.clean_plugins:
        os.system(
            'powershell.exe -Command "Remove-Item -Path .\\LunaTranslator\\files\\plugins -Recurse -Force"'
        )
    createPluginDirs()

    if args.github_actions:
        py37Path32 = "C:\\hostedtoolcache\\windows\\Python\\3.7.9\\x86\\python.exe"
        py37Path64 = "C:\\hostedtoolcache\\windows\\Python\\3.7.9\\x64\\python.exe"

    if not args.skip_python_dependencies:
        installDependencies(args.arch)
    if not args.skip_download:
        downloadBrotli()
        downloadLocaleEmulator()
        downloadNtlea()
        downloadCurl()
        downloadOCRModel("ja")
        downloadcommon()
        buildLunaHook()
    if not args.skip_build:
        if not args.skip_vc_ltl:
            installVCLTL()
        buildPlugins()
    buildLunaTranslator(args.arch)
