import windows
import threading
from PyQt5.QtGui import   QPixmap,QColor ,QIcon
from PyQt5.QtWidgets import QApplication
import gobject
import os
import time,winrtutils,winsharedutils,hashlib
from myutils.wrapper import threader
def pid_running(pid): 
    try:
        process =windows.AutoHandle(windows.OpenProcess(windows.SYNCHRONIZE, False, pid))
        if(process==0):return False
        ret =windows.WaitForSingleObject(process, 0); 
        return (ret == windows.WAIT_TIMEOUT);

    except:
        return False
@threader
def grabwindow(): 

        
        tm=time.localtime()
        
        fnamebase='./cache/screenshot/{}'.format(0)
        try:
                if gobject.baseobject.textsource.md5!='0':
                        fnamebase='./cache/screenshot/{}'.format(gobject.baseobject.textsource.basename)
        except:
                pass
        if os.path.exists(fnamebase)==False:
                os.mkdir(fnamebase)
        fname='{}/{}-{}-{}-{}-{}-{}'.format(fnamebase,tm.tm_year,tm.tm_mon,tm.tm_mday,tm.tm_hour,tm.tm_min,tm.tm_sec)
        
        hwnd=windows.FindWindow('Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22',None) 
        if hwnd: 
                @threader
                def _():
                        winrtutils._winrt_capture_window(fname+'_winrt_magpie.png',hwnd)
                _()
        hwnd=windows.FindWindow('LosslessScaling',None) 
        if hwnd: 
                @threader
                def _():
                        winrtutils._winrt_capture_window(fname+'_winrt_lossless.png',hwnd)
                _()
        hwnd= windows.GetForegroundWindow()  
        try:
                if hwnd==int(gobject.baseobject.translation_ui.winId()):
                        hwnd=gobject.baseobject.textsource.hwnd
        except:
                pass
        @threader
        def _():
                winrtutils._winrt_capture_window(fname+'_winrt.png',hwnd)
        _()
        _=windows.GetClientRect(hwnd)
        rate=dynamic_rate(hwnd,_)
        w,h= int(_[2]/rate),int(_[3]/rate)
        print(_)
        print(h,w,rate)
        p=QApplication.primaryScreen().grabWindow(hwnd,0,0,w,h)
        p=p.toImage().copy(0,0,w,h)
        if(not p.allGray()):
                p.save(fname+'_gdi.png')
        gobject.baseobject.translation_ui.displaystatus.emit("saved to "+fname,'red',True,True)
def dynamic_rate(hwnd,rect):
        if(getscreenp()==(rect[2],rect[3])):
                rate=1
        else:
                rate=hwndscalerate(hwnd)
        return rate
def getscreenp():       #一些游戏全屏时会修改分辨率，但不会修改系统gdi
        hDC = windows.GetDC(0) 
        h = windows.GetDeviceCaps(hDC, 8)
        w = windows.GetDeviceCaps(hDC, 10)
        windows.ReleaseDC(None, hDC); 
        return h,w
def hwndscalerate(hwnd):
        dpi=(windows.GetDpiForWindow(hwnd))
        rate=getScreenRate()*96/dpi
        return rate

def getpidhwndfirst(pid):
        try:
                hwnds=list()
                def get_all_hwnd(hwnd,_): 
                        if windows.IsWindow(hwnd) and windows.IsWindowEnabled(hwnd) and windows.IsWindowVisible(hwnd): 
                                if  windows.GetWindowThreadProcessId(hwnd)==pid:
                                        hwnds.append( (hwnd) )
                windows.EnumWindows(get_all_hwnd, 0)  
                return hwnds[0]
        except:
                return 0
def getwindowlist():
        windows_list=[]
        pidlist=[]
        windows.EnumWindows(lambda hWnd, param: windows_list.append(hWnd), 0) 
        for hwnd in windows_list:
                try:
                        pid=windows.GetWindowThreadProcessId(hwnd) 
                        pidlist.append(pid)
                except:
                        pass
        return list(set(pidlist))
def getprocesslist():
        
        pids= windows.EnumProcesses()
        return pids
 


def getpidexe(pid):
        hwnd1=windows.AutoHandle(windows.OpenProcess(windows.PROCESS_ALL_ACCESS,False, (pid)))
        if(hwnd1==0):
                
                hwnd1=windows.OpenProcess(windows.PROCESS_QUERY_LIMITED_INFORMATION,False, (pid))
        if(hwnd1==0):
                name_=None
        else:
                name_ = windows.GetProcessFileName( hwnd1) 
        return name_
def testprivilege(pid):
       hwnd1=windows.AutoHandle(windows.OpenProcess(windows.PROCESS_INJECT_ACCESS,False, (pid)))
       return hwnd1!=0


