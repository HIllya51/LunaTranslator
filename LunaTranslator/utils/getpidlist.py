
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