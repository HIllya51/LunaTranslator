import time
t1=time.time()   
import os
import json

import sys
# if os.path.exists('./debug')==False:
#     os.mkdir('./debug')
#sys.stderr=open('./stderr.txt','a',encoding='utf8')
# sys.stdout=open('./debug/stdout.txt','a',encoding='utf8')
from traceback import  print_exc  

dirname, filename = os.path.split(os.path.abspath(__file__))
sys.path.append(dirname)  

import threading,win32gui 
from PyQt5.QtCore import QCoreApplication ,Qt ,QObject,pyqtSignal
from PyQt5.QtWidgets import  QApplication ,QGraphicsScene,QGraphicsView,QDesktopWidget,QStyle
import utils.screen_rate  
 
from utils.wrapper import threader 
from gui.rangeselect    import rangeadjust
from  gui.settin   import Settin
 
from tts.windowstts import tts  as windowstts
from tts.huoshantts import tts as huoshantts
from tts.azuretts import tts as azuretts
from tts.voiceroid2 import tts as voiceroid2
from tts.voicevox import tts as voicevox
import  gui.selecthook   
import pyperclip
from utils.getpidlist import getwindowlist,getarch,getpidexe
 
import gui.translatorUI
from utils.config import globalconfig ,savehook_new,noundictconfig,transerrorfixdictconfig
 
from utils.xiaoxueguan import xiaoxueguan
from utils.edict import edict
from utils.linggesi import linggesi
import importlib
from functools import partial  
from gui.attachprocessdialog import AttachProcessDialog
import win32api,win32con,win32process
import re
import socket
socket.setdefaulttimeout(globalconfig['translatortimeout'])
 
