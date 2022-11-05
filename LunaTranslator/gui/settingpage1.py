
from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton
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
        # 选项卡界面
        self.tab_1 = QWidget()
        self.customSetGeometry(self.tab_1, 0, 0, self.window_width, self.window_height)
        self.tab_widget.addTab(self.tab_1,"基本设置") 
 
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 25, 160, 20)
        label.setText("选择文本输入源") 
       


        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 70, 60, 20)
        label.setText("剪切板") 
        self.copyboardswitch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['copy'] )
        self.customSetGeometry(self.copyboardswitch, 100, 70, 20,20) 
        self.copyboardswitch.clicked.connect(functools.partial(textsourcechange,self,'copy')) 
        
        # label = QLabel(self.tab_1)
        # self.customSetGeometry(label, 20, 105, 300, 20)
        # label.setText("Textractor插件") 
        # self.Textractor_forward_extension_switch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['textractor_pipe'], textOff='关闭',textOn='打开')
        # self.customSetGeometry(self.Textractor_forward_extension_switch, 130, 105, 20,20)
        # self.Textractor_forward_extension_switch.clicked.connect(functools.partial(textsourcechange,self,'textractor_pipe')) 

        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 220, 70, 35, 20)
        label.setText("OCR")

        self.ocrswitch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['ocr'] )
        self.customSetGeometry(self.ocrswitch, 300, 70, 20,20)
        self.ocrswitch.clicked.connect(functools.partial(textsourcechange,self,'ocr'))
 
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 400, 70, 100, 20)
        label.setText("Textractor")
 
        self.textractorswitch =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['sourcestatus']['textractor'] )
        self.customSetGeometry(self.textractorswitch, 500, 70, 20,20)
        self.textractorswitch.clicked.connect(functools.partial(textsourcechange,self,'textractor')) 


        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 150,220, 20)
        label.setText("提取的文本自动复制到剪贴板")
 
        self.outputtopasteboard =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['outputtopasteboard'] )
        self.customSetGeometry(self.outputtopasteboard, 240, 150, 20,20)
        self.outputtopasteboard.clicked.connect(lambda x:globalconfig.__setitem__('outputtopasteboard',x)) 

        

        # label = QLabel(self.tab_1)
        # self.customSetGeometry(label, 20, 180,220, 20)
        # label.setText("OCR模式绑定前景窗口")
 
        # b =gui.switchbutton.MySwitch(self.tab_1, sign= globalconfig['ocrautobindwindow'] )
        # self.customSetGeometry(b, 240, 180, 20,20)
        # b.clicked.connect(lambda x:globalconfig.__setitem__('ocrautobindwindow',x)) 
         
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
        
         
        # self.p=None
        # self.qq = QPushButton( "wewq", self.tab_1)
        # self.customSetIconSize(self.qq, 20, 20)
        # self.customSetGeometry(self.qq, 580, 305, 20, 20)
        # self.qq.setStyleSheet("background: transparent;") 
        # self.qq.clicked.connect(lambda :start_process(self))

        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 600, 105, 110, 20)
        label.setText("选择文本")

        self.selectbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959'))
        self.selectbutton.clicked.connect(functools.partial(settingtextractor,self,True) )
        
        self.selecthookbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959'))
        self.selecthookbutton.clicked.connect(functools.partial(settingsource,self) )
        self.sourceswitchs={'copy':self.copyboardswitch,'ocr':self.ocrswitch,'textractor':self.textractorswitch}# ,'textractor_pipe':self.Textractor_forward_extension_switch}
 

        self.resetsourcesignal.connect(functools.partial(resetsource,self))  
# def handle_stdout(self):
#         data = self.p.readAllStandardOutput()
#         stdout = bytes(data).decode("utf16")
#         print(stdout)
# def start_process(self):
#         if self.p is None:  # No process running.
             
#             self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
#             self.p.readyReadStandardOutput.connect(lambda : handle_stdout(self))  
#             self.p.start(r'C:\dataH\Textractor5.20\x64\TextractorCLI.exe')
         
#             self.p.write(('attach -P24512\r\n'.encode('utf-16-le')))
             
#         else:
#             ##inserthook必须重新手动按一下，一起写入就会结束？？？？
#             self.p.write(('HS-24@0:kernel32.dll:lstrcpyA -P24512\r\n'.encode('utf-16-le')))
            
def readerchange(self,who,checked):   
    if checked : 
        
        globalconfig['reader'][who]=True
    else:
        globalconfig['reader'][who]=False  
    
    
    
    if checked : 
            
        self.object.startreader()  

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
                self.object.textsource.reset(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,pexe,arch)

            else:
                
                self.object.textsource=textractor(self.object,self.object.textgetmethod,self.object.hookselectdialog,pid,pexe,arch) 
                
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
                self.object.translation_ui.bindcropwindowbutton.setIcon((qtawesome.icon("fa.windows" ,color='white')))

        if checked : 
            self.object.starttextsource() 
        self.selectbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959')) 
        
        self.selecthookbutton.setIcon(qtawesome.icon("fa.gear", color="#FF69B4" if globalconfig['sourcestatus']['textractor'] else '#595959')) 
        if who=='textractor':
            settingtextractor(self,True)
        
        self.object.translation_ui.showhidetoolbuttons()
    # 翻译设定标签栏