from qtsymbols import *
from gui.fluent.messagebox import ExMessageBox

# 这个可能在加载c++环境之前被调用，所以必须不能有那些复杂的依赖


def RichMessageBox(
    parent, title, text: str, iserror=True, iswarning=False, isQuestion=False
):
    icon = (
        QMessageBox.Icon.Critical
        if iserror
        else (
            QMessageBox.Icon.Warning
            if iswarning
            else (
                QMessageBox.Icon.Question
                if isQuestion
                else QMessageBox.Icon.Information
            )
        )
    )
    buttons = (
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        if isQuestion
        else QMessageBox.StandardButton.Ok
    )
    b = ExMessageBox(icon, title, text.replace("\n", "<br>"), buttons, parent)
    b.setTextFormat(Qt.TextFormat.RichText)
    return b.exec()
