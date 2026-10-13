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
    Structure,
    sizeof,
    c_char,
    byref,
)
from ctypes.wintypes import (
    LPVOID,
    RECT,
    POINT,
    HWND,
    BOOL,
    DWORD,
    LONG,
    HMONITOR,
    LPCVOID,
    INT,
    LPWSTR,
    LPCWSTR,
    HANDLE,
    UINT,
    HMODULE,
    LPLONG,
    LCID,
    LCTYPE,
    HDC,
    SHORT,
)

HRESULT = LONG
HWINEVENTHOOK = HANDLE
LRESULT = LPLONG
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
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
PIPE_READMODE_MESSAGE = 2
PIPE_TYPE_MESSAGE = 4
OPEN_EXISTING = 3
PIPE_ACCESS_DUPLEX = 3
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11
SW_MAX = 11
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
HWND_TOP = 0
SW_HIDE = 0
SWP_NOACTIVATE = 16
SWP_NOMOVE = 2
SWP_NOZORDER = 0x0004
SW_MAXIMIZE = 3
SW_SHOWNORMAL = 1
WS_EX_TOOLWINDOW = 128
SWP_NOSIZE = 1
SW_SHOW = 5
WS_THICKFRAME = 0x00040000

FILE_SHARE_READ = 0x00000001
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_HANDLE_VALUE = -1
VOLUME_NAME_DOS = 0x0
VOLUME_NAME_NT = 0x2

STANDARD_RIGHTS_REQUIRED = 0x000F0000
SYNCHRONIZE = 0x00100000
PROCESS_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF
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
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
SW_SHOWMAXIMIZED = 3
WS_EX_NOACTIVATE = 0x08000000
VK_LBUTTON = 1
VK_RBUTTON = 2
VK_MBUTTON = 4
VK_RETURN = 0xD
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_Q = 0x51
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

RGN_AND = 1
RGN_OR = 2
RGN_XOR = 3
RGN_DIFF = 4
RGN_COPY = 5


class WindowFocus:
    @staticmethod
    def giveup(hwnd):
        SetWindowLong(
            int(hwnd),
            GWL_EXSTYLE,
            GetWindowLong(int(hwnd), GWL_EXSTYLE) | WS_EX_NOACTIVATE,
        )

    @staticmethod
    def retrieve(hwnd):
        SetWindowLong(
            int(hwnd),
            GWL_EXSTYLE,
            GetWindowLong(int(hwnd), GWL_EXSTYLE) & ~WS_EX_NOACTIVATE,
        )


class MouseTrans:
    @staticmethod
    def set(hwnd):
        SetWindowLong(
            int(hwnd),
            GWL_EXSTYLE,
            GetWindowLong(int(hwnd), GWL_EXSTYLE) | WS_EX_TRANSPARENT,
        )

    @staticmethod
    def unset(hwnd):
        SetWindowLong(
            int(hwnd),
            GWL_EXSTYLE,
            GetWindowLong(int(hwnd), GWL_EXSTYLE) & ~WS_EX_TRANSPARENT,
        )


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


_user32 = windll.User32
_gdi32 = windll.Gdi32
_shell32 = windll.Shell32
_kernel32 = windll.Kernel32
_Advapi32 = windll.Advapi32
_Shlwapi = windll.Shlwapi
_Ole32 = windll.Ole32

CloseHandle = _kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE,)
CloseHandle.restype = BOOL


class AutoHandle(HANDLE):
    def detach(self):
        self.value = None

    def __del__(self):
        if self:
            CloseHandle(self)

    def __bool__(self):
        return (self.value != INVALID_HANDLE_VALUE) and (self.value != None)


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


SetCursorPos = _user32.SetCursorPos
SetCursorPos.argtypes = (c_int, c_int)


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

