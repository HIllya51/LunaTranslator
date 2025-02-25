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
    from myutils.config import get_platform

    # win7 no vcredist2015
    windows.addenvpath("./files/runtime/")
    if get_platform() != "xp":
        windows.LoadLibraryW("./files/runtime/PyQt5/Qt5/bin/Qt5Core.dll")
    else:
        windows.addenvpath("./files/runtime/Lib/site-packages/PyQt5")
        windows.LoadLibraryW("./files/runtime/Lib/site-packages/PyQt5/Qt5Core.dll")

    from qtsymbols import QApplication, isqt5, Qt, QFont, QLocale

    overridepathexists()

    if isqt5:
        # 中文字符下不能自动加载
        if get_platform() != "xp":
            plgs = "./files/runtime/PyQt5/Qt5/plugins"
        else:
            plgs = "./files/runtime/Lib/site-packages/PyQt5/plugins"

        if os.path.exists(plgs):
            QApplication.addLibraryPath(plgs)
        if get_platform() != "xp":
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    if get_platform() != "xp":
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
    from LunaTranslator import MAINUI

    gobject.baseobject = MAINUI()
    gobject.baseobject.loadui(startwithgameuid)
    # gobject.baseobject.urlprotocol()


def checklang():

    from myutils.config import globalconfig, oldlanguage, static_data
    from qtsymbols import (
        QDialog,
        pyqtSignal,
        Qt,
        QFont,
        QComboBox,
        QVBoxLayout,
        QPushButton,
    )
    from language import UILanguages
    import qtawesome

    class languageset(QDialog):
        getnewsentencesignal = pyqtSignal(str)
        getnewtranssignal = pyqtSignal(str, str)
        showsignal = pyqtSignal()

        def __init__(self):

            super(languageset, self).__init__(None, Qt.WindowType.WindowStaysOnTopHint)
            self.setWindowIcon(qtawesome.icon("fa.language"))
            self.setMinimumSize(400, 100)
            self.setWindowTitle("语言设置 LanguageSetting")
            font = QFont()
            font.setFamily("Arial")
            font.setPointSize(20)
            self.setFont(font)
            self.current = "zh"
            language_listcombox = QComboBox()
            inner, vis = [_.code for _ in UILanguages], [
                _.nativename for _ in UILanguages
            ]
            language_listcombox.addItems(vis)
            language_listcombox.currentIndexChanged.connect(
                lambda x: setattr(self, "current", inner[x])
            )
            vb = QVBoxLayout(self)

            vb.addWidget(language_listcombox)
            bt = QPushButton("OK")
            vb.addWidget(bt)
            bt.clicked.connect(self.accept)

    if "languageuse2" in globalconfig:
        return
    if globalconfig["language_setted_2.4.5"]:
        # 新版改成新的index无关的语言设置
        globalconfig["languageuse2"] = oldlanguage[globalconfig["languageuse"]]
        globalconfig["tgtlang4"] = oldlanguage[globalconfig["tgtlang3"]]
        globalconfig["srclang4"] = oldlanguage[globalconfig["srclang3"]]
        return
    x = languageset()
    x.exec()
    globalconfig["language_setted_2.4.5"] = True
    globalconfig["languageuse2"] = x.current
    globalconfig["tgtlang4"] = x.current


def checkintegrity():
    from myutils.config import _TR, static_data, get_platform
    from qtsymbols import QMessageBox

    js = static_data["checkintegrity"]
    flist = js["shared"]
    plat = get_platform()
    if plat == "xp":
        flist = js["xp"]
    else:
        flist += js[plat]
    collect = []
    for f in flist:
        if os.path.exists(f) == False:
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


def checkpermission():
    from myutils.config import _TR, saveallconfig
    from qtsymbols import QMessageBox

    try:
        saveallconfig(test=True)
        # 先写一遍试试，免得到最后配置半天白瞎。
    except PermissionError:
        msg = QMessageBox()
        msg.setText(_TR("权限不足，请以管理员权限运行！"))
        msg.setWindowTitle(_TR("错误"))
        msg.exec()
        os._exit(0)


def switchdir():
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(dirname)
    sys.path.insert(1, "./")
    sys.path.insert(1, "./userconfig")
    # 0 是当前目录
    # 后面的是系统库或runtime
    # 由于自动更新不会删除，runtime下可能有历史遗留的同名文件被优先导入
    import shutil

    # 远古版本的遗留文件，同名导入冲突
    try:
        shutil.rmtree("./LunaTranslator/requests")
    except:
        pass


def urlprotocol():
    import argparse, gobject, sys
    from urllib.parse import urlsplit
    from traceback import print_exc

    parser = argparse.ArgumentParser()
    parser.add_argument("--URLProtocol", required=False)
    parser.add_argument("--Exec", required=False)
    try:
        args = parser.parse_args()
        URLProtocol: str = args.URLProtocol
        Exec: str = args.Exec
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


if __name__ == "__main__":
    switchdir()
    prepareqtenv()
    from qtsymbols import QApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    checklang()
    checkintegrity()
    checkpermission()
    loadmainui(urlprotocol())
    app.exit(app.exec())
