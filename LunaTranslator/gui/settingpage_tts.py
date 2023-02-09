import functools 

from PyQt5.QtWidgets import   QComboBox 
from gui.inputdialog import getsomepath1
from utils.config import globalconfig    

def setTab5_direct(self) :  
    self.voicecombo=QComboBox( ) 
    self.voicelistsignal.connect(lambda x: showvoicelist(self,x))
    self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self,x))

def setTab5(self) : 
    self.tabadd_lazy(self.tab_widget, ('语音合成'), lambda :setTab5lz(self)) 
def setTab5lz(self) :
         
        
        grids=[
                [   ('WindowsTTS',3),(self.getsimpleswitch(globalconfig['reader']['windowstts'],'use',name='windowstts',callback= functools.partial(self.yuitsu_switch,'reader','readerswitchs','windowstts',self.object.startreader),pair='readerswitchs'),1),'','',
                    ('火山TTS',3),(self.getsimpleswitch(globalconfig['reader']['huoshantts'],'use',name='huoshantts',callback= functools.partial(self.yuitsu_switch,'reader','readerswitchs','huoshantts',self.object.startreader),pair='readerswitchs'),1),'','',
                    ('AzureTTS',3),(self.getsimpleswitch(globalconfig['reader']['azuretts'],'use',name='azuretts',callback= functools.partial(self.yuitsu_switch,'reader','readerswitchs','azuretts',self.object.startreader),pair='readerswitchs'),1),'',''],
                [   ('VoiceRoid2',3),(self.getsimpleswitch(globalconfig['reader']['voiceroid2'],'use',name='voiceroid2',callback= functools.partial(self.yuitsu_switch,'reader','readerswitchs','voiceroid2',self.object.startreader),pair='readerswitchs'),1),self.getcolorbutton(globalconfig,'',callback=lambda:getsomepath1(self,'voiceroid2',globalconfig['reader']['voiceroid2'],'path' ,'voiceroid2', self.object.startreader ,True),icon='fa.gear',constcolor="#FF69B4"),'',
                   ('VOICEVOX',3),(self.getsimpleswitch(globalconfig['reader']['voicevox'],'use',name='voicevox',callback= functools.partial(self.yuitsu_switch,'reader','readerswitchs','voicevox',self.object.startreader),pair='readerswitchs'),1),self.getcolorbutton(globalconfig,'',callback=lambda:getsomepath1(self,'voicevox',globalconfig['reader']['voicevox'],'path','voicevox',self.object.startreader,True),icon='fa.gear',constcolor="#FF69B4"),],
                [''],
                [("选择声音",3),(self.voicecombo,6)],
                [('语速:(-10~10)',3),(self.getspinbox(-10,10,globalconfig['ttscommon'],'rate'  ),2)],
                [('音量:(0~100)',3),(self.getspinbox(0,100,globalconfig['ttscommon'],'volume' ),2)],
                [ ('自动朗读',3),(self.getsimpleswitch(globalconfig,'autoread' ),1)],
                
        ]  
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        return gridlayoutwidget 
 
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