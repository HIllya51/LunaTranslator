
from threading import Thread
import os,time,sys
from traceback import print_exc
import codecs,hashlib
import os,win32con,time 
from traceback import print_exc
from utils.config import globalconfig,static_data,savehook_new_list,savehook_new_data,getdefaultsavehook
import win32utils,threading,queue
from utils.exceptions import TimeOut
from urllib.request import getproxies_registry
import importlib,re
from PyQt5.QtGui import QPixmap
 
def checkneed(gamepath):
    return (gamepath in savehook_new_data) and \
            ((savehook_new_data[gamepath]['imagepath'] is None) or (os.path.exists(savehook_new_data[gamepath]['imagepath'])==False) or 
             (savehook_new_data[gamepath]['infopath'] is None) or ((savehook_new_data[gamepath]['infopath'][:4].lower()!='http') and os.path.exists(savehook_new_data[gamepath]['infopath'])==False))
methodsqueues=[]

def dispatchnext(gamepath,args,idx):
     if idx+1<len(methodsqueues):
            methodsqueues[idx+1].put((gamepath,args))
def dispatachtask(gamepath): 
    if checkneed(gamepath)==False:
        return
    title=savehook_new_data[gamepath]['title']
    p=gamepath.split('\\')  
    __t=[]
    for _ in [title,p[-2],p[-1][:-4]]:
        _=_.replace('(同人ゲーム)','').replace('(18禁ゲーム)','')
        _=re.sub('\[RJ(.*?)\]','',_)
        _=re.sub('\[\d{4}-?\d{2}\-?\d{2}\]','',_)
        __t.append(_)
        _=re.sub('\[(.*?)\]','',_)
        if _ !=__t[-1]:
            __t.append(_) 
        _=re.sub('\((.*?)\)','',_)
        if _ !=__t[-1]:
            __t.append(_) 
    lst=[] 
    for i,t in enumerate(__t): 
        t=t.strip()
        if t in lst :continue
        if i>0  and (len(t)<10) and (all(ord(c) < 128 for c in t)):
            continue
        lst.append(t)
    dispatchnext(gamepath,lst,-1) 
          
def everymethodsthread(methodsidx):
    methods=static_data['searchimgmethods']
    searchimgmethod=importlib.import_module('unstablemethod.'+methods[methodsidx]).searchimgmethod   
    while True:
        gamepath,searchargs=methodsqueues[methodsidx].get()
        
        if checkneed(gamepath)==False:
            continue
        failed=True
        for searcharg in searchargs:
            try:
                saveimg= searchimgmethod(searcharg)  
            except:
                saveimg=None

            if saveimg: 
                pix=QPixmap(saveimg) 
                if pix.isNull()==False:  
                    if checkneed(gamepath) : 
                        savehook_new_data[gamepath]['imagepath']=saveimg
            try:
                searchinfomethod=importlib.import_module('unstablemethod.'+methods[methodsidx]).searchinfomethod   
                saveinfo= searchinfomethod(searcharg)  
            except:
                saveinfo=None
            if saveinfo:
                if checkneed(gamepath) : 
                    savehook_new_data[gamepath]['infopath']=saveinfo
                    savehook_new_data[gamepath]['infomethod']=methods[methodsidx]
            if saveinfo is not None and saveimg is not None:
                failed=False
                break  
        if failed:
            dispatchnext(gamepath,searchargs,methodsidx)
for i in range(len(static_data['searchimgmethods'])):
    methodsqueues.append(queue.Queue())
    threading.Thread(target=everymethodsthread,args=(i,)).start()
def checkifnewgame(gamepath):
    if gamepath not in savehook_new_list:
            savehook_new_list.insert(0,gamepath) 
    if gamepath not in savehook_new_data:
            savehook_new_data[gamepath]=getdefaultsavehook(gamepath)
    dispatachtask(gamepath)
kanjichs2ja=str.maketrans(static_data['kanjichs2ja'])
def kanjitrans(k): 
    return k.translate(kanjichs2ja) 
