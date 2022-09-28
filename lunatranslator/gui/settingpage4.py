import functools
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import  QFont

from PyQt5.QtWidgets import  QWidget,QLabel,QFrame,QPushButton ,QSlider,QSpinBox,QFontComboBox 
import qtawesome 
 
from utils.config import globalconfig 
  
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab4(self) :
     
        self.tab_4 = QWidget()
        self.tab_widget.addTab(self.tab_4, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_4), " 其他设置")
 
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 20, 200, 20)
        label.setText("textractor模式特殊设置")

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 50, 200, 20)
        label.setText("窗口最小化追随")
        self.minifollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['minifollow'],textOff='关闭',textOn='使用')
        self.customSetGeometry(self.minifollowswitch, 200, 50, 66,22)
        self.minifollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('minifollow',x)) 

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 80, 200, 20)
        label.setText("窗口移动追随")
        
        self.movefollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['movefollow'],textOff='关闭',textOn='使用')
        self.customSetGeometry(self.movefollowswitch, 200, 80,66, 22)
        self.movefollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('movefollow',x)) 

        
        # label = QLabel(self.tab_4)
        # self.customSetGeometry(label, 20, 110, 200, 20)
        # #label.setText("窗口失去焦点不再置顶")
        # label.setText("窗口失去焦点最小化")
        # self.focusfollowswitch =gui.switch.SwitchButton(self.tab_4, sign= globalconfig['focusfollow'], startX=(65-20)*self.rate,textOff='关闭',textOn='使用')
        # self.customSetGeometry(self.focusfollowswitch, 200,110, 65, 20)
        # self.focusfollowswitch.checkedChanged.connect(lambda x:globalconfig.__setitem__('focusfollow',x)) 
        # #self.focusfollowswitch.checkedChanged.connect(lambda x:setss(self,x)) 

        hookevents(self)

import ctypes,win32con,sys
import ctypes.wintypes
WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32
# limited information would be sufficient, but our platform doesn't have it.
processFlag = getattr(win32con, 'PROCESS_QUERY_LIMITED_INFORMATION',
                      win32con.PROCESS_QUERY_INFORMATION)

threadFlag = getattr(win32con, 'THREAD_QUERY_LIMITED_INFORMATION',
                     win32con.THREAD_QUERY_INFORMATION)
eventTypes = {  
    win32con.EVENT_OBJECT_FOCUS: "Focus", 
    win32con.EVENT_SYSTEM_MOVESIZEEND:"movesized_end",
    win32con.EVENT_SYSTEM_MOVESIZESTART:"movesized_start",
    win32con.EVENT_SYSTEM_MINIMIZEEND:"取消最小",
    win32con.EVENT_SYSTEM_MINIMIZESTART:"最小化"
}

def log(msg):
    print(msg)

def logError(msg):
    sys.stdout.write(msg + '\n')
def getProcessID(dwEventThread, hwnd):
    # It's possible to have a window we can get a PID out of when the thread
    # isn't accessible, but it's also possible to get called with no window,
    # so we have two approaches.

    hThread = kernel32.OpenThread(threadFlag, 0, dwEventThread)

    if hThread:
        try:
            processID = kernel32.GetProcessIdOfThread(hThread)
            if not processID:
                logError("Couldn't get process for thread %s: %s" %
                         (hThread, ctypes.WinError()))
        finally:
            kernel32.CloseHandle(hThread)
    else:
        errors = ["No thread handle for %s: %s" %
                  (dwEventThread, ctypes.WinError(),)]

        if hwnd:
            processID = ctypes.wintypes.DWORD()
            threadID = user32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(processID))
            if threadID != dwEventThread:
                logError("Window thread != event thread? %s != %s" %
                         (threadID, dwEventThread))
            if processID:
                processID = processID.value
            else:
                errors.append(
                    "GetWindowThreadProcessID(%s) didn't work either: %s" % (
                    hwnd, ctypes.WinError()))
                processID = None
        else:
            processID = None

        if not processID:
            for err in errors:
                logError(err)

    return processID

def callback(self,hWinEventHook, event, hwnd, idObject, idChild, dwEventThread,
             dwmsEventTime ):
    global lastTime
    # length = user32.GetWindowTextLengthW(hwnd)
    # title = ctypes.create_unicode_buffer(length + 1)
    # user32.GetWindowTextW(hwnd, title, length + 1)
   
    #print(rect.left,rect.left,rect.right,rect.top)
    processID = getProcessID(dwEventThread, hwnd)
    if globalconfig['sourcestatus']['textractor']:
        if 'hookpid' in dir(self): 
            # if  globalconfig['focusfollow'] and event==win32con.EVENT_OBJECT_FOCUS:
            #     if processID==self.hookpid: 
            #         self.object.translation_ui.hookfollowsignal.emit(1,(0,0))
            #     else:
            #         self.object.translation_ui.hookfollowsignal.emit(2,(0,0))
             
            if processID==self.hookpid: 
                     
                    if event==win32con.EVENT_SYSTEM_MOVESIZESTART:
                        if globalconfig['movefollow']:
                            rect=ctypes.wintypes.RECT()
                            user32.GetWindowRect(hwnd, ctypes.byref(rect))
                            self.movestart=[rect.left,rect.top,rect.right,rect.bottom]
                            print('startmove')
                    elif event==win32con.EVENT_SYSTEM_MOVESIZEEND:
                        if globalconfig['movefollow']:
                            rect=ctypes.wintypes.RECT()
                            user32.GetWindowRect(hwnd, ctypes.byref(rect))
                            moveend=[rect.left,rect.top,rect.right,rect.bottom]
                            self.object.translation_ui.hookfollowsignal.emit(5,(moveend[0]-self.movestart[0],moveend[1]-self.movestart[1]))
                    elif event==win32con.EVENT_SYSTEM_MINIMIZESTART:
                        if globalconfig['minifollow']: 
                            self.object.translation_ui.hookfollowsignal.emit(4,(0,0))
                    elif event==win32con.EVENT_SYSTEM_MINIMIZEEND:
                        
                        if globalconfig['minifollow']:
                            self.object.translation_ui.hookfollowsignal.emit(3,(0,0))
                          
                # log(u"%-10s\t"
                #     u"P:%-8d\t"
                #     u"%s" % (eventTypes.get(event, hex(event)),
                #     processID or -1,title.value))


def setHook(WinEventProc, eventType):
    return user32.SetWinEventHook(
        eventType,
        eventType,
        0,
        WinEventProc,
        0,
        0,
        win32con.WINEVENT_OUTOFCONTEXT
    )
import threading
 
def hookevents(self):
     
    self.hookthread=threading.Thread(target=functools.partial(hookthreadf,self))
     
    self.hookthread.start()
    
def hookthreadf(self):
    ole32.CoInitialize()
    WinEventProc = WinEventProcType(functools.partial(callback,self))
    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

    self.hooks = [setHook(WinEventProc, et) for et in eventTypes.keys()]
    if not any(self.hooks):
        print('SetWinEventHook failed')
        sys.exit(1)
    msg = ctypes.wintypes.MSG()
     
    while True: 
        ret=user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) 
        
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    
    #ole32.CoUninitialize()
