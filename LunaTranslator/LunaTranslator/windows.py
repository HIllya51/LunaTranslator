from ctypes import (
    c_int,
    POINTER,
    pointer,
    c_uint,
    windll,
    c_char_p,
    create_unicode_buffer,
    c_wchar_p,
    c_void_p,
    c_byte,
    c_size_t,
    c_bool,
    c_ushort,
    create_string_buffer,
    c_short,
)
from ctypes import (
    Structure,
    c_int,
    POINTER,
    c_uint,
    WINFUNCTYPE,
    c_void_p,
    sizeof,
    byref,
)
import ctypes, os
from traceback import print_exc
from ctypes.wintypes import (
    RECT,
    POINT,
    HWND,
    BOOL,
    WORD,
    DWORD,
    BYTE,
    LPCWSTR,
    HANDLE,
    UINT,
)

WAIT_TIMEOUT = 258
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_SHOWNOACTIVATE = 4

SW_NORMAL = 1
STARTF_USESTDHANDLES = 256
STARTF_USESHOWWINDOW = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_MAXIMIZE = 3

EVENT_SYSTEM_MINIMIZESTART = 22
EVENT_SYSTEM_MINIMIZEEND = 23
EVENT_SYSTEM_MOVESIZESTART = 10
EVENT_SYSTEM_MOVESIZEEND = 11
EVENT_SYSTEM_FOREGROUND = 3


PIPE_ACCESS_INBOUND = 0x00000001
PIPE_ACCESS_OUTBOUND = 0x00000002
SW_SHOW = 5
SW_MINIMIZE = 6
PROCESS_QUERY_INFORMATION = 1024
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_VM_READ = 16
NMPWAIT_WAIT_FOREVER = -1
SECURITY_DESCRIPTOR_REVISION = 1
PIPE_UNLIMITED_INSTANCES = 255
PIPE_WAIT = 0
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
PIPE_READMODE_MESSAGE = 2
PIPE_TYPE_MESSAGE = 4
OPEN_EXISTING = 3
PIPE_ACCESS_DUPLEX = 3
FILE_ATTRIBUTE_NORMAL = 128
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11
SW_MAX = 11
WS_MINIMIZE = 536870912
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SW_HIDE = 0
SWP_NOACTIVATE = 16
SWP_NOMOVE = 2
SW_MAXIMIZE = 3
SW_SHOWNORMAL = 1
WS_EX_TOOLWINDOW = 128
SWP_NOSIZE = 1
SW_SHOW = 5
WS_MAXIMIZE = 16777216
NMPWAIT_WAIT_FOREVER = -1
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 128
STANDARD_RIGHTS_REQUIRED = 983040
SYNCHRONIZE = 1048576
PROCESS_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 4095
PROCESS_CREATE_THREAD = 0x0002
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_WRITE = 0x0020
PROCESS_INJECT_ACCESS = (
    PROCESS_CREATE_THREAD
    | PROCESS_QUERY_INFORMATION
    | PROCESS_VM_OPERATION
    | PROCESS_VM_WRITE
    | PROCESS_VM_READ
)
KEYEVENTF_KEYUP = 2
GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_BORDER = 8388608
WS_DLGFRAME = 4194304
WS_THICKFRAME = 262144
WS_EX_TRANSPARENT = 32
WS_EX_WINDOWEDGE = 256
WS_POPUP = -2147483648
WS_EX_TOPMOST = 8
SW_SHOWMAXIMIZED = 3
WS_EX_APPWINDOW = 262144
DESKTOPHORZRES = 118
LOGPIXELSX = 88
WM_HOTKEY = 786

VK_LBUTTON = 1
VK_RBUTTON = 2


WNDENUMPROC = WINFUNCTYPE(c_bool, c_void_p, c_void_p)


class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ("length", c_uint),
        ("flags", c_uint),
        ("showCmd", c_uint),
        ("ptMinPosition", POINT),
        ("ptMaxPosition", POINT),
        ("rcNormalPosition", RECT),
        ("rcDevice", RECT),
    ]


