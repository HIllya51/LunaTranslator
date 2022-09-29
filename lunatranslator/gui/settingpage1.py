 
from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton
import qtawesome 
import functools 
from utils.config import globalconfig 
import json
import os
import gui.switchbutton 
import gui.attachprocessdialog  
import gui.selecthook
import pywintypes
from textsource.textractor import textractor
def setTabOne(self) :
    
        # 选项卡界面
        self.tab_1 = QWidget()
        self.customSetGeometry(self.tab_1, 0, 0, self.window_width, self.window_height)
        self.tab_widget.addTab(self.tab_1, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_1), "基本设置")
 
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 25, 160, 20)
        label.setText("选择文本输入源") 
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 70, 60, 20)
        label.setText("剪切板") 
        self.copyboardswitch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['copy'] ,textOff='关闭',textOn='打开')
        self.customSetGeometry(self.copyboardswitch, 100, 70, 66, 22) 
        self.copyboardswitch.clicked.connect(functools.partial(textsourcechange,self,'copy')) 
        
        # label = QLabel(self.tab_1)
        # self.customSetGeometry(label, 20, 105, 300, 20)
        # label.setText("Textractor插件") 
        # self.Textractor_forward_extension_switch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['textractor_pipe'], textOff='关闭',textOn='打开')
        # self.customSetGeometry(self.Textractor_forward_extension_switch, 130, 105, 66, 22)
        # self.Textractor_forward_extension_switch.clicked.connect(functools.partial(textsourcechange,self,'textractor_pipe')) 

        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 220, 70, 35, 20)
        label.setText("OCR")

        self.ocrswitch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['ocr'], textOff='关闭',textOn='使用')
        self.customSetGeometry(self.ocrswitch, 300, 70, 66, 22)
        self.ocrswitch.clicked.connect(functools.partial(textsourcechange,self,'ocr'))
 
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 400, 70, 100, 20)
        label.setText("Textractor")
 
        self.textractorswitch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['textractor'], textOff='关闭',textOn='使用')
        self.customSetGeometry(self.textractorswitch, 500, 70, 66, 22)
        self.textractorswitch.clicked.connect(functools.partial(textsourcechange,self,'textractor')) 

         
        self.selectbutton = QPushButton( "", self.tab_1)
        self.customSetIconSize(self.selectbutton, 20, 20)
        self.customSetGeometry(self.selectbutton, 580, 70, 20, 20)
        self.selectbutton.setStyleSheet("background: transparent;") 
        
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 600, 70, 110, 20)
        label.setText("选择游戏")

        
        self.selecthookbutton = QPushButton( "", self.tab_1)
        self.customSetIconSize(self.selecthookbutton, 20, 20)
        self.customSetGeometry(self.selecthookbutton, 580, 105, 20, 20)
        self.selecthookbutton.setStyleSheet("background: transparent;") 
        
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 600, 105, 110, 20)
        label.setText("选择文本")

        self.selectbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959'))
        self.selectbutton.clicked.connect(functools.partial(settingtextractor,self) )
        
        self.selecthookbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959'))
        self.selecthookbutton.clicked.connect(functools.partial(settingsource,self) )
        self.sourceswitchs={'copy':self.copyboardswitch,'ocr':self.ocrswitch,'textractor':self.textractorswitch}# ,'textractor_pipe':self.Textractor_forward_extension_switch}

        self.hookselectdialog=gui.selecthook.hookselect(self)
 
         

        self.resetsourcesignal.connect(functools.partial(resetsource,self))  
def readerchange(self,who,checked):   
    if checked : 
        
        globalconfig['reader'][who]=True
    else:
        globalconfig['reader'][who]=False  
    
    
    
    if checked : 
            
        self.object.startreader()  

def settingtextractor(self): 
        if globalconfig['sourcestatus']['textractor']==False:
            return 
        self.hookselectdialog.hide()
        import win32process,win32api 
        self.hide()
        self.a=gui.attachprocessdialog.AttachProcessDialog()
        
        
        if(self.a.exec_()): 
            try:
                pid,pexe=( self.a.selectedp)   
            except:
                self.show()
                return 
            
            try:
                process=win32api.OpenProcess(2097151,False, pid) #PROCESS_ALL_ACCESS
            except pywintypes.error:
                self.object.translation_ui.displayraw.emit(f'打开进程失败！','#ff0000') 
                return
            if 'textsource' in dir(self.object) and self.object.textsource and self.object.textsource.ending==False:
                self.object.textsource.end() 
                self.object.hookselectdialog=gui.selecthook.hookselect(self )
            else:
                self.show()
            arch='86' if win32process.IsWow64Process( process)  else '64' 
            self.hookpid=pid
            self.object.textsource=textractor(self.object.textgetmethod,self.hookselectdialog,pid,pexe,arch) 
            # if not os.path.exists('./files/savehook.json'):
            #     js={}
            # with open('./files/savehook.json','r',encoding='utf8') as ff:
            #     js=json.load(ff)
            # if pexe in js:
            #     self.object.textsource.selectedhook=js[pexe]
            # else:
            settingsource(self)
        else:
            self.show()
def settingsource(self):
        if globalconfig['sourcestatus']['textractor']==False:
            return 
        self.hide()
        self.hookselectdialog.show() 
        self.hookselectdialog.hiding=False
def resetsource(self):
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
        if checked : 
            self.object.starttextsource() 
        self.selectbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959')) 
        
        self.selecthookbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959')) 
        if who=='textractor':
            settingtextractor(self)
    # 翻译设定标签栏