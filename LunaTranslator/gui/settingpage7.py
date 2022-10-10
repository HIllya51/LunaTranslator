from distutils.command.config import config
import functools 
 
from cmath import exp
import functools

from PyQt5.QtWidgets import QApplication, QWidget, QTableView, QAbstractItemView, QLabel, QVBoxLayout

from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QTextEdit

from PyQt5.QtGui import QStandardItem, QStandardItemModel
import qtawesome
from PyQt5.QtCore import QThread
import subprocess
from utils.config import globalconfig ,postprocessconfig,noundictconfig,transerrorfixdictconfig
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
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_7), " 翻译预处理")

        
        initpostswitchs_auto(self)
def initpostswitchs_auto(self):
        num=0
        
        for post in postprocessconfig:
            y=10+40*num
            x=20
            #print(post)
            initpostswitchs(self,post,(x, y, 270, 20),(x+270, y, 20,20),1,(x+300, y, 20,20))
            num+=1

        x=20
        y=300
        initdictswitchs(self,(x, y, 270, 20),(x+270, y, 20,20),1,(x+300, y, 20,20))
        y+=40
        initdictswitchs2(self,(x, y, 270, 20),(x+270, y, 20,20),1,(x+300, y, 20,20))
def initdictswitchs(self,namepos,switchpos,colorpos,settingpos):
    label = QLabel(self.tab_7)
    self.customSetGeometry(label, *namepos)
    label.setText("使用专有名词翻译:")
    p=gui.switchbutton.MySwitch(self.tab_7, sign=noundictconfig['use'] )
    
    self.customSetGeometry(p, *switchpos) 
    p.clicked.connect(lambda x:noundictconfig.__setitem__('use',x)) 
    
    s1 = QPushButton( "", self.tab_7)
    self.customSetIconSize(s1, 20, 20)
    self.customSetGeometry(s1, *settingpos)
    s1.setStyleSheet("background: transparent;")   
    s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
    s1.clicked.connect(lambda x:noundictconfigdialog(self,noundictconfig,'专有名词翻译设置'))
def initdictswitchs2(self,namepos,switchpos,colorpos,settingpos):
    label = QLabel(self.tab_7)
    self.customSetGeometry(label, *namepos)
    label.setText("使用翻译结果修正")
    p=gui.switchbutton.MySwitch(self.tab_7, sign=transerrorfixdictconfig['use'] )
    
    self.customSetGeometry(p, *switchpos) 
    p.clicked.connect(lambda x:transerrorfixdictconfig.__setitem__('use',x)) 
    
    s1 = QPushButton( "", self.tab_7)
    self.customSetIconSize(s1, 20, 20)
    self.customSetGeometry(s1, *settingpos)
    s1.setStyleSheet("background: transparent;")   
    s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
    s1.clicked.connect(lambda x:noundictconfigdialog(self,transerrorfixdictconfig,'翻译结果替换设置',['翻译','替换'],'./userconfig/transerrorfixdictconfig.json'))

def noundictconfigdialog(object,configdict,title,label=[ '日文','翻译'],fname='./userconfig/noundictconfig.json'):
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle(title)
    #dialog.setWindowModality(Qt.ApplicationModal)
    
    formLayout = QVBoxLayout(dialog)  # 配置layout
        
    model=QStandardItemModel(len(list(configdict['dict'].keys())),1 , dialog)
    row=0
    for key in  (configdict['dict']):                                   # 2
            
            item = QStandardItem( key )
            model.setItem(row, 0, item)
            item = QStandardItem(configdict['dict'][key] )
            model.setItem(row, 1, item)
            row+=1
    model.setHorizontalHeaderLabels(label)
    table = QTableView(dialog)
    table.setModel(model)
    table.horizontalHeader().setStretchLastSection(True)
    #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #table.clicked.connect(self.show_info)
    button=QPushButton(dialog)
    button.setText('添加行')
    def clicked1(): 
        model.insertRow(0,[QStandardItem(''),QStandardItem('')]) 
    button.clicked.connect(clicked1)
    button2=QPushButton(dialog)
    button2.setText('删除选中行')
    def clicked2():
        
        model.removeRow(table.currentIndex().row())
    button2.clicked.connect(clicked2)
    button3=QPushButton(dialog)
    button3.setText('保存并关闭')
    def clicked3():
        rows=model.rowCount() 
        newdict={}
        for row in range(rows):
            if model.item(row,0).text()=="":
                continue
            newdict[model.item(row,0).text()]=model.item(row,1).text()
        configdict['dict']=newdict
        with open(fname,'w',encoding='utf-8') as ff:
            import json
            ff.write(json.dumps(configdict,ensure_ascii=False,sort_keys=False, indent=4))
        dialog.close()
    button3.clicked.connect(clicked3)
    formLayout.addWidget(table)
    formLayout.addWidget(button)
    formLayout.addWidget(button2)
    formLayout.addWidget(button3)
    dialog.resize(QSize(400,400))
    dialog.show()
 
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
        dialog.resize(QSize(400,1))
    elif type(configdict[key])==type([]): 
        # lines=QTextEdit(dialog)
        # lines.setPlainText('\n'.join(configdict[key]))
        # lines.textChanged.connect(lambda   :configdict.__setitem__(key,lines.toPlainText().split('\n')))
        # formLayout.addWidget(lines)
        model=QStandardItemModel(len(configdict[key]),1 , dialog)
         
        for row in range(len(configdict[key])):                                   # 2
             
                item = QStandardItem(configdict[key][row])
                model.setItem(row, 0, item)
        model.setHorizontalHeaderLabels([ key])
        table = QTableView(dialog)
        table.setModel(model)
        table.setWordWrap(False) 
        table.horizontalHeader().setStretchLastSection(True)
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        button=QPushButton(dialog)
        button.setText('添加行')
        def clicked1(): 
            model.insertRow(0,[QStandardItem('')]) 
        button.clicked.connect(clicked1)
        button2=QPushButton(dialog)
        button2.setText('删除选中行')
        def clicked2():
            
            model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
        button3=QPushButton(dialog)
        button3.setText('保存并关闭')
        def clicked3():
            rows=model.rowCount() 
            newdict=[]
            for row in range(rows):
                if model.item(row,0).text()=="":
                    continue
                newdict.append(model.item(row,0).text())
            configdict[key]=newdict
            dialog.close()
        button3.clicked.connect(clicked3)
        formLayout.addWidget(table)
        formLayout.addWidget(button)
        formLayout.addWidget(button2)
        formLayout.addWidget(button3)
        dialog.resize(QSize(400,400))
    dialog.show()
 