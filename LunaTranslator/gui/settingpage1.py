
from PyQt5.QtWidgets import   QLabel 
import functools 
from utils.config import globalconfig 
from traceback import print_exc
import os

from utils.getpidlist import getarch
import gui.attachprocessdialog   
from textsource.textractor import textractor
def clicksourcefuntion(self,i):
    if i==0:
        self.copyboardswitch.click()
    elif i==1:
        self.ocrswitch.click()
    elif i==2:
        self.textractorswitch.click()
def setTabOne(self) :
        self.clicksourcesignal.connect(functools.partial(clicksourcefuntion,self))
  
        grids=[
                [ ('选择文本输入源',3)],
                [   ('剪贴板',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'copy',name='copyboardswitch',callback=functools.partial(textsourcechange,self,'copy')),1),'',
                    ('OCR',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'ocr',name='ocrswitch',callback=functools.partial(textsourcechange,self,'ocr')),1),'',
                    ('Textractor',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'textractor',name='textractorswitch',callback=functools.partial(textsourcechange,self,'textractor')),1)],
                
                [('TXT文件',3),(self.getsimpleswitch(globalconfig['sourcestatus'],'txt',name='txtswitch',callback=functools.partial(textsourcechange,self,'txt')),1),('',6),('选择游戏',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selectbutton',icon='fa.gear',constcolor="#FF69B4",callback=functools.partial(settingtextractor,self) ),1)],
                [('',10),('选择文本',3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selecthookbutton',icon='fa.gear',constcolor="#FF69B4",callback=functools.partial(settingsource,self)),1)],
                [''], 
                [('提取的文本自动复制到剪贴板',5),(self.getsimpleswitch(globalconfig ,'outputtopasteboard',name='outputtopasteboard'),1)], 
        ] 
        self.yitiaolong("基本设置",grids)
        
 
        self.sourceswitchs={'copy':self.copyboardswitch,'ocr':self.ocrswitch,'textractor':self.textractorswitch ,'txt':self.txtswitch}# ,'textractor_pipe':self.Textractor_forward_extension_switch}
 

        self.resetsourcesignal.connect(functools.partial(resetsource,self))   
             
def settingtextractor(self ): 
         
        if globalconfig['sourcestatus']['textractor']==False:
            return 
         
        self.object.hookselectdialog.hide() 
        
        # self.a=gui.attachprocessdialog.AttachProcessDialog(self.object.translation_ui)
        # self.a.show()
        #ret=self.a.exec_()
        self.object.AttachProcessDialog.callback=functools.partial(callback,self)
        self.object.AttachProcessDialog.show() 
def callback(self,selectedp) :
    
            #self.object.textsource=None
            pid,pexe,hwnd=(  selectedp)   
        
            arch=getarch(pid)
            if arch is None:
                return
            if   self.object.textsource:
                self.object.textsource.end()  
            
            self.object.hookselectdialog.changeprocessclearsignal.emit()
            #  
            self.object.textsource=textractor(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,hwnd,pexe )  
            settingsource(self)
        
def settingsource(self):
    if globalconfig['sourcestatus']['textractor']==False:
                return 
    #self.hide()
    self.object.hookselectdialog.showNormal() 
    self.object.hookselectdialog.hiding=False
def resetsource(self):
        self.object.hookselectdialog.changeprocessclearsignal.emit()
        for k in self.sourceswitchs:
                if globalconfig['sourcestatus'][k]==True:
                    if k=='textractor':
                        if 'textsource' in dir(self.object) and  self.object.textsource and self.object.textsource.ending==False: 
                            self.object.textsource.end() 
                    self.sourceswitchs[k].setChecked(False) 
                    globalconfig['sourcestatus'][k]=False
def textsourcechange(self,who,checked):   
        if checked : 
            resetsource(self)
            globalconfig['sourcestatus'][who]=True
        else:
            globalconfig['sourcestatus'][who]=False  
            if 'textsource' in dir(self.object) and self.object.textsource:
                self.object.textsource.end() 
            
        
        self.object.translation_ui.showhidestate=False 
        self.object.translation_ui.refreshtooliconsignal.emit()
        self.object.rect=None
        self.object.range_ui.hide()
        self.object.textsource=None
        if checked : 
            self.object.starttextsource() 
        self.selectbutton.setEnabled(globalconfig['sourcestatus']['textractor']) 
        self.selecthookbutton.setEnabled(globalconfig['sourcestatus']['textractor'])
        if who=='textractor' and checked:
            settingtextractor(self )
        
        self.object.translation_ui.showhidetoolbuttons()
    # 翻译设定标签栏