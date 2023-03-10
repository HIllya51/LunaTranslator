
from ctypes import  c_int,POINTER,pointer,c_uint,windll,c_char_p,create_unicode_buffer,c_wchar_p,c_void_p,c_byte,c_size_t,c_bool,c_ushort,create_string_buffer
from ctypes import Structure,c_int,POINTER,c_uint,WINFUNCTYPE,c_void_p,sizeof,byref
import ctypes
BOOL=c_int
WORD=c_ushort
DWORD=c_uint
WNDENUMPROC =WINFUNCTYPE(c_bool,POINTER(c_int),POINTER(c_int))
class PROCESS_MEMORY_COUNTERS_EX(Structure):
    _fields_=[
        ('cb', c_uint),
        ('PageFaultCount', c_uint),
        ('PeakWorkingSetSize', c_size_t),
        ('WorkingSetSize', c_size_t),
        ('QuotaPeakPagedPoolUsage', c_size_t),
        ('QuotaPagedPoolUsage', c_size_t),
        ('QuotaPeakNonPagedPoolUsage', c_size_t),
        ('QuotaNonPagedPoolUsage', c_size_t),
        ('PagefileUsage', c_size_t),
        ('PeakPagefileUsage', c_size_t),
        ('PrivateUsage', c_size_t),
    ]
 
class RECT(Structure):
    _fields_ = [
        ('left', c_int),
        ('top', c_int),
        ('right', c_int),
        ('botton', c_int)
    ]

class POINT(Structure):
    _fields_=[
            ('x',c_int),
            ('y',c_int),
        ]
class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ('length', c_uint),
        ('flags', c_uint),
        ('showCmd', c_uint),
        ('ptMinPosition', POINT),
        ('ptMaxPosition', POINT),
        ('rcNormalPosition', RECT),
        ('rcDevice', RECT)
        
        
    ]
class STARTUPINFO(Structure):
    _fields_ = [
            ("cb",               c_uint),
            ("lpReserved",       c_wchar_p),
            ("lpDesktop",        c_wchar_p),
            ("lpTitle",          c_wchar_p),
            ("dwX",              c_uint),
            ("dwY",              c_uint),
            ("dwXSize",          c_uint),
            ("dwYSize",          c_uint),
            ("dwXCountChars",    c_uint),
            ("dwYCountChars",    c_uint),
            ("dwFillAtrribute",  c_uint),
            ("dwFlags",          c_uint),
            ("wShowWindow",      c_ushort),
            ("cbReserved2",      c_ushort),
            ("lpReserved2",      POINTER(c_byte)),
            ("hStdInput",        c_void_p),
            ("hStdOutput",       c_void_p),
            ("hStdError",        c_void_p)
    ]

class PROCESS_INFORMATION(Structure):
    _fields_ = [
               ("hProcess",         c_void_p),
               ("hThread",          c_void_p),
               ("dwProcessId",      c_uint),
               ("dwThreadId",       c_uint),
              ]
_user32=windll.User32
_gdi32=windll.Gdi32
_shell32=windll.Shell32
_kernel32=windll.Kernel32
_psapi=windll.Psapi
_Advapi32=windll.Advapi32

_SetWindowPlacement=_user32.SetWindowPlacement
_SetWindowPlacement.argtypes=c_int,POINTER(WINDOWPLACEMENT)
_GetWindowPlacement=_user32.GetWindowPlacement
_GetWindowPlacement.argtypes=c_int,POINTER(WINDOWPLACEMENT)
_GetWindowRect=_user32.GetWindowRect
_GetWindowRect.argtypes=c_int,POINTER(RECT)
_GetForegroundWindow=_user32.GetForegroundWindow
_WindowFromPoint=_user32.WindowFromPoint 
_WindowFromPoint.argtypes=POINT,
_ShowWindow=_user32.ShowWindow
_ShowWindow.argtypes=c_int,c_int

_GetWindowLong=_user32.GetWindowLongW
_GetWindowLong.argtypes=c_int,c_int

_SetWindowLongW=_user32.SetWindowLongW
_SetWindowLongW.argtypes=c_int,c_int,c_int

_GetDC=_user32.GetDC

_GetCursorPos=_user32.GetCursorPos
_GetCursorPos.argtypes=POINTER(POINT),

_GetSystemMetrics=_user32.GetSystemMetrics