class STARTUPINFO(Structure):
    _fields_ = [
        ("cb", c_uint),
        ("lpReserved", c_wchar_p),
        ("lpDesktop", c_wchar_p),
        ("lpTitle", c_wchar_p),
        ("dwX", c_uint),
        ("dwY", c_uint),
        ("dwXSize", c_uint),
        ("dwYSize", c_uint),
        ("dwXCountChars", c_uint),
        ("dwYCountChars", c_uint),
        ("dwFillAtrribute", c_uint),
        ("dwFlags", c_uint),
        ("wShowWindow", c_ushort),
        ("cbReserved2", c_ushort),
        ("lpReserved2", POINTER(c_byte)),
        ("hStdInput", c_void_p),
        ("hStdOutput", c_void_p),
        ("hStdError", c_void_p),
    ]


class PROCESS_INFORMATION(Structure):
    _fields_ = [
        ("hProcess", c_void_p),
        ("hThread", c_void_p),
        ("dwProcessId", c_uint),
        ("dwThreadId", c_uint),
    ]


class UNIVERSAL_NAME_INFO(Structure):
    _fields_ = [("lpUniversalName", c_wchar_p)]


_user32 = windll.User32
_gdi32 = windll.Gdi32
_shell32 = windll.Shell32
_kernel32 = windll.Kernel32
_psapi = windll.Psapi
_Advapi32 = windll.Advapi32

_SetWindowPlacement = _user32.SetWindowPlacement
_SetWindowPlacement.argtypes = c_int, POINTER(WINDOWPLACEMENT)
_GetWindowPlacement = _user32.GetWindowPlacement
_GetWindowPlacement.argtypes = c_int, POINTER(WINDOWPLACEMENT)
_GetWindowRect = _user32.GetWindowRect
_GetWindowRect.argtypes = c_int, POINTER(RECT)
_GetForegroundWindow = _user32.GetForegroundWindow
_WindowFromPoint = _user32.WindowFromPoint
_WindowFromPoint.argtypes = (POINT,)
_ShowWindow = _user32.ShowWindow
_ShowWindow.argtypes = c_int, c_int

_GetWindowLong = _user32.GetWindowLongW
_GetWindowLong.argtypes = c_int, c_int

_SetWindowLongW = _user32.SetWindowLongW
_SetWindowLongW.argtypes = c_int, c_int, c_int

_GetDC = _user32.GetDC
_GetDC.restype = c_void_p
_ReleaseDC = _user32.ReleaseDC
_ReleaseDC.argtypes = c_void_p, c_void_p


def ReleaseDC(_, hdc):
    return _ReleaseDC(_, hdc)


_GetCursorPos = _user32.GetCursorPos
_GetCursorPos.argtypes = (POINTER(POINT),)


_GetDeviceCaps = _gdi32.GetDeviceCaps
_GetDeviceCaps.argtypes = c_int, c_int
_SetWindowPos = _user32.SetWindowPos
_SetWindowPos.argtypes = c_int, c_void_p, c_int, c_int, c_int, c_int, c_uint
_GetWindowText = _user32.GetWindowTextW
_GetWindowText.argtypes = HWND, c_wchar_p, c_int
_GetWindowTextLength = _user32.GetWindowTextLengthW
_MoveWindow = _user32.MoveWindow
_MoveWindow.argtypes = c_int, c_int, c_int, c_int, c_int, c_bool

_IsWindow = _user32.IsWindow
_IsWindowEnabled = _user32.IsWindowEnabled
_IsWindowVisible = _user32.IsWindowVisible

_SetForegroundWindow = _user32.SetForegroundWindow
_SetForegroundWindow.argtypes = (c_int,)
_GetClientRect = _user32.GetClientRect
_GetClientRect.argtypes = c_int, POINTER(RECT)

