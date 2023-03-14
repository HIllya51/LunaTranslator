
from threading import Thread
import os,time,sys
from traceback import print_exc
import codecs
import os,win32con,time 
from traceback import print_exc
from utils.config import globalconfig 
import win32utils
from utils.exceptions import TimeOut
def getsysproxy():
    hkey=win32utils.RegOpenKeyEx(win32utils.HKEY_CURRENT_USER,'Software\Microsoft\Windows\CurrentVersion\Internet Settings',0,win32utils.KEY_ALL_ACCESS)

    count,MaxValueNameLen,MaxValueLen=(win32utils.RegQueryInfoKey(hkey))
    ProxyEnable=False
    ProxyServer=''
    for i in range(count):
        k,v=(win32utils.RegEnumValue(hkey,i,MaxValueNameLen,MaxValueLen))
        if k=='ProxyEnable':
            ProxyEnable=(v=='\x01')
        elif  k=='ProxyServer':
            ProxyServer=v
    if ProxyEnable:
         return ProxyServer
    else:
         return ''

def argsort(l):
    ll=list(range(len(l)))
    ll.sort(key= lambda x:l[x])
    return ll
def quote_identifier(s, errors="strict"):
        encodable = s.encode("utf-8", errors).decode("utf-8")

        nul_index = encodable.find("\x00")

        if nul_index >= 0:
            error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                    nul_index, nul_index + 1, "NUL not allowed")
            error_handler = codecs.lookup_error(errors)
            replacement, _ = error_handler(error)
            encodable = encodable.replace("\x00", replacement)

        return "\"" + encodable.replace("\"", "\"\"") + "\""
class wavmp3player( ):
    def __init__(self):
        self.i=0
    def mp3playfunction(self,path,volume):
        if os.path.exists(path)==False:
            return 
        self._playsoundWin(path,volume)
    def _playsoundWin(self,sound,volume ):  
        try:
            win32utils.mciSendString((f"stop lunatranslator_mci_{self.i}") );
            win32utils.mciSendString((f"close lunatranslator_mci_{self.i}") );
            self.i+=1 

            win32utils.mciSendString(f'open "{sound}" alias lunatranslator_mci_{self.i}');  
            win32utils.mciSendString(f'setaudio lunatranslator_mci_{self.i} volume to {volume*10}'); 
            win32utils.mciSendString((f'play lunatranslator_mci_{self.i}'))
        except:
            pass
        

def selectdebugfile(path ):
 
    p= os.path.abspath(os.path.join('./LunaTranslator',path)) 
    
    if os.path.exists(p)==False:
          with open(p,'w',encoding='utf8') as ff:
                if path=='translator/selfbuild.py':
                      ff.write('''
import requests
from translator.basetranslator import basetrans
class TS(basetrans): 
    def translate(self,content):  
        #在这里编写
        return content''')
                elif path=='postprocess/mypost.py':
                      ff.write('''
def POSTSOLVE(line): 
    #请在这里编写自定义处理
    return line''')
    os.startfile(p)
    return p
class Threadwithresult(Thread):
    def __init__(self, func,  defalut,ignoreexceptions):
        super(Threadwithresult, self).__init__()
        self.func = func 
        self.result=defalut
        self.istimeout=True
        self.ignoreexceptions=ignoreexceptions
        self.exception=None
    def run(self):
        try:
            self.result = self.func( )
        except Exception as e:
            self.exception=e
        self.istimeout=False
    def get_result(self,timeout=1):
        Thread.join(self,timeout)  
        if self.ignoreexceptions:
            return self.result
        else:
            if self.istimeout:
                 raise TimeOut()
            elif self.exception:
                 raise self.exception
            else:
                 return self.result
def timeoutfunction( func, timeout=100,default=None,ignoreexceptions=True):
    t=Threadwithresult(func,  default,ignoreexceptions)
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

