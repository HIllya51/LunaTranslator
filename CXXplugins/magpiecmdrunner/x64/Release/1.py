import subprocess,win32gui,win32process,time,os
 
from ctypes import *
import win32api

WM_SETTEXT  =   0x000C

def ChangeActiveWindowTtile():
    hwnd=windll.user32.FindWindowW(u"Notepad",u"无标题 - 记事本")
    if (windll.user32.IsWindow(hwnd)):
        windll.user32.SendMessageW(hwnd,WM_DESTORYHOST,None,u"我是标题")
      
while True:
    hwnd=win32gui.GetForegroundWindow()
    pid=win32process.GetWindowThreadProcessId(hwnd)[1]
    if pid==16624:
        magpiepath='C:\\dataH\\Magpie_v0.9.1'
        magpiehwnd=list()
        def get_all_hwnd(hwnd,mouse):
            #print(win32process.GetWindowThreadProcessId(hwnd)[1],end=' ')
            #if pid==win32process.GetWindowThreadProcessId(hwnd)[1]==ss.pid:
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                magpiehwnd.append(win32process.GetWindowThreadProcessId(hwnd)[1])
        win32gui.EnumWindows(get_all_hwnd, 0) 
        print(sorted(magpiehwnd))
        ss=subprocess.Popen(f'./magpiecmdrunner.exe "{magpiepath}" {hwnd}')
        print(f'./magpiecmdrunner.exe "{magpiepath}" {hwnd}')
        time.sleep(1)
        print(ss.pid)
        WM_DESTORYHOST=win32api.RegisterWindowMessage( "MAGPIE_WM_DESTORYHOST")  
        print(WM_DESTORYHOST)
        magpiehwnd=list()
        allhwnd=list()
        def get_all_hwnd(hwnd,mouse):
            #print(win32process.GetWindowThreadProcessId(hwnd)[1],end=' ')
            #if pid==win32process.GetWindowThreadProcessId(hwnd)[1]==ss.pid:
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                allhwnd.append(win32process.GetWindowThreadProcessId(hwnd)[1])
                if  win32process.GetWindowThreadProcessId(hwnd)[1]==ss.pid:
                    magpiehwnd.append( (hwnd) )
        win32gui.EnumWindows(get_all_hwnd, 0) 
        print(sorted(magpiehwnd))
        print(sorted(allhwnd))
        win32api.SendMessage(magpiehwnd[0],WM_DESTORYHOST)
        time.sleep(1)
        win32api.SendMessage(magpiehwnd[0],WM_DESTORYHOST)
        break

    