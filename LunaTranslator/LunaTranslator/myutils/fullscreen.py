import os,json,math
import windows
from myutils.config import globalconfig ,magpie10_config
from myutils.hwnd import  letfullscreen,recoverwindow,pid_running
from traceback import print_exc
from myutils.subproc import subproc_w
import time,threading

class fullscreen():
    def __init__(self,_externalfsend) -> None: 
        self.savewindowstatus=None 
        self._externalfsend=_externalfsend
        self.status=False
        self.lasthwnd=None
    def end(self):
        if self.status and self.lasthwnd:
            self.__call__(self.lasthwnd,not self.status)
    @property
    def fsmethod(self):return globalconfig['fullscreenmethod_3']
    # def runmagpie10(self):
    #     exes=[_[1] for _ in ListProcess()]  
    #     if os.path.join(globalconfig['magpie10path'],'Magpie.exe').replace('/','\\') not in exes: 
    #         subproc_w(os.path.join(globalconfig['magpie10path'],'Magpie.exe'),cwd=globalconfig['magpie10path'] ,name='magpie10' ) 
     
    # def _1(self,hwnd,full):
    #     self.runmagpie10()  
    #     windows.SetForegroundWindow(hwnd )   
    #     time.sleep(0.1)
    #     configpath=os.path.join(globalconfig['magpie10path'],'config/config.json')
    #     if os.path.exists(configpath)==False:
    #         configpath=os.path.join(os.environ['LOCALAPPDATA'],'Magpie/config/config.json')
    #     if os.path.exists(configpath)==False:
    #         return 
    #     with open(configpath,'r',encoding='utf8') as ff:
    #         config=json.load(ff)
    #     shortcuts=config['shortcuts']['scale']
    #     mp1={'SHIFT': 16, 'WIN': 91,'CTRL': 17,'ALT': 18}
    #     mp={
    #         0x100:'WIN',
    #         0x200:'CTRL',
    #         0x400:'ALT',
    #         0x800:'SHIFT'
    #     }
        
        
    #     for k in mp:
    #         if shortcuts&k !=0:
    #             windows.keybd_event(mp1[mp[k]],0,0,0)
        
    #     k2=shortcuts &0xff
    #     windows.keybd_event(k2,0,0,0)      
    #     windows.keybd_event(k2, 0, windows.KEYEVENTF_KEYUP, 0)
    #     for k in mp:
    #         if shortcuts&k !=0:
    #             windows.keybd_event(mp1[mp[k]],0,windows.KEYEVENTF_KEYUP,0)
    def _4(self,hwnd,full):
        if full:  
            self.engine= subproc_w(r'./files/plugins/shareddllproxy64.exe lossless "{}" "{}" {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(globalconfig['lossless']['path'],hwnd,
                                                                                                                                                                             
            globalconfig['lossless']['scalingMode'],
            globalconfig['lossless']['scalingFitMode'],
            globalconfig['lossless']['scalingType'],
            globalconfig['lossless']['scalingSubtype'],
            globalconfig['lossless']['scaleFactor'],
            globalconfig['lossless']['resizeBeforeScale'],
            globalconfig['lossless']['windowedMode'],
            globalconfig['lossless']['sharpness'],
            globalconfig['lossless']['VRS'],
            globalconfig['lossless']['clipCursor'],
            globalconfig['lossless']['cursorSensitivity'],
            globalconfig['lossless']['hideCursor'],
            globalconfig['lossless']['scaleCursor'],
            globalconfig['lossless']['doubleBuffering'],
            globalconfig['lossless']['vrrSupport'],
            globalconfig['lossless']['hdrSupport'],
            globalconfig['lossless']['allowTearing'],
            globalconfig['lossless']['legacyCaptureApi'],
            globalconfig['lossless']['drawFps'],
            globalconfig['lossless']['gpuId'],
            globalconfig['lossless']['displayId'],
            globalconfig['lossless']['captureOffsetLeft'],
            globalconfig['lossless']['captureOffsetTop'],
            globalconfig['lossless']['captureOffsetRight'],
            globalconfig['lossless']['captureOffsetBottom'],
            globalconfig['lossless']['multiDisplayMode'],
            os.getpid(),
            globalconfig['lossless']['frameGeneration']),cwd=globalconfig['lossless']['path'])
            self._waitenginestop()
        else:
            endevent =windows.AutoHandle(windows.CreateEvent(False, False,'LOSSLESS_WAITFOR_STOP_SIGNAL'+str(self.engine.pid)))
            windows.SetEvent(endevent)
    def _waitenginestop(self):
        def _waitexternalend():
            #self.engine.wait()
            while pid_running(self.engine.pid):
                time.sleep(0.5)
            self._externalfsend()
            self.status=False
        threading.Thread(target=_waitexternalend ).start()
    def _0(self,hwnd,full):
        if full:  
            profiles_index=globalconfig['profiles_index']
            if profiles_index>len(magpie10_config['profiles']):
                profiles_index=0
                
            jspath=os.path.abspath('./userconfig/magpie10_config.json')
            with open(jspath,'w',encoding='utf-8') as ff:
                    ff.write(json.dumps(magpie10_config,ensure_ascii=False,sort_keys=False, indent=4))
            self.engine= subproc_w('./files/plugins/Magpie10/Magpie.Core.exe {} {} "{}"'.format(profiles_index,hwnd,jspath),cwd='./files/plugins/Magpie10/')
            self._waitenginestop()
        else:
            endevent =windows.AutoHandle(windows.CreateEvent(False, False,'MAGPIE_WAITFOR_STOP_SIGNAL'+str(self.engine.pid)))
            windows.SetEvent(endevent)
             
    # magpie9
    # def _0(self,hwnd,full):
    #     if full:
    #         SetForegroundWindow(hwnd )    
    #         callmagpie(('./files/plugins/Magpie_v0.9.1'),hwnd,globalconfig['magpiescalemethod'],globalconfig['magpieflags'],globalconfig['magpiecapturemethod'])
    #     else:
    #         hwnd=FindWindow('Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22',None) 
    #         if hwnd==0:
    #             return
    #         WM_DESTORYHOST=RegisterWindowMessage( "MAGPIE_WM_DESTORYHOST") 
    #         SendMessage(hwnd, WM_DESTORYHOST)
    def _2(self,hwnd,full):
        windows.SetForegroundWindow(hwnd )   
        windows.keybd_event(18,0,0,0)     # alt
        windows.keybd_event(13,0,0,0)     # enter
                            
        windows.keybd_event(13, 0, windows.KEYEVENTF_KEYUP, 0)
        windows.keybd_event(18, 0, windows.KEYEVENTF_KEYUP, 0)
    def _3(self,hwnd,full):
        if full: 
            self.savewindowstatus=letfullscreen(hwnd)
        else:
            recoverwindow(hwnd,self.savewindowstatus)
    def __call__(self, hwnd=0,full=False):  
        try: 
            [
                self._0,
                self._2,
                self._3,
                self._4
            ][self.fsmethod](hwnd,full) 
            self.status=full
            self.lasthwnd=hwnd
        except:
            print_exc()