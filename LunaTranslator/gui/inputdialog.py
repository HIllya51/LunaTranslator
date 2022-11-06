import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QHBoxLayout,QLineEdit,QFileDialog,QPushButton,QLabel,QColorDialog
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QColor 
import qtawesome
from utils.config import globalconfig,syncconfig
import json
import os 
def autoinitdialog(object,title,width,lines):
    dialog=QDialog(object)
    dialog.setWindowTitle(title)
    dialog.resize(QSize(width,10))
    formLayout = QFormLayout()
    dialog.setLayout(formLayout)
    regist=[]
    def save(callback=None):
        for l in regist:
            l[0][l[1]]=l[2].text() 
        dialog.close()
        if callback:
            callback()
    def openfiledirectory(edit,isdir,filter1='*.*'):
        if isdir:
            f=QFileDialog.getExistingDirectory(directory= edit.text())
            res=f
        else:
            f=QFileDialog.getOpenFileName(directory= edit.text(),filter=filter1)
            res=f[0]
        if res!='':
            edit.setText(res)
    for line in lines:
        if line['t']=='okcancel':
            button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel) 
            formLayout.addRow(button)
            button.rejected.connect(dialog.close)
            button.accepted.connect(functools.partial(save,None if 'callback' not in line else line['callback']))

            button.button(QDialogButtonBox.Ok).setText('保存并关闭')
            button.button(QDialogButtonBox.Cancel).setText('取消')
        elif line['t']=='lineedit':   
            dd=line['d']
            key=line['k'] 
            e=QLineEdit(dd[key])
            regist.append([dd,key,e])  
            formLayout.addRow((line['l']),e)
        elif line['t']=='file': 
            dd=line['d']
            key=line['k'] 
            e=QLineEdit(dd[key])
            regist.append([dd,key,e])  
            bu=QPushButton('选择'+('文件夹' if line['dir'] else '文件')  )
            bu.clicked.connect(functools.partial(openfiledirectory,e,line['dir'],'' if line['dir'] else line['filter']  ))
            hori=QHBoxLayout()
            hori.addWidget(e)
            hori.addWidget(bu)
            formLayout.addRow((line['l']),hori)
    dialog.show()
 
def getsomepath1(object,title,d,k,label,callback=None,isdir=False,filter1="*.db"):
    autoinitdialog(object,title,900,[ 
                                {'t':'file','l':label,'d':d,'k':k,'dir':isdir,'filter':filter1}, 
                                {'t':'okcancel','callback':callback},
                                ])

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
     