import xml.etree.ElementTree as ET  
class MAINUI(QObject) :
    mainuiloadok=pyqtSignal()
    def __init__(self) -> None:
        self.screen_scale_rate = utils.screen_rate.getScreenRate() 
        self.translators={}
        self.reader=None
        self.rect=None
        self.textsource=None
        self.savetextractor=None
        super(MAINUI,self).__init__( )
        self.mainuiloadok.connect(self.mainuiloadafter)
    @threader  
    def loadvnrshareddict(self):
        cnt=0
        cnt1=0
        regcnt=0
        cnt2=0
        sim=0
        skip=0
        self.vnrshareddict={}
        self.vnrsharedreg=[]
        if globalconfig['gongxiangcishu']['use'] and os.path.exists(globalconfig['gongxiangcishu']['path']) :
            xml=ET.parse(globalconfig['gongxiangcishu']['path']) 
            
            for _ in xml.find('terms').findall('term'):
                
                src=_.find('sourceLanguage').text
                tgt=_.find('language').text
                if tgt=='en':
                    continue
                pattern=_.find('pattern').text
                try:
                    text=_.find('text').text
                except:
                    text=''
                cnt+=1

                try:
                    regex=_.find('regex').text
                    regcnt+=1
                    #搞不明白这个玩意
                    #self.vnrsharedreg.append((re.compile(pattern),src,tgt,text))
                    #print(pattern,text,src,tgt)
                except:
                    cnt2+=1
                    # if pattern not in self.vnrshareddict:
                    #     self.vnrshareddict[pattern]=[{'src':src,'tgt':tgt,'text':text }]
                    # else:
                    #     self.vnrshareddict[pattern]+=[{'src':src,'tgt':tgt,'text':text }]
                    if pattern in self.vnrshareddict and self.vnrshareddict[pattern]['tgt']=='zhs':
                         
                        continue
                    if src==tgt:# and tgt=='ja':
                        sim+=1
                        #print(pattern,{'src':src,'tgt':tgt,'text':text })
                        continue
                    if 'eos' in text or 'amp' in text or '&' in text:
                        skip+=1
                        continue
                    self.vnrshareddict[pattern]={'src':src,'tgt':tgt,'text':text }
                    cnt1+=1
        #print(cnt1,cnt2,regcnt,cnt,sim,skip)
        # print(len(list(self.vnrsharedreg)))
        # print(len(list(self.vnrshareddict.keys())))
    def solvebeforetrans(self,content):
    
        zhanweifu=0
        mp1={} 
        mp2={}
        mp3={}
        if noundictconfig['use'] :
            for key in noundictconfig['dict']: 
                usedict=False
                if type(noundictconfig['dict'][key][0])==str:
                    usedict=True
                else:

                    if noundictconfig['dict'][key][0]=='0' :
                        usedict=True
                
                    if noundictconfig['dict'][key][0]==self.textsource.md5:
                        usedict=True
                     
                if usedict and  key in content:
                    xx=f'ZX{chr(ord("B")+zhanweifu)}Z'
                    content=content.replace(key,xx)
                    mp1[xx]=key
                    zhanweifu+=1
        if globalconfig['gongxiangcishu']['use']:
            for key in self.vnrshareddict:
                
                if key in content:
                    # print(key)
                    # if self.vnrshareddict[key]['src']==self.vnrshareddict[key]['tgt']:
                    #     content=content.replace(key,self.vnrshareddict[key]['text'])
                    # else:
                        xx=f'ZX{chr(ord("B")+zhanweifu)}Z'
                        content=content.replace(key,xx)
                        mp2[xx]=key
                        zhanweifu+=1
             
        return content,(mp1,mp2,mp3)
    def solveaftertrans(self,res,mp): 
        mp1,mp2,mp3=mp
        #print(res,mp)#hello
        if noundictconfig['use'] :
            for key in mp1: 
                reg=re.compile(re.escape(key), re.IGNORECASE)
                if type(noundictconfig['dict'][mp1[key]])==str:
                    v=noundictconfig['dict'][mp1[key]]
                elif type(noundictconfig['dict'][mp1[key]])==list:
                    v=noundictconfig['dict'][mp1[key]][1]
                res=reg.sub(v,res)
        if globalconfig['gongxiangcishu']['use']:
            for key in mp2: 
                reg=re.compile(re.escape(key), re.IGNORECASE)
                res=reg.sub(self.vnrshareddict[mp2[key]]['text'],res)
             
        if transerrorfixdictconfig['use']:
            for key in transerrorfixdictconfig['dict']:
                res=res.replace(key,transerrorfixdictconfig['dict'][key])
        return res
    def textgetmethod(self,paste_str,shortlongskip=True):
        if paste_str=='':
            return 
        if paste_str[:len('<notrans>')]=='<notrans>':
            self.translation_ui.displayraw1.emit([],paste_str[len('<notrans>'):],globalconfig['rawtextcolor'],1)
            return 
        if paste_str=='':
            return
        if len(paste_str)>100000:
            return 

        t1=time.time()
        postsolve=importlib.import_module('postprocess.post').POSTSOLVE
        try:
            paste_str=postsolve(paste_str)
        except:
            print_exc() 
        if len(paste_str)>10000:
            return 
        if globalconfig['outputtopasteboard'] and globalconfig['sourcestatus']['copy']==False:
            pyperclip.copy(paste_str)
        

        self.translation_ui.original=paste_str 
        if 'hira_' in dir(self):
                hira=self.hira_.fy(paste_str)
        else:
            hira=[]
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
              
            self.translation_ui.displayraw1.emit(hira,paste_str,globalconfig['rawtextcolor'],2)
        elif globalconfig['isshowrawtext']:
            self.translation_ui.displayraw1.emit(hira,paste_str,globalconfig['rawtextcolor'],1)
        else:
            self.translation_ui.displayraw1.emit(hira,paste_str,globalconfig['rawtextcolor'],0)
        try:
            if globalconfig['autoread']:
                self.reader.read(paste_str)
        except:
            pass
            
        skip=False 
        paste_str_solve= self.solvebeforetrans(paste_str) 
        if shortlongskip and  (len(paste_str_solve[0])<globalconfig['minlength'] or len(paste_str_solve[0])>globalconfig['maxlength'] ):
            skip=True  
        if (set(paste_str) -set('「…」、。？！―'))==set():
            skip=True 
             
        for engine in self.translators:
            #print(engine)
            self.translators[engine].gettask((paste_str,paste_str_solve,skip)) 
        try:
            if skip==False and globalconfig['transkiroku']  and 'sqlwrite2' in dir(self.textsource):
                paste_str=paste_str.replace('"','""')   
                ret=self.textsource.sqlwrite.execute(f'SELECT * FROM artificialtrans WHERE source = "{paste_str}"').fetchone()
                if ret is  None:                     
                    self.textsource.sqlwrite.execute(f'INSERT INTO artificialtrans VALUES(NULL,"{paste_str}","","");')
                
                    self.textsource.sqlwrite.commit() 
                
                ret=self.textsource.sqlwrite2.execute(f'SELECT * FROM artificialtrans WHERE source = "{paste_str}"').fetchone()
                if ret is  None:                     
                    self.textsource.sqlwrite2.execute(f'INSERT INTO artificialtrans VALUES(NULL,"{paste_str}","{json.dumps({})}");')
                
                    self.textsource.sqlwrite2.commit() 
        except:
            print_exc()
    @threader
    def startreader(self):
        if globalconfig['reader']:
            use=None
            ttss={'windowstts':windowstts,
                    'huoshantts':huoshantts,
                    'azuretts':azuretts,
                    'voiceroid2':voiceroid2,
                    'voicevox':voicevox}
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
        #不能删
        if now:
            threading.Thread(target=self.fanyiloader,args=(now,)).start()
        else:
            for source in globalconfig['fanyi']: 
                if globalconfig['fanyi'][source]['use']:
                    threading.Thread(target=self.fanyiloader,args=(source,)).start()
    @threader
    def startxiaoxueguan(self,type_=0):
        if type_==0:
            self.xiaoxueguan=xiaoxueguan()
            self.edict=edict()
            self.linggesi=linggesi()
        elif type_==1:
            self.xiaoxueguan=xiaoxueguan()
        elif type_==2:
            self.edict=edict()
        elif type_==3:
            self.linggesi=linggesi()
    def _maybeyrengong(self,classname,contentraw,_):
        
        classname,res,mp=_
        if classname not in ['rengong','premt']: 
            res=self.solveaftertrans(res,mp)
        if globalconfig['fanjian']:
            import zhconv  
        if classname=='premt':
            for k in res:
                if globalconfig['fanjian']!=0:
                    
                    res[k]=zhconv.convert(res[k], ['zh-cn', 'zh-tw', 'zh-hk', 'zh-sg', 'zh-hans', 'zh-hant'][globalconfig['fanjian']])

                if k  in globalconfig['fanyi']:
                    self.translation_ui.displayres.emit(k,res[k])
                else:
                    self.translation_ui.displayres.emit('premt',res[k])
        else:
            if globalconfig['fanjian']!=0 and globalconfig['tgtlang']==0:
                res=zhconv.convert(res, ['zh-cn', 'zh-tw', 'zh-hk', 'zh-sg', 'zh-hans', 'zh-hant'][globalconfig['fanjian']])
            self.translation_ui.displayres.emit(classname,res)
        
        if classname not in ['rengong','premt']:
             
            res=res.replace('"','""')   
            contentraw=contentraw.replace('"','""')   
            try:
                if   globalconfig['transkiroku'] and 'sqlwrite' in dir(self.textsource):
                    if globalconfig['transkirokuuse']==classname:
                        self.textsource.sqlwrite.execute(f'UPDATE artificialtrans SET machineTrans = "{res}" WHERE source = "{contentraw}"')
                        self.textsource.sqlwrite.commit() 
                    elif classname not in ['rengong','premt']:
                        ret=self.textsource.sqlwrite.execute(f'SELECT * FROM artificialtrans WHERE source = "{contentraw}"').fetchone()
                        
                        if ret is None or ret[2] =='':                     
                            self.textsource.sqlwrite.execute(f'UPDATE artificialtrans SET machineTrans = "{res}" WHERE source = "{contentraw}"')
                        
                            self.textsource.sqlwrite.commit() 
            except:
                print_exc()
            try:
                if  globalconfig['transkiroku'] and 'sqlwrite2' in dir(self.textsource):
                    ret=self.textsource.sqlwrite2.execute(f'SELECT machineTrans FROM artificialtrans WHERE source = "{contentraw}"').fetchone() 
                
                    ret=json.loads(ret[0]) 
                    ret[classname]=res
                    ret=json.dumps(ret).replace('"','""') 
                    
                    self.textsource.sqlwrite2.execute(f'UPDATE artificialtrans SET machineTrans = "{ret}" WHERE source = "{contentraw}"')
                
                    self.textsource.sqlwrite2.commit() 
            except:
                print_exc()
    def fanyiloader(self,classname):
                    try:
                        aclass=importlib.import_module('translator.'+classname).TS
                    except:
                        return
                    aclass.settypename(classname)
                    if classname in ['rengong','premt']:
                        _=aclass(self)
                    else:
                        _=aclass()
                    _.show=partial(self._maybeyrengong,classname)
                    self.translators[classname]=_ 
    # 主函数
    def setontopthread(self):
        while True:
            #self.translation_ui.keeptopsignal.emit() 
            
            try:  
                
                #if self.settin_ui.isHidden():
                    win32gui.SetWindowPos(int(self.translation_ui.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE)  
                #else:
                    #win32gui.SetWindowPos(int(self.settin_ui.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE)  
                 #   pass
                #win32gui.BringWindowToTop(int(self.translation_ui.winId())) 
            except:
                print_exc() 
            time.sleep(0.3)


    def onwindowloadautohook(self):
        if not(globalconfig['autostarthook'] and globalconfig['sourcestatus']['textractor']):
            return 
        else:
            if 'textsource' not in dir(self) or self.textsource is None:
                
            
                try:
                        hwnd=win32gui.GetForegroundWindow()
                        pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                        name_=getpidexe(pid)
                         
                        if name_ in savehook_new: 
                            self.settin_ui.autostarthooksignal.emit(pid,hwnd, name_,(savehook_new[name_]))
                    
                except:
                        print_exc()
                
                
    def autohookmonitorthread(self):
        while True:
            self.onwindowloadautohook()
            time.sleep(0.5)
    def aa(self): 
        self.translation_ui =gui.translatorUI.QUnFrameWindow(self)   
        
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
        threading.Thread(target=self.mainuiloadok.emit).start()
#        self.mainuiloadok.emit() 
    def mainuiloadafter(self):   
        
        #print(time.time()-t1)
        self.loadvnrshareddict()
        self.prepare()  
        self.starthira()  
        self.starttextsource() 
        #print(time.time()-t1)
        self.settin_ui = Settin(self) 
        #print(time.time()-t1)
        self.startreader() 
        self.startxiaoxueguan()
        self.AttachProcessDialog=AttachProcessDialog(self.translation_ui)
        self.range_ui = rangeadjust(self)   
        self.hookselectdialog=gui.selecthook.hookselect(self ,self.translation_ui)
        threading.Thread(target=self.autohookmonitorthread).start()   
        threading.Thread(target=self.setontopthread).start()
        
if __name__ == "__main__" :
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    main = MAINUI()

    app = QApplication(sys.argv) 
    app.setQuitOnLastWindowClosed(False)
    main.scrollwidth=(app.style().pixelMetric(QStyle.PM_ScrollBarExtent))
    main.aa()
    app.exit(app.exec_())