def ListProcess(filt=True):  
        ret=[]
        pids=getprocesslist()
        for pid in pids: 
                    if os.getpid()==pid:
                           continue
                    try: 
                        name_=getpidexe(pid)
                        if name_ is None:continue
                        name=name_.lower()
                        if filt:
                                if ':\\windows\\'  in name   or '\\microsoft\\'  in name or '\\windowsapps\\'  in name:
                                        continue 
                        ret.append([pid,name_ ])
                    except:
                        pass 
        kv={}
        for pid,exe in ret:
                if exe in kv:
                        kv[exe]['pid'].append(pid)
                else:
                        kv[exe]={'pid':[pid]}
        # for exe in kv:
        #         if len(kv[exe]['pid'])>1:
        #                 mems=[getprocessmem(_) for _ in kv[exe]['pid']]
        #                 _i=argsort(mems)
        #                 kv[exe]['pid']=[kv[exe]['pid'][_i[-1]]]
        xxx=[]
        for exe in kv:
                xxx.append([kv[exe]['pid'],exe])
        return xxx

def getExeIcon( name,icon=True,cache=False ): 
            if name.lower()[-4:]=='.lnk':
                  exepath,args,iconpath,dirp=(winsharedutils.GetLnkTargetPath(name))
                  if os.path.exists(iconpath):
                          name=iconpath
                  elif os.path.exists(exepath):
                          name=exepath
            data=winsharedutils.extracticon2data(name)
            if cache:
                fn='./cache/icon/{}.bmp'.format(hashlib.md5(name.encode('utf8')).hexdigest())
            if data: 
                pixmap=QPixmap()
                pixmap.loadFromData(data)  
                if cache:
                        with open(fn,'wb') as ff:
                                ff.write(data)
            else: 
                   succ=False
                   if cache and os.path.exists(fn):
                        try:
                                with open(fn,'rb') as ff:
                                        data=ff.read()
                                pixmap=QPixmap()
                                pixmap.loadFromData(data)  
                                succ=True
                        except:
                                pass
                                #print_exc()
                   if succ==False:
                           pixmap=QPixmap(100,100)
                           pixmap.fill(QColor.fromRgba(0))
            if icon:
                    return QIcon(pixmap)
            else:
                    return pixmap
__rate=0
def getScreenRate() :
    global __rate
    if __rate==0:
        hDC = windows.GetDC(0) 
        dpiX = windows.GetDeviceCaps(hDC, windows.LOGPIXELSX) /96.0;
        windows.ReleaseDC(None, hDC); 
        __rate = round(dpiX, 2)  
    return __rate


def mouseselectwindow(callback): 
        
        def _loop():
                while True:
                        keystate=windows.GetKeyState(windows.VK_LBUTTON ) #必须使用GetKeyState, GetAsyncKeyState或SetWindowHookEx都无法检测到高权限应用上的点击事件。
                        if(keystate<0):
                                break
                        time.sleep(0.01)
                try:
                        pos=windows.GetCursorPos()
                        hwnd=windows.GetAncestor(windows.WindowFromPoint(pos))
                        pid=windows.GetWindowThreadProcessId(hwnd)
                        callback(pid,hwnd)
                except:
                        pass
        threading.Thread(target=_loop).start()
        

def letfullscreen(hwnd):
        wpc= windows.GetWindowPlacement( hwnd,False )
        HWNDStyle = windows.GetWindowLong( hwnd, windows.GWL_STYLE )
        HWNDStyleEx = windows.GetWindowLong( hwnd, windows.GWL_EXSTYLE  )
        NewHWNDStyle=HWNDStyle
        NewHWNDStyle &= ~windows.WS_BORDER;
        NewHWNDStyle &= ~windows.WS_DLGFRAME;
        NewHWNDStyle &= ~windows.WS_THICKFRAME;
        NewHWNDStyleEx=HWNDStyleEx
        NewHWNDStyleEx &= ~windows.WS_EX_WINDOWEDGE;
        windows.SetWindowLong( hwnd, windows.GWL_STYLE, NewHWNDStyle | windows.WS_POPUP );
        windows.SetWindowLong( hwnd, windows.GWL_EXSTYLE, NewHWNDStyleEx | windows.WS_EX_TOPMOST )
        windows.ShowWindow(hwnd,windows.SW_SHOWMAXIMIZED )
        return (wpc,HWNDStyle,HWNDStyleEx)

def recoverwindow(hwnd,status):
        wpc,HWNDStyle,HWNDStyleEx=status
        windows.SetWindowLong( hwnd, windows.GWL_STYLE,  HWNDStyle );
        windows.SetWindowLong( hwnd, windows.GWL_EXSTYLE,  HWNDStyleEx );
        windows.ShowWindow( hwnd, windows.SW_SHOWNORMAL );
        windows.SetWindowPlacement( hwnd, wpc );
def showintab(hwnd,show):
        style_ex=windows.GetWindowLong( hwnd, windows.GWL_EXSTYLE )
        if(show):
                style_ex|=windows.WS_EX_APPWINDOW
                style_ex &= ~windows.WS_EX_TOOLWINDOW
        else: 
                style_ex &=~windows.WS_EX_APPWINDOW
                style_ex |= windows.WS_EX_TOOLWINDOW
        windows.SetWindowLong(hwnd,windows.GWL_EXSTYLE,style_ex)