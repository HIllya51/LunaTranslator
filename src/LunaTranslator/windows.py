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
    cast,
)
import os
from ctypes.wintypes import (
    MAX_PATH,
    RECT,
    POINT,
    HWND,
    BOOL,
    LCID,
    LCTYPE,
    DWORD,
    LONG,
    HMONITOR,
    LPCVOID,
    LPWSTR,
    LPCWSTR,
    HANDLE,
    UINT,
    HMODULE,
    LPLONG,
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

VK_LBUTTON = 1
VK_RBUTTON = 2
VK_RETURN = 0xD
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101


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

CloseHandle = _kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE,)
CloseHandle.restype = BOOL


class AutoHandle(HANDLE):

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
RegisterWindowMessage = _user32.RegisterWindowMessageW
RegisterWindowMessage.argtypes = (LPCWSTR,)
RegisterWindowMessage.restype = UINT
_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_GetWindowThreadProcessId.argtypes = HWND, c_void_p
GetClipboardOwner = _user32.GetClipboardOwner
GetClipboardOwner.restype = HWND
try:
    _GetModuleFileNameExW = _kernel32.K32GetModuleFileNameExW
except:
    _GetModuleFileNameExW = _psapi.GetModuleFileNameExW
_GetModuleFileNameExW.argtypes = HANDLE, HMODULE, LPWSTR, DWORD
_GetModuleFileNameExW.restype = DWORD


_QueryDosDeviceW = _kernel32.QueryDosDeviceW
_QueryDosDeviceW.argtypes = c_wchar_p, c_wchar_p, c_uint

try:
    _GetProcessImageFileNameW = _kernel32.K32GetProcessImageFileNameW
except:
    _GetProcessImageFileNameW = _psapi.GetProcessImageFileNameW
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
        buffer = create_unicode_buffer(result + 1)
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
    return None


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


try:
    GetFinalPathNameByHandleW = _kernel32.GetFinalPathNameByHandleW
    GetFinalPathNameByHandleW.argtypes = (HANDLE, LPWSTR, DWORD, DWORD)
    GetFinalPathNameByHandleW.restype = DWORD
except:
    GetFinalPathNameByHandleW = None


def parseuncex(v: str, t) -> str:
    hFile = CreateFile(
        v,
        GENERIC_READ,
        FILE_SHARE_READ,
        None,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        None,
    )
    if not GetFinalPathNameByHandleW:
        return
    if not hFile:
        return
    sz = GetFinalPathNameByHandleW(hFile, None, 0, t)
    if not sz:
        return
    buff = create_unicode_buffer(sz + 1)
    GetFinalPathNameByHandleW(hFile, buff, sz, t)
    return buff.value


def check_maybe_unc_file(v: str):
    if not v.startswith("\\"):
        return v
    res = check_unc_file(v)
    if res:
        return res
    # 有时候GetModuleFileNameExW返回的就是VOLUME_NAME_GUID（例如sshfs），无法CreateFile，但是可以QueryDosDevice查询到
    # mac上parallel返回的NT路径无法用QueryDosDevice查询到（应该是需要再额外查注册表处理一下才行的，所以只好用GetFinalPathNameByHandleW去查DOS路径
    dos = parseuncex(v, VOLUME_NAME_DOS)
    # 按照文档所说，VOLUME_NAME_NT之后QueryDosDevice是可以转成X:\xxxx的，然而实测经常查不到根本没卵用
    # 获取的结果是\\?\的UNC路径。虽然没办法转成X:\xxxx，但实测可以管用。
    if dos:
        if dos.startswith("\\\\?\\"):
            # 虽然这个东西很真实，但实际上大部分程序根本不适配，他只在长路径下实际有意义，否则反而使一些东西运行不正常
            dos = dos[4:]
        return dos
    return v


def _GetProcessFileName(hHandle):
    w = create_unicode_buffer(65535)
    # 我佛了，太混乱了，不同权限获取的东西完全不一样
    size = DWORD(65535)
    # 这三者越前面的越直接得到好路径，后面的经常得到辣鸡路径
    if (
        (_GetModuleFileNameExW(hHandle, None, w, 65535) == 0)
        and (
            _QueryFullProcessImageNameW == 0
            or _QueryFullProcessImageNameW(hHandle, 0, w, pointer(size)) == 0
        )
        and (_GetProcessImageFileNameW(hHandle, w, 65535) == 0)
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


def OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId):
    return _OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)


def SendMessage(hwnd, message, wp=None, lp=None):
    return _SendMessage(hwnd, message, wp, lp)


def keybd_event(bVk, bScan, dwFlags, _):
    _keybd_event(bVk, bScan, dwFlags, _)


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


def MapViewOfFile(
    hfmap,
    acc=FILE_MAP_READ | FILE_MAP_WRITE,
    high=0,
    low=0,
    size=1024 * 1024 * 16,
):
    return _MapViewOfFile(hfmap, acc, high, low, size)


IsZoomed = _user32.IsZoomed
IsZoomed.argtypes = (HWND,)
IsZoomed.restype = BOOL


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


PathFileExists = windll.Shlwapi.PathFileExistsW
PathFileExists.argtypes = (LPCWSTR,)
PathFileExists.restype = BOOL


class HRESULT_ERROR(Exception):
    pass


def CHECK_FAILURE(hr, module=None):
    if hr < 0:
        raise HRESULT_ERROR(FormatMessage(hr, module))


GetClassNameW = _user32.GetClassNameW
GetClassNameW.argtypes = HWND, LPWSTR, c_int
GetClassNameW.restype = c_int


def GetClassName(hwnd):
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


def GetLocale():
    lcid = GetUserDefaultLCID()
    buff = create_unicode_buffer(10)
    buff2 = create_unicode_buffer(10)
    GetLocaleInfoW(lcid, LOCALE_SISO639LANGNAME, buff, 10)
    GetLocaleInfoW(lcid, LOCALE_SISO3166CTRYNAME, buff2, 10)
    return buff.value, buff2.value
