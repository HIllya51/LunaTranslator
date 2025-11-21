import os, sys, re
import shutil
import subprocess, time
import hashlib

rootDir = os.path.dirname(__file__)
if not rootDir:
    rootDir = os.path.abspath(".")
else:
    rootDir = os.path.abspath(rootDir)
rootthisfiledir = rootDir


absthisfile = os.path.join(rootthisfiledir, os.path.basename(__file__))

rootDir = os.path.abspath(os.path.join(rootDir, ".."))

originmakedirs = os.makedirs


def fuckmakedirs(*a, **kw):
    try:
        originmakedirs(*a, **kw)
    except:
        pass


os.makedirs = fuckmakedirs


def fuckmove(src, tgt):
    print(src, tgt)
    try:
        shutil.move(src, tgt)
    except:
        try:
            shutil.copy(src, tgt)
        except:
            shutil.copytree(src, tgt)


pluginDirs = ["DLL32", "DLL64"]

localeEmulatorFile = "https://github.com/xupefei/Locale-Emulator/releases/download/v2.5.0.1/Locale.Emulator.2.5.0.1.zip"
LocaleRe = "https://github.com/InWILL/Locale_Remulator/releases/download/v1.6.0/Locale_Remulator.1.6.0.zip"

curlFile32xp = "https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator_x86_winxp.zip"  # "https://web.archive.org/web/20220101212640if_/https://curl.se/windows/dl-7.80.0/curl-7.80.0-win32-mingw.zip"
curlFile32 = "https://curl.se/windows/dl-8.8.0_3/curl-8.8.0_3-win32-mingw.zip"
curlFile64 = "https://curl.se/windows/dl-8.8.0_3/curl-8.8.0_3-win64-mingw.zip"

availableLocales = ["cht", "en", "ja", "ko", "ru", "zh"]


def createPluginDirs():
    os.chdir(rootDir + "\\files")
    for pluginDir in pluginDirs:
        if not os.path.exists(pluginDir):
            os.mkdir(pluginDir)
    os.chdir(rootDir)


def move_directory_contents(source_dir, destination_dir):
    contents = os.listdir(source_dir)

    for item in contents:
        if item == ".git":
            continue
        item_path = os.path.join(source_dir, item)
        try:
            fuckmove(item_path, destination_dir)
        except:
            for k in os.listdir(item_path):
                fuckmove(
                    os.path.join(item_path, k), os.path.join(destination_dir, item)
                )


def downloadmapie():
    os.chdir(f"{rootDir}/scripts/temp")
    subprocess.run(
        f"curl -C - -LO https://github.com/HIllya51/Magpie/releases/download/common/magpie.zip"
    )
    subprocess.run(f"7z x -y magpie.zip")
    os.chdir(rootDir)
    os.rename("scripts/temp/Magpie", "files/Magpie")


def downloadlr():

    os.chdir(f"{rootDir}/scripts/temp")
    subprocess.run(f"curl -C - -LO {LocaleRe}")
    base = LocaleRe.split("/")[-1]
    fn = os.path.splitext(base)[0]
    subprocess.run(f"7z x -y {base}")
    os.chdir(rootDir)
    os.makedirs("files/Locale/Locale_Remulator")

    for f in [
        "LRHookx64.dll",
        "LRHookx32.dll",
        # "LRConfig.xml",
        "LRProc.exe",
        "LRSubMenus.dll",
    ]:
        fuckmove(os.path.join("scripts/temp", fn, f), "files/Locale/Locale_Remulator")


def downloadLocaleEmulator():
    os.chdir(f"{rootDir}/scripts/temp")
    subprocess.run(f"curl -C - -LO {localeEmulatorFile}")
    subprocess.run(f"7z x -y {localeEmulatorFile.split('/')[-1]} -oLocaleEmulator")

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
        os.chdir(rootDir)
        os.makedirs("files/Locale/Locale.Emulator")
        fuckmove(
            os.path.join("scripts/temp/LocaleEmulator", f),
            "files/Locale/Locale.Emulator",
        )


