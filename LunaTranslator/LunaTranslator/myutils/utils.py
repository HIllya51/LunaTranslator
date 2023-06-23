
from threading import Thread
import os,time,sys
from traceback import print_exc
import codecs,hashlib
import os,win32con,time 
import socket,functools
import ctypes
import time
import ctypes.wintypes
import win32con,gobject
from traceback import print_exc
from myutils.config import globalconfig,static_data,savehook_new_list,savehook_new_data,getdefaultsavehook,translatorsetting
import win32utils,threading,queue
from urllib.request import getproxies_registry
import importlib,re
def checkimage(gamepath):
    return (savehook_new_data[gamepath]['imagepath'] is None) or (os.path.exists(savehook_new_data[gamepath]['imagepath'])==False)
def checkinfo(gamepath):
    return (savehook_new_data[gamepath]['infopath'] is None) or ((savehook_new_data[gamepath]['infopath'][:4].lower()!='http') and os.path.exists(savehook_new_data[gamepath]['infopath'])==False)
def checkneed(gamepath):
    return (gamepath in savehook_new_data) and \
            (checkimage(gamepath) or checkinfo(gamepath) )
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
    searchdatamethod=importlib.import_module('unstablemethod.'+methods[methodsidx]).searchdatamethod   
    while True:
        gamepath,searchargs=methodsqueues[methodsidx].get()
        
        if checkneed(gamepath)==False:
            continue
        failed=True
        for searcharg in searchargs:
            try:
                data= searchdatamethod(searcharg)  
            except:
                data={}
            saveimg=data.get('imagepath',None)
            saveinfo=data.get('infopath',None)
            if saveimg: 
                if checkimage(gamepath) : 
                    savehook_new_data[gamepath]['imagepath']=saveimg
            
            if saveinfo:
                if checkinfo(gamepath) : 
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
def checkportavailable(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        return True
    except OSError:
        return False
    finally:
        sock.close()
def splittranslatortypes():
    pre,offline,free,dev,api=set(),set(),set(),set(),set()
    for k in globalconfig['fanyi']:
        try:
            {
                'pre':pre,'offline':offline,'free':free,'dev':dev,'api':api
            }[globalconfig['fanyi'][k].get('type','free')].add(k)
        except:
            pass
     
    return offline,pre,free,dev,api
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
            
            win32utils.mciSendString(("stop lunatranslator_mci_{}".format(self.i)) );
            win32utils.mciSendString(("close lunatranslator_mci_{}".format(self.i)) );
            self.i+=1 
            if self.lastfile:
                os.remove(self.lastfile)
            self.lastfile=sound
            win32utils.mciSendString('open "{}" type mpegvideo  alias lunatranslator_mci_{}'.format(sound,self.i));  
            win32utils.mciSendString('setaudio lunatranslator_mci_{} volume to {}'.format(self.i,volume*10)); 
            win32utils.mciSendString(('play lunatranslator_mci_{}'.format(self.i)))
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
        
        user32 = ctypes.windll.user32

        WinEventProcType = ctypes.CFUNCTYPE(
            None,
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LONG,
            ctypes.wintypes.LONG,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD,
        )
        def win_event_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            try:
                if gobject.baseobject.textsource is None:
                    return 
                if gobject.baseobject.textsource.hwnd==0: 
                    return
                
                _focusp=win32utils.GetWindowThreadProcessId(hwnd)
                if event ==win32con.EVENT_SYSTEM_FOREGROUND:  
                    if globalconfig['focusfollow']: 
                        if _focusp ==os.getpid():
                            pass 
                        elif _focusp in gobject.baseobject.textsource.pids: 
                            self.hookfollowsignal.emit(3,(hwnd,))
                        else:
                            self.hookfollowsignal.emit(4,(0,0)) 
                    if globalconfig['keepontop'] and globalconfig['focusnotop']:  
                        if _focusp ==os.getpid():
                            pass
                        elif _focusp in gobject.baseobject.textsource.pids: 
                            gobject.baseobject.translation_ui.settop()
                        else:
                            gobject.baseobject.translation_ui.canceltop()
                if _focusp!= win32utils.GetWindowThreadProcessId(gobject.baseobject.textsource.hwnd ) :
                    return
                 
                rect=win32utils.GetWindowRect( hwnd) 
                if event == win32con.EVENT_SYSTEM_MINIMIZEEND: 
                    if globalconfig['minifollow']:
                        self.hookfollowsignal.emit(3,(hwnd,))
                elif event == win32con.EVENT_SYSTEM_MINIMIZESTART: 
                    if globalconfig['minifollow']:
                        self.hookfollowsignal.emit(4,(0,0)) 
                elif event == win32con.EVENT_SYSTEM_MOVESIZESTART: # 
                    self.lastpos=rect
                elif event == win32con.EVENT_SYSTEM_MOVESIZEEND: # 
                    if globalconfig['movefollow']:
                        self.hookfollowsignal.emit(5,(rect[0]-self.lastpos[0],rect[1]-self.lastpos[1]))
                    
            except:
                print_exc()
        win_event_callback_cfunc = WinEventProcType(win_event_callback)

        eventpairs=(
            (win32con.EVENT_SYSTEM_MOVESIZESTART,win32con.EVENT_SYSTEM_MOVESIZEEND),
            (win32con.EVENT_SYSTEM_MINIMIZESTART,win32con.EVENT_SYSTEM_MINIMIZEEND),
            (win32con.EVENT_SYSTEM_FOREGROUND,win32con.EVENT_SYSTEM_FOREGROUND),
        )

        def _():
            for pair in eventpairs: 
                hook_id = user32.SetWinEventHook(
                    pair[0],
                    pair[1],
                    0,
                    win_event_callback_cfunc,
                    0,
                    0,
                    0
                )

            msg = ctypes.wintypes.MSG()
            while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

            ctypes.windll.user32.UnhookWindowsHookEx(hook_id)
        _() 

def makehtml(text,base=False,show=None):
    if base:
        show=text.split('/')[-1]
    elif show:
        pass
    else:
          show=text
    return '<a href="{}">{}</a>'.format(text,show)

