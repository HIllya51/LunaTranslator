from qtsymbols import *

# 这个可能在加载c++环境之前被调用，所以必须不能有那些复杂的依赖


def RichMessageBox(parent, title, text: str, iserror=True, iswarning=False):
    b = QMessageBox(parent)
    icon = (
        QMessageBox.Icon.Critical
        if iserror
        else (QMessageBox.Icon.Warning if iswarning else QMessageBox.Icon.Information)
    )
    b.setIcon(icon)
    b.setWindowTitle(title)
    b.setText(text.replace("\n", "<br>"))
    b.setTextFormat(Qt.TextFormat.RichText)
    return b.exec()
