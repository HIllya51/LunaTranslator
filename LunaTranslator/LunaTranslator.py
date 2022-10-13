import time
starttime=time.time() 
from threading import Thread
import os
import json
import sys
if os.path.exists('./debug')==False:
    os.mkdir('./debug')
sys.stderr=open('./debug/stderr.txt','a',encoding='utf8')
sys.stdout=open('./debug/stdout.txt','a',encoding='utf8')
from traceback import  print_exc  
dirname, filename = os.path.split(os.path.abspath(__file__))
sys.path.append(dirname)  
import threading,win32gui
from PyQt5.QtCore import QCoreApplication ,Qt ,pyqtSignal,QUrl
from PyQt5.QtWidgets import  QApplication ,QGraphicsScene,QGraphicsView,QDesktopWidget
import utils.screen_rate  
from utils.wrapper import timer,threader 
import gui.rangeselect   
import gui.settin     
from tts.windowstts import tts  as windowstts
from tts.huoshantts import tts as huoshantts
from tts.azuretts import tts as azuretts
import gui.selecthook
import pyperclip
from utils.getpidlist import getwindowlist
import gui.translatorUI
from utils.config import globalconfig ,savehook_new
import importlib
from functools import partial 
#print(time.time()-starttime)
import win32api,win32con,win32process
import sqlite3
class MAINUI() :
    
    def __init__(self) -> None:
        self.screen_scale_rate = utils.screen_rate.getScreenRate() 
        self.translators={}
        self.reader=None
        self.rect=None
        self.textsource=None
        self.savetextractor=None
        
    def textgetmethod(self,paste_str,shortlongskip=True):
        if paste_str[:len('<notrans>')]=='<notrans>':
            self.translation_ui.displayraw1.emit(paste_str[len('<notrans>'):],globalconfig['rawtextcolor'],1)
            return 
        if paste_str=='':
            return
        


        postsolve=importlib.import_module('postprocess.post').POSTSOLVE
        try:
            paste_str=postsolve(paste_str)
        except:
            print_exc() 
        if globalconfig['outputtopasteboard'] and globalconfig['sourcestatus']['copy']==False:
            pyperclip.copy(paste_str)


        self.translation_ui.original=paste_str 
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
            if 'hira_' in dir(self):
                hiratext2,hiratext1,rawtext,guiuse=self.hira_.fy(paste_str)  
                self.translation_ui.displayraw1.emit(guiuse,globalconfig['rawtextcolor'],1)
        elif globalconfig['isshowrawtext']:
            self.translation_ui.displayraw1.emit(paste_str,globalconfig['rawtextcolor'],1)
        else:
            self.translation_ui.displayraw1.emit(paste_str,globalconfig['rawtextcolor'],0)
        try:
            if globalconfig['autoread']:
                self.reader.read(paste_str)
        except:
            pass
        if shortlongskip and  (len(paste_str)<globalconfig['minlength'] or len(paste_str)>globalconfig['maxlength'] ):
            skip=True 
        else:
            skip=False
        for engine in self.translators:
            #print(engine)
            self.translators[engine].gettask((paste_str,skip)) 
        if skip==False and globalconfig['transkiroku']  and 'sqlwrite' in dir(self.textsource):
            ret=self.textsource.sqlwrite.execute(f'SELECT * FROM artificialtrans WHERE source = "{paste_str}"').fetchone()
            if ret is  None:                     
                self.textsource.sqlwrite.execute(f'INSERT INTO artificialtrans VALUES(NULL,"{paste_str}","","");')
            
                self.textsource.sqlwrite.commit() 
    @threader
    def startreader(self):
        if globalconfig['reader']:
            use=None
            ttss={'windowstts':windowstts,
                    'huoshantts':huoshantts,
                    'azuretts':azuretts}
            for key in ttss:
                if globalconfig['reader'][key]['use']:
                    use=key
                    self.reader_usevoice=use
                    break
            if use:
                
                #from tts.
                
                self.reader=ttss[use]( self.settin_ui.voicelistsignal,self.settin_ui.mp3playsignal) 
    @threader
    def starttextsource(self):
         
        if hasattr(self,'textsource') and self.textsource and self.textsource.ending==False :
            self.textsource.end()  
        if True:#try:
            #classes={'ocr':ocrtext,'copy':copyboard,'textractor':textractor}#,'textractor_pipe':namepipe}
            classes=['ocr','copy','textractor']
            use=None  
            for k in classes: 
                if globalconfig['sourcestatus'][k]:
                    use=k 
                    break
            if use is None:
                self.textsource=None
            elif use=='textractor':
                #from textsource.textractor import textractor 
                 
                pass
            elif use=='ocr':
                from textsource.ocrtext import ocrtext
                self.textsource=ocrtext(self.textgetmethod,self) 
            # elif use=='textractor_pipe': 
                    #from textsource.namepipe import namepipe
            #     self.textsource=classes[use](self.textgetmethod) 
            #     return True
                
            elif use=='copy': 
                from textsource.copyboard import copyboard 
                self.textsource=copyboard(self.textgetmethod) 
              
            return True 
    @threader
    def starthira(self): 
        

        from utils.hira import hira   
        self.hira_=hira()  
    

    @threader
    def prepare(self,now=None):  
        
        
        import requests
        if now:
            Thread(target=self.fanyiloader,args=(now,)).start()
        else:
            for source in globalconfig['fanyi']: 
                if globalconfig['fanyi'][source]['use']:
                    Thread(target=self.fanyiloader,args=(source,)).start()
    def _maybeyrengong(self,classname,contentraw,res):
        if globalconfig['sourcestatus']['textractor'] and globalconfig['transkiroku']:
            if globalconfig['transkirokuuse']==classname:
                self.textsource.sqlwrite.execute(f'UPDATE artificialtrans SET machineTrans = "{res}" WHERE source = "{contentraw}"')
                self.textsource.sqlwrite.commit() 
            elif classname!='rengong':
                ret=self.textsource.sqlwrite.execute(f'SELECT * FROM artificialtrans WHERE source = "{contentraw}"').fetchone()
                
                if ret is None or ret[2] =='':                     
                    self.textsource.sqlwrite.execute(f'UPDATE artificialtrans SET machineTrans = "{res}" WHERE source = "{contentraw}"')
                
                    self.textsource.sqlwrite.commit() 
        self.translation_ui.displayres.emit(classname,res)
    def fanyiloader(self,classname):
                    try:
                        aclass=importlib.import_module('translator.'+classname).TS
                    except:
                        return
                    aclass.settypename(classname)
                    if classname=='rengong':
                        _=aclass(self)
                    else:
                        _=aclass()
                    _.show=partial(self._maybeyrengong,classname)
                    self.translators[classname]=_ 
    # 主函数
    def setontopthread(self):
        while True:
            #self.translation_ui.keeptopsignal.emit() 
             
            win32gui.BringWindowToTop(int(self.translation_ui.winId())) 
        
            time.sleep(0.5)


    def onwindowloadautohook(self):
        if not(globalconfig['autostarthook'] and globalconfig['sourcestatus']['textractor']):
            return False
        else:
            if 'textsource' not in dir(self) or self.textsource is None:
                 
                plist = getwindowlist() 
                for pid in plist:
                    #print(pid)
                    try:
                            hwnd = win32api.OpenProcess(
                                win32con.PROCESS_ALL_ACCESS, False, (pid))
                            name_ = win32process.GetModuleFileNameEx(
                                hwnd, None)
                    except:
                        continue
                    
                    if name_ in savehook_new:
                        self.settin_ui.autostarthooksignal.emit(pid, name_,(savehook_new[name_]))
                        return True
        return False
    def autohookmonitorthread(self):
        while True:
            if(self.onwindowloadautohook()):
                #break
                pass
            time.sleep(0.5)
    def aa(self):
        t1=time.time()
        if os.path.exists('./transkiroku')==False:
            os.mkdir('./transkiroku')
        self.translation_ui =gui.translatorUI.QUnFrameWindow(self)  
        #print(time.time()-t1)
        if globalconfig['rotation']==0:
            self.translation_ui.show()
            #print(time.time()-t1) 
        else:
            self.scene = QGraphicsScene()
            
            self.oneTestWidget = self.scene.addWidget(self.translation_ui) 
            self.oneTestWidget.setRotation(globalconfig['rotation']*90)
            self.view = QGraphicsView(self.scene)
            self.view.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
            self.view.setAttribute(Qt.WA_TranslucentBackground) 
            self.view.setStyleSheet('background-color: rgba(255, 255, 255, 0);')
            self.view.setGeometry(QDesktopWidget().screenGeometry())
            self.view.show()      
        #print(time.time()-t1)
        threading.Thread(target=self.setontopthread).start()
        #print(time.time()-t1)
        self.prepare()  
        self.starthira()  
        self.starttextsource() 
        #print(time.time()-t1)
        self.settin_ui =gui.settin.Settin(self) 
        #print(time.time()-t1)
        self.startreader() 
        self.range_ui =gui.rangeselect.rangeadjust(self)   
        self.hookselectdialog=gui.selecthook.hookselect(self )
        threading.Thread(target=self.autohookmonitorthread).start()
        #self.translation_ui.displayraw.emit('欢迎','#0000ff')
        #print(time.time()-t1)
        #print(time.time()-t1)
    def main(self) : 
        # 自适应高分辨率
        t1=time.time()
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        app = QApplication(sys.argv) 
        app.setQuitOnLastWindowClosed(False)
        
        self.aa()
        ##print(time.time()-t1)
        #print(time.time()-starttime)
        app.exit(app.exec_())
        
if __name__ == "__main__" :
     
    app = MAINUI()
    
    app.main()
