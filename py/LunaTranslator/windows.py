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
    CFUNCTYPE,
    c_short,
    Structure,
    WINFUNCTYPE,
    sizeof,
    byref,
    cast,
)
import os
from ctypes.wintypes import (
    RECT,
    POINT,
    HWND,
    BOOL,
    WORD,
    DWORD,
    LONG,
    MSG,
    PHKEY,
    HKEY,
    LPDWORD,
    LPBYTE,
    HMONITOR,
    LPCVOID,
    LPMSG,
    LPWSTR,
    WPARAM,
    LPARAM,
    INT,
    LPCWSTR,
    HANDLE,
    UINT,
    HHOOK,
    HMODULE,
    LPLONG,
    HDC,
    SHORT,
    USHORT,
)

HRESULT = LONG
HWINEVENTHOOK = HANDLE
LRESULT = LPLONG
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
EVENT_OBJECT_DESTROY = 0x8001
OBJID_WINDOW = 0
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
HWND_TOP = 0
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
VK_RETURN = 0xD
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

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

_GetWindowRect = _user32.GetWindowRect
_GetWindowRect.argtypes = HWND, POINTER(RECT)
GetForegroundWindow = _user32.GetForegroundWindow
GetForegroundWindow.restype = HWND
WindowFromPoint = _user32.WindowFromPoint
WindowFromPoint.argtypes = (POINT,)
WindowFromPoint.restype = HWND
ShowWindow = _user32.ShowWindow
ShowWindow.argtypes = HWND, c_int
ShowWindow.restype = BOOL
GetWindowLong = _user32.GetWindowLongW
GetWindowLong.argtypes = HWND, c_int
GetWindowLong.restype = LONG

SetWindowLong = _user32.SetWindowLongW
SetWindowLong.argtypes = HWND, c_int, LONG
SetWindowLong.restype = LONG
BringWindowToTop = _user32.BringWindowToTop
BringWindowToTop.argtypes = (HWND,)
GetDC = _user32.GetDC
GetDC.restype = HDC
ReleaseDC = _user32.ReleaseDC
ReleaseDC.argtypes = HWND, HDC
ReleaseDC.restype = c_int


_GetCursorPos = _user32.GetCursorPos
_GetCursorPos.argtypes = (POINTER(POINT),)


GetDeviceCaps = _gdi32.GetDeviceCaps
GetDeviceCaps.argtypes = HDC, c_int
GetDeviceCaps.restype = c_int
_SetWindowPos = _user32.SetWindowPos
_SetWindowPos.argtypes = c_int, c_void_p, c_int, c_int, c_int, c_int, c_uint
_GetWindowText = _user32.GetWindowTextW
_GetWindowText.argtypes = HWND, c_wchar_p, c_int
_GetWindowTextLength = _user32.GetWindowTextLengthW
_MoveWindow = _user32.MoveWindow
_MoveWindow.argtypes = c_int, c_int, c_int, c_int, c_int, c_bool

SetForegroundWindow = _user32.SetForegroundWindow
SetForegroundWindow.argtypes = (HWND,)
_GetClientRect = _user32.GetClientRect
_GetClientRect.argtypes = c_int, POINTER(RECT)

FindWindow = _user32.FindWindowW
FindWindow.argtypes = LPCWSTR, LPCWSTR
FindWindow.restype = HWND
SetFocus = _user32.SetFocus
SetFocus.argtypes = (HWND,)
_EnumWindows = _user32.EnumWindows
_EnumWindows.argtypes = WNDENUMPROC, c_void_p
_ShellExecuteW = _shell32.ShellExecuteW
_ShellExecuteW.argtypes = c_void_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int
_OpenProcess = _kernel32.OpenProcess
_OpenProcess.argtypes = c_uint, c_bool, c_uint
CloseHandle = _kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE,)
CloseHandle.restype = BOOL
_SendMessage = _user32.SendMessageW
_SendMessage.argtypes = c_int, c_uint, c_void_p, c_void_p
_keybd_event = _user32.keybd_event
_keybd_event.argtypes = c_byte, c_byte, c_uint, c_void_p
RegisterWindowMessage = _user32.RegisterWindowMessageW
RegisterWindowMessage.argtypes = (LPCWSTR,)
RegisterWindowMessage.restype = UINT
_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_GetWindowThreadProcessId.argtypes = HWND, c_void_p
GetClipboardOwner = _user32.GetClipboardOwner
GetClipboardOwner.restype = HWND
try:
    _GetModuleFileNameExW = _psapi.GetModuleFileNameExW