_GetDeviceCaps=_gdi32.GetDeviceCaps
_GetDeviceCaps.argtypes=c_int,c_int
_SetWindowPos=_user32.SetWindowPos
_SetWindowPos.argtypes=c_int,c_void_p,c_int,c_int,c_int,c_int,c_uint
_GetWindowText=_user32.GetWindowTextW
_GetWindowText.argtypes=c_int,c_wchar_p,c_int
_GetWindowTextLength=_user32.GetWindowTextLengthW
_MoveWindow=_user32.MoveWindow
_MoveWindow.argtypes=c_int,c_int,c_int,c_int,c_int,c_bool

_IsWindow=_user32.IsWindow
_IsWindowEnabled=_user32.IsWindowEnabled
_IsWindowVisible=_user32.IsWindowVisible

_SetForegroundWindow=_user32.SetForegroundWindow
_SetForegroundWindow.argtypes=c_int,
_GetClientRect=_user32.GetClientRect
_GetClientRect.argtypes=c_int,POINTER(RECT)
_ExtractIconEx=_shell32.ExtractIconExW
_ExtractIconEx.argtypes=c_wchar_p,c_int,c_void_p,c_void_p,c_uint
_FindWindow=_user32.FindWindowW
_FindWindow.argtypes=c_wchar_p,c_wchar_p
_SetFocus=_user32.SetFocus
_SetFocus.argtypes=c_int,
_EnumWindows=_user32.EnumWindows
_EnumWindows.argtypes=WNDENUMPROC,c_void_p
_ShellExecuteW=_shell32.ShellExecuteW
_ShellExecuteW.argtypes=c_void_p,c_wchar_p,c_wchar_p,c_wchar_p,c_wchar_p,c_int
_OpenProcess=_kernel32.OpenProcess
_OpenProcess.argtypes=c_uint,c_bool,c_uint
_CloseHandle=_kernel32.CloseHandle
_SendMessage=_user32.SendMessageW
_SendMessage.argtypes=c_int,c_uint,c_void_p,c_void_p
_keybd_event=_user32.keybd_event
_keybd_event.argtypes=c_byte,c_byte,c_uint,c_void_p
_RegisterWindowMessage=_user32.RegisterWindowMessageW

_GetWindowThreadProcessId=_user32.GetWindowThreadProcessId
_GetClipboardOwner=_user32.GetClipboardOwner
try:
    _GetProcessMemoryInfo=_psapi.GetProcessMemoryInfo
except:
    _GetProcessMemoryInfo=_kernel32.GetProcessMemoryInfo
_GetProcessMemoryInfo.argtypes=c_void_p,POINTER(PROCESS_MEMORY_COUNTERS_EX),c_uint

try:
    _GetModuleFileNameExW=_psapi.GetModuleFileNameExW
except:
    _GetModuleFileNameExW=_kernel32.GetModuleFileNameExW
_GetModuleFileNameExW.argtypes=c_void_p,c_void_p,c_wchar_p,c_uint

_IsWow64Process=_kernel32.IsWow64Process
_CreateProcessW=_kernel32.CreateProcessW
_CreateProcessW.argtypes=c_wchar_p,c_wchar_p,c_void_p,c_void_p,c_bool,c_uint,c_void_p,c_wchar_p,POINTER(STARTUPINFO),POINTER(PROCESS_INFORMATION)

CREATE_NO_WINDOW=0x08000000
def CreateProcess(appName: str, commandLine: str, processAttributes, threadAttributes,  bInheritHandles, dwCreationFlags, newEnvironment, currentDirectory, startupinfo):
    _pinfo=PROCESS_INFORMATION()
    startupinfo.cb = sizeof(startupinfo)
    _CreateProcessW(appName,commandLine,processAttributes,threadAttributes,bInheritHandles,dwCreationFlags,newEnvironment,currentDirectory,byref(startupinfo),byref(_pinfo))
    return  _pinfo
def IsWow64Process(phandle):
    b=c_bool()
    _IsWow64Process(phandle,byref(b))
    return b.value
def GetModuleFileNameEx(hHandle,hmodule):
    w=create_unicode_buffer(65535)
    _GetModuleFileNameExW(hHandle,hmodule,w,65535)
    return w.value
