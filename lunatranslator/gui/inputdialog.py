from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QHBoxLayout,QLineEdit
from PyQt5.QtCore import Qt,QSize
from utils.config import globalconfig
def GetUserPlotItems(object,name) -> tuple: 
        dialog = QDialog(object)  # 自定义一个dialog
        dialog.setWindowTitle(globalconfig['fanyi'][name]['name']+'设置')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(QSize(400,10))
        formLayout = QFormLayout(dialog)  # 配置layout
        d={}
        for arg in globalconfig['fanyi'][name]['args']:
             
            line=QLineEdit(globalconfig['fanyi'][name]['args'][arg])
            d[arg]=line 
            if 'notwriteable' in globalconfig['fanyi'][name] and arg in globalconfig['fanyi'][name]['notwriteable']:
                line.setReadOnly(True) 
            formLayout.addRow(arg, line) 
        button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        formLayout.addRow(button)
        dialog.show()

        button.clicked.connect(dialog.accept)

        if dialog.exec() == QDialog.Accepted:
            for arg in globalconfig['fanyi'][name]['args']:
                globalconfig['fanyi'][name]['args'][arg]=d[arg].text()
            pass