import win32api,win32gui,win32process,win32con,win32print
import time
while True:
        
    pid=win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow()) [1]
    print(pid)
    hwnd=win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION,False, (pid))
    rect=win32gui.GetWindowRect(win32gui.GetForegroundWindow())   
    hDC = win32gui.GetDC(0) 
    print(win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES) )
    print(win32api.GetSystemMetrics(0))
    if pid==14936:
       
        win32gui.SetWindowPos(win32gui.GetForegroundWindow(),win32con.HWND_NOTOPMOST, 0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1),  win32con.SWP_NOMOVE)
        #win32gui.MoveWindow(win32gui.GetForegroundWindow(),0,0,1200,600,False)
    print(rect)
    name_ = win32process.GetModuleFileNameEx(
                                    hwnd, None)
    print(name_)
    time.sleep(1)