def downloadNtlea():
    os.chdir(f"{rootDir}/scripts/temp")
    ntleaFile = (
        "https://github.com/zxyacb/ntlea/releases/download/0.46/ntleas046_x64.7z"
    )
    subprocess.run(f"curl -C - -LO {ntleaFile}")
    subprocess.run(f"7z x -y {ntleaFile.split('/')[-1]} -ontlea")

    os.chdir(rootDir)
    os.makedirs("files/Locale/ntleas046_x64")
    shutil.copytree("scripts/temp/ntlea/x86", "files/Locale/ntleas046_x64/x86")
    shutil.copytree("scripts/temp/ntlea/x64", "files/Locale/ntleas046_x64/x64")


def downloadCurl(target):
    if target == "winxp":
        os.chdir(f"{rootDir}/scripts/temp")
        subprocess.run(f"curl -C - -LO {curlFile32xp}")
        subprocess.run(f"7z x -y {curlFile32xp.split('/')[-1]}")
        os.chdir(rootDir)
        outputDirName32 = curlFile32xp.split("/")[-1].replace(".zip", "")
        # fuckmove(f"scripts/temp/{outputDirName32}/bin/libcurl.dll", "files/DLL32")
        for _dir, _, _fs in os.walk(f"scripts/temp/{outputDirName32}"):
            for _f in _fs:
                if _f == "libcurl.dll":
                    shutil.move(os.path.join(_dir, _f), "files/DLL32")
        return
    os.chdir(f"{rootDir}/scripts/temp")
    subprocess.run(f"curl -C - -LO {curlFile32}")
    subprocess.run(f"curl -C - -LO {curlFile64}")
    subprocess.run(f"7z x -y {curlFile32.split('/')[-1]}")
    subprocess.run(f"7z x -y {curlFile64.split('/')[-1]}")
    os.chdir(rootDir)
    outputDirName32 = curlFile32.split("/")[-1].replace(".zip", "")
    fuckmove(f"scripts/temp/{outputDirName32}/bin/libcurl.dll", "files/DLL32")
    outputDirName64 = curlFile64.split("/")[-1].replace(".zip", "")
    fuckmove(f"scripts/temp/{outputDirName64}/bin/libcurl-x64.dll", "files/DLL64")


def downloadOCRModel():
    os.chdir(rootDir + "\\files")
    if not os.path.exists("ocrmodel"):
        os.mkdir("ocrmodel/")
    link = "https://lunatranslator.org/r2/luna/ocr_models_v5/jazhchten.zip"
    os.chdir("ocrmodel")
    __ = hashlib.md5(link.encode()).hexdigest()
    os.makedirs(__)
    os.chdir(__)
    subprocess.run(f"curl -C - -LO {link}")
    subprocess.run(f"7z x -y jazhchten.zip")
    with open("jazhchten.zip", "rb") as ff:
        md5 = hashlib.md5(ff.read()).hexdigest()
    os.remove(f"jazhchten.zip")
    os.chdir("..")
    os.rename(__, md5)
    os.chdir(rootDir)


def buildhook(arch, target):

    os.chdir("NativeImpl/LunaHook")
    archA = ("win32", "x64")[arch == "x64"]
    vsver = "Visual Studio 17 2022"
    Tool = "v141_xp" if target == "winxp" else f"host={arch}"
    if target == "win10":
        config = "-DWIN10ABOVE=ON"
    elif target == "win7":
        config = "-DWIN10ABOVE=OFF"
    elif target == "winxp":
        config = "-DWINXP=ON -DWIN10ABOVE=OFF"
    subprocess.run(
        f'cmake {config} -DBUILD_HOST=OFF ./CMakeLists.txt -G "{vsver}" -A {archA} -T {Tool} -B ./build/{arch}_{target}_2'
    )
    subprocess.run(
        f"cmake --build ./build/{arch}_{target}_2 --config Release --target ALL_BUILD -j {os.cpu_count()}"
    )
    if target != "win10":
        config += " -DUSE_VC_LTL=ON "
    subprocess.run(
        f'cmake {config} -DBUILD_HOOK=OFF ./CMakeLists.txt -G "{vsver}" -A {archA} -T {Tool} -B ./build/{arch}_{target}_1'
    )
    subprocess.run(
        f"cmake --build ./build/{arch}_{target}_1 --config Release --target ALL_BUILD -j {os.cpu_count()}"
    )
    release = os.path.join("builds", os.listdir("builds")[0])
    os.makedirs("builds/Release")
    for f in os.listdir(release):
        shutil.move(os.path.join(release, f), "builds/Release")
    shutil.rmtree(release)


