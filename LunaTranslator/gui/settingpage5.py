import functools 

from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox,QDoubleSpinBox 
 
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
        self.customSetGeometry(self.gugettsswitch, 100, 70, 20,20)
        self.gugettsswitch.clicked.connect(functools.partial(readerchange,self,'windows')) 

        label = QLabel(tab)
        self.customSetGeometry(label, 20, 115, 160, 20)
        label.setText("选择声音") 
        self.voicecombo=QComboBox(tab)
        
        self.customSetGeometry(self.voicecombo, 20, 115, 400, 20) 
        self.voicelistsignal.connect(lambda x: showvoicelist(self,x))
        self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self,x))

        label = QLabel(tab)
        self.customSetGeometry(label, 20, 160, 145, 16)
        label.setText("语速:(-10~10)") 
         
        self.voice_spinBox = QDoubleSpinBox(tab)
        self.customSetGeometry(self.voice_spinBox, 120, 160, 50, 25)
        self.voice_spinBox.setRange(-10,10) 
        self.voice_spinBox.setValue(globalconfig['windowstts']['rate']) 
        self.voice_spinBox.setSingleStep(1)
        self.voice_spinBox.setDecimals(0)
        self.voice_spinBox.valueChanged.connect(lambda x:globalconfig['windowstts'].__setitem__('rate',x))

        
        label = QLabel(tab)
        self.customSetGeometry(label, 20, 200, 145, 16)
        label.setText("音量:(0~100)") 
         
        self.volume_spinBox = QDoubleSpinBox(tab)
        self.customSetGeometry(self.volume_spinBox, 120, 200, 50, 25)
        self.volume_spinBox.setRange(0,100) 
        self.volume_spinBox.setValue(globalconfig['windowstts']['volume']) 
        self.volume_spinBox.setSingleStep(1)
        self.volume_spinBox.setDecimals(0)
        self.volume_spinBox.valueChanged.connect(lambda x:globalconfig['windowstts'].__setitem__('volume',x))

        label = QLabel(tab)
        self.customSetGeometry(label, 20, 250, 160, 20)
        label.setText("自动朗读") 
        self.autoreadswitch =gui.switchbutton.MySwitch(tab, sign=globalconfig['autoread'])
        self.customSetGeometry(self.autoreadswitch, 100, 250, 20,20)
        self.autoreadswitch.clicked.connect(lambda x:globalconfig.__setitem__('autoread',x)) 
def changevoice(self,text):
    globalconfig['windowstts']['voice']=text
def showvoicelist(self,vl):
    self.voicecombo.blockSignals(True)
    self.voicecombo.clear()
    self.voicecombo.addItems(vl)
    if globalconfig['windowstts']['voice'] in vl:
        i=vl.index(globalconfig['windowstts']['voice'])
    
        self.voicecombo.setCurrentIndex(i)
    self.voicecombo.blockSignals(False)
def readerchange(self,who,checked):   
    if checked : 
        
        globalconfig['reader'][who]=True
    else:
        globalconfig['reader'][who]=False  
        self.object.reader=None
    
    
    if checked : 
            
        self.object.startreader()  