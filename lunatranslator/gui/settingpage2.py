 
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton,QColorDialog
from PyQt5.QtGui import QColor,QFont
import functools
from utils.config import globalconfig 
import qtawesome
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook 

from gui.inputdialog import GetUserPlotItems
def setTabTwo(self) :
 
        self.tab_2 = QWidget()
        self.tab_widget.addTab(self.tab_2, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2), " 翻译设置")
 
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 25, 140, 20)
        label.setText("是否显示翻译器名称")
        p=gui.switchbutton.MySwitch(self.tab_2, sign=globalconfig['showfanyisource'], textOff='隐藏',textOn='显示')
        self.customSetGeometry(p, 160, 25, 66, 22 )
        p.clicked.connect(lambda x: globalconfig.__setitem__('showfanyisource',x))

        initfanyiswitchs_auto(self)

def initfanyiswitchs_auto(self):
        num=0
        
        for fanyi in globalconfig['fanyi']:
            y=70+40*(num//3)
            x=20+220*(num%3)
            initfanyiswitchs(self,fanyi,(x, y, 65, 20),(x+70, y, 66, 22),(x+145, y, 20,20),(x+175, y, 20,20))
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
     

        
        if 'args' in globalconfig['fanyi'][name]:
            s = QPushButton( "", self.tab_2)
            self.customSetIconSize(s, 20, 20)
            self.customSetGeometry(s, *settingpos)
            s.setStyleSheet("background: transparent;") 
            
            s.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
            s.clicked.connect(lambda x:GetUserPlotItems(self,name))
     