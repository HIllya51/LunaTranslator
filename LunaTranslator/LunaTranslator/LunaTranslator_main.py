import sys, windows
import platform, os

if __name__ == "__main__":
    dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(dirname)
    windows.addenvpath("./LunaTranslator/runtime/")  # win7 no vcredist2015
    windows.loadlibrary(
        "./LunaTranslator/runtime/PyQt5/Qt5/bin/Qt5Core.dll"
    )  # win7 no vcredist2015

    from myutils.config import _TR, static_data, globalconfig

    sys.path.append("./userconfig")
    sys.path.insert(
        0, "./LunaTranslator/network/" + ["winhttp", "libcurl"][globalconfig["network"]]
    )

    from gui.usefulwidget import getQMessageBox
    from LunaTranslator import MAINUI
    import gobject

    gobject.overridepathexists()

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QFont

    QApplication.addLibraryPath(
        "./LunaTranslator/runtime/PyQt5/Qt5/plugins"
    )  # 中文字符下不能自动加载
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    font = QFont()
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
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

    gobject.baseobject = MAINUI()
    gobject.baseobject.checklang()
    gobject.baseobject.aa()
    app.exit(app.exec_())
