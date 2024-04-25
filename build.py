import argparse
import os
import shutil
import subprocess

py37Path32 = os.path.join(
    os.environ["LOCALAPPDATA"], "Programs\\Python\\Python37-32\\python.exe"
)
py37Path64 = os.path.join(
    os.environ["LOCALAPPDATA"], "Programs\\Python\\Python37\\python.exe"
)
py311Path = os.path.join(
    os.environ["LOCALAPPDATA"], "Programs\\Python\\Python311\\python.exe"
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
onnxruntimeFile = "https://github.com/RapidAI/OnnxruntimeBuilder/releases/download/1.14.1/onnxruntime-1.14.1-vs2019-static-mt.7z"
onnxruntimeFileName = "onnxruntime-1.14.1-vs2019-static-mt.7z"
opencvFile = "https://github.com/RapidAI/OpenCVBuilder/releases/download/4.7.0/opencv-4.7.0-windows-vs2019-mt.7z"
opencvFileName = "opencv-4.7.0-windows-vs2019-mt.7z"

mecabUrl = "https://github.com/HIllya51/mecab.git"
webviewUrl = "https://github.com/HIllya51/webview.git"
localeRemulatorUrl = "https://github.com/HIllya51/Locale_Remulator.git"
lunaHookUrl = "https://github.com/HIllya51/LunaHook.git"
magpieUrl = "https://github.com/HIllya51/Magpie_CLI.git"
lunaOCRUrl = "https://github.com/HIllya51/LunaOCR.git"

ocrModelUrl = "https://github.com/HIllya51/RESOURCES/releases/download/ocr_models"
availableLocales = ["cht", "en", "ja", "ko", "ru", "zh"]


rootDir = os.path.dirname(__file__)


def createPluginDirs():
    os.chdir(rootDir + "\\LunaTranslator\\files")
    if not os.path.exists("plugins"):
        os.mkdir("plugins")
    os.chdir("plugins")
    for pluginDir in pluginDirs:
        if not os.path.exists(pluginDir):
            os.mkdir(pluginDir)


def installDependencies():
    os.chdir(rootDir)
    subprocess.run(f"{py37Path32} -m pip install --upgrade pip")
    subprocess.run(f"{py37Path64} -m pip install --upgrade pip")
    subprocess.run(f"{py311Path} -m pip install --upgrade pip")

    os.chdir(rootDir + "\\LunaTranslator")
    subprocess.run(f"{py37Path32} -m pip install -r requirements.txt")
    subprocess.run(f"{py37Path64} -m pip install -r requirements.txt")
    subprocess.run(f"{py311Path} -m pip install conan cmake pefile")


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


def buildMecab():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"git clone {mecabUrl}")
    os.chdir("mecab\\mecab")

    subprocess.run(f'cmd /c "{vcvars32Path}" & call make.bat')
    shutil.move("src/libmecab.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL32")

    subprocess.run(f'cmd /c "{vcvars64Path}" & call makeclean.bat & call make.bat')
    shutil.move("src/libmecab.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL64")


def buildWebview():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"git clone {webviewUrl}")
    os.chdir("webview\\script")
    subprocess.run(f"cmd /c set TARGET_ARCH=x86 & call build.bat")
    shutil.move(
        "../build/library/webview.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL32"
    )
    subprocess.run(f"cmd /c set TARGET_ARCH=x64 & call build.bat")
    shutil.move(
        "../build/library/webview.dll", f"{rootDir}/LunaTranslator/files/plugins/DLL64"
    )


def buildLocaleRemulator():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"git clone {localeRemulatorUrl}")
    os.chdir("Locale_Remulator")
    subprocess.run(f"nuget restore")
    os.chdir("LRHook")
    subprocess.run(
        f'"{msbuildPath}" LRHook.vcxproj /p:Configuration=Release /p:Platform=x86'
    )
    shutil.move(
        "x64/Release/LRHookx32.dll",
        f"{rootDir}/LunaTranslator/files/plugins/Locale_Remulator",
    )
    subprocess.run(
        f'"{msbuildPath}" LRHook.vcxproj /p:Configuration=Release /p:Platform=x64'
    )
    shutil.move(
        "x64/Release/LRHookx64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/Locale_Remulator",
    )


