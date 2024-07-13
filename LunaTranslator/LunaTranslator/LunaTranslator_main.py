import sys, windows
import platform, os, time

if __name__ == "__main__":
    _lock = windows.AutoHandle(windows.CreateMutex(False, "LUNA_UPDATER_BLOCK"))
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(dirname)
    windows.addenvpath("./LunaTranslator/runtime/")  # win7 no vcredist2015
    windows.loadlibrary(
        "./LunaTranslator/runtime/PyQt5/Qt5/bin/Qt5Core.dll"
    )  # win7 no vcredist2015

    from myutils.config import _TR, static_data, globalconfig

    sys.path.append("./")
    sys.path.append("./userconfig")

    import gobject

    gobject.overridepathexists()
    from qtsymbols import *

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

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    js = static_data["checkintegrity"]
    flist = js["shared"]
    if platform.architecture()[0] == "64bit":
        flist += js["64"]
    else:
        flist += js["32"]
    collect = []
    for f in flist:
        if os.path.exists(f) == False:
            collect.append(f)
    if len(collect):
        from gui.usefulwidget import getQMessageBox

        getQMessageBox(
            None,
            _TR("错误"),
            _TR("找不到重要组件：")
            + "\n"
            + "\n".join(collect)
            + "\n"
            + _TR("请重新下载并关闭杀毒软件后重试"),
            tr=False,
        )
        os._exit(0)

    from LunaTranslator import MAINUI

    gobject.baseobject = MAINUI()
    gobject.baseobject.checklang()
    gobject.baseobject.loadui()
    app.exit(app.exec())
