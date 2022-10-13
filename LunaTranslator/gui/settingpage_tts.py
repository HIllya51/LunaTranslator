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
        self.customSetGeometry(label, 20, 70, 120, 20)
        label.setText("WindowsTTS(离线)") 
        self.WindowsTTSswitch =gui.switchbutton.MySwitch(tab, sign=globalconfig['reader']['windowstts']['use'] )
        self.customSetGeometry(self.WindowsTTSswitch, 150, 70, 20,20)
        self.WindowsTTSswitch.clicked.connect(functools.partial(readerchange,self,'windowstts'))  
         
        label = QLabel(tab)
        self.customSetGeometry(label, 220, 70, 120, 20)
        label.setText("AzureTTS")
        self.AzureTTSswitch =gui.switchbutton.MySwitch(tab, sign=globalconfig['reader']['azuretts']['use'] )
        self.customSetGeometry(self.AzureTTSswitch,350, 70, 20,20)
        self.AzureTTSswitch.clicked.connect(functools.partial(readerchange,self,'azuretts'))  
 
        label = QLabel(tab)
        self.customSetGeometry(label, 400, 70, 120, 20)
        label.setText("火山TTS")
 
        self.huoshanTTSswitch =gui.switchbutton.MySwitch(tab, sign= globalconfig['reader']['huoshantts']['use'] )
        self.customSetGeometry(self.huoshanTTSswitch, 550, 70, 20,20)
        self.huoshanTTSswitch.clicked.connect(functools.partial(readerchange,self,'huoshantts')) 

        self.readerwitchs={'huoshantts':self.huoshanTTSswitch,
                            'windowstts':self.WindowsTTSswitch,
                            'azuretts':self.AzureTTSswitch}


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
        self.voice_spinBox.setValue(globalconfig['ttscommon']['rate']) 
        self.voice_spinBox.setSingleStep(1)
        self.voice_spinBox.setDecimals(0)
        self.voice_spinBox.valueChanged.connect(lambda x:globalconfig['ttscommon'].__setitem__('rate',x))

        
        label = QLabel(tab)
        self.customSetGeometry(label, 20, 200, 145, 16)
        label.setText("音量:(0~100)") 
         
        self.volume_spinBox = QDoubleSpinBox(tab)
        self.customSetGeometry(self.volume_spinBox, 120, 200, 50, 25)
        self.volume_spinBox.setRange(0,100) 
        self.volume_spinBox.setValue(globalconfig['ttscommon']['volume']) 
        self.volume_spinBox.setSingleStep(1)
        self.volume_spinBox.setDecimals(0)
        self.volume_spinBox.valueChanged.connect(lambda x:globalconfig['ttscommon'].__setitem__('volume',x))

        label = QLabel(tab)
        self.customSetGeometry(label, 20, 250, 160, 20)
        label.setText("自动朗读") 
        self.autoreadswitch =gui.switchbutton.MySwitch(tab, sign=globalconfig['autoread'])
        self.customSetGeometry(self.autoreadswitch, 100, 250, 20,20)
        self.autoreadswitch.clicked.connect(lambda x:globalconfig.__setitem__('autoread',x)) 
def changevoice(self,text):
    globalconfig['reader'][self.object.reader_usevoice]['voice']=text
def showvoicelist(self,vl):
    self.voicecombo.blockSignals(True)
    self.voicecombo.clear()
    self.voicecombo.addItems(vl)
    if globalconfig['reader'][self.object.reader_usevoice]['voice'] in vl:
        i=vl.index(globalconfig['reader'][self.object.reader_usevoice]['voice'])
    
        self.voicecombo.setCurrentIndex(i)
    self.voicecombo.blockSignals(False)
def readerchange(self,who,checked):   
    
    if checked : 
         
        for k in self.readerwitchs:
                if globalconfig['reader'][k]['use']==True:
                     
                    self.readerwitchs[k].setChecked(False) 
                    globalconfig['reader'][k]['use']=False
        globalconfig['reader'][who]['use']=True
    else:
        globalconfig['reader'][who]['use']=False  
        self.object.reader=None
    
    
    if checked : 
            
        self.object.startreader()  