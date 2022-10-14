 
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton,QColorDialog,QSpinBox,QComboBox
from PyQt5.QtGui import QColor,QFont
import functools
from utils.config import globalconfig 
import qtawesome
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook 
import importlib
from gui.inputdialog import GetUserPlotItems
def setTabTwo(self) :
 
        self.tab_2 = QWidget()
        self.tab_widget.addTab(self.tab_2, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2), " 翻译设置")
 
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 25, 140, 20)
        label.setText("是否显示翻译器名称")
        p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['showfanyisource'], textOff='隐藏',textOn='显示')
        self.customSetGeometry(p, 160, 25, 20,20 )
        p.clicked.connect(lambda x: globalconfig.__setitem__('showfanyisource',x))
 
        initfanyiswitchs_auto(self) 
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 470, 200, 20)
        label.setText("最短翻译字数")
        self.minlength=QSpinBox(self.tab_2)
        self.minlength.setMinimum(0)
        self.minlength.setMaximum(500)
        self.minlength.setValue(globalconfig['minlength']) 
        self.customSetGeometry(self.minlength, 150,470,50,20)
        self.minlength.valueChanged.connect(lambda x:globalconfig.__setitem__('minlength',x)) 



        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 220, 470, 200, 20)
        label.setText("最长翻译字数")
        self.maxlength=QSpinBox(self.tab_2)
        self.maxlength.setMinimum(0)
        self.maxlength.setMaximum(500)
        self.maxlength.setValue(globalconfig['maxlength']) 
        self.customSetGeometry(self.maxlength, 350, 470,50,20)
        self.maxlength.valueChanged.connect(lambda x:globalconfig.__setitem__('maxlength',x)) 

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 420, 470, 200, 20)
        label.setText("在线翻译超时(s)")
        self.translatortimeout=QSpinBox(self.tab_2)
        self.translatortimeout.setMinimum(1)
        self.translatortimeout.setMaximum(20)
        import socket
        socket.setdefaulttimeout(globalconfig['translatortimeout'])
        self.translatortimeout.setValue(globalconfig['translatortimeout']) 
        self.customSetGeometry(self.translatortimeout, 550,470,50,20)
        def __timeout(x):

            globalconfig.__setitem__('translatortimeout',x)
            socket.setdefaulttimeout(globalconfig['translatortimeout'])
        self.translatortimeout.valueChanged.connect(lambda x:__timeout(x)) 

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 500, 200, 20)
        label.setText("源语言")
        self.srclangcom=QComboBox(self.tab_2) 
        self.srclangcom.addItems(['日文','英文']) 
        self.srclangcom.setCurrentIndex(globalconfig['srclang'])
        self.customSetGeometry(self.srclangcom, 150,500,50,20)
        self.srclangcom.currentIndexChanged.connect(lambda x:globalconfig.__setitem__('srclang',x)) 
def initfanyiswitchs_auto(self):
        num=0
        
        for fanyi in globalconfig['fanyi']:
            y=70+35*(num//3)
            x=20+220*(num%3)
            try:
                importlib.import_module('translator.'+fanyi)
            except:
                continue
            initfanyiswitchs(self,fanyi,(x, y, 65, 20),(x+70, y, 20,20),(x+110, y, 20,20),(x+150, y, 20,20))
            num+=1

def initfanyiswitchs(self,name,namepos,switchpos,colorpos,settingpos):

        label = QLabel(self.tab_2)
        self.customSetGeometry(label, *namepos)
        label.setText(globalconfig['fanyi'][name]['name']+":")
        p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['fanyi'][name]['use'], textOff='关闭',textOn='使用')
        
        self.customSetGeometry(p, *switchpos)
        def fanyiselect( who,checked):
            if checked : 
                globalconfig['fanyi'][who]['use']=True
                self.object.prepare(who)

            else:
                globalconfig['fanyi'][who]['use']=False 
        p.clicked.connect(functools.partial( fanyiselect,name))
        s=QPushButton(qtawesome.icon('fa.paint-brush', color=globalconfig['fanyi'][name]['color']), "", self.tab_2)
         
        self.customSetIconSize(s, 20, 20)
        self.customSetGeometry(s, *colorpos) 
        s.setStyleSheet("background: transparent;" )
        s.clicked.connect(lambda: self.ChangeTranslateColor(name,s))  
     

        
        if 'argsfile' in globalconfig['fanyi'][name]:
            s1 = QPushButton( "", self.tab_2)
            self.customSetIconSize(s1, 20, 20)
            self.customSetGeometry(s1, *settingpos)
            s1.setStyleSheet("background: transparent;") 
            
            s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
            aclass=importlib.import_module('translator.'+name).TS
            df=aclass.defaultsetting()
            s1.clicked.connect(lambda x:GetUserPlotItems(self,globalconfig['fanyi'][name]['argsfile'],df,globalconfig['fanyi'][name]['name']+'设置'))
     