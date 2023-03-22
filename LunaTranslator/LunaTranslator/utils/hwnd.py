
import win32con ,win32utils
from traceback import print_exc
from PyQt5.QtWinExtras  import QtWin
from PyQt5.QtGui import   QPixmap,QColor ,QIcon
import os
from utils.utils import argsort
def pid_running(pid): 
    try:
        process =win32utils.OpenProcess(win32con.SYNCHRONIZE, False, pid);
        ret =win32utils.WaitForSingleObject(process, 0);
        win32utils.CloseHandle(process);
        return (ret == win32con.WAIT_TIMEOUT);

    except:
        return False
def getpidhwnds(pid):
        try:
                hwnds=list()
                def get_all_hwnd(hwnd,_): 
                        if win32utils.IsWindow(hwnd) and win32utils.IsWindowEnabled(hwnd) and win32utils.IsWindowVisible(hwnd): 
                                if  win32utils.GetWindowThreadProcessId(hwnd)[1]==pid:
                                        hwnds.append( (hwnd) )
                win32utils.EnumWindows(get_all_hwnd, 0)  
                return hwnds
        except:
                return []
def getwindowlist():
        windows_list=[]
        pidlist=[]
        win32utils.EnumWindows(lambda hWnd, param: windows_list.append(hWnd), 0) 
        for hwnd in windows_list:
                try:
                        tid, pid=win32utils.GetWindowThreadProcessId(hwnd) 
                        pidlist.append(pid)
                except:
                        pass
        return list(set(pidlist))
def getprocesslist():
        
        pids= win32utils.EnumProcesses()
        return pids
 
def getarch(pid):
        try: 
                 process=win32utils.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
                  
                 arch='86' if win32utils.IsWow64Process( process)  else '64' 
        except:
                arch=None
        return arch
def getpidexe(pid):
        try:
                hwnd1=win32utils.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
                name_ = win32utils.GetModuleFileNameEx( hwnd1,None )
        except:
                name_=''
        return name_
def getwindowhwnd(pid):
        windows_list=[]
        pidlist=[]
        win32utils.EnumWindows(lambda hWnd, param: windows_list.append(hWnd), 0) 
        for hwnd in windows_list:
                try:
                        tid, _pid=win32utils.GetWindowThreadProcessId(hwnd) 
                        if pid==_pid: 
                                if win32utils.IsWindow(hwnd) and win32utils.IsWindowEnabled(hwnd) and win32utils.IsWindowVisible(hwnd):
                                        return hwnd
                except:
                        pass
        return 0
def ListProcess_old(): 
        windows_list = []
        ret=[]
        win32utils.EnumWindows(lambda hWnd, param: windows_list.append(hWnd), 0)
        for hwnd in windows_list:
            if win32utils.IsWindow(hwnd) and win32utils.IsWindowEnabled(hwnd) and win32utils.IsWindowVisible(hwnd):
                
                  
                    try:
                        pid=win32utils.GetWindowThreadProcessId(hwnd)[1]
                        name_=getpidexe(pid)
 
                        name=name_.lower()
                        if name[-4:]!='.exe' or ':\\windows\\'  in name   or '\\microsoft\\'  in name or '\\windowsapps\\'  in name:
                            continue
                        import os
                        ret.append([pid,name_,hwnd])
                    except:
                        pass
        #print(windows_list)
        #print(ret)
        return ret
  
def getprocessmem(pid):
        try:
                process=win32utils.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, pid)
                memory_info = win32utils.GetProcessMemoryInfo( process )
                return memory_info.WorkingSetSize
        except:
                return 0
def ListProcess(): 
        pid_exe_hwnd= ListProcess_old()

        ret=[]
        pids=getprocesslist()
        for pid in pids: 
                    if os.getpid()==pid:
                           continue
                    try: 
                        name_=getpidexe(pid)
 
                        name=name_.lower()
                        if name[-4:]!='.exe' or ':\\windows\\'  in name   or '\\microsoft\\'  in name or '\\windowsapps\\'  in name:
                            continue 
                        ret.append([pid,name_ ])
                    except:
                        pass
        #print(windows_list)
        #print(ret)
        
        kv={}
        for pid,exe in ret:
                if exe in kv:
                        kv[exe]['pid'].append(pid)
                else:
                        kv[exe]={'pid':[pid],'hwnd':0}
        for exe in kv:
                if len(kv[exe]['pid'])>1:
                        mems=[getprocessmem(_) for _ in kv[exe]['pid']]
                        _i=argsort(mems)
                        kv[exe]['pid']=[kv[exe]['pid'][_i[-1]]]
        for pid,exe,hwnd in pid_exe_hwnd:
                if exe in kv:
                        kv[exe]['hwnd']=hwnd

        xxx=[]
        for exe in kv:
                xxx.append([kv[exe]['pid'][0],exe,kv[exe]['hwnd']])
        return xxx
def getExeIcon( name ): 
            large = win32utils.ExtractIconEx(name)
            if large:
                    pixmap =QtWin.fromHICON(large)
            else:
                   pixmap=QPixmap(100,100)
                   pixmap.fill(QColor.fromRgba(0))
            return QIcon(pixmap)
def getScreenRate() :
    hDC = win32utils.GetDC(0) 
    screen_scale_rate = round(win32utils.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES) /  win32utils.GetSystemMetrics(0), 2) 
    return screen_scale_rate
import pyWinhook
def mouseselectwindow(callback): 
        hm = pyWinhook.HookManager()
        def OnMouseEvent(event):  
            hwnd=win32utils.WindowFromPoint(win32utils.GetCursorPos())
            hm.UnhookMouse()    
            #for pid in pids:
            if True:
                try:
                    tid, pid=win32utils.GetWindowThreadProcessId(hwnd)
                     
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
        wpc=win32utils. GetWindowPlacement( hwnd,False )
        HWNDStyle = win32utils.GetWindowLong( hwnd, win32con.GWL_STYLE )
        HWNDStyleEx = win32utils.GetWindowLong( hwnd, win32con.GWL_EXSTYLE  )
        NewHWNDStyle=HWNDStyle
        NewHWNDStyle &= ~win32con.WS_BORDER;
        NewHWNDStyle &= ~win32con.WS_DLGFRAME;
        NewHWNDStyle &= ~win32con.WS_THICKFRAME;
        NewHWNDStyleEx=HWNDStyleEx
        NewHWNDStyleEx &= ~win32con.WS_EX_WINDOWEDGE;
        win32utils.SetWindowLong( hwnd, win32con.GWL_STYLE, NewHWNDStyle | win32con.WS_POPUP );
        win32utils.SetWindowLong( hwnd, win32con.GWL_EXSTYLE, NewHWNDStyleEx | win32con.WS_EX_TOPMOST )
        win32utils.ShowWindow(hwnd,win32con.SW_SHOWMAXIMIZED )
        return (wpc,HWNDStyle,HWNDStyleEx)

def recoverwindow(hwnd,status):
        wpc,HWNDStyle,HWNDStyleEx=status
        win32utils.SetWindowLong( hwnd, win32con.GWL_STYLE,  HWNDStyle );
        win32utils.SetWindowLong( hwnd, win32con.GWL_EXSTYLE,  HWNDStyleEx );
        win32utils.ShowWindow( hwnd, win32con.SW_SHOWNORMAL );
        win32utils.SetWindowPlacement( hwnd, wpc );
