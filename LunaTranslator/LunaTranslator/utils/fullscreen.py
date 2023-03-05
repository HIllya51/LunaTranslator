import os,win32con,json,math
import win32utils
from utils.config import globalconfig 
from utils.magpie import callmagpie
from utils.getpidlist import  letfullscreen,recoverwindow,ListProcess
from traceback import print_exc
from utils.subproc import subproc
import time
key_map = {
    "0": 49, "1": 50, "2": 51, "3": 52, "4": 53, "5": 54, "6": 55, "7": 56, "8": 57, "9": 58,
    'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117, 'F7': 118, 'F8': 119,
    'F9': 120, 'F10': 121, 'F11': 122, 'F12': 123, 'F13': 124, 'F14': 125, 'F15': 126, 'F16': 127,
    "A": 65, "B": 66, "C": 67, "D": 68, "E": 69, "F": 70, "G": 71, "H": 72, "I": 73, "J": 74,
    "K": 75, "L": 76, "M": 77, "N": 78, "O": 79, "P": 80, "Q": 81, "R": 82, "S": 83, "T": 84,
    "U": 85, "V": 86, "W": 87, "X": 88, "Y": 89, "Z": 90,
    'BACKSPACE': 8, 'TAB': 9, 'TABLE': 9, 'CLEAR': 12,
    'ENTER': 13, 'SHIFT': 16, 'CTRL': 17,
    'CONTROL': 17, 'ALT': 18, 'ALTER': 18, 'PAUSE': 19, 'BREAK': 19, 'CAPSLK': 20, 'CAPSLOCK': 20, 'ESC': 27,
    'SPACE': 32, 'SPACEBAR': 32, 'PGUP': 33, 'PAGEUP': 33, 'PGDN': 34, 'PAGEDOWN': 34, 'END': 35, 'HOME': 36,
    'LEFT': 37, 'UP': 38, 'RIGHT': 39, 'DOWN': 40, 'SELECT': 41, 'PRTSC': 42, 'PRINTSCREEN': 42, 'SYSRQ': 42,
    'SYSTEMREQUEST': 42, 'EXECUTE': 43, 'SNAPSHOT': 44, 'INSERT': 45, 'DELETE': 46, 'HELP': 47, 'WIN': 91,
    'WINDOWS': 91, 'NMLK': 144,
    'NUMLK': 144, 'NUMLOCK': 144, 'SCRLK': 145,
    '[': 219, ']': 221, '+': 107, '-': 109}
class fullscreen():
    def __init__(self) -> None:
        self.savewindowstatus=None 
        self.savemagpie_pid=None
        if self.fsmethod==1:self.runmagpie10() 
    @property
    def fsmethod(self):return globalconfig['fullscreenmethod_2']
    def runmagpie10(self):
        exes=[_[1] for _ in ListProcess()]  
        if os.path.join(globalconfig['magpie10path'],'Magpie.exe').replace('/','\\') not in exes: 
            subproc(os.path.join(globalconfig['magpie10path'],'Magpie.exe'),cwd=globalconfig['magpie10path'] ,keep=True ) 
     
    def _1(self,hwnd,full):
        self.runmagpie10()  
        win32utils.SetForegroundWindow(hwnd )   
        time.sleep(0.1)
        configpath=os.path.join(globalconfig['magpie10path'],'config/config.json')
        if os.path.exists(configpath)==False:
            configpath=os.path.join(os.environ['LOCALAPPDATA'],'Magpie/config/config.json')
        if os.path.exists(configpath)==False:
            return 
        with open(configpath,'r',encoding='utf8') as ff:
            config=json.load(ff)
        shortcuts=config['shortcuts']['scale']
        code=shortcuts&0xff 
        control=key_map[['WIN','CTRL','ALT','SHIFT'][ int(math.log2((shortcuts-code)//0x100))]] 
        k1=control
        k2=code 
        win32utils.keybd_event(k1,0,0,0)    
        win32utils.keybd_event(k2,0,0,0)      
        win32utils.keybd_event(k2, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32utils.keybd_event(k1, 0, win32con.KEYEVENTF_KEYUP, 0) 
        
         
    def _0(self,hwnd,full):
        if full:
            win32utils.SetForegroundWindow(hwnd )    
            self.savemagpie_pid=callmagpie(('./files/Magpie_v0.9.1'),hwnd,globalconfig['magpiescalemethod'],globalconfig['magpieflags'],globalconfig['magpiecapturemethod'])
        else:
            if self.savemagpie_pid is None:
                return  
                
            hwnd=win32utils.FindWindow('Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22',None) 
            if hwnd==0:
                return
            WM_DESTORYHOST=win32utils.RegisterWindowMessage( "MAGPIE_WM_DESTORYHOST") 
            win32utils.SendMessage(hwnd, WM_DESTORYHOST)
    def _2(self,hwnd,full):
        win32utils.SetForegroundWindow(hwnd )   
        win32utils.keybd_event(18,0,0,0)     # alt
        win32utils.keybd_event(13,0,0,0)     # enter
                            
        win32utils.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32utils.keybd_event(18, 0, win32con.KEYEVENTF_KEYUP, 0)
    def _3(self,hwnd,full):
        if full: 
            self.savewindowstatus=letfullscreen(hwnd)
        else:
            recoverwindow(hwnd,self.savewindowstatus)
    def __call__(self, hwnd,full):  
        try: 
            [
                self._0,
                self._1,
                self._2,
                self._3
            ][self.fsmethod](hwnd,full) 
        except:
            print_exc()