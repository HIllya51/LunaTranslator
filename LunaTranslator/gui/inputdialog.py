from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QHBoxLayout,QLineEdit
from PyQt5.QtCore import Qt,QSize
from utils.config import globalconfig
import json
import os
import importlib
def GetUserPlotItems(object,configfile,defaultsetting,title) -> tuple: 
        dialog = QDialog(object)  # 自定义一个dialog
        dialog.setWindowTitle(title)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(QSize(900,10))
        formLayout = QFormLayout(dialog)  # 配置layout
        d={}
 
        if os.path.exists(configfile)==False:
            
            js=defaultsetting
        else:
            with open(configfile,'r',encoding='utf8') as ff:
                js=json.load(ff)
        for arg in js['args']:
             
            line=QLineEdit(js['args'][arg])
            d[arg]=line 
            if 'notwriteable' in js and arg in js['notwriteable']:
                line.setReadOnly(True) 
            formLayout.addRow(arg, line) 
        button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        formLayout.addRow(button)
        dialog.show()

        button.clicked.connect(dialog.accept)

        if dialog.exec() == QDialog.Accepted:
            for arg in js['args']:
                js['args'][arg]=d[arg].text()
            with open(configfile,'w',encoding='utf8') as ff:
                ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
