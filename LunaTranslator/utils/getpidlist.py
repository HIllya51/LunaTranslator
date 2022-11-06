
import win32gui,win32process,win32api,win32con
from traceback import print_exc
from PyQt5.QtWinExtras  import QtWin
def getwindowlist():
        windows_list=[]
        pidlist=[]
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), windows_list) 
        for hwnd in windows_list:
                try:
                        tid, pid=win32process.GetWindowThreadProcessId(hwnd) 
                        pidlist.append(pid)
                except:
                        pass
        return list(set(pidlist))
def getarch(pid):
        try: 
                 process=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
                  
                 arch='86' if win32process.IsWow64Process( process)  else '64' 
        except:
                arch=None
        return arch
def getpidexe(pid):
        try:
                hwnd1=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
                        #hwnd=win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION,False, (pid))
                name_ = win32process.GetModuleFileNameEx(
                            hwnd1, None)
        except:
                name_=''
        return name_
def getwindowhwnd(pid):
        windows_list=[]
        pidlist=[]
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), windows_list) 
        for hwnd in windows_list:
                try:
                        tid, _pid=win32process.GetWindowThreadProcessId(hwnd) 
                        if pid==_pid:
                                title = win32gui.GetWindowText(hwnd)
                                if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                                        return hwnd
                except:
                        pass
        return 0
def ListProcess(): 
        windows_list = []
        ret=[]
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), windows_list)
        for hwnd in windows_list:
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                
                  
                    try:
                        # classname = win32gui.GetClassName(hwnd)
                        # title = win32gui.GetWindowText(hwnd)
                        #print(f'classname:{classname} title:{title}') 
                        pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                        name_=getpidexe(pid)
 
                        name=name_.lower()
                        if name[-4:]!='.exe' or ':\\windows\\'  in name   or '\\microsoft\\'  in name:
                            continue
                        import os
                        ret.append([pid,name_,hwnd])
                    except:
                        pass
        #print(windows_list)
        #print(ret)
        return ret
def getExeIcon( name ): 
        try:
            large, small = win32gui.ExtractIconEx(name,0)
            pixmap =QtWin.fromHICON(large[0])
            return pixmap
        except:
            return None
        
def mouseselectwindow(callback):
        import PyHook3
        hm = PyHook3.HookManager()
        def OnMouseEvent(event): 
            
            p=win32api.GetCursorPos()

            hwnd=win32gui.WindowFromPoint(p)
            hm.UnhookMouse()    
            #for pid in pids:
            if True:
                try:
                    tid, pid=win32process.GetWindowThreadProcessId(hwnd)
                    #print(pid,  win32gui.GetWindowText(hwnd))
                     
                    name_=getpidexe(pid)
                    #print(name_) 
                    print(pid,hwnd,name_)
                    callback(pid,hwnd,name_) 
                except: 
                    print_exc()
            
            return True
        hm.MouseAllButtonsDown = OnMouseEvent
        hm.HookMouse()

def letfullscreen(hwnd):
        wpc=win32gui. GetWindowPlacement( hwnd )
        HWNDStyle = win32gui.GetWindowLong( hwnd, win32con.GWL_STYLE )
        HWNDStyleEx = win32gui.GetWindowLong( hwnd, win32con.GWL_EXSTYLE  )
        NewHWNDStyle=HWNDStyle
        NewHWNDStyle &= ~win32con.WS_BORDER;
        NewHWNDStyle &= ~win32con.WS_DLGFRAME;
        NewHWNDStyle &= ~win32con.WS_THICKFRAME;
        NewHWNDStyleEx=HWNDStyleEx
        NewHWNDStyleEx &= ~win32con.WS_EX_WINDOWEDGE;
        win32gui.SetWindowLong( hwnd, win32con.GWL_STYLE, NewHWNDStyle | win32con.WS_POPUP );
        win32gui.SetWindowLong( hwnd, win32con.GWL_EXSTYLE, NewHWNDStyleEx | win32con.WS_EX_TOPMOST )
        win32gui.ShowWindow(hwnd,win32con.SW_SHOWMAXIMIZED )
        return (wpc,HWNDStyle,HWNDStyleEx)

def recoverwindow(hwnd,status):
        wpc,HWNDStyle,HWNDStyleEx=status
        win32gui.SetWindowLong( hwnd, win32con.GWL_STYLE,  HWNDStyle );
        win32gui.SetWindowLong( hwnd, win32con.GWL_EXSTYLE,  HWNDStyleEx );
        win32gui.ShowWindow( hwnd, win32con.SW_SHOWNORMAL );
        win32gui.SetWindowPlacement( hwnd, wpc );
