import functools 

from PyQt5.QtWidgets import   QComboBox 
from gui.inputdialog import getsomepath1
from myutils.config import globalconfig    
import os,functools
def setTab5_direct(self) :  
    self.voicecombo=QComboBox( ) 
    self.voicelistsignal.connect(functools.partial(showvoicelist,self ))
    self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self,x))
    
def setTab5(self) : 
    self.tabadd_lazy(self.tab_widget, ('语音合成'), lambda :setTab5lz(self)) 


def getttsgrid(self) :
        
          
        grids=[ ] 
        i=0 
        self.ocrswitchs={}
        line=[]
        for name in globalconfig['reader']:
              
            _f='./LunaTranslator/tts/{}.py'.format(name)
            if os.path.exists(_f)==False:  
                continue 
            
            line+=[
                 ((globalconfig['reader'][name]['name']),6),
                 self.getsimpleswitch(globalconfig['reader'][name],'use',name=name,callback=functools.partial(self.yuitsu_switch,'reader','readerswitchs',name,self.object.startreader),pair='readerswitchs'), 
                 
                 ] 
            if 'path' in globalconfig['reader'][name]:
                 line+=[self.getcolorbutton(globalconfig,'',callback=functools.partial(getsomepath1,self,globalconfig['reader'][name]['name'],globalconfig['reader'][name] ,'path',globalconfig['reader'][name]['name'],self.object.startreader,True),icon='fa.gear',constcolor="#FF69B4")]
            else:
                 line+=['']
            if i%3==2  :
                grids.append(line) 
                line=[]
            else:
                line+=['']
            i+=1
        if len(line):
             grids.append(line) 
        return grids
       
        
def setTab5lz(self) :
         
        grids=getttsgrid(self)
        grids+=[ 
                [''],
                [("选择声音",5),(self.voicecombo,15)],
                [('语速:(-10~10)',5),(self.getspinbox(-10,10,globalconfig['ttscommon'],'rate'  ),2)],
                [('音量:(0~100)',5),(self.getspinbox(0,100,globalconfig['ttscommon'],'volume' ),2)],
                [ ('自动朗读',5),(self.getsimpleswitch(globalconfig,'autoread' ),1)],
                
        ]  
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        return gridlayoutwidget 
 
def changevoice(self,text):

    globalconfig['reader'][self.object.reader_usevoice]['voice']=self.object.reader.voicelist[self.voicecombo.currentIndex()]
def showvoicelist(self,vl,idx):
    self.voicecombo.blockSignals(True)
    self.voicecombo.clear()
    self.voicecombo.addItems(vl)
    if idx>=0:
        self.voicecombo.setCurrentIndex(idx)
    self.voicecombo.blockSignals(False) 