_FindWindow = _user32.FindWindowW
_FindWindow.argtypes = c_wchar_p, c_wchar_p
_SetFocus = _user32.SetFocus
_SetFocus.argtypes = (c_int,)
_EnumWindows = _user32.EnumWindows
_EnumWindows.argtypes = WNDENUMPROC, c_void_p
_ShellExecuteW = _shell32.ShellExecuteW
_ShellExecuteW.argtypes = c_void_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int
_OpenProcess = _kernel32.OpenProcess
_OpenProcess.argtypes = c_uint, c_bool, c_uint
_CloseHandle = _kernel32.CloseHandle
_SendMessage = _user32.SendMessageW
_SendMessage.argtypes = c_int, c_uint, c_void_p, c_void_p
_keybd_event = _user32.keybd_event
_keybd_event.argtypes = c_byte, c_byte, c_uint, c_void_p
_RegisterWindowMessage = _user32.RegisterWindowMessageW

_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_GetClipboardOwner = _user32.GetClipboardOwner

try:
    _GetModuleFileNameExW = _psapi.GetModuleFileNameExW
except:
    _GetModuleFileNameExW = _kernel32.GetModuleFileNameExW
_GetModuleFileNameExW.argtypes = c_void_p, c_void_p, c_wchar_p, c_uint


def GetModuleFileNameEx(handle, module=None):
    buff = create_unicode_buffer(260)
    _GetModuleFileNameExW(handle, module, buff, 260)
    return buff.value


_GetLogicalDrives = _kernel32.GetLogicalDrives
_QueryDosDeviceW = _kernel32.QueryDosDeviceW
_QueryDosDeviceW.argtypes = c_wchar_p, c_wchar_p, c_uint

try:
    _GetProcessImageFileNameW = _psapi.GetProcessImageFileNameW
except:
    _GetProcessImageFileNameW = _kernel32.GetProcessImageFileNameW
_GetProcessImageFileNameW.argtypes = c_void_p, c_wchar_p, c_uint

_Mpr = windll.Mpr
_WNetGetConnectionW = _Mpr.WNetGetConnectionW
_WNetGetConnectionW.argtypes = c_wchar_p, c_wchar_p, c_void_p

_WNetGetUniversalNameW = _Mpr.WNetGetUniversalNameW
_WNetGetUniversalNameW.argtypes = c_wchar_p, c_uint, c_wchar_p, POINTER(c_uint)

_GetLogicalDriveStringsW = _kernel32.GetLogicalDriveStringsW
_GetLogicalDriveStringsW.argtypes = c_uint, c_wchar_p

_GetCurrentDirectoryW = _kernel32.GetCurrentDirectoryW
_GetCurrentDirectoryW.argtypes = c_uint, c_wchar_p

try:
    _QueryFullProcessImageNameW = _kernel32.QueryFullProcessImageNameW
    _QueryFullProcessImageNameW.argtypes = c_void_p, c_uint, c_wchar_p, c_void_p
except:
    _QueryFullProcessImageNameW = 0


def GetProcessFileName(hHandle):
    w = create_unicode_buffer(65535)
    # 我佛了，太混乱了，不同权限获取的东西完全不一样
    if (
        _GetModuleFileNameExW(hHandle, None, w, 65535) == 0
        and (
            _QueryFullProcessImageNameW != 0
            and _QueryFullProcessImageNameW(hHandle, 0, w, pointer(c_uint())) == 0
        )
        and _GetProcessImageFileNameW(hHandle, w, 65535) == 0
    ):
        return

    v = w.value
    if v[0] == "\\":

        buf = create_unicode_buffer(65535)
        for i in range(26):
            A = ord("A") + i
            if _QueryDosDeviceW(chr(A) + ":", buf, 65535) != 0:
                prefixdos = buf.value
                if v.startswith(prefixdos):
                    v = chr(A) + ":" + v[len(prefixdos) :]
                    break

            # Get network drive

            # 我操了，使用管理员权限时，这个玩意会失败
            if _WNetGetUniversalNameW(chr(A) + ":", 1, buf, byref(c_uint(65535))) == 0:
                prefixnetwork = ctypes.cast(
                    buf, POINTER(UNIVERSAL_NAME_INFO)
                ).contents.lpUniversalName
                if v.startswith(prefixnetwork):
                    v = chr(A) + ":" + v[len(prefixnetwork) :]
                    break
        return v
    else:
        return v


