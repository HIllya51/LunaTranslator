import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QSlider,QDoubleSpinBox,QFontComboBox ,QComboBox
import qtawesome 
 
from utils.config import globalconfig 
from gui.inputdialog import multicolorset
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
from gui.inputdialog import getsomepath
def setTabcishu(self) :
     
        self.tab_cishu = QWidget()
        self.tab_widget.addTab(self.tab_cishu, "辞书设置") 
        
        label = QLabel(self.tab_cishu)
        self.customSetGeometry(label, 20, 20, 150, 20) 
        label.setText("使用MeCab辞书分词:")
        
        def __changemecabstate(self,x):
                globalconfig['mecab']['use']=x 
                self.object.starthira()
        s =gui.switchbutton.MySwitch(self.tab_cishu, sign=globalconfig['mecab']['use'])
        self.customSetGeometry(s,  180,20, 20,20)
        s.clicked.connect(lambda x: __changemecabstate(self,x))  
        
        
        s2 = QPushButton( "", self.tab_cishu)
        self.customSetIconSize(s2, 20, 20)
        self.customSetGeometry(s2,  210,20,20,20)
        s2.setStyleSheet("background: transparent;")   
        s2.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
        def __getmecabpath(self):
                getsomepath(self,'mecab',globalconfig['mecab']['path'],'mecab',lambda x:globalconfig['mecab'].__setitem__('path',x),True)
                self.object.starthira()
        s2.clicked.connect(lambda :__getmecabpath(self))
 
        label = QLabel(self.tab_cishu)
        self.customSetGeometry(label, 20, 50, 150, 20) 
        label.setText("显示不同颜色词性:") 
        s =gui.switchbutton.MySwitch(self.tab_cishu, sign=globalconfig['showcixing'])
        self.customSetGeometry(s,  180,50, 20,20)
        s.clicked.connect(lambda x:globalconfig.__setitem__("showcixing",x))  

        
        s2 = QPushButton( "", self.tab_cishu)
        self.customSetIconSize(s2, 20, 20)
        self.customSetGeometry(s2,  210,50,20,20)
        s2.setStyleSheet("background: transparent;")   
        s2.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
         
        s2.clicked.connect(lambda :multicolorset(self))
 


        label = QLabel(self.tab_cishu)
        self.customSetGeometry(label, 20, 80, 250, 20) 
        label.setText("开启快捷查词(点击原文可查词)") 
        s =gui.switchbutton.MySwitch(self.tab_cishu, sign=globalconfig['usesearchword'])
        self.customSetGeometry(s,  280,80, 20,20)
        s.clicked.connect(lambda x: globalconfig.__setitem__('usesearchword',x))  
        
        s1 = QPushButton( "", self.tab_cishu)
        self.customSetIconSize(s1, 20, 20)
        self.customSetGeometry(s1,  310,80,20,20)
        s1.setStyleSheet("background: transparent;")   
        s1.setIcon(qtawesome.icon("fa.search", color="#FF69B4"  ))
        s1.clicked.connect(self.object.translation_ui.searchwordW.show )

        label = QLabel(self.tab_cishu)
        self.customSetGeometry(label, 20, 110, 150, 20) 
        label.setText("小学馆辞书:")
         
        s1 = QPushButton( "", self.tab_cishu)
        self.customSetIconSize(s1, 20, 20)
        self.customSetGeometry(s1,  180,110,20,20)
        s1.setStyleSheet("background: transparent;")   
        s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
        def __getpath(self):
                getsomepath(self,'小学馆',globalconfig['xiaoxueguan']['path'],'小学馆',lambda x:globalconfig['xiaoxueguan'].__setitem__('path',x),False)
                self.object.startxiaoxueguan(1)
        s1.clicked.connect(lambda :__getpath(self))

        

        label = QLabel(self.tab_cishu)
        self.customSetGeometry(label, 20, 140, 150, 20) 
        label.setText("灵格斯词典:")
         
        s1 = QPushButton( "", self.tab_cishu)
        self.customSetIconSize(s1, 20, 20)
        self.customSetGeometry(s1,  180,140,20,20)
        s1.setStyleSheet("background: transparent;")   
        s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
        def __getpath2(self):
                getsomepath(self,'灵格斯',globalconfig['linggesi']['path'],'灵格斯',lambda x:globalconfig['linggesi'].__setitem__('path',x),True)
                self.object.startxiaoxueguan(3)
        s1.clicked.connect(lambda :__getpath2(self))



        label = QLabel(self.tab_cishu)
        self.customSetGeometry(label, 20, 170, 150, 20) 
        label.setText("EDICT词典(日英):")
         
        s1 = QPushButton( "", self.tab_cishu)
        self.customSetIconSize(s1, 20, 20)
        self.customSetGeometry(s1,  180,170,20,20)
        s1.setStyleSheet("background: transparent;")   
        s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
        def __getpath3(self):
                getsomepath(self,'edict',globalconfig['edict']['path'],'edict',lambda x:globalconfig['edict'].__setitem__('path',x),False)
                self.object.startxiaoxueguan(2)
        s1.clicked.connect(lambda :__getpath3(self))