except:
    _GetModuleFileNameExW = _kernel32.GetModuleFileNameExW
_GetModuleFileNameExW.argtypes = HANDLE, HMODULE, LPWSTR, DWORD
_GetModuleFileNameExW.restype = DWORD


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
_GetLogicalDriveStringsW.argtypes = DWORD, LPWSTR
_GetLogicalDriveStringsW.restype = DWORD

_GetCurrentDirectoryW = _kernel32.GetCurrentDirectoryW
_GetCurrentDirectoryW.argtypes = c_uint, c_wchar_p

try:
    _QueryFullProcessImageNameW = _kernel32.QueryFullProcessImageNameW
    _QueryFullProcessImageNameW.argtypes = c_void_p, c_uint, c_wchar_p, c_void_p
except:
    _QueryFullProcessImageNameW = 0

_GetLongPathName = _kernel32.GetLongPathNameW
_GetLongPathName.argtypes = (LPCWSTR, LPWSTR, DWORD)
_GetLongPathName.restype = DWORD
MAX_PATH = 260


def GetLongPathName(file):
    succ = _GetLongPathName(file, None, 0)
    if succ == 0:
        return file
    buff = create_unicode_buffer(succ + 1)
    succ = _GetLongPathName(file, buff, succ)
    path = buff.value
    return path


def get_logical_drivers():
    buffsize = 300
    buffer = create_unicode_buffer(buffsize)

    result = _GetLogicalDriveStringsW(buffsize, buffer)

    if not result:
        return []

    if buffsize < result:
        buffer = create_unicode_buffer(result)
        result = _GetLogicalDriveStringsW(result, buffer)

    drivers = buffer[:result].split("\0")
    if drivers and not drivers[-1]:
        drivers.pop()
    return drivers


def check_unc_file(v: str):
    buf = create_unicode_buffer(65535)
    for A in get_logical_drivers():
        A = A[:-1]
        if _QueryDosDeviceW(A, buf, 65535) != 0:
            prefixdos = buf.value
            if v.startswith(prefixdos):
                return A + v[len(prefixdos) :]

        # 我操了，使用管理员权限时，这个玩意会失败
        if _WNetGetUniversalNameW(A, 1, buf, byref(c_uint(65535))) == 0:
            prefixnetwork = cast(
                buf, POINTER(UNIVERSAL_NAME_INFO)
            ).contents.lpUniversalName
            if v.startswith(prefixnetwork):
                return A + v[len(prefixnetwork) :]
    return v


def check_maybe_unc_file(v: str):
    if v.startswith("\\"):
        v = check_unc_file(v)
        if v.startswith("\\"):
            return None
    return v


def _GetProcessFileName(hHandle):
    w = create_unicode_buffer(65535)
    # 我佛了，太混乱了，不同权限获取的东西完全不一样
    size = DWORD(65535)
    if (
        _GetModuleFileNameExW(hHandle, None, w, 65535) == 0
        and (
            _QueryFullProcessImageNameW != 0
            and _QueryFullProcessImageNameW(hHandle, 0, w, pointer(size)) == 0
        )
        and _GetProcessImageFileNameW(hHandle, w, 65535) == 0
    ):
        return

    v: str = w.value

    return check_maybe_unc_file(v)


def GetProcessFileName(hHandle):
    p = _GetProcessFileName(hHandle)
    if p:
        # GetModuleFileNameExW有可能莫名其妙得到短路径，导致部分路径无法匹配
        p = GetLongPathName(p)
    return p


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


def GetWindowThreadProcessId(hwnd):
    pid = c_uint()
    handle = _GetWindowThreadProcessId(hwnd, pointer(pid))
    if handle == 0:
        return 0
    return pid.value


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


def SetWindowPos(hwnd, InsertAfter, X, Y, cx, cy, uFlags):
    return _SetWindowPos(hwnd, InsertAfter, X, Y, cx, cy, uFlags)


def GetWindowText(hwnd):
    length = _GetWindowTextLength(hwnd)
    wchar = create_unicode_buffer(length + 1)
    _GetWindowText(hwnd, wchar, length + 1)
    return wchar.value


def MoveWindow(hwnd, X, Y, w, h, bRepaint):
    return _MoveWindow(hwnd, X, Y, w, h, bRepaint)