def startgame(game,settingui):
    try:         
        if os.path.exists(game):
            mode=savehook_new_data[game]['onloadautochangemode']
            if mode==0:
                    pass
            else:
                    _={
                    1:'texthook',
                    2:'embedded',
                    3:'copy',
                    4:'ocr'
                    } 
                    if globalconfig['sourcestatus'][_[mode]]['use']==False:
                            globalconfig['sourcestatus'][_[mode]]['use']=True
                            
                            settingui.yuitsu_switch('sourcestatus','sourceswitchs',_[mode],None ,True) 
                            settingui.object.starttextsource(use=_[mode],checked=True)
     
            if savehook_new_data[game]['leuse'] :
                    localeswitcher=savehook_new_data[game]['localeswitcher'] 
                    b=win32utils.GetBinaryType(game) 
                    if b==6 and localeswitcher==0:
                            localeswitcher=1
                    if (localeswitcher==2 and b==6):
                            _exe='shareddllproxy64'
                    else:
                            _exe='shareddllproxy32'
                    exe=(os.path.abspath('./files/plugins/'+_exe)) 
                    _cmd={0:'le',1:"LR",2:"ntleas"}[localeswitcher] 
                    win32utils.CreateProcess(None,f'"{exe}" {_cmd} "{(game)}"', None,None,False,0,None, os.path.dirname(game), win32utils.STARTUPINFO()  ) 
                                    
            else:
                    win32utils.ShellExecute(None, "open", game, "", os.path.dirname(game), win32con.SW_SHOW) 
    except:
            print_exc()
def getsysproxy():
    proxies=getproxies_registry()
    try:
         return proxies[list(proxies.keys())[0]].split('//')[1]
    except:
         return ''
    # hkey=win32utils.RegOpenKeyEx(win32utils.HKEY_CURRENT_USER,'Software\Microsoft\Windows\CurrentVersion\Internet Settings',0,win32utils.KEY_ALL_ACCESS)

    # count,MaxValueNameLen,MaxValueLen=(win32utils.RegQueryInfoKey(hkey))
    # ProxyEnable=False
    # ProxyServer=''
    # for i in range(count):
    #     k,v=(win32utils.RegEnumValue(hkey,i,MaxValueNameLen,MaxValueLen))
    #     if k=='ProxyEnable':
    #         ProxyEnable=(v=='\x01')
    #     elif  k=='ProxyServer':
    #         ProxyServer=v
    # if ProxyEnable:
    #      return ProxyServer
    # else:
    #      return ''
def getproxy():
    if globalconfig['useproxy']:
            if globalconfig['usesysproxy']:
                p=getsysproxy()
            else:
                p=(globalconfig['proxy'])
    else:
        p=None
    return {'https':p,'http':p}
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
        self.lastfile=None
    def mp3playfunction(self,path,volume):
        if os.path.exists(path)==False:
            return 
        self._playsoundWin(path,volume)
    def _playsoundWin(self,sound,volume ):  
        try:
            
            win32utils.mciSendString((f"stop lunatranslator_mci_{self.i}") );
            win32utils.mciSendString((f"close lunatranslator_mci_{self.i}") );
            self.i+=1 
            if self.lastfile:
                os.remove(self.lastfile)
            self.lastfile=sound
            win32utils.mciSendString(f'open "{sound}" type mpegvideo  alias lunatranslator_mci_{self.i}');  
            win32utils.mciSendString(f'setaudio lunatranslator_mci_{self.i} volume to {volume*10}'); 
            win32utils.mciSendString((f'play lunatranslator_mci_{self.i}'))
        except:
            pass
        

def selectdebugfile(path ):
 
    p= os.path.abspath((path)) 
    
    if os.path.exists(p)==False:
          with open(p,'w',encoding='utf8') as ff:
                if path=='./userconfig/selfbuild.py':
                      ff.write('''
import requests
from translator.basetranslator import basetrans
class TS(basetrans): 
    def translate(self,content):  
        #在这里编写
        return content''')
                elif path=='./userconfig/mypost.py':
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

def getfilemd5(file,default='0'):
    try:
        with open(file,'rb') as ff:
            bs=ff.read()
        md5=hashlib.md5(bs).hexdigest()
        return md5
    except:
        return default
def minmaxmoveobservefunc(self): 
        
        self.lasthwnd=None
        self.lastfocus=None
        while(True):
                 
                
                try:
                    if self.object.textsource.hwnd: 
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
                                _focusp=win32utils.GetWindowThreadProcessId(focus)
                                if _focusp in self.object.textsource.pids: 
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
 

def makehtml(text,base=False,show=None):
    if base:
        show=text.split('/')[-1]
    elif show:
        pass
    else:
          show=text
    return f'<a href="{text}">{show}</a>'

