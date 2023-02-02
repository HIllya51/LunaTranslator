import os,win32gui,win32api,win32con,win32process
from utils.config import globalconfig
from traceback import print_exc
import subprocess
from utils.magpie import callmagpie
from utils.getpidlist import getpidhwnds,mouseselectwindow,letfullscreen,recoverwindow 
class fullscreen():
    def __init__(self) -> None:
        self.savewindowstatus=None 
        self.savemagpie_pid=None
    def __call__(self, hwnd,full):  
            if globalconfig['fullscreenmethod']==0:  
                if full:
                    win32gui.SetForegroundWindow(hwnd )    
                    self.savemagpie_pid=callmagpie((globalconfig['magpiepath']),hwnd,globalconfig['magpiescalemethod'],globalconfig['magpieflags'],globalconfig['magpiecapturemethod'])
                else:
                    if self.savemagpie_pid is None:
                        return  
                    hwnds=getpidhwnds(self.savemagpie_pid)
                    if len(hwnds)==0:
                        return
                    WM_DESTORYHOST=win32api.RegisterWindowMessage( "MAGPIE_WM_DESTORYHOST") 
                    for hwnd in hwnds:
                        win32api.SendMessage(hwnd, WM_DESTORYHOST)
            elif globalconfig['fullscreenmethod']==1:  
                win32gui.SetForegroundWindow(hwnd )   
                win32api.keybd_event(18,0,0,0)     # alt
                win32api.keybd_event(13,0,0,0)     # enter
                                    
                win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(18, 0, win32con.KEYEVENTF_KEYUP, 0)
            elif globalconfig['fullscreenmethod']==2: 
                if full: 
                    self.savewindowstatus=letfullscreen(hwnd)
                else:
                    recoverwindow(hwnd,self.savewindowstatus)
             