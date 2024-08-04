import sys, os


def prepareqtenv():
    import windows, gobject

    # win7 no vcredist2015
    windows.addenvpath("./LunaTranslator/runtime/")
    windows.loadlibrary("./LunaTranslator/runtime/PyQt5/Qt5/bin/Qt5Core.dll")

    from qtsymbols import QApplication, isqt5, Qt, QFont, QLocale

    gobject.overridepathexists()

    if isqt5:
        # 中文字符下不能自动加载
        QApplication.addLibraryPath("./LunaTranslator/runtime/PyQt5/Qt5/plugins")
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    if gobject.testuseqwebengine():
        # maybe use qwebengine

        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        if not isqt5:
            # devtool
            QApplication.setAttribute(
                Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings
            )

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


def loadmainui():
    import gobject
    from LunaTranslator import MAINUI

    gobject.baseobject = MAINUI()
    gobject.baseobject.loadui()


def checklang():

    from myutils.config import globalconfig, oldlanguage, loadlangviss
    from qtsymbols import (
        QDialog,
        pyqtSignal,
        Qt,
        QFont,
        QComboBox,
        QVBoxLayout,
        QPushButton,
    )
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
            _, vis = loadlangviss()
            language_listcombox.addItems(vis)
            language_listcombox.currentIndexChanged.connect(
                lambda x: setattr(self, "current", _[x])
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
    if globalconfig["tgtlang4"] == "ja":
        globalconfig["srclang4"] = "zh"


def checkintegrity():
    import platform
    from myutils.config import _TR, static_data
    from qtsymbols import QMessageBox

    js = static_data["checkintegrity"]
    flist = js["shared"]
    if platform.architecture()[0] == "64bit":
        flist += js["64"]
    else:
        flist += js["32"]
    collect = []
    for f in flist:
        if os.path.exists(f) == False:
            collect.append(os.path.normpath(os.path.abspath(f)))
    if len(collect):
        msg = QMessageBox()
        msg.setText(
            _TR("找不到重要组件：")
            + "\n"
            + "\n".join(collect)
            + "\n"
            + _TR("请重新下载并关闭杀毒软件后重试")
        )
        msg.setWindowTitle(_TR("错误"))
        msg.exec()
        os._exit(0)


def checkpermission():
    from myutils.config import _TR
    from qtsymbols import QMessageBox

    try:
        os.makedirs("userconfig", exist_ok=True)
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


if __name__ == "__main__":
    switchdir()
    prepareqtenv()
    from qtsymbols import QApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    checklang()
    checkintegrity()
    checkpermission()
    loadmainui()
    app.exit(app.exec())
