import os,win32gui,subprocess,win32con,time ,win32process
from traceback import print_exc
from utils.config import globalconfig 
def minmaxmoveobservefunc(self): 
        
        while(True):
                 
                 
                try:
                    if self.object.textsource.pid: 
                        hwnd=self.object.textsource.hwnd


                        tup = win32gui.GetWindowPlacement(hwnd)
                        rect=win32gui.GetWindowRect( hwnd) 
                        if globalconfig['minifollow']:
                                if 'lastminmax'   in dir(self) and  tup[1]!=self.lastminmax:
                                        if tup[1] == win32con.SW_SHOWMINIMIZED:
                                                self.hookfollowsignal.emit(4,(0,0))
                                        elif tup[1] == win32con.SW_SHOWNORMAL:
                                                self.hookfollowsignal.emit(3,(0,0))
                                self.lastminmax=tup[1]
                        if globalconfig['movefollow']:
                                if tup[1] == win32con.SW_SHOWNORMAL:
                                        if 'lastpos'   in dir(self) and rect!=self.lastpos:  
                                                self.hookfollowsignal.emit(5,(rect[0]-self.lastpos[0],rect[1]-self.lastpos[1]))
                                        self.lastpos=rect 
                except:
                        pass
                  
                time.sleep(0.1)