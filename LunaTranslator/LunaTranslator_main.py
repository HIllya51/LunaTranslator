import time
t1=time.time()   
import os
import json
import Levenshtein
import sys 
from traceback import  print_exc  
import requests
dirname, filename = os.path.split(os.path.abspath(__file__))
sys.path.append(dirname)  
from utils.config import globalconfig ,savehook_new,noundictconfig,transerrorfixdictconfig,setlanguage 
import threading,win32gui 
from PyQt5.QtCore import QCoreApplication ,Qt ,QObject,pyqtSignal
from PyQt5.QtWidgets import  QApplication ,QGraphicsScene,QGraphicsView,QDesktopWidget,QStyle  

from utils.minmaxmove import minmaxmoveobservefunc
from utils.wrapper import threader 
from gui.showword import searchwordW
from gui.rangeselect    import rangeadjust
from  gui.settin   import Settin
from utils.getpidlist import pid_running
from tts.windowstts import tts  as windowstts
from tts.huoshantts import tts as huoshantts
from tts.azuretts import tts as azuretts
from tts.voiceroid2 import tts as voiceroid2
from tts.voicevox import tts as voicevox

from textsource.copyboard import copyboard   
from textsource.ocrtext import ocrtext
from textsource.txt import txt 
import  gui.selecthook    
from utils.getpidlist import getpidexe,ListProcess,getScreenRate
 
import gui.translatorUI
from queue import Queue

import gui.transhist 
import gui.edittext
import importlib
from functools import partial  
from gui.attachprocessdialog import AttachProcessDialog
import win32event,win32con,win32process,win32api 
import re
import socket
socket.setdefaulttimeout(globalconfig['translatortimeout'])
from utils.post import POSTSOLVE
import xml.etree.ElementTree as ET   

