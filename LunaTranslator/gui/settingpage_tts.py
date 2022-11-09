import functools 

from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox,QDoubleSpinBox ,QPushButton,QGridLayout
from gui.inputdialog import getsomepath1
from utils.config import globalconfig 
import qtawesome
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab5(self) :
         
        self.voicecombo=QComboBox( ) 
        self.voicelistsignal.connect(lambda x: showvoicelist(self,x))
        self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self,x))
        grids=[
                [   ('WindowsTTS',3),(self.getsimpleswitch(globalconfig['reader']['windowstts'],'use',name='WindowsTTSswitch',callback=functools.partial(readerchange,self,'windowstts')),1),'','',
                    ('火山TTS',3),(self.getsimpleswitch(globalconfig['reader']['huoshantts'],'use',name='huoshanTTSswitch',callback=functools.partial(readerchange,self,'huoshantts')),1),'','',
                    ('AzureTTS',3),(self.getsimpleswitch(globalconfig['reader']['azuretts'],'use',name='AzureTTSswitch',callback=functools.partial(readerchange,self,'azuretts')),1),'',''],
                [   ('VoiceRoid2',3),(self.getsimpleswitch(globalconfig['reader']['voiceroid2'],'use',name='VoiceRoid2TTSswitch',callback=functools.partial(readerchange,self,'voiceroid2')),1),self.getcolorbutton(globalconfig,'',callback=lambda:getsomepath1(self,'voiceroid2',globalconfig['reader']['voiceroid2'],'path' ,'voiceroid2', self.object.startreader ,True),icon='fa.gear',constcolor="#FF69B4"),'',
                   ('VOICEVOX',3),(self.getsimpleswitch(globalconfig['reader']['voicevox'],'use',name='voicevoxswitch',callback=functools.partial(readerchange,self,'voicevox')),1),self.getcolorbutton(globalconfig,'',callback=lambda:getsomepath1(self,'voicevox',globalconfig['reader']['voicevox'],'path','voicevox',self.object.startreader,True),icon='fa.gear',constcolor="#FF69B4"),],
                [''],
                [("选择声音",3),(self.voicecombo,6)],
                [('语速:(-10~10)',3),(self.getspinbox(-10,10,globalconfig['ttscommon'],'rate'  ),2)],
                [('音量:(0~100)',3),(self.getspinbox(0,100,globalconfig['ttscommon'],'volume' ),2)],
                [ ('自动朗读',3),(self.getsimpleswitch(globalconfig,'autoread' ),1)],
                
        ]  
        self.yitiaolong("语音设置",grids)
        self.readerwitchs={'huoshantts':self.huoshanTTSswitch,
                            'windowstts':self.WindowsTTSswitch,
                            'azuretts':self.AzureTTSswitch,
                            'voiceroid2':self.VoiceRoid2TTSswitch,
                            'voicevox':self.voicevoxswitch}
   
 
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