import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QHBoxLayout,QLineEdit,QFileDialog,QPushButton
from PyQt5.QtCore import Qt,QSize
from utils.config import globalconfig,syncconfig
import json
import os
import importlib
def GetUserPlotItems(object,configfile,defaultsetting,title) -> tuple: 
        dialog = QDialog(object)  # 自定义一个dialog
        dialog.setWindowTitle(title)
        #dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(QSize(900,10))
        formLayout = QFormLayout(dialog)  # 配置layout
        d={}
        
        
        if os.path.exists(configfile)==False:
            
            js=defaultsetting
        else:
            with open(configfile,'r',encoding='utf8') as ff:
                js=json.load(ff) 
            syncconfig(js,defaultsetting,True)
        for arg in js['args']:
            hori=QHBoxLayout()
                
            
            line=QLineEdit(js['args'][arg])
            hori.addWidget(line)
            if arg=='路径'   :
                button=QPushButton('选择路径')
                def __(l,_):
                    f=QFileDialog.getExistingDirectory(directory= js['args'][arg])
                    if f!='':
                        l.setText(f)
                button.clicked.connect(functools.partial(__,line))
                hori.addWidget(button)
            elif arg=='json文件':
                button=QPushButton('选择文件')
                def __(l,_):
                    f=QFileDialog.getOpenFileName(directory= js['args'][arg])
                    if f[0]!='':
                        l.setText(f[0])
                button.clicked.connect(functools.partial(__,line))
                hori.addWidget(button)
            d[arg]=line 
            if 'notwriteable' in js and arg in js['notwriteable']:
                line.setReadOnly(True) 
            
            formLayout.addRow(arg, hori) 
        button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        formLayout.addRow(button)
        dialog.show()

        button.clicked.connect(dialog.accept)

        if dialog.exec() == QDialog.Accepted:
            for arg in js['args']:
                js['args'][arg]=d[arg].text()
            with open(configfile,'w',encoding='utf8') as ff:
                ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
def getlepath(object) -> tuple: 
        dialog = QDialog(object)  # 自定义一个dialog
        dialog.setWindowTitle('LocaleEmulator 路径')
        #dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(QSize(900,10))
        formLayout = QFormLayout(dialog)  # 配置layout
        d={}
 
        hori=QHBoxLayout()
        line=QLineEdit(globalconfig['LocaleEmulator'])
        hori.addWidget(line)
        button=QPushButton('选择路径')
        def __(l,_):
            f=QFileDialog.getExistingDirectory(directory= globalconfig['LocaleEmulator'])
            if f!='':
                l.setText(f)
        button.clicked.connect(functools.partial(__,line))
        hori.addWidget(button)
        formLayout.addRow('LocaleEmulator:', hori) 
        button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        formLayout.addRow(button)
        dialog.show()

        button.clicked.connect(dialog.accept)

        if dialog.exec() == QDialog.Accepted:
            globalconfig['LocaleEmulator']=line.text()
             