def GetProcessMemoryInfo(processhandle):
    c=PROCESS_MEMORY_COUNTERS_EX()
    _GetProcessMemoryInfo(processhandle,byref(c),sizeof(c))
    return c
def GetClipboardOwner():
    return _GetClipboardOwner()
def GetWindowThreadProcessId(hwnd):
    pid=c_uint()
    handle=_GetWindowThreadProcessId(hwnd,pointer(pid))
    return handle,pid.value
def RegisterWindowMessage(lpString):
    return _RegisterWindowMessage(c_wchar_p(lpString))
def SetFocus(hwnd):
    return _SetFocus(hwnd)
def GetForegroundWindow():
    return _GetForegroundWindow()
def GetWindowRect(hwnd):
    _rect=RECT()
    _GetWindowRect(hwnd,pointer(_rect))
    return (_rect.left,_rect.top,_rect.right,_rect.botton)
def GetClientRect(hwnd): 
    _rect=RECT()
    _GetClientRect(hwnd,pointer(_rect))
    return (_rect.left,_rect.top,_rect.right,_rect.botton)
def GetWindowPlacement(hwnd,_simple):
    _place=WINDOWPLACEMENT()
    _GetWindowPlacement(hwnd,pointer(_place))
    if _simple:
        return (_place.flags, _place.showCmd,)   #只用的着showCmd，所以就先这样了
    else:
        return _place
def SetWindowPlacement(hwnd,_place):
    return _SetWindowPlacement(hwnd,pointer(_place))
def ShowWindow(hwnd,nCmdShow):
    return _ShowWindow(hwnd,nCmdShow)
def GetWindowLong(hwnd,nIndex):
    return _GetWindowLong(hwnd,nIndex)
def SetWindowLong(hwnd,nIndex,value):
    return _SetWindowLongW(hwnd,nIndex,value)
def GetDC(hwnd):
    return _GetDC(hwnd)
def GetSystemMetrics(nIndex):
    return _GetSystemMetrics(nIndex)
def GetCursorPos():
    _p=POINT()
    _GetCursorPos(pointer(_p))
    return _p
def GetDeviceCaps(hdc,index):
    return _GetDeviceCaps(hdc,index)
def WindowFromPoint(point):
    return _WindowFromPoint(point)
def SetWindowPos(hwnd, InsertAfter, X,Y,cx,cy,uFlags):
    return _SetWindowPos(hwnd,InsertAfter,X,Y,cx,cy,uFlags)
def GetWindowText(hwnd):
    length=_GetWindowTextLength(hwnd)
    wchar=create_unicode_buffer(length+1)
    _GetWindowText(hwnd,wchar,length+1)
    return wchar.value
def MoveWindow(hwnd,X,Y,w,h,bRepaint):
    return _MoveWindow(hwnd,X,Y,w,h,bRepaint)
def IsWindow(hwnd):
    return _IsWindow(hwnd)
def IsWindowEnabled(hwnd):
    return _IsWindowEnabled(hwnd)
def IsWindowVisible(hwnd):
    return _IsWindowVisible(hwnd)
def SetForegroundWindow(hwnd):
    return _SetForegroundWindow(hwnd)
def ExtractIconEx(lpszFile): 
    icon1=c_void_p()
    icon2=c_void_p()
    _ExtractIconEx(c_wchar_p(lpszFile),0,pointer(icon1),pointer(icon2),1)
    return icon1.value
def FindWindow(classname,windowname):
    return _FindWindow(c_wchar_p(classname),c_wchar_p(windowname))
def EnumWindows(lpEnumFunc,lParam):
    return _EnumWindows(WNDENUMPROC(lpEnumFunc),0)
def ShellExecute(hwnd: int, op: str, file: str, params: str, _dir: str, bShow):
    return _ShellExecuteW(hwnd,op,file,params,_dir,bShow)
def OpenProcess(dwDesiredAccess,bInheritHandle,dwProcessId):
    return _OpenProcess(dwDesiredAccess,bInheritHandle,dwProcessId)
def CloseHandle(handle):
    return _CloseHandle(handle)
def SendMessage(hwnd,message):
    return _SendMessage(hwnd,message,0,0)
def keybd_event(bVk,bScan,dwFlags,_):
    _keybd_event(bVk,bScan,dwFlags,_)

try:
    _EnumProcesses=_kernel32.EnumProcesses