def buildPlugins(arch, target, configx="", sexe=False):
    os.chdir(rootDir + "/NativeImpl")
    archA = ("win32", "x64")[arch == "x64"]
    if target == "win10":
        config = "-DWIN10ABOVE=ON"
    elif target == "win7":
        config = "-DWIN10ABOVE=OFF"
    elif target == "winxp":
        config = "-DWINXP=ON -DWIN10ABOVE=OFF"
    sysver = " -DCMAKE_SYSTEM_VERSION=10.0.26621.0 "
    vsver = "Visual Studio 17 2022"
    Tool = "v141_xp" if target == "winxp" else f"host={arch}"

    if arch == "x86" and target == "win10":
        # 对于64位会使用自带的vcrt，win7/xp会静态编译，仅win10 shareddllproxy32这个文件可能会缺少vcrt，因此把它也静态编译以避免无法运行导致注入失败。
        config += " -DSTATIC_FORCE=ON"
    config += configx
    if sexe:
        config += " -DBUILD_S_EXE_ONLY=ON"
    subprocess.run(
        f'cmake {config} ./CMakeLists.txt -G "{vsver}" -A {archA} -T {Tool} -B ./build/{arch}_{target} {sysver}'
    )
    subprocess.run(
        f"cmake --build ./build/{arch}_{target} --config Release --target ALL_BUILD -j {os.cpu_count()}"
    )
    for _dir, _, _fs in os.walk("builds"):
        print(_dir, _fs)
        for _f in _fs:
            ff = os.path.join(_dir, _f)
            if os.path.splitext(ff)[1].lower() not in (".dll", ".exe"):
                os.remove(ff)
    os.chdir(rootDir)


def downloadbass():

    for link in (
        "https://www.un4seen.com/files/bass24.zip",
        "https://www.un4seen.com/files/z/2/bass_spx24.zip",
        "https://www.un4seen.com/files/z/2/bass_aac24.zip",
        "https://www.un4seen.com/files/bassopus24.zip",
        "https://www.un4seen.com/files/bassenc24.zip",
        "https://www.un4seen.com/files/bassenc_mp324.zip",
        "https://www.un4seen.com/files/bassenc_opus24.zip",
    ):
        os.chdir(f"{rootDir}/scripts/temp")
        name = link.split("/")[-1]
        d = name.split(".")[0]
        subprocess.run("curl -C - -LO " + link)
        subprocess.run(f"7z x -y {name} -o{d}")
        os.chdir(rootDir)
        fuckmove(f"scripts/temp/{d}/{d[:-2]}.dll", "files/DLL32")
        fuckmove(f"scripts/temp/{d}/x64/{d[:-2]}.dll", "files/DLL64")


def downloadalls(target):
    os.chdir(rootDir)
    os.makedirs("scripts/temp")
    createPluginDirs()
    downloadNtlea()
    downloadbass()
    downloadCurl(target)
    downloadLocaleEmulator()
    downloadlr()
    if target == "winxp":
        return
    downloadmapie()
    downloadOCRModel()


