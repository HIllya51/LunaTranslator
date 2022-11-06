
from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton,QGridLayout
import qtawesome  
import functools 
from utils.config import globalconfig 
import json
import os
import gui.switchbutton 
import gui.attachprocessdialog  
import win32con
import pywintypes
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
                [ (QLabel('选择文本输入源'),3)],
                [   (QLabel('剪贴板'),3),(self.getsimpleswitch(globalconfig['sourcestatus'],'copy',name='copyboardswitch',callback=functools.partial(textsourcechange,self,'copy')),1),'',
                    (QLabel('OCR'),3),(self.getsimpleswitch(globalconfig['sourcestatus'],'ocr',name='ocrswitch',callback=functools.partial(textsourcechange,self,'ocr')),1),'',
                    (QLabel('Textractor'),3),(self.getsimpleswitch(globalconfig['sourcestatus'],'textractor',name='textractorswitch',callback=functools.partial(textsourcechange,self,'textractor')),1)],
                [(QLabel(''),10),(QLabel('选择游戏'),3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selectbutton',icon='fa.gear',constcolor="#FF69B4",callback=functools.partial(settingtextractor,self,True) ),1)],
                [(QLabel(''),10),(QLabel('选择文本'),3),(self.getcolorbutton(globalconfig ,'',enable=globalconfig['sourcestatus']['textractor'],name='selecthookbutton',icon='fa.gear',constcolor="#FF69B4",callback=functools.partial(settingsource,self)),1)],
                [''], 
                [(QLabel('提取的文本自动复制到剪贴板'),3),(self.getsimpleswitch(globalconfig ,'outputtopasteboard',name='outputtopasteboard'),1)],
                [(QLabel('游戏最小化时窗口隐藏'),3),(self.getsimpleswitch(globalconfig,'minifollow'),1)],
                [(QLabel('游戏失去焦点时窗口隐藏'),3),(self.getsimpleswitch(globalconfig,'focusfollow'),1)],
                [(QLabel('游戏窗口移动时同步移动'),3),(self.getsimpleswitch(globalconfig,'movefollow'),1)],
        ] 
        self.yitiaolong("基本设置",grids)
        
 
        self.sourceswitchs={'copy':self.copyboardswitch,'ocr':self.ocrswitch,'textractor':self.textractorswitch}# ,'textractor_pipe':self.Textractor_forward_extension_switch}
 

        self.resetsourcesignal.connect(functools.partial(resetsource,self))   
            
 
def settingtextractor(self,show1 ): 
         
        if globalconfig['sourcestatus']['textractor']==False:
            return 
        if 'a' in dir(self) and self.a :
            return 
        self.object.hookselectdialog.hide()
        import win32process,win32api 
        
        if show1: 
            self.hide()
        self.a=gui.attachprocessdialog.AttachProcessDialog()
        
        ret=self.a.exec_()
        if show1:
                    self.show()
        if(ret): 
            try:
                pid,pexe,hwnd=( self.a.selectedp)   
            except:
                if show1:
                    self.show()
                return 
            
            # if pid==self.hookpid:
            #     self.show()
            #     return
            try:
                if True:
                #try:

                    process=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
                # except:
                #     process=win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION,False, (pid))
                
            except pywintypes.error:
                self.object.translation_ui.displayraw.emit(f'打开进程失败！','#ff0000') 
                return
            if pexe=='':
              
                pexe=win32process.GetModuleFileNameEx(process,None) 
            
            if   self.object.textsource:
                self.object.textsource.end()  
             
            arch='86' if win32process.IsWow64Process( process)  else '64' 
            self.hookpid=pid
            self.hookhwnd=hwnd
            self.object.hookselectdialog.changeprocessclearsignal.emit()
            if self.object.savetextractor:
                self.object.textsource=self.object.savetextractor
                self.object.textsource.reset(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,hwnd,pexe,arch)

            else:
                
                self.object.textsource=textractor(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,hwnd,pexe,arch) 
                
                self.object.savetextractor=self.object.textsource
            # if not os.path.exists('./files/savehook.json'):
            #     js={}
            # with open('./files/savehook.json','r',encoding='utf8') as ff:
            #     js=json.load(ff)
            # if pexe in js:
            #     self.object.textsource.selectedhook=js[pexe]
            # else:

            settingsource(self)
        else:
            self.object.textsource=None
        self.a=None
def settingsource(self):
    if globalconfig['sourcestatus']['textractor']==False:
                return 
    #self.hide()
    self.object.hookselectdialog.show() 
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
            
            if who=='ocr'   :
                self.object.translation_ui.showhidestate=True
                self.object.translation_ui.showhide()
                self.object.translation_ui.refreshtooliconsignal.emit()

        if checked : 
            self.object.starttextsource() 
        self.selectbutton.setEnabled(globalconfig['sourcestatus']['textractor']) 
        self.selecthookbutton.setEnabled(globalconfig['sourcestatus']['textractor'])
        if who=='textractor':
            settingtextractor(self,True)
        
        self.object.translation_ui.showhidetoolbuttons()
    # 翻译设定标签栏