_CreateProcessW = _kernel32.CreateProcessW
_CreateProcessW.argtypes = (
    c_wchar_p,
    c_wchar_p,
    c_void_p,
    c_void_p,
    c_bool,
    c_uint,
    c_void_p,
    c_wchar_p,
    POINTER(STARTUPINFO),
    POINTER(PROCESS_INFORMATION),
)

CREATE_NO_WINDOW = 0x08000000


def CreateProcess(
    appName,
    commandLine,
    processAttributes,
    threadAttributes,
    bInheritHandles,
    dwCreationFlags,
    newEnvironment,
    currentDirectory,
    startupinfo,
):
    _pinfo = PROCESS_INFORMATION()
    startupinfo.cb = sizeof(startupinfo)
    _CreateProcessW(
        appName,
        commandLine,
        processAttributes,
        threadAttributes,
        bInheritHandles,
        dwCreationFlags,
        newEnvironment,
        currentDirectory,
        byref(startupinfo),
        byref(_pinfo),
    )
    return _pinfo


def GetClipboardOwner():
    return _GetClipboardOwner()


def GetWindowThreadProcessId(hwnd):
    pid = c_uint()
    handle = _GetWindowThreadProcessId(hwnd, pointer(pid))
    return pid.value


def RegisterWindowMessage(lpString):
    return _RegisterWindowMessage(c_wchar_p(lpString))


def SetFocus(hwnd):
    return _SetFocus(hwnd)


def GetForegroundWindow():
    return _GetForegroundWindow()


def GetWindowRect(hwnd):
    _rect = RECT()
    if _GetWindowRect(hwnd, pointer(_rect)):
        return (_rect.left, _rect.top, _rect.right, _rect.bottom)
    else:
        return None


def GetClientRect(hwnd):
    _rect = RECT()
    _GetClientRect(hwnd, pointer(_rect))
    return (_rect.left, _rect.top, _rect.right, _rect.bottom)


def GetWindowPlacement(hwnd, _simple):
    _place = WINDOWPLACEMENT()
    _GetWindowPlacement(hwnd, pointer(_place))
    if _simple:
        return (
            _place.flags,
            _place.showCmd,
        )  # 只用的着showCmd，所以就先这样了
    else:
        return _place


def SetWindowPlacement(hwnd, _place):
    return _SetWindowPlacement(hwnd, pointer(_place))


def ShowWindow(hwnd, nCmdShow):
    return _ShowWindow(hwnd, nCmdShow)


def GetWindowLong(hwnd, nIndex):
    return _GetWindowLong(hwnd, nIndex)


def SetWindowLong(hwnd, nIndex, value):
    return _SetWindowLongW(hwnd, nIndex, value)


def GetDC(hwnd):
    return _GetDC(hwnd)


def GetDpiForWindow(hwnd):
    try:
        _GetDpiForWindow = _user32.GetDpiForWindow
        _GetDpiForWindow.argtypes = (HWND,)
        _GetDpiForWindow.restype = UINT
        return _GetDpiForWindow(hwnd)
    except:
        return 96


def GetCursorPos():
    _p = POINT()
    _GetCursorPos(pointer(_p))
    return _p


def GetDeviceCaps(hdc, index):
    return _GetDeviceCaps(hdc, index)


def WindowFromPoint(point):
    return _WindowFromPoint(point)


def SetWindowPos(hwnd, InsertAfter, X, Y, cx, cy, uFlags):
    return _SetWindowPos(hwnd, InsertAfter, X, Y, cx, cy, uFlags)


def GetWindowText(hwnd):
    length = _GetWindowTextLength(hwnd)
    wchar = create_unicode_buffer(length + 1)
    _GetWindowText(hwnd, wchar, length + 1)
    return wchar.value


def MoveWindow(hwnd, X, Y, w, h, bRepaint):
    return _MoveWindow(hwnd, X, Y, w, h, bRepaint)


def IsWindow(hwnd):
    return _IsWindow(hwnd)


def IsWindowEnabled(hwnd):
    return _IsWindowEnabled(hwnd)


def IsWindowVisible(hwnd):
    return _IsWindowVisible(hwnd)


