import sys, os


def prepareqtenv():
    import windows, gobject

    # win7 no vcredist2015
    windows.addenvpath("./LunaTranslator/runtime/")
    windows.loadlibrary("./LunaTranslator/runtime/PyQt5/Qt5/bin/Qt5Core.dll")

    from qtsymbols import QApplication, isqt5, Qt, QFont

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


def loadmainui():
    import gobject
    from LunaTranslator import MAINUI

    gobject.baseobject = MAINUI()
    gobject.baseobject.loadui()


def checklang():

    from myutils.config import globalconfig, loadlanguage, static_data
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

        def __init__(self, language_list):

            super(languageset, self).__init__(None, Qt.WindowType.WindowStaysOnTopHint)
            self.setWindowIcon(qtawesome.icon("fa.language"))
            self.setMinimumSize(400, 100)
            self.setWindowTitle("语言设置 LanguageSetting")
            font = QFont()
            font.setFamily("Arial")
            font.setPointSize(20)
            self.setFont(font)
            self.current = 0
            language_listcombox = QComboBox()
            language_listcombox.addItems(language_list)
            language_listcombox.currentIndexChanged.connect(
                lambda x: setattr(self, "current", x)
            )
            vb = QVBoxLayout(self)

            vb.addWidget(language_listcombox)
            bt = QPushButton("OK")
            vb.addWidget(bt)
            bt.clicked.connect(self.accept)

    if globalconfig["language_setted_2.4.5"] == False:

        x = languageset(static_data["language_list_show"])
        x.exec()
        globalconfig["language_setted_2.4.5"] = True
        globalconfig["languageuse"] = x.current
        globalconfig["tgtlang3"] = x.current
        loadlanguage()


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


def switchdir():
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(dirname)
    sys.path.append("./")
    sys.path.append("./userconfig")


if __name__ == "__main__":
    switchdir()
    prepareqtenv()
    from qtsymbols import QApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    checklang()
    checkintegrity()
    loadmainui()
    app.exit(app.exec())
