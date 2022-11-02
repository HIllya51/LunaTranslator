import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QHBoxLayout,QLineEdit,QFileDialog,QPushButton,QLabel,QColorDialog
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QColor 
import qtawesome
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
            elif arg=='json文件' or arg=='sqlite文件':
                button=QPushButton('选择文件')
                def __(l,_):
                    f=QFileDialog.getOpenFileName(directory= js['args'][arg],filter="*.json" if  arg=='json文件' else "*.sqlite")
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


def getsomepath(object,title,initpath,label,callback,isdir=False,filter1="*.db"):
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle(title)
    #dialog.setWindowModality(Qt.ApplicationModal)
    dialog.resize(QSize(900,10))
    formLayout = QFormLayout(dialog)  # 配置layout 

    hori=QHBoxLayout()
    line=QLineEdit(initpath)
    hori.addWidget(line)
    button=QPushButton('选择路径' if isdir else "选择文件")
    def __(l,_):
        if isdir:
            f=QFileDialog.getExistingDirectory(directory=initpath)
            if f!='':
                l.setText(f)
        else:
            f=QFileDialog.getOpenFileName(directory=initpath,filter=filter1)
            if f[0]!='':
                l.setText(f[0]) 
        
    button.clicked.connect(functools.partial(__,line))
    hori.addWidget(button)
    formLayout.addRow(label, hori) 
    button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
    formLayout.addRow(button)
    dialog.show()

    button.clicked.connect(dialog.accept)

    if dialog.exec() == QDialog.Accepted:
        callback(line.text())

def ChangeTranslateColor(self,button,item) :
        color = QColorDialog.getColor(QColor(globalconfig['cixingcolor'][item]), self, item)
        
    
        button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
        globalconfig['cixingcolor'][item]=color.name() 

def multicolorset(object ):
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle("颜色设置") 
    dialog.resize(QSize(300,10))
    formLayout = QFormLayout(dialog)  # 配置layout 
    _hori=QHBoxLayout()
    l=QLabel("透明度")
    _hori.addWidget(l)
    _s=QSpinBox()
    _s.setValue(globalconfig['showcixing_touming'])
    _s.setMinimum(1)
    _s.setMaximum(100)
    _hori.addWidget(_s)
    formLayout.addRow(_hori)
    _s.valueChanged.connect(lambda x:globalconfig.__setitem__('showcixing_touming',x))
    for k in globalconfig['cixingcolor']:
        hori=QHBoxLayout()
         
        l=QLabel()
        l.setText(k)
         
        hori.addWidget(l)
        
        p=QPushButton(qtawesome.icon("fa.paint-brush", color=globalconfig['cixingcolor'][k]), "" )
        
        p.setIconSize(QSize(20*object.rate,20*object.rate))
         
        p.setStyleSheet("background: transparent;")
        p.clicked.connect(functools.partial(ChangeTranslateColor,dialog,p,k))
        hori.addWidget(p)
        
        formLayout.addRow(hori)
    dialog.show()
     