if __name__ == "__main__":
    os.chdir(rootDir)

    if sys.argv[1] == "download":
        downloadalls(sys.argv[2] if len(sys.argv) >= 3 else "")
    elif sys.argv[1] == "loadversion":
        with open("NativeImpl/version.cmake", "r", encoding="utf8") as ff:
            pattern = r"set\(VERSION_MAJOR\s*(\d+)\s*\)\nset\(VERSION_MINOR\s*(\d+)\s*\)\nset\(VERSION_PATCH\s*(\d+)\s*\)\nset\(VERSION_REVISION\s*(\d+)\s*\)"
            match = re.findall(pattern, ff.read())[0]
            version_major, version_minor, version_patch, version_revison = match
            versionstring = f"v{version_major}.{version_minor}.{version_patch}"
            if int(version_revison):
                versionstring += f".{version_revison}"
            print("version=" + versionstring)
            exit()
    elif sys.argv[1] == "cpp":
        if sys.argv[-1] != "0":
            argv = sys.argv.copy()
            argv.append("0")
            argv[0] = absthisfile
            if argv[3] == "winxp":
                argv[2] = "x86"
                argv.insert(len(argv) - 1, "0")
                subprocess.run([sys.executable, *argv])
                argv[2] = "x64"
                argv[3] = "win7"
                argv.insert(len(argv) - 1, "1")
                subprocess.run([sys.executable, *argv])
            elif argv[3] == "win10" or argv[3] == "win7":
                argv[2] = "x86"
                argv.insert(len(argv) - 1, str(int(argv[2] == sys.argv[2])))
                subprocess.run([sys.executable, *argv])
                argv[2] = "x64"
                argv.insert(len(argv) - 1, str(int(argv[2] == sys.argv[2])))
                subprocess.run([sys.executable, *argv])
            exit(0)
        buildPlugins(sys.argv[2], sys.argv[3], sexe=int(sys.argv[4]))
    elif sys.argv[1] == "hook":
        if sys.argv[-1] != "0":
            argv = sys.argv.copy()
            argv.append("0")
            argv[0] = absthisfile
            if argv[3] == "winxp":
                argv[2] = "x86"
                subprocess.run([sys.executable, *argv])
                argv[2] = "x64"
                argv[3] = "win7"
                subprocess.run([sys.executable, *argv])
            elif argv[3] == "win10" or argv[3] == "win7":
                argv[2] = "x86"
                subprocess.run([sys.executable, *argv])
                argv[2] = "x64"
                subprocess.run([sys.executable, *argv])
            exit(0)
        buildhook(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "pyrt":
        arch = sys.argv[2]
        pythonversion = sys.argv[3]
        target = sys.argv[4]
        py37Path = (
            f"C:\\hostedtoolcache\\windows\\Python\\{pythonversion}\\{arch}\\python.exe"
        )
        os.chdir(rootDir)
        subprocess.run(f"{py37Path} -m pip install --upgrade pip")
        if 1:  # target == "win7":
            subprocess.run(f"{py37Path} -m pip install tinycss2 PyQt5")
        else:
            subprocess.run(f"{py37Path} -m pip install tinycss2 pyqt6")

        # 3.8之后会莫名其妙引用这个b东西，然后这个b东西会把一堆没用的东西导入进来
        shutil.rmtree(os.path.join(os.path.dirname(py37Path), "Lib\\test"))
        shutil.rmtree(os.path.join(os.path.dirname(py37Path), "Lib\\unittest"))
        # 放弃，3.8需要安装KB2533623才能运行，3.7用不着。
        subprocess.run(
            f"{py37Path} {os.path.join(rootthisfiledir,'collectpyruntime.py')} {target}"
        )
    elif sys.argv[1] == "merge":
        arch = sys.argv[2]
        target = sys.argv[3]
        downloadalls(target)

        os.chdir(rootDir)
        if target == "winxp":
            shutil.copytree("NativeImpl/LunaHook/builds/Release_win7", "files/LunaHook")
            shutil.copytree(
                "NativeImpl/LunaHook/builds/Release_winxp", "files/LunaHook"
            )
            os.remove("files/LunaHook/LunaHost64.dll")
            os.makedirs("files/DLL32")
            shutil.copy("NativeImpl/builds/_x86_winxp/shareddllproxy32.exe", "files")
            shutil.copy("NativeImpl/builds/_x64_win7/shareddllproxy64.exe", "files")
            os.system(f"robocopy NativeImpl/builds/_x86_winxp files/DLL32 *.dll")
            os.system(
                f"python {os.path.join(rootthisfiledir,'collectall.py')} {arch} {target}"
            )
            exit()
        shutil.copytree(
            f"NativeImpl/LunaHook/builds/Release_{target}", "files/LunaHook"
        )
        shutil.copytree(f"NativeImpl/builds/_x64_{target}", "NativeImpl/builds")
        shutil.copytree(f"NativeImpl/builds/_x86_{target}", "NativeImpl/builds")
        os.makedirs("files/DLL32")
        shutil.copy(f"NativeImpl/builds/_x86_{target}/shareddllproxy32.exe", "files")
        os.system(f"robocopy NativeImpl/builds/_x86_{target} files/DLL32 *.dll")
        os.makedirs("files/DLL64")
        shutil.copy(f"NativeImpl/builds/_x64_{target}/shareddllproxy64.exe", "files")
        os.system(f"robocopy NativeImpl/builds/_x64_{target} files/DLL64 *.dll")

        if arch == "x86":
            os.remove(f"files/LunaHook/LunaHost64.dll")
        else:
            os.remove("files/LunaHook/LunaHost32.dll")
        os.system(
            f"python {os.path.join(rootthisfiledir,'collectall.py')} {arch} {target}"
        )
