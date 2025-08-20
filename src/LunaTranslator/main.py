import sys, os


def dopathexists(file: str):
    import windows

    if not file:
        return False
    if not file.strip():
        return False
    file = windows.check_maybe_unc_file(file)
    if not file:
        return False
    return bool(windows.PathFileExists(os.path.abspath(file)))


originstartfile = os.startfile
originisdir = os.path.isdir
originisfile = os.path.isfile


def doisdir(file: str):
    return dopathexists(file) and originisdir(file)


def doisfile(file: str):
    return dopathexists(file) and originisfile(file)


def safestartfile(f):
    import windows

    # startfile在windows上，有时会谜之把http链接当成exe用run导致崩溃
    windows.ShellExecute(
        None,
        "open",
        f,
        None,
        None,
        windows.SW_SHOWNORMAL,
    )


def overridepathexists():
    # win7上，如果假如没有D盘，然后os.path.exists("D:/...")，就会弹窗说不存在D盘
    # 对于不存在的UNC路径，会先进行网络探测，达到timeout才会返回，导致非常卡顿
    os.path.exists = dopathexists
    os.path.isdir = doisdir
    os.path.isfile = doisfile
    os.startfile = safestartfile


def prepareqtenv():
    import windows
    from gobject import runtime_for_xp, runtimedir

    # 对于如果使用的动态链接的x64_win10版本，由于vc++在14.38->14.40之间破坏了兼容性，
    # 虽然打包版已经正确处理了依赖，不过在测试时，如果先加载Qt则会导致加载Qt自带的14.26vcrt导致NativeUtils内部无法正确初始化
    # 因此如果编译为动态的，测试时必须先加载14.40+vcrt来避免Qt捣乱，这里采用的方法即是预先加载它使其加载系统的vcrt
    # 虽然这个仅是对测试时的问题，不过没有负面影响，因此没问题。
    import NativeUtils

    # pyqt5.15依赖AddDllDirectory来加载Qt，在Win7早期版本上无法成功，导致缺失dll，手动加载Qt可解。
    qtdlls = ("Qt5Core.dll", "Qt5Gui.dll", "Qt5Widgets.dll", "Qt5Svg.dll")
    if not runtime_for_xp:
        qtdir = "{}/PyQt5/Qt5/bin".format(runtimedir)
        if os.path.isdir(qtdir):
            for _ in qtdlls:
                windows.LoadLibrary(os.path.join(qtdir, _))

    from qtsymbols import QApplication, isqt5, Qt, QFont, QLocale

    overridepathexists()

    if isqt5:
        # 中文字符下不能自动加载
        if not runtime_for_xp:
            plgs = "{}/PyQt5/Qt5/plugins".format(runtimedir)
        else:
            plgs = "{}/Lib/site-packages/PyQt5/plugins".format(runtimedir)

        if os.path.exists(plgs):
            QApplication.addLibraryPath(plgs)
        if not runtime_for_xp:
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    if not runtime_for_xp:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    font = QFont()
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    # 必须PreferFullHinting，不能PreferNoHinting，否则阿拉伯语显示不出来
    QApplication.setFont(font)
    QLocale.setDefault(QLocale(QLocale.Language.C, QLocale.Country.AnyCountry))
    # 香港地区数字乱码


def loadmainui(startwithgameuid):
    import gobject
    from LunaTranslator import BASEOBJECT

    gobject.base = BASEOBJECT()
    gobject.base.loadui(startwithgameuid)
    # gobject.base.urlprotocol()


def checklang():

    from myutils.config import globalconfig
    from language import GetUILanguage
    import windows

    if "languageuse2" in globalconfig:
        return
    lang = GetUILanguage(windows.GetLocale())
    globalconfig["languageuse2"] = lang.code
    globalconfig["tgtlang4"] = lang.code


def checkintegrity():
    from myutils.config import _TR
    from qtsymbols import QMessageBox
    from gobject import runtime_for_xp, runtime_for_win10, runtime_bit_64
    import platform, gobject

    dll3264 = [
        "NativeUtils.dll",
        "onnxruntime.dll" if not runtime_for_xp else None,
        "DirectML.dll" if runtime_for_win10 else None,
        "CVUtils.dll",
        "bass.dll",
        "bass_spx.dll",
        "bass_aac.dll",
    ]

    dll3264.append(("libcurl.dll", "libcurl-x64.dll")[runtime_bit_64])

    flist = []
    for f in dll3264:
        if f:
            flist.append(gobject.GetDllpath(f))

    dllshared = [
        "LunaHook/" + ("LunaHost32.dll", "LunaHost64.dll")[runtime_bit_64],
        "shareddllproxy32.exe",
        "shareddllproxy64.exe",
        "Magpie/Magpie.Core.exe" if not runtime_for_xp else None,
        "LunaHook/LunaHook32.dll",
        "LunaHook/LunaHook64.dll",
    ]
    for f in dllshared:
        if f:
            flist.append("files/" + f)
    collect = []
    for f in flist:
        if not os.path.exists(f):
            collect.append(os.path.normpath(os.path.abspath(f)))
    if len(collect):
        QMessageBox.critical(
            None,
            _TR("错误"),
            _TR("找不到重要组件：\n{modules}\n请重新下载并关闭杀毒软件后重试").format(
                modules="\n".join(collect)
            ),
        )
        os._exit(0)


def switchdir():
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(dirname)
    sys.path.insert(1, ".")
    # 0 是当前目录
    # 后面的是系统库或runtime
    # 由于自动更新不会删除，runtime下可能有历史遗留的同名文件被优先导入


def _parseargs():
    import argparse, gobject
    from urllib.parse import urlsplit
    from traceback import print_exc

    parser = argparse.ArgumentParser()
    parser.add_argument("--URLProtocol", required=False)
    parser.add_argument("--Exec", required=False)
    parser.add_argument("--test", required=False, action="store_true")
    parser.add_argument("--userconfig", required=False)
    try:
        args = parser.parse_args()
        URLProtocol: str = args.URLProtocol
        Exec: str = args.Exec
        gobject.istest = args.test
        userconfig = args.userconfig
        gobject.thisuserconfig = userconfig if userconfig else gobject.thisuserconfig
        if URLProtocol:
            print(URLProtocol)
            result = urlsplit(URLProtocol)
            netloc = result.netloc.lower()
            if netloc == "bangumioauth":
                # code=xxx
                bangumioauth = gobject.getcachedir("bangumioauth")
                with open(bangumioauth, "w", encoding="utf8") as ff:
                    ff.write(result.query[5:])
                os._exit(0)
            elif netloc == "exec":
                # lunatranslator://Exec?{gameuid}
                return result.query
        if Exec:
            return Exec
    except Exception:
        print_exc()


def parseargs():
    import gobject

    _ = _parseargs()
    sys.path.insert(1, gobject.thisuserconfig)
    return _


if __name__ == "__main__":
    switchdir()
    startwithgameuid = parseargs()
    prepareqtenv()
    from qtsymbols import QApplication

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)
    checklang()
    checkintegrity()
    loadmainui(startwithgameuid)
    app.exit(app.exec())
    os._exit(0)