class MAINUI(QObject) :
    mainuiloadok=pyqtSignal()
    setclipboardsignal=pyqtSignal(str)
    def __init__(self) -> None:
        
        self.translators={}
        self.cishus={}
        self.reader=None
        self.textsource=None
        self.rect=None
        self.last_paste_str=''
        self.textsource=None 
        super(MAINUI,self).__init__( )
        self.mainuiloadok.connect(self.mainuiloadafter)
        self.setclipboardsignal.connect(self.setclipboard)
    def setclipboard(self,_paste_str):
        QApplication.clipboard().setText(_paste_str)
    @threader  
    def loadvnrshareddict(self):
        
        self.vnrshareddict={}
        self.vnrshareddict_pre={}
        self.vnrshareddict_post={}
        self.sorted_vnrshareddict=[]
        self.sorted_vnrshareddict_pre=[]
        self.sorted_vnrshareddict_post=[]
        self.vnrsharedreg=[]
        
        if globalconfig['gongxiangcishu']['use'] and os.path.exists(globalconfig['gongxiangcishu']['path']) :
            xml=ET.parse(globalconfig['gongxiangcishu']['path']) 
            
            for _ in xml.find('terms').findall('term'):
                #print(_.get('type'))
                #macro 宏(正则) 忽略
                #yomi 人名读音 可忽略
                #input 直接替换
                #trans 翻译优化
                #output 输出替换
                #tts 忽略
                #game #游戏名 忽略
                #name #人名 忽略
                #suffix #后缀（们）等 忽略
                #prefix #前缀 忽略
                _type=_.get('type')
                try:
                    src=_.find('sourceLanguage').text
                    tgt=_.find('language').text
                    if tgt=='en':
                        continue
                    pattern=_.find('pattern').text
                    try:
                        text=_.find('text').text
                    except:
                        text=''
                        

                    try:
                        regex=_.find('regex').text
                        
                    except:
                        
                        
                        if 'eos' in text or 'amp' in text or '&' in text:
                            
                            continue
                        if _type=='trans':
                            self.vnrshareddict[pattern]={'src':src,'tgt':tgt,'text':text }
                        elif _type=='input':
                            self.vnrshareddict_pre[pattern]={'src':src,'tgt':tgt,'text':text }
                        elif _type=='output':
                            self.vnrshareddict_post[pattern]={'src':src,'tgt':tgt,'text':text }
                except:
                    pass
                  
            keys=list(self.vnrshareddict.keys())
            keys.sort(key=lambda key:len(key),reverse=True)
            self.sorted_vnrshareddict=[(key,self.vnrshareddict[key]) for key in keys]
            keys=list(self.vnrshareddict_pre.keys())
            keys.sort(key=lambda key:len(key),reverse=True)
            self.sorted_vnrshareddict_pre=[(key,self.vnrshareddict_pre[key]) for key in keys]
            keys=list(self.vnrshareddict_post.keys())
            keys.sort(key=lambda key:len(key),reverse=True)
            self.sorted_vnrshareddict_post=[(key,self.vnrshareddict_post[key]) for key in keys]
                  
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
                if type(noundictconfig['dict'][key])==str:
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
            for key,value in self.sorted_vnrshareddict_pre:
                
                if key in content:
                    content=content.replace(key,value['text']) 
            for key,value in self.sorted_vnrshareddict:
                
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
            for key,value in self.sorted_vnrshareddict_post: 
                if key in res:
                    res=res.replace(key,value['text']) 
        if transerrorfixdictconfig['use']:
            for key in transerrorfixdictconfig['dict']:
                res=res.replace(key,transerrorfixdictconfig['dict'][key])
        return res

    
    def textgetmethod(self,paste_str,shortlongskip=True):
        if type(paste_str)==str:
            if paste_str[:len('<notrans>')]=='<notrans>':
                self.translation_ui.displayraw1.emit([],paste_str[len('<notrans>'):],globalconfig['rawtextcolor'],1)
                return 
        
        if type(paste_str)==list: 
            _paste_str='\n'.join(paste_str)
        else:
            _paste_str=paste_str
        if _paste_str=='':
            return  
        if _paste_str=='':
            return
        if len(_paste_str)>100000:
            return 
 
         
        try:
            if type(paste_str)==list:
                paste_str=[POSTSOLVE(_) for _ in paste_str] 
                _paste_str='\n'.join(paste_str)
            else:
                _paste_str=POSTSOLVE(paste_str) 
            
        except:
            return 
        while len(_paste_str) and _paste_str[-1] in '\r\n \t':  #在后处理之后在去除换行，这样换行符可以当作行结束符给后处理用
            _paste_str=_paste_str[:-1]  

        if set(_paste_str)-set('\r\n \t')==set():
            return 
         
        if len(_paste_str)>1000:
            return  
        if shortlongskip and _paste_str==self.last_paste_str:
            return 
        self.last_paste_str=_paste_str  
        if globalconfig['outputtopasteboard'] and globalconfig['sourcestatus']['copy']==False:  
            self.setclipboardsignal.emit(_paste_str)
        self.translation_ui.original=_paste_str 
        try:
            hira=self.hira_.fy(_paste_str)
        except:
            hira=[]
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
              
            self.translation_ui.displayraw1.emit(hira,_paste_str,globalconfig['rawtextcolor'],2)
        elif globalconfig['isshowrawtext']:
            self.translation_ui.displayraw1.emit(hira,_paste_str,globalconfig['rawtextcolor'],1)
        else:
            self.translation_ui.displayraw1.emit(hira,_paste_str,globalconfig['rawtextcolor'],0)
        try:
            if globalconfig['autoread']:
                self.reader.read(_paste_str)
        except:
            pass
            
        skip=False 
        paste_str_solve= self.solvebeforetrans(_paste_str) 
        if shortlongskip and  (len(paste_str_solve[0])<globalconfig['minlength'] or len(paste_str_solve[0])>globalconfig['maxlength'] ):
            skip=True  
        if (set(_paste_str) -set('「…」、。？！―'))==set():
            skip=True 
              
        try:
            if skip==False : 
                _paste_str=_paste_str.replace('"','""')    
                ret=self.textsource.sqlwrite2.execute(f'SELECT * FROM artificialtrans WHERE source = "{_paste_str}"').fetchone()
                if ret is  None:                     
                    self.textsource.sqlwrite2.execute(f'INSERT INTO artificialtrans VALUES(NULL,"{_paste_str}","{json.dumps({})}");')
        except:
            print_exc()
        
        for engine in self.translators: 
            self.translators[engine].gettask((_paste_str,paste_str_solve,skip)) 
         
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
                    self.reader=ttss[use]( self.settin_ui.voicelistsignal,self.settin_ui.mp3playsignal) 
    #@threader
    def starttextsource(self): 
        if  self.textsource and self.textsource.ending==False :
            self.textsource.end()  
        
        classes={'ocr':ocrtext,'copy':copyboard,'textractor':None,'txt':txt} 
        use=list(filter(lambda _ :globalconfig['sourcestatus'][_],classes.keys()) )
        use=None if len(use)==0 else use[0]
        if use is None:
            self.textsource=None
        elif use=='textractor': 
            pass
        else:
            self.textsource=classes[use](self.textgetmethod,self)   
    
    @threader
    def starthira(self): 
         
        hirasettingbase=globalconfig['hirasetting']
        if hirasettingbase['local']['use']:
            from hiraparse.localhira import hira 
        elif hirasettingbase['mecab']['use']:
            from hiraparse.mecab import hira 
        elif hirasettingbase['mojinlt']['use']:
            from hiraparse.mojinlt import hira 
        else:
            self.hira_=None
            return 
        self.hira_=hira()  
    
    
    @threader
    def prepare(self,now=None):   
        def initx(classname):
            aclass=importlib.import_module('translator.'+classname).TS 
            _=aclass(classname)  
            _.show=partial(self._maybeyrengong,classname)
            return _
        self.commonloader('fanyi',self.translators,initx,now)
         
    def commonloader(self,fanyiorcishu,dictobject,initmethod,_type=None):
        if _type:
            self.commonloader_warp(fanyiorcishu,dictobject,initmethod,_type)
        else:
            for key in globalconfig[fanyiorcishu]:
                print(key)
                self.commonloader_warp(fanyiorcishu,dictobject,initmethod,key)
    @threader
    def commonloader_warp(self,fanyiorcishu,dictobject,initmethod,_type):
        try:
            if _type in dictobject:
                _=dictobject.pop(_type)
                del _
            if globalconfig[fanyiorcishu][_type]['use']==False:
                return
            item=initmethod(_type)
            if item:
                dictobject[_type]=item
        except:
            print_exc()

    @threader
    def startxiaoxueguan(self,type_=None): 

        self.commonloader('cishu',self.cishus,self.cishuinitmethod,type_) 
    def cishuinitmethod(self,type_):
                try:
                    aclass=importlib.import_module('cishu.'+type_)
                    aclass=getattr(aclass,type_)
                except:
                    print_exc()
                    return 
                class cishuwrapper:
                    def __init__(self,_type) -> None:
                        self._=_type()
                        self.queue=Queue()
                        threading.Thread(target=self.monitor).start()
                    def search(self,sentence):
                         
                        self.queue.put(sentence)
                    def monitor(self):
                        while True:
                            s=self.queue.get() 
                             
                            try:
                                res=self._.search(s)
                                 
                            except:
                                print_exc()
                                continue
                            if res is None or res=='':  
                                continue
                             
                            self.callback(res)
                _=cishuwrapper(aclass)
                return _
    def _maybeyrengong(self,classname,contentraw,_):
        
        classname,res,mp=_
        if classname not in globalconfig['fanyi_pre']: 
            res=self.solveaftertrans(res,mp)
         

        l=globalconfig['normallanguagelist'][globalconfig['tgtlang2']] 
        if l=='cht' and l not in globalconfig['fanyi'][classname]['lang']:
            needconv=True
        else:
            needconv=False
        if needconv:
            import zhconv  
        if classname=='premt':
            for k in res:
                if needconv: 
                    res[k]=zhconv.convert(res[k],  'zh-tw' )

                if k  in globalconfig['fanyi']:
                    self.translation_ui.displayres.emit(k,res[k])
                else:
                    self.translation_ui.displayres.emit('premt',res[k])
        else:
            if needconv: 
                res=zhconv.convert(res, 'zh-tw')
            self.translation_ui.displayres.emit(classname,res)
         
            
        if classname not in globalconfig['fanyi_pre']:
             
            res=res.replace('"','""')   
            contentraw=contentraw.replace('"','""')    
            try:
                #if  globalconfig['transkiroku'] and 'sqlwrite2' in dir(self.textsource):
                    ret=self.textsource.sqlwrite2.execute(f'SELECT machineTrans FROM artificialtrans WHERE source = "{contentraw}"').fetchone() 
                
                    ret=json.loads(ret[0]) 
                    ret[classname]=res
                    ret=json.dumps(ret).replace('"','""') 
                    
                    self.textsource.sqlwrite2.execute(f'UPDATE artificialtrans SET machineTrans = "{ret}" WHERE source = "{contentraw}"')
            except:
                print_exc() 
    
      

    def onwindowloadautohook(self):
        if not(globalconfig['autostarthook'] and globalconfig['sourcestatus']['textractor']):
            return 
        else:
            try:
                
                
                if   self.textsource is None: 
                        hwnd=win32gui.GetForegroundWindow()
                        pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                        name_=getpidexe(pid)
                          
                
                        if name_ in savehook_new: 
                            from textsource.textractor import textractor
                            
                            lps=ListProcess()
                            for pid_real,_exe,_ in lps:
                                if _exe==name_:
                                     
                    
                                    self.hookselectdialog.changeprocessclearsignal.emit() 
                                    self.textsource=textractor(self,self.textgetmethod,self.hookselectdialog,pid_real,hwnd,name_,True,savehook_new[name_])
                            
                
                else: 
                    if pid_running(self.textsource.pid)==False or win32process.GetWindowThreadProcessId( self.textsource.hwnd )[0]==0:
                            try:
                                self.textsource.end(True)  
                                 
                            except:
                                print_exc()
                            self.textsource=None  
            except:
                        print_exc()
    def setontopthread(self):
        while True:
            #self.translation_ui.keeptopsignal.emit() 
            
            try:  
               
                if globalconfig['forcekeepontop']:
                    if win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[1] !=os.getpid():
                        win32gui.SetWindowPos(int(self.translation_ui.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE)  
                #win32gui.BringWindowToTop(int(self.translation_ui.winId())) 
            except:
                print_exc() 
            time.sleep(0.3)            
    def autohookmonitorthread(self):
        while True:
            self.onwindowloadautohook()
            time.sleep(0.3)
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
        threading.Thread(target=self.setontopthread).start()
#        self.mainuiloadok.emit() 
    def mainuiloadafter(self):   
        self.localocrstarted=False
        #print(time.time()-t1)
        self.loadvnrshareddict()
        self.prepare()  
        self.starthira()  
        self.starttextsource() 
        #print(time.time()-t1)
        self.settin_ui = Settin(self) 
        #print(time.time()-t1)
        self.startreader() 
        
        self.transhis=gui.transhist.transhist(self.translation_ui)  
        self.edittextui=gui.edittext.edittext(self.translation_ui)  
        self.searchwordW=searchwordW(self.translation_ui)
        self.AttachProcessDialog=AttachProcessDialog(self.settin_ui)
        self.range_ui = rangeadjust(self)   
        self.hookselectdialog=gui.selecthook.hookselect(self ,self.settin_ui)
        threading.Thread(target=self.autohookmonitorthread).start()   
        

       
        threading.Thread(target=minmaxmoveobservefunc,args=(self.translation_ui,)).start()   
        self.startxiaoxueguan()
if __name__ == "__main__" :
    
    
    
    
    screen_scale_rate = getScreenRate()  
     
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv) 
    app.setQuitOnLastWindowClosed(False)
    if  globalconfig['language_setted']==False:
        from gui.languageset import languageset
        x=languageset(globalconfig['language_list_show'])
        x.exec()
        globalconfig['language_setted']=True
        globalconfig['languageuse']=x.current
        setlanguage()
    main = MAINUI() 
    
    main.screen_scale_rate =screen_scale_rate 
    main.scrollwidth=(app.style().pixelMetric(QStyle.PM_ScrollBarExtent))
    main.aa()
    app.exit(app.exec_())