def buildLunaHook():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"git clone {lunaHookUrl}")
    os.chdir("LunaHook\\scripts")
    subprocess.run("cmd /c build32.bat")
    subprocess.run("cmd /c build64.bat")
    shutil.move(
        "../builds/Release_English/LunaHook32.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )
    shutil.move(
        "../builds/Release_English/LunaHost32.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )
    shutil.move(
        "../builds/Release_English/LunaHook64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )
    shutil.move(
        "../builds/Release_English/LunaHost64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/LunaHook",
    )


def buildLunaOCR():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"git clone {lunaOCRUrl}")
    os.chdir("LunaOCR")
    os.chdir("onnxruntime-static")
    subprocess.run(f"curl -LO {onnxruntimeFile}")
    subprocess.run(f"7z x {onnxruntimeFileName}")
    os.chdir("..")
    os.chdir("opencv-static")
    subprocess.run(f"curl -LO {opencvFile}")
    subprocess.run(f"7z x {opencvFileName}")
    os.chdir("..")

    buildType = "Release"
    buildOutput = "CLIB"
    mtEnabled = "True"
    onnxType = "CPU"
    toolset = "v143"
    arch32 = "Win32"
    arch64 = "x64"

    os.makedirs(f"build/win-{buildOutput}-{onnxType}-{arch32}")
    os.chdir(f"build/win-{buildOutput}-{onnxType}-{arch32}")
    subprocess.run(
        f'cmake -T "{toolset},host=x64" -A {arch32} '
        f"-DCMAKE_INSTALL_PREFIX=install "
        f"-DCMAKE_BUILD_TYPE={buildType} -DOCR_OUTPUT={buildOutput} "
        f"-DOCR_BUILD_CRT={mtEnabled} -DOCR_ONNX={onnxType} ../.."
    )
    subprocess.run(f"cmake --build . --config {buildType} -j {os.cpu_count()}")
    subprocess.run(f"cmake --build . --config {buildType} --target install")

    os.chdir(f"{rootDir}/temp/LunaOCR")

    os.makedirs(f"build/win-{buildOutput}-{onnxType}-{arch64}")
    os.chdir(f"build/win-{buildOutput}-{onnxType}-{arch64}")
    subprocess.run(
        f'cmake -T "{toolset},host=x64" -A {arch64} '
        f"-DCMAKE_INSTALL_PREFIX=install "
        f"-DCMAKE_BUILD_TYPE={buildType} -DOCR_OUTPUT={buildOutput} "
        f"-DOCR_BUILD_CRT={mtEnabled} -DOCR_ONNX={onnxType} ../.."
    )
    subprocess.run(f"cmake --build . --config {buildType} -j {os.cpu_count()}")
    subprocess.run(f"cmake --build . --config {buildType} --target install")

    os.chdir(f"{rootDir}/temp/LunaOCR")

    shutil.move(
        f"build/win-{buildOutput}-{onnxType}-{arch32}/install/bin/LunaOCR32.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL32",
    )
    shutil.move(
        f"build/win-{buildOutput}-{onnxType}-{arch64}/install/bin/LunaOCR64.dll",
        f"{rootDir}/LunaTranslator/files/plugins/DLL64",
    )


def buildMagpie():
    os.chdir(rootDir + "\\temp")
    subprocess.run(f"git clone {magpieUrl}")
    os.chdir("Magpie_CLI")
    subprocess.run(
        f'"{msbuildPath}" -restore -p:RestorePackagesConfig=true;Configuration=Release;Platform=x64;OutDir={os.getcwd()}\\publish\\x64\\ Magpie.sln'
    )
    shutil.move(
        "publish/x64/Magpie.Core.exe", f"{rootDir}/LunaTranslator/files/plugins/Magpie"
    )
    shutil.move("publish/x64/effects", f"{rootDir}/LunaTranslator/files/plugins/Magpie")


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


def buildLunaTranslator():
    os.chdir(rootDir + "\\LunaTranslator")
    subprocess.run(
        f"{py37Path32} -m nuitka --standalone --assume-yes-for-downloads --windows-disable-console --plugin-enable=pyqt5 --output-dir=..\\build\\x86 LunaTranslator\\LunaTranslator_main.py --windows-icon-from-ico=..\\plugins\\exec\\luna.ico"
    )
    subprocess.run(
        f"{py37Path64} -m nuitka --standalone --assume-yes-for-downloads --windows-disable-console --plugin-enable=pyqt5 --output-dir=..\\build\\x64 LunaTranslator\\LunaTranslator_main.py --windows-icon-from-ico=..\\plugins\\exec\\luna.ico"
    )
    subprocess.run(f"cmd /c pack32.cmd")
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
        py311Path = "C:\\hostedtoolcache\\windows\\Python\\3.11.7\\x64\\python.exe"
    else:
        programFiles32 = os.environ["ProgramFiles(x86)"]
        vswherePath = (
            f"{programFiles32}\\Microsoft Visual Studio\\Installer\\vswhere.exe"
        )
        msbuildPath = (
            subprocess.run(
                f'"{vswherePath}" -latest -requires Microsoft.Component.MSBuild -find MSBuild\\**\\Bin\\MSBuild.exe',
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .replace("\n", "")
        )
        vcvars32Path = (
            subprocess.run(
                f'"{vswherePath}" -latest -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find VC\\Auxiliary\\Build\\vcvars32.bat',
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .replace("\n", "")
        )
        vcvars64Path = (
            subprocess.run(
                f'"{vswherePath}" -latest -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find VC\\Auxiliary\\Build\\vcvars64.bat',
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .replace("\n", "")
        )

    if not args.skip_python_dependencies:
        installDependencies()
    if not args.skip_download:
        downloadBrotli()
        downloadLocaleEmulator()
        downloadNtlea()
        downloadCurl()
        downloadOCRModel("ja")
    if not args.skip_build:
        if not args.skip_vc_ltl:
            installVCLTL()
        buildMecab()
        buildWebview()
        buildLocaleRemulator()
        buildLunaHook()
        buildLunaOCR()
        buildMagpie()
        buildPlugins()
    buildLunaTranslator()
