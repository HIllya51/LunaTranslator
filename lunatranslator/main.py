from threading import Thread
import time 
import os
import sys
from traceback import print_exc 
#sys.stdout = open("mylog.txt", "w")
dirname, filename = os.path.split(os.path.abspath(__file__))
sys.path.append(dirname) 
from PyQt5.QtCore import QCoreApplication ,Qt,pyqtSignal
from PyQt5.QtWidgets import  QApplication 
import utils.screen_rate 
from concurrent.futures import ThreadPoolExecutor,as_completed
from utils.wrapper import timer,threader 
import gui.rangeselect   
import gui.settin   
import gui.selecthook   
import gui.translatorUI
from utils.config import globalconfig 
import importlib
from functools import partial
class MAINUI() :
    
    def __init__(self) -> None:
        self.screen_scale_rate = utils.screen_rate.getScreenRate() 
        self.translators={}
        self.reader=None
        self.rect=None
    def textgetmethod(self,paste_str,shortlongskip=True):
        if paste_str=='':
            return
        if len(paste_str)>2000 or   len(paste_str.split('\n'))>20:
            return 
        
        postsolve=importlib.import_module('postprocess.post').POSTSOLVE
        try:
            paste_str=postsolve(paste_str)
        except:
            print_exc()
            



        self.translation_ui.original=paste_str 
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
            if 'hira_' in dir(self):
                hiratext2,hiratext1,rawtext,guiuse=self.hira_.fy(paste_str)  
                self.translation_ui.displayraw1.emit(guiuse,globalconfig['rawtextcolor'],1)
        elif globalconfig['isshowrawtext']:
            self.translation_ui.displayraw1.emit(paste_str,globalconfig['rawtextcolor'],1)
        else:
            self.translation_ui.displayraw1.emit(paste_str,globalconfig['rawtextcolor'],0)
         
        if shortlongskip and  (len(paste_str)<6 or len(paste_str)>150 or len(paste_str.split('\n'))>5):
            return 
        for engine in self.translators:
            #print(engine)
            self.translators[engine].gettask(paste_str) 
    @threader
    def startreader(self):
        if globalconfig['reader']:
             
            from tts.windowstts import tts   
            use=None  
            if globalconfig['reader']['windows']:
                     
                self.reader=tts( self.settin_ui.voicelistsignal)
                  
           
    @threader
    def starttextsource(self):
        
        from textsource.ocrtext import ocrtext
        from textsource.copyboard import copyboard
        from textsource.namepipe import namepipe
        from textsource.textractor import textractor 
        if hasattr(self,'textsource') and self.textsource and self.textsource.ending==False :
            self.textsource.end()  
        if True:#try:
            classes={'ocr':ocrtext,'copy':copyboard,'textractor':textractor,'textractor_pipe':namepipe}
            use=None  
            for k in classes: 
                if globalconfig['sourcestatus'][k]:
                    use=k 
            if use is None:
                self.textsource=None
            elif use=='textractor':
                pass
            elif use=='ocr':
                
                self.textsource=classes[use](self.textgetmethod,self) 
            elif use=='textractor_pipe': 
                
                self.textsource=classes[use](self.textgetmethod) 
                return True
                
            else:
                self.textsource=classes[use](self.textgetmethod) 
             
           
            return True 
    @threader
    def starthira(self): 
        from utils.hira import hira   
        self.hira_=hira()  
    

    @threader
    def prepare(self,now=None):  
        
        
        if now:
            Thread(target=self.fanyiloader,args=(now,)).start()
        else:
            for source in globalconfig['fanyi']: 
                if globalconfig['fanyi'][source]['use']:
                    Thread(target=self.fanyiloader,args=(source,)).start()
             
    def fanyiloader(self,classname):
                if classname in self.translators:
                    self.translators[classname].__init__()
                else:
                    aclass=importlib.import_module('translator.'+classname).TS
                    _=aclass()
                    _.show=partial(self.translation_ui.displayres.emit,classname)
                    self.translators[classname]=_ 
    # 主函数
     
    def aa(self):
        t1=time.time()
        self.translation_ui =gui.translatorUI.QUnFrameWindow(self)  
        self.translation_ui.show()  
        self.translation_ui.displayraw.emit('加载中','#0000ff')
        print(time.time()-t1)
        
        self.prepare()
        print(time.time()-t1)
        self.starthira()
        print(time.time()-t1)
        self.starttextsource() 
        self.startreader()
        print(time.time()-t1) 
        # 设置界面
        self.settin_ui =gui.settin.Settin(self)
        # 翻译界面设置页面按键信号
        print(time.time()-t1) 
        self.range_ui =gui.rangeselect.rangeadjust(self)  
        print(time.time()-t1) 
        self.translation_ui.displayraw.emit('加载完毕','#0000ff')
    def main(self) : 
        # 自适应高分辨率
        t1=time.time()
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        app = QApplication(sys.argv) 
        #print(time.time()-t1)
        self.aa()
        app.exit(app.exec_())
        
if __name__ == "__main__" :
 
    app = MAINUI()
    app.main()