except:
    _EnumProcesses=_psapi.EnumProcesses

def EnumProcesses():
    buf=(c_uint*1024)()
    dwneed=c_uint()
    _EnumProcesses(pointer(buf),sizeof(buf),pointer(dwneed))
    return (list(buf  )[:dwneed.value//sizeof(c_uint)])

_WaitForSingleObject=_kernel32.WaitForSingleObject
_WaitForSingleObject.argtypes=c_void_p,c_uint
def WaitForSingleObject(handle,dwms):
    return _WaitForSingleObject(handle,dwms)
INFINITE=-1

_SetEvent=_kernel32.SetEvent
def SetEvent(hevent):
    return _SetEvent(hevent)

class ACLStruct(Structure):
    _fields_ = [("AclRevision", c_byte), 
                ("Sbz1", c_byte), 
                ("AclSize", WORD), 
                ("AceCount", WORD), 
                ("Sbz2", WORD)]
 
 
class SID_IDENTIFIER_AUTHORITYStruct(Structure):
    _fields_ = [("Value", c_byte * 6)]
 
 
class SIDStruct(Structure):
    _fields_ = [("Revision", c_byte), 
                ("SubAuthorityCount", c_byte), 
                ("IdentifierAuthority", SID_IDENTIFIER_AUTHORITYStruct), 
                ("SubAuthority", DWORD * 1)]
class SECURITY_DESCRIPTORStruct(Structure):
    _fields_ = [("Revision", c_byte), 
                ("Sbz1",c_byte), 
                ("Control", WORD), 
                ("Owner", ctypes.POINTER(SIDStruct)), 
                ("Group", ctypes.POINTER(SIDStruct)), 
                ("Sacl", ctypes.POINTER(ACLStruct)), 
                ("Dacl", ctypes.POINTER(ACLStruct))]
 
 
class SECURITY_ATTRIBUTESStruct(Structure):
    _fields_ = [("nLength", DWORD), 
                ("lpSecurityDescriptor", ctypes.POINTER(SECURITY_DESCRIPTORStruct)), 
                ("bInheritHandle", BOOL)]
 
_CreateEventW=_kernel32.CreateEventW
_CreateEventW.argtypes=POINTER(SECURITY_ATTRIBUTESStruct),c_bool,c_bool,c_wchar_p
def CreateEvent(secu,bManualReset,bInitialState,lpName):
    return _CreateEventW((secu),bManualReset,bInitialState,lpName)

_InitializeSecurityDescriptor = _Advapi32.InitializeSecurityDescriptor
_InitializeSecurityDescriptor.argtypes = [ctypes.c_void_p, DWORD]
_InitializeSecurityDescriptor.restype = BOOL
_SetSecurityDescriptorDacl = _Advapi32.SetSecurityDescriptorDacl
_SetSecurityDescriptorDacl.argtypes = [ctypes.c_void_p, BOOL, ctypes.c_void_p, BOOL]

def get_SECURITY_ATTRIBUTES():
    sd=SECURITY_DESCRIPTORStruct()
    _InitializeSecurityDescriptor(pointer(sd),1)
    
    _SetSecurityDescriptorDacl(pointer(sd), True, None, False);
    allacc=SECURITY_ATTRIBUTESStruct()
    allacc.nLength=sizeof(allacc)
    allacc.bInheritHandle=False
    allacc.lpSecurityDescriptor=pointer(sd)
    return allacc

_GetBinaryTypeW=_kernel32.GetBinaryTypeW
def GetBinaryType(filename):
    res=c_uint()
    _GetBinaryTypeW(c_wchar_p(filename),byref(res))
    return res.value


_ReadFile=_kernel32.ReadFile
_ReadFile.argtypes=c_void_p,c_char_p,c_uint,c_void_p,c_void_p
def ReadFile(handle,nNumberOfBytesToRead,lpOverlapped):
    buf=create_string_buffer( nNumberOfBytesToRead)
    dwread=c_int()
    _ReadFile(c_void_p(int(handle)),buf,nNumberOfBytesToRead,pointer(dwread),lpOverlapped)
    return buf.raw[:dwread.value]

_WriteFile=_kernel32.WriteFile
_WriteFile.argtypes=c_void_p,c_char_p,c_uint,c_void_p,c_void_p
def WriteFile(handle,_bytes):
    dwread=c_int()
    return _WriteFile(c_void_p(int(handle)),c_char_p(_bytes),len(_bytes),pointer(dwread),None)


_CreateFileW=_kernel32.CreateFileW
_CreateFileW.argtypes=c_wchar_p,c_uint,c_uint,POINTER(SECURITY_ATTRIBUTESStruct),c_uint,c_uint,c_void_p
def CreateFile(fileName,desiredAccess, shareMode,attributes ,CreationDisposition,flagsAndAttributes,hTemplateFile):
    return _CreateFileW(fileName,desiredAccess,shareMode,attributes,CreationDisposition,flagsAndAttributes,hTemplateFile)

_WaitNamedPipeW=_kernel32.WaitNamedPipeW
_WaitNamedPipeW.argtypes=c_wchar_p,c_uint
def WaitNamedPipe(pipename,timeout):
    return _WaitNamedPipeW(pipename,timeout)

_TerminateProcess=_kernel32.TerminateProcess 
_TerminateProcess.argtypes=c_void_p,c_uint
def TerminateProcess(phandle,code):
    return _TerminateProcess(phandle,code)
 
_CreatePipe=_kernel32.CreatePipe 
_CreatePipe.argtypes=c_void_p,c_void_p,c_void_p,c_uint
def CreatePipe(lpsecu,sz):
    hread=c_void_p()
    hwrite=c_void_p()
    _CreatePipe(pointer(hread),pointer(hwrite),lpsecu,sz)
    return hread.value,hwrite.value

_GetCurrentProcess=_kernel32.GetCurrentProcess
_DuplicateHandle=_kernel32.DuplicateHandle
_DuplicateHandle.argtypes=c_void_p,c_void_p,c_void_p,c_void_p,c_uint,c_bool,c_uint
DUPLICATE_SAME_ACCESS=2
def DuplicateHandle(handle):
    TargetHandle=c_void_p()
    _DuplicateHandle(_GetCurrentProcess(),handle,_GetCurrentProcess(),pointer(TargetHandle),0,1,DUPLICATE_SAME_ACCESS)
    return TargetHandle.value

def mciSendString(s):
    _winmm=windll.winmm
    _mciSendStringW=_winmm.mciSendStringW
    _mciSendStringW.argtypes=c_wchar_p,c_wchar_p,c_uint,c_void_p
    return _mciSendStringW(s,None,0,None)



_RegOpenKeyExW=_Advapi32.RegOpenKeyExW
_RegOpenKeyExW.argtypes=c_void_p,c_wchar_p,c_uint,c_uint,c_void_p
ERROR_SUCCESS=0
def RegOpenKeyEx(hKey,lpSubkey,ulOptions,samDesired):
    key=c_void_p()
    if _RegOpenKeyExW(hKey,lpSubkey,ulOptions,samDesired,pointer(key))!=ERROR_SUCCESS:
        raise Exception("RegOpenKeyEx failed")
    return key.value

HKEY_CURRENT_USER=0x80000001
KEY_ALL_ACCESS=0xf003f

_RegQueryInfoKeyW=_Advapi32.RegQueryInfoKeyW
_RegQueryInfoKeyW.argtypes=c_void_p,c_wchar_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p
def RegQueryInfoKey(hkey):
    ValueCount=c_uint()
    MaxValueNameLen=c_uint()
    MaxValueLen=c_uint()
    if _RegQueryInfoKeyW(hkey,None,None,None,None,None,None,pointer(ValueCount),pointer(MaxValueNameLen),pointer(MaxValueLen),None,None)!=ERROR_SUCCESS:
        raise Exception("RegQueryInfoKey failed")
    return ValueCount.value,MaxValueNameLen.value,MaxValueLen.value

_RegEnumValueW=_Advapi32.RegEnumValueW
_RegEnumValueW.argtypes=c_void_p,c_uint,c_wchar_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p

def RegEnumValue(hkey,dwIndex,MaxValueNameLen,MaxValueLen):
    key=create_unicode_buffer(MaxValueNameLen+1)
    value=create_unicode_buffer(MaxValueLen+1)
    vType=c_uint()
    _RegEnumValueW(hkey,dwIndex,key,pointer(c_uint(MaxValueNameLen)),None,pointer(vType),value,pointer(c_uint(MaxValueLen)))
    return key.value,value.value

