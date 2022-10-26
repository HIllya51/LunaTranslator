import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QSlider,QDoubleSpinBox,QFontComboBox ,QComboBox
import qtawesome 
 
from utils.config import globalconfig 
  
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
from gui.inputdialog import getxiaoxueguanpath
def setTabcishu(self) :
     
        self.tab_cishu = QWidget()
        self.tab_widget.addTab(self.tab_cishu, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_cishu), " 辞书设置") 
        label = QLabel(self.tab_cishu)
        self.customSetGeometry(label, 20, 20, 150, 20) 
        label.setText("使用小学馆辞书:")
        
        def __changexxgstate(self,x):
                globalconfig['xiaoxueguan']['use']=x
                self.object.translation_ui.showhiderawbutton.setIcon(qtawesome.icon("fa.eye"   if globalconfig['xiaoxueguan']['use'] else "fa.eye-slash" ,color="white"))

        self.show_original_switch =gui.switchbutton.MySwitch(self.tab_cishu, sign=globalconfig['xiaoxueguan']['use'])
        self.customSetGeometry(self.show_original_switch,  180,20, 20,20)
        self.show_original_switch.clicked.connect(lambda x: __changexxgstate(self,x))  
        
        s1 = QPushButton( "", self.tab_cishu)
        self.customSetIconSize(s1, 20, 20)
        self.customSetGeometry(s1,  210,20,20,20)
        s1.setStyleSheet("background: transparent;")   
        s1.setIcon(qtawesome.icon("fa.gear", color="#FF69B4"  ))
        def __getpath(self):
                getxiaoxueguanpath(self)
                self.object.startxiaoxueguan()
        s1.clicked.connect(lambda :__getpath(self))