FindWindow = _user32.FindWindowW
FindWindow.argtypes = LPCWSTR, LPCWSTR
FindWindow.restype = HWND
FindWindowEx = _user32.FindWindowExW
FindWindowEx.argtypes = HWND, HWND, LPCWSTR, LPCWSTR
FindWindowEx.restype = HWND
SetFocus = _user32.SetFocus
SetFocus.argtypes = (HWND,)
GetFocus = _user32.GetFocus
GetFocus.restype = HWND
_ShellExecuteW = _shell32.ShellExecuteW
_ShellExecuteW.argtypes = c_void_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int
_OpenProcess = _kernel32.OpenProcess
_OpenProcess.argtypes = c_uint, c_bool, c_uint
_OpenProcess.restype = AutoHandle
_SendMessage = _user32.SendMessageW
_SendMessage.argtypes = HWND, UINT, c_void_p, c_void_p
_keybd_event = _user32.keybd_event
_keybd_event.argtypes = c_byte, c_byte, c_uint, c_void_p
_mouse_event = _user32.mouse_event
_mouse_event.argtypes = DWORD, DWORD, DWORD, DWORD, c_void_p
RegisterWindowMessage = _user32.RegisterWindowMessageW
RegisterWindowMessage.argtypes = (LPCWSTR,)
RegisterWindowMessage.restype = UINT
_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_GetWindowThreadProcessId.argtypes = HWND, c_void_p
GetClipboardOwner = _user32.GetClipboardOwner
GetClipboardOwner.restype = HWND
_CreateFileW = _kernel32.CreateFileW
_CreateFileW.argtypes = (LPCWSTR, DWORD, DWORD, LPCVOID, DWORD, DWORD, HANDLE)
_CreateFileW.restype = AutoHandle


def CreateFile(
    fileName,
    desiredAccess=GENERIC_READ | GENERIC_WRITE,
    shareMode=0,
    attributes=None,
    CreationDisposition=OPEN_EXISTING,
    flagsAndAttributes=FILE_ATTRIBUTE_NORMAL,
    hTemplateFile=None,
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


def ShellExecute(hwnd: int, op: str, file: str, params: str, _dir: str, bShow):
    return _ShellExecuteW(hwnd, op, file, params, _dir, bShow)


ERROR_FILE_NOT_FOUND = 2
ERROR_PATH_NOT_FOUND = 3
SE_ERR_ACCESSDENIED = ERROR_ACCESS_DENIED = 5


def OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId):
    return _OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)


def SendMessage(hwnd, message, wp=None, lp=None):
    return _SendMessage(hwnd, message, wp, lp)


def keybd_event(bVk, bScan, dwFlags, _):
    _keybd_event(bVk, bScan, dwFlags, _)


def mouse_event(dwFlags, dx, dy, dwData, dwExtraInfo=None):
    _mouse_event(dwFlags, dx, dy, dwData, dwExtraInfo)


MOUSEEVENTF_LEFTDOWN = 2
MOUSEEVENTF_LEFTUP = 4
MOUSEEVENTF_MIDDLEDOWN = 0x20
MOUSEEVENTF_MIDDLEUP = 0x40
MOUSEEVENTF_RIGHTDOWN = 8
MOUSEEVENTF_RIGHTUP = 0x10

_WaitForSingleObject = _kernel32.WaitForSingleObject
_WaitForSingleObject.argtypes = HANDLE, DWORD
_WaitForSingleObject.restype = DWORD

INFINITE = -1


def WaitForSingleObject(obj, _=INFINITE):
    return _WaitForSingleObject(obj, _)


SetEvent = _kernel32.SetEvent
SetEvent.argtypes = (HANDLE,)
SetEvent.restype = BOOL

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


_WaitNamedPipe = _kernel32.WaitNamedPipeW
_WaitNamedPipe.argtypes = LPCWSTR, DWORD
_WaitNamedPipe.restype = BOOL


def WaitNamedPipe(pipename, _=NMPWAIT_WAIT_FOREVER):
    return _WaitNamedPipe(pipename, _)


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


GetModuleHandle = _kernel32.GetModuleHandleW
GetModuleHandle.argtypes = (LPCWSTR,)
GetModuleHandle.restype = HMODULE


LoadLibrary = _kernel32.LoadLibraryW
LoadLibrary.argtypes = (LPCWSTR,)
LoadLibrary.restype = HMODULE

