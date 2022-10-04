from distutils.command.config import config
import functools 
 
from cmath import exp
import functools
from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QTextEdit
import qtawesome
from PyQt5.QtCore import QThread
import subprocess
from utils.config import globalconfig ,postprocessconfig
from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox,QDoubleSpinBox 
 
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton,QColorDialog
from PyQt5.QtGui import QColor,QFont
import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QSpinBox,QVBoxLayout,QLineEdit
from PyQt5.QtCore import Qt,QSize
from utils.config import globalconfig 
import qtawesome
from utils.config import globalconfig 

import importlib
from gui.inputdialog import GetUserPlotItems
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab7(self) :
     
        self.tab_7 = QWidget()
        self.tab_widget.addTab(self.tab_7, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_7), " 后处理设置")

        
        initpostswitchs_auto(self)
def initpostswitchs_auto(self):
        num=0
        
        for post in postprocessconfig:
            y=70+40*num
            x=20
            #print(post)
            initpostswitchs(self,post,(x, y, 270, 20),(x+270, y, 20,20),1,(x+300, y, 20,20))
            num+=1

def initpostswitchs(self,name,namepos,switchpos,colorpos,settingpos):

        label = QLabel(self.tab_7)
        self.customSetGeometry(label, *namepos)
        label.setText(postprocessconfig[name]['name']+":")
        p=gui.switchbutton.MySwitch(self.tab_7, sign=postprocessconfig[name]['use'], textOff='关闭',textOn='使用')
        
        self.customSetGeometry(p, *switchpos)
        def fanyiselect( who,checked):
            if checked : 
                postprocessconfig[who]['use']=True  
            else:
                postprocessconfig[who]['use']=False 
        p.clicked.connect(functools.partial( fanyiselect,name)) 
        
        if 'args' in postprocessconfig[name]:
            s1 = QPushButton( "", self.tab_7)
            self.customSetIconSize(s1, 20, 20)
            self.customSetGeometry(s1, *settingpos)
            s1.setStyleSheet("background: transparent;")   
            s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
            s1.clicked.connect(lambda x:postconfigdialog(self,postprocessconfig[name]['args'],postprocessconfig[name]['name']+'设置'))

def postconfigdialog(object,configdict,title):
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle(title)
    #dialog.setWindowModality(Qt.ApplicationModal)
    dialog.resize(QSize(400,1))
    formLayout = QVBoxLayout(dialog)  # 配置layout
     
    key=list(configdict.keys())[0]
    lb=QLabel(dialog)
    lb.setText(key) 
    formLayout.addWidget(lb) 
    if type(configdict[key])==type(1): 
        spin=QSpinBox(dialog)
        spin.setMinimum(0)
        spin.setMaximum(100)
        spin.setValue(configdict[key])
        spin.valueChanged.connect(lambda x:configdict.__setitem__(key,x))
        formLayout.addWidget(spin)
    elif type(configdict[key])==type([]): 
        lines=QTextEdit(dialog)
        lines.setPlainText('\n'.join(configdict[key]))
        lines.textChanged.connect(lambda   :configdict.__setitem__(key,lines.toPlainText().split('\n')))
        formLayout.addWidget(lines)
    dialog.show()
 