import functools
from PyQt5.QtCore import Qt ,pyqtSignal
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QSlider,QSpinBox,QFontComboBox ,QComboBox
import qtawesome 
 
from utils.config import globalconfig 
  
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab5(self) :
     
        tab = QWidget()
        self.tab_widget.addTab(tab, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(tab), " 语音设置")
 
        label = QLabel(tab)
        self.customSetGeometry(label, 20, 25, 160, 20)
        label.setText("Window TTS设置") 
        label = QLabel(tab)
        self.customSetGeometry(label, 20, 70, 160, 20)
        label.setText("windows TTS") 
        self.gugettsswitch =gui.switchbutton.MySwitch(tab, sign=globalconfig['reader']['windows'] ,textOff='关闭',textOn='打开')
        self.customSetGeometry(self.gugettsswitch, 100, 70, 66,22)
        self.gugettsswitch.clicked.connect(functools.partial(readerchange,self,'windows')) 

        label = QLabel(tab)
        self.customSetGeometry(label, 20, 115, 160, 20)
        label.setText("选择声音") 
        self.voicecombo=QComboBox(tab)
        
        self.customSetGeometry(self.voicecombo, 20, 115, 400, 20) 
        self.voicelistsignal.connect(lambda x: showvoicelist(self,x))
        self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self,x))
def changevoice(self,text):
    globalconfig['windowstts']['voice']=text
def showvoicelist(self,vl):
    print(vl)
    self.voicecombo.clear()
    self.voicecombo.addItems(vl)
def readerchange(self,who,checked):   
    if checked : 
        
        globalconfig['reader'][who]=True
    else:
        globalconfig['reader'][who]=False  
        self.object.reader=None
    
    
    if checked : 
            
        self.object.startreader()  