SECTION_MAP_WRITE = 0x0002
SECTION_MAP_READ = 0x0004
FILE_MAP_WRITE = SECTION_MAP_WRITE
FILE_MAP_READ = SECTION_MAP_READ
_OpenFileMapping = _kernel32.OpenFileMappingW
_OpenFileMapping.argtypes = DWORD, BOOL, LPCWSTR
_OpenFileMapping.restype = AutoHandle


def OpenFileMapping(name, acc=FILE_MAP_READ | FILE_MAP_WRITE, inher=False):
    return _OpenFileMapping(acc, inher, name)


_MapViewOfFile = _kernel32.MapViewOfFile
_MapViewOfFile.argtypes = HANDLE, DWORD, DWORD, DWORD, c_size_t
_MapViewOfFile.restype = POINTER(c_char)


def MapViewOfFile(hfmap, size, acc=FILE_MAP_READ | FILE_MAP_WRITE, high=0, low=0):
    return _MapViewOfFile(hfmap, acc, high, low, size)


IsZoomed = _user32.IsZoomed
IsZoomed.argtypes = (HWND,)
IsZoomed.restype = BOOL


MONITOR_DEFAULTTONEAREST = 0x00000002
_MonitorFromWindow = _user32.MonitorFromWindow
_MonitorFromWindow.argtypes = HWND, DWORD
_MonitorFromWindow.restype = HMONITOR


def MonitorFromWindow(hwnd, dwFlags=MONITOR_DEFAULTTONEAREST):
    return _MonitorFromWindow(hwnd, dwFlags)


PathFileExists = windll.Shlwapi.PathFileExistsW
PathFileExists.argtypes = (LPCWSTR,)
PathFileExists.restype = BOOL


def FAILED(hr):
    hr = HRESULT(hr).value
    return hr < 0


def SUCCEEDDED(hr):
    hr = HRESULT(hr).value
    return hr >= 0


GetClassNameW = _user32.GetClassNameW
GetClassNameW.argtypes = HWND, LPWSTR, c_int
GetClassNameW.restype = c_int


def GetClassName(hwnd: int) -> "str|None":
    buff = create_unicode_buffer(256)
    ret = GetClassNameW(hwnd, buff, 256)
    if not ret:
        return
    return buff.value


GetUserDefaultLCID = _kernel32.GetUserDefaultLCID
GetUserDefaultLCID.restype = LCID
GetLocaleInfoW = _kernel32.GetLocaleInfoW
GetLocaleInfoW.argtypes = LCID, LCTYPE, LPCWSTR, c_int
LOCALE_SISO639LANGNAME = 0x59
LOCALE_SISO3166CTRYNAME = 0x5A


def GetLocale() -> "tuple[str, str]":
    lcid = GetUserDefaultLCID()
    buff = create_unicode_buffer(10)
    buff2 = create_unicode_buffer(10)
    GetLocaleInfoW(lcid, LOCALE_SISO639LANGNAME, buff, 10)
    GetLocaleInfoW(lcid, LOCALE_SISO3166CTRYNAME, buff2, 10)
    return buff.value, buff2.value


CreateEventW = _kernel32.CreateEventW
CreateEventW.argtypes = LPCVOID, BOOL, BOOL, LPCWSTR
CreateEventW.restype = AutoHandle

CreateMutexW = _kernel32.CreateMutexW
CreateMutexW.argtypes = LPCVOID, BOOL, LPCWSTR
CreateMutexW.restype = AutoHandle


StrCmpLogicalW = _Shlwapi.StrCmpLogicalW
StrCmpLogicalW.argtypes = (LPCWSTR, LPCWSTR)
StrCmpLogicalW.restype = INT

CoInitialize = _Ole32.CoInitialize
CoInitialize.argtypes = (LPVOID,)
CoInitialize.restype = HRESULT


CoUninitialize = _Ole32.CoUninitialize


class CO_INIT:
    def __init__(self):
        self.hr = CoInitialize(None)

    def __del__(self):
        if SUCCEEDDED(self.hr):
            CoUninitialize()


WM_APP = 0x8000
WM_DESTROY = 0x2

DestroyWindow = _user32.DestroyWindow
DestroyWindow.argtypes = (HWND,)