def EnumWindows(lpEnumFunc, lParam):
    return _EnumWindows(WNDENUMPROC(lpEnumFunc), 0)


def ShellExecute(hwnd: int, op: str, file: str, params: str, _dir: str, bShow):
    return _ShellExecuteW(hwnd, op, file, params, _dir, bShow)


def OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId):
    return _OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)


def SendMessage(hwnd, message, wp=None, lp=None):
    return _SendMessage(hwnd, message, wp, lp)


def keybd_event(bVk, bScan, dwFlags, _):
    _keybd_event(bVk, bScan, dwFlags, _)


WaitForSingleObject = _kernel32.WaitForSingleObject
WaitForSingleObject.argtypes = HANDLE, DWORD
WaitForSingleObject.restype = DWORD


INFINITE = -1

SetEvent = _kernel32.SetEvent
SetEvent.argtypes = (HANDLE,)
SetEvent.restype = BOOL


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
        ("Owner", POINTER(SIDStruct)),
        ("Group", POINTER(SIDStruct)),
        ("Sacl", POINTER(ACLStruct)),
        ("Dacl", POINTER(ACLStruct)),
    ]


class SECURITY_ATTRIBUTESStruct(Structure):
    _fields_ = [
        ("nLength", DWORD),
        ("lpSecurityDescriptor", POINTER(SECURITY_DESCRIPTORStruct)),
        ("bInheritHandle", BOOL),
    ]


_InitializeSecurityDescriptor = _Advapi32.InitializeSecurityDescriptor
_InitializeSecurityDescriptor.argtypes = [c_void_p, DWORD]
_InitializeSecurityDescriptor.restype = BOOL
_SetSecurityDescriptorDacl = _Advapi32.SetSecurityDescriptorDacl
_SetSecurityDescriptorDacl.argtypes = [c_void_p, BOOL, c_void_p, BOOL]


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


GetLastError = _kernel32.GetLastError
GetLastError.restype = DWORD


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


WaitNamedPipe = _kernel32.WaitNamedPipeW
WaitNamedPipe.argtypes = LPCWSTR, DWORD
WaitNamedPipe.restype = BOOL


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


_IsUserAnAdmin = _shell32.IsUserAnAdmin


def IsUserAnAdmin():
    try:
        return bool(_IsUserAnAdmin())
    except:
        return False


GetKeyState = _user32.GetKeyState
GetKeyState.argtypes = (c_int,)
GetKeyState.restype = SHORT

GetAsyncKeyState = _user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = (c_int,)
GetAsyncKeyState.restype = SHORT


GA_ROOT = 2
_GetAncestor = _user32.GetAncestor
_GetAncestor.argtypes = HWND, UINT
_GetAncestor.restype = HWND


def GetAncestor(hwnd):
    return _GetAncestor(hwnd, GA_ROOT)


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


CopyFile = _kernel32.CopyFileW
CopyFile.argtypes = LPCWSTR, LPCWSTR, BOOL
CopyFile.restype = BOOL


SetProp = _user32.SetPropW
SetProp.argtypes = HWND, LPCWSTR, HANDLE
SetProp.restype = BOOL


_GetEnvironmentVariableW = _kernel32.GetEnvironmentVariableW
_GetEnvironmentVariableW.argtypes = c_wchar_p, c_wchar_p, DWORD
_SetEnvironmentVariableW = _kernel32.SetEnvironmentVariableW
_SetEnvironmentVariableW.argtypes = LPCWSTR, LPCWSTR


def addenvpath(path):
    path = os.path.abspath(path)
    env = create_unicode_buffer(65535)
    _GetEnvironmentVariableW("PATH", env, 65535)
    _SetEnvironmentVariableW("PATH", env.value + ";" + path)


LoadLibraryW = _kernel32.LoadLibraryW
LoadLibraryW.argtypes = (LPCWSTR,)


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

WNDPROCTYPE = WINFUNCTYPE(INT, HWND, INT, WPARAM, LPARAM)

GWLP_WNDPROC = -4
if sizeof(c_void_p) == 8:
    SetWindowLongPtr = _user32.SetWindowLongPtrW
    GetWindowLongPtr = _user32.GetWindowLongPtrW
else:
    SetWindowLongPtr = _user32.SetWindowLongW
    GetWindowLongPtr = _user32.GetWindowLongW
