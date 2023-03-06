
from threading import Thread
import os,time,sys
from traceback import print_exc
import codecs
import os,win32con,time 
from traceback import print_exc
from utils.config import globalconfig 
import win32utils
def argsort(l):
    ll=list(range(len(l)))
    ll.sort(key= lambda x:l[x])
    return ll


def selectdebugfile(path ):
    p=None
    if os.path.exists(os.path.join('./LunaTranslator',path)):
        p= os.path.abspath(os.path.join('./LunaTranslator',path)) 
    if p  :
        os.startfile(p)
    return p
class Threadwithresult(Thread):
    def __init__(self, func,  defalut=None):
        super(Threadwithresult, self).__init__()
        self.func = func 
        self.result=defalut
    def run(self):
        try:
            self.result = self.func( )
        except:
            print_exc()
    def get_result(self,timeout=1):
        Thread.join(self,timeout)  
        return self.result
def timeoutfunction( func, timeout=100,default=None):
    t=Threadwithresult(func=func,  defalut=default)
    t.start()
    return t.get_result(timeout)


 
def checkchaos(text ):
        code=globalconfig['accept_encoding']
        
        text= filter(lambda x: x not in globalconfig['accept_character'],text) 

        if globalconfig['accept_use_unicode']:
            _start=globalconfig['accept_use_unicode_start']
            _end=globalconfig['accept_use_unicode_end']
            chaos=False
            for ucode in map(lambda x:ord(x),text):
                print(ucode,_start,_end)
                if ucode<_start or ucode >_end:
                    chaos=True
                    break 
        else: 
            chaos=True 
            text=''.join(text)
            for c in code:
                try:
                    text.encode(c)
                    chaos=False
                    break
                except:
                    pass
            return chaos

def checkencoding(code):
     
    try:
        codecs.lookup(code)
        return True
    except LookupError:
        return False
    

def minmaxmoveobservefunc(self): 
        
        self.lasthwnd=None
        self.lastfocus=None
        while(True):
                 
                
                try:
                    if self.object.textsource.pid: 
                        hwnd=self.object.textsource.hwnd
                        if hwnd!=self.lasthwnd:
                                self.lastminmax=None
                                self.lastpos=None
                        self.lasthwnd=hwnd
                        tup = win32utils.GetWindowPlacement(hwnd,True)
                        #print(tup)
                        rect=win32utils.GetWindowRect( hwnd) 
                        if globalconfig['focusfollow']:
                                focus=win32utils.GetForegroundWindow()
                                _focusp=win32utils.GetWindowThreadProcessId(focus)[1]
                                if _focusp ==self.object.textsource.pid: 
                                        self.hookfollowsignal.emit(3,(hwnd,))
                                elif _focusp ==os.getpid():
                                        pass
                                else:
                                        self.hookfollowsignal.emit(4,(0,0)) 
                                
                        if globalconfig['minifollow']:
                                if self.lastminmax and  tup[1]!=self.lastminmax:
                                        if tup[1] == win32con.SW_SHOWMINIMIZED:
                                                self.hookfollowsignal.emit(4,(0,0)) 
                                        elif tup[1] == win32con.SW_SHOWNORMAL:
                                                self.hookfollowsignal.emit(3,(hwnd,))
                                self.lastminmax=tup[1]
                                
                        if globalconfig['movefollow']:
                                if tup[1] == win32con.SW_SHOWNORMAL:
                                        if self.lastpos and rect!=self.lastpos:  
                                                self.hookfollowsignal.emit(5,(rect[0]-self.lastpos[0],rect[1]-self.lastpos[1]))
                                        self.lastpos=rect 
                except:
                        #print_exc()
                        pass
                  
                time.sleep(0.1)



def update():
    with open('./cache/update/update.bat','w',encoding='utf8') as ff:
                
                ff.write(r''' 
:start 
timeout 1
tasklist|find /i "Lunatranslator_main.exe" 
if %errorlevel%==0 goto start 

xcopy .\cache\update\LunaTranslator\ .\ /s /e /c /y /h /r 
exit
                
                ''') 
    win32utils.ShellExecute(None, "open", 'cache\\update\\update.bat', "", os.path.dirname('.'), win32con.SW_HIDE)


def makehtml(text,base=False):
    if base:
        show=text.split('/')[-1]
    else:
          show=text
    return f'<a href="{text}">{show}</a>'