def SetForegroundWindow(hwnd):
    return _SetForegroundWindow(hwnd)


def FindWindow(classname, windowname):
    return _FindWindow(c_wchar_p(classname), c_wchar_p(windowname))


def EnumWindows(lpEnumFunc, lParam):
    return _EnumWindows(WNDENUMPROC(lpEnumFunc), 0)


def ShellExecute(hwnd: int, op: str, file: str, params: str, _dir: str, bShow):
    return _ShellExecuteW(hwnd, op, file, params, _dir, bShow)


def OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId):
    return _OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)


def CloseHandle(handle):
    return _CloseHandle(handle)


def SendMessage(hwnd, message, wp=None, lp=None):
    return _SendMessage(hwnd, message, wp, lp)


def keybd_event(bVk, bScan, dwFlags, _):
    _keybd_event(bVk, bScan, dwFlags, _)


try:
    _EnumProcesses = _kernel32.EnumProcesses
except:
    _EnumProcesses = _psapi.EnumProcesses


def EnumProcesses():
    buf = (c_uint * 1024)()
    dwneed = c_uint()
    _EnumProcesses(pointer(buf), sizeof(buf), pointer(dwneed))
    return list(buf)[: dwneed.value // sizeof(c_uint)]


_WaitForSingleObject = _kernel32.WaitForSingleObject
_WaitForSingleObject.argtypes = c_void_p, c_uint


def WaitForSingleObject(handle, dwms):
    return _WaitForSingleObject(handle, dwms)


INFINITE = -1

_SetEvent = _kernel32.SetEvent


def SetEvent(hevent):
    return _SetEvent(hevent)


class ACLStruct(Structure):
    _fields_ = [
        ("AclRevision", c_byte),
        ("Sbz1", c_byte),
        ("AclSize", WORD),
        ("AceCount", WORD),
        ("Sbz2", WORD),
    ]


class SID_IDENTIFIER_AUTHORITYStruct(Structure):
    _fields_ = [("Value", c_byte * 6)]


class SIDStruct(Structure):
    _fields_ = [
        ("Revision", c_byte),
        ("SubAuthorityCount", c_byte),
        ("IdentifierAuthority", SID_IDENTIFIER_AUTHORITYStruct),
        ("SubAuthority", DWORD * 1),
    ]


class SECURITY_DESCRIPTORStruct(Structure):
    _fields_ = [
        ("Revision", c_byte),
        ("Sbz1", c_byte),
        ("Control", WORD),
        ("Owner", ctypes.POINTER(SIDStruct)),
        ("Group", ctypes.POINTER(SIDStruct)),
        ("Sacl", ctypes.POINTER(ACLStruct)),
        ("Dacl", ctypes.POINTER(ACLStruct)),
    ]


class SECURITY_ATTRIBUTESStruct(Structure):
    _fields_ = [
        ("nLength", DWORD),
        ("lpSecurityDescriptor", ctypes.POINTER(SECURITY_DESCRIPTORStruct)),
        ("bInheritHandle", BOOL),
    ]


_InitializeSecurityDescriptor = _Advapi32.InitializeSecurityDescriptor
_InitializeSecurityDescriptor.argtypes = [ctypes.c_void_p, DWORD]
_InitializeSecurityDescriptor.restype = BOOL
_SetSecurityDescriptorDacl = _Advapi32.SetSecurityDescriptorDacl
_SetSecurityDescriptorDacl.argtypes = [ctypes.c_void_p, BOOL, ctypes.c_void_p, BOOL]


def get_SECURITY_ATTRIBUTES():
    sd = SECURITY_DESCRIPTORStruct()
    _InitializeSecurityDescriptor(pointer(sd), 1)

    _SetSecurityDescriptorDacl(pointer(sd), True, None, False)
    allacc = SECURITY_ATTRIBUTESStruct()
    allacc.nLength = sizeof(allacc)
    allacc.bInheritHandle = False
    allacc.lpSecurityDescriptor = pointer(sd)
    return allacc


_CreateEventW = _kernel32.CreateEventW
_CreateEventW.argtypes = POINTER(SECURITY_ATTRIBUTESStruct), c_bool, c_bool, c_wchar_p


def CreateEvent(bManualReset, bInitialState, lpName, secu=get_SECURITY_ATTRIBUTES()):
    return _CreateEventW(pointer(secu), bManualReset, bInitialState, lpName)


_CreateMutexW = _kernel32.CreateMutexW
_CreateMutexW.argtypes = POINTER(SECURITY_ATTRIBUTESStruct), BOOL, LPCWSTR


def CreateMutex(bInitialOwner, lpName, secu=get_SECURITY_ATTRIBUTES()):
    return _CreateMutexW(pointer(secu), bInitialOwner, lpName)


_GetLastError = _kernel32.GetLastError


def GetLastError():
    return _GetLastError()


ERROR_ALREADY_EXISTS = 183

_GetBinaryTypeW = _kernel32.GetBinaryTypeW


def GetBinaryType(filename):
    res = c_uint()
    _GetBinaryTypeW(c_wchar_p(filename), byref(res))
    return res.value


_ReadFile = _kernel32.ReadFile
_ReadFile.argtypes = HANDLE, c_char_p, c_uint, c_void_p, c_void_p


def ReadFile(handle, nNumberOfBytesToRead, lpOverlapped=None):
    buf = create_string_buffer(nNumberOfBytesToRead)
    dwread = c_int()
    _ReadFile(handle, buf, nNumberOfBytesToRead, pointer(dwread), lpOverlapped)
    return buf.raw[: dwread.value]


_WriteFile = _kernel32.WriteFile
_WriteFile.argtypes = HANDLE, c_char_p, c_uint, c_void_p, c_void_p


def WriteFile(handle, _bytes):
    dwread = c_int()
    return _WriteFile(handle, c_char_p(_bytes), len(_bytes), pointer(dwread), None)


_CreateFileW = _kernel32.CreateFileW
_CreateFileW.argtypes = (
    c_wchar_p,
    c_uint,
    c_uint,
    POINTER(SECURITY_ATTRIBUTESStruct),
    c_uint,
    c_uint,
    c_void_p,
)
_CreateFileW.restype = HANDLE


def CreateFile(
    fileName,
    desiredAccess,
    shareMode,
    attributes,
    CreationDisposition,
    flagsAndAttributes,
    hTemplateFile,
):
    return _CreateFileW(
        fileName,
        desiredAccess,
        shareMode,
        attributes,
        CreationDisposition,
        flagsAndAttributes,
        hTemplateFile,
    )


_WaitNamedPipeW = _kernel32.WaitNamedPipeW
_WaitNamedPipeW.argtypes = c_wchar_p, c_uint


def WaitNamedPipe(pipename, timeout):
    return _WaitNamedPipeW(pipename, timeout)


# _TerminateProcess=_kernel32.TerminateProcess
# _TerminateProcess.argtypes=c_void_p,c_uint
# def TerminateProcess(phandle,code):
#     return _TerminateProcess(phandle,code)


# _GetCurrentProcess=_kernel32.GetCurrentProcess
# _DuplicateHandle=_kernel32.DuplicateHandle
# _DuplicateHandle.argtypes=c_void_p,c_void_p,c_void_p,c_void_p,c_uint,c_bool,c_uint
# DUPLICATE_SAME_ACCESS=2
# def DuplicateHandle(handle):
#     TargetHandle=c_void_p()
#     _DuplicateHandle(_GetCurrentProcess(),handle,_GetCurrentProcess(),pointer(TargetHandle),0,1,DUPLICATE_SAME_ACCESS)
#     return TargetHandle.value


def mciSendString(s):
    _winmm = windll.winmm
    _mciSendStringW = _winmm.mciSendStringW
    _mciSendStringW.argtypes = c_wchar_p, c_wchar_p, c_uint, c_void_p
    bf = create_unicode_buffer(1024)
    if _mciSendStringW(s, bf, 1024, None) != 0:
        return None
    return bf.value


# _RegOpenKeyExW=_Advapi32.RegOpenKeyExW
# _RegOpenKeyExW.argtypes=c_void_p,c_wchar_p,c_uint,c_uint,c_void_p
# ERROR_SUCCESS=0
# def RegOpenKeyEx(hKey,lpSubkey,ulOptions,samDesired):
#     key=c_void_p()
#     if _RegOpenKeyExW(hKey,lpSubkey,ulOptions,samDesired,pointer(key))!=ERROR_SUCCESS:
#         raise Exception("RegOpenKeyEx failed")
#     return key.value

# HKEY_CURRENT_USER=0x80000001
# KEY_ALL_ACCESS=0xf003f

# _RegQueryInfoKeyW=_Advapi32.RegQueryInfoKeyW
# _RegQueryInfoKeyW.argtypes=c_void_p,c_wchar_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p
# def RegQueryInfoKey(hkey):
#     ValueCount=c_uint()
#     MaxValueNameLen=c_uint()
#     MaxValueLen=c_uint()
#     if _RegQueryInfoKeyW(hkey,None,None,None,None,None,None,pointer(ValueCount),pointer(MaxValueNameLen),pointer(MaxValueLen),None,None)!=ERROR_SUCCESS:
#         raise Exception("RegQueryInfoKey failed")
#     return ValueCount.value,MaxValueNameLen.value,MaxValueLen.value

# _RegEnumValueW=_Advapi32.RegEnumValueW
# _RegEnumValueW.argtypes=c_void_p,c_uint,c_wchar_p,c_void_p,c_void_p,c_void_p,c_void_p,c_void_p

# def RegEnumValue(hkey,dwIndex,MaxValueNameLen,MaxValueLen):
#     key=create_unicode_buffer(MaxValueNameLen+1)
#     value=create_unicode_buffer(MaxValueLen+1)
#     vType=c_uint()
#     _RegEnumValueW(hkey,dwIndex,key,pointer(c_uint(MaxValueNameLen)),None,pointer(vType),value,pointer(c_uint(MaxValueLen)))
#     return key.value,value.value

_IsUserAnAdmin = _shell32.IsUserAnAdmin


def IsUserAnAdmin():
    try:
        return bool(_IsUserAnAdmin())
    except:
        return False


_GetKeyState = _user32.GetKeyState
_GetKeyState.restype = c_short


def GetKeyState(key):
    return _GetKeyState(key)


GA_ROOT = 2
_GetAncestor = _user32.GetAncestor


def GetAncestor(hwnd):
    return _GetAncestor(hwnd, GA_ROOT)


_CreateNamedPipe = _kernel32.CreateNamedPipeW
_CreateNamedPipe.argtypes = (
    c_wchar_p,
    c_uint,
    c_uint,
    c_uint,
    c_uint,
    c_uint,
    c_uint,
    c_void_p,
)


def CreateNamedPipe(
    pipeName,
    openMode,
    pipeMode,
    nMaxInstances,
    nOutBufferSize,
    nInBufferSize,
    nDefaultTimeOut,
    sa=pointer(get_SECURITY_ATTRIBUTES()),
):
    return _CreateNamedPipe(
        pipeName,
        openMode,
        pipeMode,
        nMaxInstances,
        nOutBufferSize,
        nInBufferSize,
        nDefaultTimeOut,
        sa,
    )


PIPE_TYPE_BYTE = 0
PIPE_READMODE_BYTE = 0
_DisconnectNamedPipe = _kernel32.DisconnectNamedPipe


def DisconnectNamedPipe(pipe):
    return _DisconnectNamedPipe(pipe)


_ConnectNamedPipe = _kernel32.ConnectNamedPipe


def ConnectNamedPipe(pipe, lpoverlap):
    return _ConnectNamedPipe(pipe, lpoverlap)


_MessageBoxW = _user32.MessageBoxW
_MessageBoxW.argtypes = c_void_p, c_wchar_p, c_wchar_p, c_uint


def MessageBox(hwnd, text, title, _type):
    return _MessageBoxW(hwnd, text, title, _type)


_CancelIo = _kernel32.CancelIo
_CancelIo.argtypes = (c_void_p,)


def CancelIo(hfile):
    return _CancelIo(hfile)


def GetDpiForWindow(hwnd):
    try:
        _GetDpiForWindow = _user32.GetDpiForWindow
    except:
        return 96

    return _GetDpiForWindow(hwnd)


_ScreenToClient = _user32.ScreenToClient
_ScreenToClient.argtypes = c_void_p, POINTER(POINT)


def ScreenToClient(hwnd, x, y):
    P = POINT()
    P.x = int(x)
    P.y = int(y)
    _ScreenToClient(hwnd, pointer(P))
    return (P.x, P.y)


INVALID_HANDLE_VALUE = -1


class AutoHandle(HANDLE):
    def __new__(cls, value) -> None:
        instance = super().__new__(cls, value)
        return instance

    def __del__(self):
        if self:
            CloseHandle(self)

    def __bool__(self):
        return (self.value != INVALID_HANDLE_VALUE) and (self.value != None)


_MapVirtualKey = _user32.MapVirtualKeyW
_MapVirtualKey.argtypes = UINT, UINT
_MapVirtualKey.restype = UINT
MAPVK_VK_TO_VSC = 0
MAPVK_VSC_TO_VK = 1
MAPVK_VK_TO_CHAR = 2


def MapVirtualKey(char, uMapType=MAPVK_VK_TO_CHAR):
    return _MapVirtualKey(ord(char), uMapType)


_CreatePipe = _kernel32.CreatePipe
_CreatePipe.argtypes = c_void_p, c_void_p, c_void_p, c_uint


def CreatePipe(lpsecu=None, sz=0):
    hread = HANDLE()
    hwrite = HANDLE()
    _CreatePipe(pointer(hread), pointer(hwrite), lpsecu, sz)
    return AutoHandle(hread.value), AutoHandle(hwrite.value)


_CopyFile = _kernel32.CopyFileW
_CopyFile.argtypes = LPCWSTR, LPCWSTR, BOOL
_CopyFile.restype = BOOL


def CopyFile(src, dst, bFailIfExists):
    return _CopyFile(src, dst, bFailIfExists)


_SetPropW = _user32.SetPropW
_SetPropW.argtypes = HWND, LPCWSTR, HANDLE
_SetPropW.restype = BOOL


def SetProp(hwnd, string, hdata):
    return _SetPropW(hwnd, string, hdata)


_GetEnvironmentVariableW = _kernel32.GetEnvironmentVariableW
_GetEnvironmentVariableW.argtypes = c_wchar_p, c_wchar_p, DWORD
_SetEnvironmentVariableW = _kernel32.SetEnvironmentVariableW
_SetEnvironmentVariableW.argtypes = LPCWSTR, LPCWSTR


def addenvpath(path):
    path = os.path.abspath(path)
    env = create_unicode_buffer(65535)
    _GetEnvironmentVariableW("PATH", env, 65535)
    _SetEnvironmentVariableW("PATH", env.value + ";" + path)


_LoadLibraryW = _kernel32.LoadLibraryW
_LoadLibraryW.argtypes = (LPCWSTR,)


def loadlibrary(path):
    _LoadLibraryW(path)


SECTION_MAP_WRITE = 0x0002
SECTION_MAP_READ = 0x0004
FILE_MAP_WRITE = SECTION_MAP_WRITE
FILE_MAP_READ = SECTION_MAP_READ
_OpenFileMapping = _kernel32.OpenFileMappingW
_OpenFileMapping.argtypes = DWORD, BOOL, LPCWSTR
_OpenFileMapping.restype = HANDLE


def OpenFileMapping(acc, inher, name):
    return _OpenFileMapping(acc, inher, name)


_MapViewOfFile = _kernel32.MapViewOfFile
_MapViewOfFile.argtypes = HANDLE, DWORD, DWORD, DWORD, c_size_t
_MapViewOfFile.restype = c_void_p


def MapViewOfFile(hfmap, acc, high, low, size):
    return _MapViewOfFile(hfmap, acc, high, low, size)


IsZoomed = _user32.IsZoomed
IsZoomed.argtypes = (HWND,)
IsZoomed.restype = BOOL