SetWindowLongPtr.argtypes = HWND, INT, c_void_p
SetWindowLongPtr.restype = c_void_p
GetWindowLongPtr.argtypes = HWND, INT
GetWindowLongPtr.restype = c_void_p
WM_LBUTTONDOWN = 0x0201
WM_COMMAND = 0x0111
WM_LBUTTONUP = 0x0202
WM_MOUSEMOVE = 0x0200

FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x100
FORMAT_MESSAGE_FROM_HMODULE = 0x800
FORMAT_MESSAGE_FROM_SYSTEM = 0x1000
FORMAT_MESSAGE_IGNORE_INSERTS = 0x200
FormatMessageW = _kernel32.FormatMessageW
FormatMessageW.argtypes = DWORD, LPCVOID, DWORD, DWORD, LPWSTR, DWORD, LPCVOID
FormatMessageW.restype = c_size_t
LocalFree = _kernel32.LocalFree
LocalFree.argtypes = (c_void_p,)


def FormatMessage(code, module=None):
    mess = LPWSTR()
    flag = (
        FORMAT_MESSAGE_ALLOCATE_BUFFER
        | FORMAT_MESSAGE_FROM_SYSTEM
        | FORMAT_MESSAGE_IGNORE_INSERTS
    )
    if module:
        flag |= FORMAT_MESSAGE_FROM_HMODULE

    length = FormatMessageW(
        flag, module, code, 0x400, cast(pointer(mess), LPWSTR), 0, None
    )
    if mess.value is None:
        return ""
    res = mess.value[:length]
    if length:
        LocalFree(mess)
    return res.strip()


MONITOR_DEFAULTTONEAREST = 0x00000002
_MonitorFromWindow = _user32.MonitorFromWindow
_MonitorFromWindow.argtypes = HWND, DWORD
_MonitorFromWindow.restype = HMONITOR


def MonitorFromWindow(hwnd, dwFlags=MONITOR_DEFAULTTONEAREST):
    return _MonitorFromWindow(hwnd, dwFlags)


WINEVENTPROC = WINFUNCTYPE(
    None,
    HANDLE,
    DWORD,
    HWND,
    LONG,
    LONG,
    DWORD,
    DWORD,
)


PM_REMOVE = 0x0001

PeekMessageA = _user32.PeekMessageA
PeekMessageA.argtypes = LPMSG, HWND, UINT, UINT, UINT
PeekMessageA.restype = BOOL
RegisterHotKey = _user32.RegisterHotKey
RegisterHotKey.argtypes = HWND, c_int, UINT, UINT
RegisterHotKey.restype = BOOL
UnregisterHotKey = _user32.UnregisterHotKey
UnregisterHotKey.restype = BOOL
UnregisterHotKey.argtypes = HWND, c_int

UnhookWindowsHookEx = _user32.UnhookWindowsHookEx
UnhookWindowsHookEx.argtypes = (HHOOK,)
UnhookWindowsHookEx.restype = BOOL
TranslateMessage = _user32.TranslateMessage
TranslateMessage.argtypes = (LPMSG,)
TranslateMessage.restype = BOOL
DispatchMessageW = _user32.DispatchMessageW
DispatchMessageW.argtypes = (LPMSG,)
DispatchMessageW.restype = LRESULT
GetMessageW = _user32.GetMessageW
GetMessageW.argtypes = LPMSG, HWND, UINT, UINT
GetMessageW.restype = BOOL
SetWinEventHook = _user32.SetWinEventHook
SetWinEventHook.restype = HWINEVENTHOOK
SetWinEventHook.argtypes = DWORD, DWORD, HMODULE, WINEVENTPROC, DWORD, DWORD, DWORD

PathFileExists = windll.Shlwapi.PathFileExistsW
PathFileExists.argtypes = (LPCWSTR,)
PathFileExists.restype = BOOL

_SHGetFolderPathW = _shell32.SHGetFolderPathW
_SHGetFolderPathW.argtypes = (
    HWND,
    c_int,
    HANDLE,
    DWORD,
    LPWSTR,
)
_SHGetFolderPathW.restype = HRESULT
CSIDL_MYPICTURES = 0x27
SHGFP_TYPE_CURRENT = 0
S_OK = 0


def SHGetFolderPathW(csidl):
    buff = create_unicode_buffer(MAX_PATH + 100)
    if _SHGetFolderPathW(None, csidl, None, SHGFP_TYPE_CURRENT, buff) != S_OK:
        return None
    return buff.value
