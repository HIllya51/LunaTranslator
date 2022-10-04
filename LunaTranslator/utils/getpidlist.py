
import win32gui,win32process

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