# coding: utf8
# skwinapi.py
# 10/5/2012 jichi
# Windows only

from ctypes import *            # c_int, c_char_p, etc
from ctypes.wintypes import *   # DWORD, CHAR, etc
import win32con

kernel32 = windll.kernel32
shell32 = windll.shell32
user32 = windll.user32
#ole32 = windll.kernel32
#gdi32 = windll.gdi32
try: dwmapi = windll.dwmapi
except WindowsError: dwmapi = None

UCHAR = c_ubyte
STRING = c_char_p
INT8 = c_byte
PINT8 = POINTER(c_byte)
PINT16 = POINTER(c_short)
INT16 = c_short
INT32 = c_int
PINT32 = POINTER(c_int)
PINT64 = POINTER(c_longlong)
INT64 = c_longlong
UINT8 = c_ubyte
PUINT8 = POINTER(c_ubyte)
PUINT16 = POINTER(c_ushort)
UINT16 = c_ushort
UINT32 = c_uint
PUINT32 = POINTER(c_uint)
PUINT64 = POINTER(c_ulonglong)
UINT64 = c_ulonglong
PLONG32 = POINTER(c_int)
LONG32 = c_int
PULONG32 = POINTER(c_uint)
ULONG32 = c_uint
PDWORD32 = POINTER(c_uint)
DWORD32 = c_uint
PINT_PTR = POINTER(c_int)
INT_PTR = c_int
PUINT_PTR = POINTER(c_uint)
UINT_PTR = c_uint
LONG_PTR = c_long
PLONG_PTR = POINTER(c_long)
PULONG_PTR = POINTER(c_ulong)
ULONG_PTR = c_ulong
PUHALF_PTR = POINTER(c_ushort)
UHALF_PTR = c_ushort
PHALF_PTR = POINTER(c_short)
HALF_PTR = c_short
SHANDLE_PTR = c_long
HANDLE_PTR = c_ulong
SIZE_T = ULONG_PTR
SSIZE_T = LONG_PTR
DWORD_PTR = ULONG_PTR
PDWORD_PTR = POINTER(ULONG_PTR)
LONG64 = c_longlong
PLONG64 = POINTER(c_longlong)
PULONG64 = POINTER(c_ulonglong)
ULONG64 = c_ulonglong
DWORD64 = c_ulonglong
PDWORD64 = POINTER(c_ulonglong)

HRESULT = ULONG

PULONG = POINTER(ULONG)
USHORT = c_ushort
PUSHORT = POINTER(USHORT)
PUCHAR = POINTER(UCHAR)
PSZ = STRING
FLOAT = c_float
PFLOAT = POINTER(FLOAT)
PBOOL = POINTER(BOOL)
LPBOOL = POINTER(BOOL)
PBYTE = POINTER(BYTE)
LPBYTE = POINTER(BYTE)
PINT = POINTER(c_int)
LPINT = POINTER(c_int)
PWORD = POINTER(WORD)
LPWORD = POINTER(WORD)
LPLONG = POINTER(c_long)
PDWORD = POINTER(DWORD)
LPDWORD = POINTER(DWORD)
PCVOID = c_void_p
LPCVOID = c_void_p
LPSIZE_T = POINTER(ULONG_PTR)
PSIZE_T = LPSIZE_T
LPSSIZE_T = POINTER(LONG_PTR)
PSSIZE_T = LPSSIZE_T
INT = c_int
UINT = c_uint
PUINT = POINTER(c_uint)
LRESULT = LONG_PTR

LPVOID = c_void_p
HCURSOR = HICON

## Gdi32 ##

# http://msdn.microsoft.com/en-us/library/windows/desktop/dd183326%28v=vs.85%29.aspx
#AddFontResourceW = gdi32.AddFontResourceW
#AddFontResourceW.restype = int
#AddFontResourceW.argtype = LPCWSTR
#
#AddFontResourceA = gdi32.AddFontResourceA
#AddFontResourceA.restype = int
#AddFontResourceA.argtype = LPCSTR

## Ole32 ##

COINIT_APARTMENTTHREADED = 0x2
COINIT_MULTITHREADED     = 0x0
COINIT_DISABLE_OLE1DDE   = 0x4
COINIT_SPEED_OVER_MEMORY = 0x8

#CoUninitialize = ole32.CoUninitialize
#CoUninitialize.restype = None
#CoUninitialize.argtypes = None

#CoInitialize = ole32.CoInitialize
#CoInitialize.restype = HRESULT
#CoInitialize.argtype = LPVOID

#CoInitializeEx = ole32.CoInitializeEx
#CoInitializeEx.restype = HRESULT
#CoInitializeEx.argtypes = LPVOID, DWORD

## DwmApi ##

DWM_BB_ENABLE                = 0x00000001 # fEnable has been specified
DWM_BB_BLURREGION            = 0x00000002 # hRgnBlur has been specified
DWM_BB_TRANSITIONONMAXIMIZED = 0x00000004 # fTransitionOnMaximized has been specified

WM_DWMCOMPOSITIONCHANGED     = 0x031E     # Composition changed window message

class _MARGINS(Structure):
  _fields_ = [
    ('cxLeftWidth', INT),
    ('cxRightWidth', INT),
    ('cyTopHeight', INT),
    ('cyBottomHeight', INT)
  ]
MARGINS = _MARGINS
LPMARGINS = POINTER(_MARGINS)
PMARGINS = LPMARGINS

class _DWM_BLURBEHIND(Structure):
  _fields_ = [
    ('dwFlags', DWORD),
    ('fEnable', BOOL),
    ('hRgnBlur', HRGN),
    ('fTransitionOnMaximized', BOOL),
  ]
DWM_BLURBEHIND = _DWM_BLURBEHIND
LPDWM_BLURBEHIND = POINTER(_DWM_BLURBEHIND)
PDWM_BLURBEHIND = LPDWM_BLURBEHIND

if dwmapi:
  DwmIsCompositionEnabled = dwmapi.DwmIsCompositionEnabled
  DwmIsCompositionEnabled.restype = HRESULT
  DwmIsCompositionEnabled.argtype = LPBOOL

  DwmExtendFrameIntoClientArea = dwmapi.DwmExtendFrameIntoClientArea
  DwmExtendFrameIntoClientArea.restype = HRESULT
  #DwmExtendFrameIntoClientArea.argtypes = HWND, LPMARGINS
  DwmExtendFrameIntoClientArea.argtypes = ULONG, LPMARGINS

  DwmEnableBlurBehindWindow = dwmapi.DwmEnableBlurBehindWindow
  DwmEnableBlurBehindWindow.restype = HRESULT
  #DwmEnableBlurBehindWindow.argtypes = HWND, LPDWM_BLURBEHIND
  DwmEnableBlurBehindWindow.argtypes = ULONG, LPDWM_BLURBEHIND

  DwmGetColorizationColor = dwmapi.DwmGetColorizationColor
  DwmGetColorizationColor.restype = HRESULT
  DwmGetColorizationColor.argtypes = LPDWORD, LPBOOL

else:
  def DwmIsCompositionEnabled(pfEnabled): return 0
  def DwmExtendFrameIntoClientArea(hWnd, pMarInset): return 0
  def DwmEnableBlurBehindWindow(hWnd, pBlurBehind): return 0
  def DwmGetColorizationColor(pcrColorization, pfOpaqueBlend): return 0

## User32 ##

# Windows Vista+
# For Vista+: http://social.msdn.microsoft.com/forums/en-US/windowssdk/thread/2168f10c-9179-4d8c-99b0-60ba47a53d21/
MSGFLT_ADD = 1
MSGFLT_REMOVE = 2

WM_COPYGLOBALDATA = 0x0049 # http://blog.sina.com.cn/s/blog_6294abe70101bko6.html

try:
  ChangeWindowMessageFilter = user32.ChangeWindowMessageFilter
  ChangeWindowMessageFilter.restype = BOOL
  ChangeWindowMessageFilter.argtypes = UINT, DWORD
except AttributeError:
  #def ChangeWindowMessageFilter(message, dwFlags): return False
  ChangeWindowMessageFilter = None


# See: http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7
try:
  SetCurrentProcessExplicitAppUserModelID = shell32.SetCurrentProcessExplicitAppUserModelID
  SetCurrentProcessExplicitAppUserModelID.restype = HRESULT
  SetCurrentProcessExplicitAppUserModelID.argtype = LPCWSTR
except AttributeError:
  def SetCurrentProcessExplicitAppUserModelID(appId): return 0

try:
  GetCurrentProcessExplicitAppUserModelID = shell32.GetCurrentProcessExplicitAppUserModelID
  GetCurrentProcessExplicitAppUserModelID.restype = HRESULT
  GetCurrentProcessExplicitAppUserModelID.argtype = POINTER(LPWSTR)
except AttributeError:
  def GetCurrentProcessExplicitAppUserModelID(appId): return 0

# Windows 7+
MSGFLT_ALLOW = 1
MSGFLT_DISALLOW = 2
MSGFLT_RESET = 0
try:
  ChangeWindowMessageFilterEx = user32.ChangeWindowMessageFilterEx
  ChangeWindowMessageFilterEx.restype = BOOL
  #ChangeWindowMessageFilterEx.argtypes = HWND, UINT, DWORD, PCHANGEFILTERSTRUCT
  ChangeWindowMessageFilterEx.argtypes = ULONG, UINT, DWORD, ULONG
except AttributeError:
  #def ChangeWindowMessageFilterEx(message, dwFlags): return False
  ChangeWindowMessageFilterEx = None

SendMessageW = user32.SendMessageW
SendMessageW.restype = int
#SendMessageW.argtypes = HWND, UINT, WPARAM, LPARAM
SendMessageW.argtypes = ULONG, UINT, WPARAM, LPARAM

PostMessageW = user32.PostMessageW
PostMessageW.restype = int
#PostMessageW.argtypes = HWND, UINT, WPARAM, LPARAM
PostMessageW.argtypes = ULONG, UINT, WPARAM, LPARAM

class _HARDWAREINPUT(Structure):
  _fields_ = [
    ('uMsg', DWORD),
    ('wParamL', WORD),
    ('wParamH', WORD),
  ]
HARDWAREINPUT = _HARDWAREINPUT
LPHARDWAREINPUT = POINTER(_HARDWAREINPUT)
PHARDWAREINPUT = LPHARDWAREINPUT

class _KEYBDINPUT(Structure):
  _fields_ = [
    ('wVk', WORD),
    ('wScan', WORD),
    ('dwFlags', DWORD),
    ('time', DWORD),
    ('dwExtraInfo', ULONG_PTR),
  ]
KEYBDINPUT = _KEYBDINPUT
LPKEYBDINPUT = POINTER(_KEYBDINPUT)
PKEYBDINPUT = LPKEYBDINPUT

class _MOUSEINPUT(Structure):
  _fields_ = [
    ('dx', LONG),
    ('dy', LONG),
    ('mouseData', DWORD),
    ('dwFlags', DWORD),
    ('time', DWORD),
    ('dwExtraInfo', ULONG_PTR),
  ]
MOUSEINPUT = _MOUSEINPUT
LPMOUSEINPUT = POINTER(_MOUSEINPUT)
PMOUSEINPUT = LPMOUSEINPUT

class _INPUT_UNION(Union):
  _fields_ = [
    ('mi', MOUSEINPUT),
    ('ki', KEYBDINPUT),
    ('hi', HARDWAREINPUT),
  ]

class _INPUT(Structure):
  _anonymous_ = '_0',
  _fields_ = [
    ('type', DWORD),
    ('_0', _INPUT_UNION),
  ]
INPUT = _INPUT
LPINPUT = POINTER(_INPUT)
PINPUT = LPINPUT

SendInput = user32.SendInput
SendInput.restype = UINT
SendInput.argtypes = UINT, LPINPUT, INT

# See: http://coffeeghost.net/src/pyperclip.py

OpenClipboard = user32.OpenClipboard
OpenClipboard.restype = BOOL
#OpenClipboard.argtype = HWND
OpenClipboard.argtype = ULONG

EmptyClipboard = user32.EmptyClipboard
EmptyClipboard.restype = BOOL
EmptyClipboard.argtypes = []

CloseClipboard = user32.CloseClipboard
CloseClipboard.restype = BOOL
CloseClipboard.argtypes = []

SetClipboardData = user32.SetClipboardData
SetClipboardData.restype = HANDLE
SetClipboardData.argtypes = UINT, HANDLE

# See: http://stackoverflow.com/questions/7921307/temporarily-change-cursor-using-python
CopyIcon = user32.CopyIcon
CopyIcon.restype = HICON
CopyIcon.argtype = HICON

#define CopyCursor(pcur) ((HCURSOR)CopyIcon((HICON)(pcur)))
CopyCursor = user32.CopyIcon
CopyCursor.restype = HCURSOR
CopyCursor.argtype = HCURSOR

SetSystemCursor = user32.SetSystemCursor
SetSystemCursor.restype = BOOL
SetSystemCursor.argtypes = HCURSOR, DWORD

LoadCursorFromFileA = user32.LoadCursorFromFileA
LoadCursorFromFileA.restype = HCURSOR
LoadCursorFromFileA.argtype = LPCSTR

LoadCursorFromFileW = user32.LoadCursorFromFileW
LoadCursorFromFileW.restype = HCURSOR
LoadCursorFromFileW.argtype = LPCWSTR

GetWindowTextA = user32.GetWindowTextA
GetWindowTextA.restype = int
#GetWindowTextA.argtypes = HWND, LPSTR, int
GetWindowTextA.argtypes = ULONG, LPSTR, INT

GetWindowTextW = user32.GetWindowTextW
GetWindowTextW.restype = int
#GetWindowTextW.argtypes = HWND, LPWSTR, int
GetWindowTextW.argtypes = ULONG, LPWSTR, INT

RealGetWindowClass = user32.RealGetWindowClassW
RealGetWindowClass.restype = UINT
#RealGetWindowClass.argtyeps = HWND, LPCWSTR, UINT
RealGetWindowClass.argtyeps = ULONG, LPWSTR, UINT

## Shell32 ##
# See: http://justicecode.wordpress.com/2008/08/13/shfileoperationw-in-python-hint-ctypes/
# See: https://github.com/bradrobertson/sublime-packages/blob/master/Default/send2trash/plat_win.py

FILEOP_FLAGS = WORD
class _SHFILEOPSTRUCTW(Structure):
  _fields_ = [
    ('hwnd', HWND),
    ('wFunc', UINT),
    ('pFrom', LPCWSTR),
    ('pTo', LPCWSTR),
    ('fFlags', FILEOP_FLAGS),
    ('fAnyOperationsAborted', BOOL),
    ('hNameMappings', LPVOID),
    ('lpszProgressTitle', LPCWSTR),
  ]
SHFILEOPSTRUCTW = _SHFILEOPSTRUCTW
LPSHFILEOPSTRUCTW = POINTER(_SHFILEOPSTRUCTW)
PSHFILEOPSTRUCTW = LPSHFILEOPSTRUCTW

SHFileOperationW = shell32.SHFileOperationW
SHFileOperationW.restype = int
SHFileOperationW.argtype = LPSHFILEOPSTRUCTW

SHGetFolderPathW = shell32.SHGetFolderPathW
SHGetFolderPathW.restype = HRESULT
#SHGetFolderPathW.argtypes = HWND, INT, HANDLE, DWORD, LPWSTR
SHGetFolderPathW.argtypes = ULONG, INT, ULONG, DWORD, LPWSTR

class _APPBARDATA(Structure):
  _fields_ = [
    ('cbSize', DWORD),
    #('hWnd', HWND),
    ('hWnd', ULONG),
    ('uCallbackMessage', UINT),
    ('uEdge', UINT),
    ('rc', RECT),
    ('lParam', LPARAM),
  ]
APPBARDATA = _APPBARDATA
LPAPPBARDATA = POINTER(_APPBARDATA)
PAPPBARDATA = LPAPPBARDATA

ABM_SETSTATE = 0xa # missed in win32com.shell.shellcon

SHAppBarMessage = shell32.SHAppBarMessage
#SHAppBarMessage.restype = UINT_PTR
SHAppBarMessage.restype = int
SHAppBarMessage.argtypes = DWORD, LPAPPBARDATA

## Kernel32 ##

class _SECURITY_ATTRIBUTES(Structure):
  _fields_ = [
    ('nLength', DWORD),
    ('lpSecurityDescriptor', LPVOID),
    ('bInheritHandle', BOOL),
  ]
SECURITY_ATTRIBUTES = _SECURITY_ATTRIBUTES
LPSECURITY_ATTRIBUTES = POINTER(_SECURITY_ATTRIBUTES)
PSECURITY_ATTRIBUTES = LPSECURITY_ATTRIBUTES

class _PROCESS_INFORMATION(Structure):
   _fields_ = [
    ('hProcess', HANDLE),
    ('hThread', HANDLE),
    ('dwProcessId', DWORD),
    ('dwThreadId', DWORD),
  ]
PROCESS_INFORMATION = _PROCESS_INFORMATION
LPPROCESS_INFORMATION = POINTER(_PROCESS_INFORMATION)
PPROCESS_INFORMATION = LPPROCESS_INFORMATION

class _STARTUPINFOA(Structure):
  _fields_ = [
    ('cb', DWORD),
    ('lpReserved', LPSTR),
    ('lpDesktop', LPSTR),
    ('lpTitle', LPSTR),
    ('dwX', DWORD),
    ('dwY', DWORD),
    ('dwXSize', DWORD),
    ('dwYSize', DWORD),
    ('dwXCountChars', DWORD),
    ('dwYCountChars', DWORD),
    ('dwFillAttribute', DWORD),
    ('dwFlags', DWORD),
    ('wShowWindow', WORD),
    ('cbReserved2', WORD),
    ('lpReserved2', LPBYTE),
    ('hStdInput', HANDLE),
    ('hStdOutput', HANDLE),
    ('hStdError', HANDLE),
  ]
STARTUPINFOA = _STARTUPINFOA
LPSTARTUPINFOA = POINTER(_STARTUPINFOA)
PSTARTUPINFOA = LPSTARTUPINFOA

class _STARTUPINFOW(Structure):
  _fields_ = [
    ('cb', DWORD),
    ('lpReserved', LPWSTR),
    ('lpDesktop', LPWSTR),
    ('lpTitle', LPWSTR),
    ('dwX', DWORD),
    ('dwY', DWORD),
    ('dwXSize', DWORD),
    ('dwYSize', DWORD),
    ('dwXCountChars', DWORD),
    ('dwYCountChars', DWORD),
    ('dwFillAttribute', DWORD),
    ('dwFlags', DWORD),
    ('wShowWindow', WORD),
    ('cbReserved2', WORD),
    ('lpReserved2', LPBYTE),
    ('hStdInput', HANDLE),
    ('hStdOutput', HANDLE),
    ('hStdError', HANDLE),
  ]
STARTUPINFOW = _STARTUPINFOW
LPSTARTUPINFOW = POINTER(_STARTUPINFOW)
PSTARTUPINFOW = LPSTARTUPINFOW

class _EXCEPTION_POINTERS(Structure):
  pass # ignored
PEXCEPTION_POINTERS = POINTER(_EXCEPTION_POINTERS)
LPEXCEPTION_POINTERS = PEXCEPTION_POINTERS

PTOP_LEVEL_EXCEPTION_FILTER = WINFUNCTYPE(LONG, POINTER(_EXCEPTION_POINTERS))
LPTOP_LEVEL_EXCEPTION_FILTER = PTOP_LEVEL_EXCEPTION_FILTER

GetACP = kernel32.GetACP
GetACP.restype = UINT

GetOEMCP = kernel32.GetOEMCP
GetOEMCP.restype = UINT

SetUnhandledExceptionFilter = kernel32.SetUnhandledExceptionFilter
SetUnhandledExceptionFilter.restype = LPTOP_LEVEL_EXCEPTION_FILTER
SetUnhandledExceptionFilter.argtype = LPTOP_LEVEL_EXCEPTION_FILTER

GetModuleFileNameA = kernel32.GetModuleFileNameA
GetModuleFileNameA.argtypes = HANDLE, LPSTR, DWORD
GetModuleFileNameA.restype = DWORD

GetModuleFileNameW = kernel32.GetModuleFileNameW
GetModuleFileNameW.argtypes = HANDLE, LPWSTR, DWORD
GetModuleFileNameW.restype = DWORD

CreateProcessA = kernel32.CreateProcessW
CreateProcessA.argtypes = LPCSTR, LPSTR, LPSECURITY_ATTRIBUTES, LPSECURITY_ATTRIBUTES, BOOL, DWORD, LPVOID, LPCSTR, LPSTARTUPINFOA, LPPROCESS_INFORMATION
CreateProcessA.restype = BOOL
CreateProcessW = kernel32.CreateProcessW
CreateProcessW.argtypes = LPCWSTR, LPWSTR, LPSECURITY_ATTRIBUTES, LPSECURITY_ATTRIBUTES, BOOL, DWORD, LPVOID, LPCWSTR, LPSTARTUPINFOW, LPPROCESS_INFORMATION
CreateProcessW.restype = BOOL

GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = UINT, SIZE_T
GlobalAlloc.restype = HGLOBAL

GlobalFree = kernel32.GlobalFree
GlobalFree.argtype = HGLOBAL
GlobalFree.restype = HGLOBAL

GlobalLock = kernel32.GlobalLock
GlobalLock.argtype = HGLOBAL
GlobalLock.restype = LPVOID

GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.argtype = HGLOBAL
GlobalUnlock.restype = BOOL

class _SYSTEMTIME(Structure):
  _fields_ = [
    ('wYear', WORD),
    ('wMonth', WORD),
    ('wDayOfWeek', WORD),
    ('wDay', WORD),
    ('wHour', WORD),
    ('wMinute', WORD),
    ('wSecond', WORD),
    ('wMilliseconds', WORD),
  ]
LPSYSTEMTIME = POINTER(_SYSTEMTIME)
PSYSTEMTIME = POINTER(_SYSTEMTIME)
SYSTEMTIME = _SYSTEMTIME

class _TIME_ZONE_INFORMATION(Structure):
  _fields_ = [
    ('Bias', LONG),
    ('StandardName', WCHAR * 32),
    ('StandardDate', SYSTEMTIME),
    ('StandardBias', LONG),
    ('DaylightName', WCHAR * 32),
    ('DaylightDate', SYSTEMTIME),
    ('DaylightBias', LONG),
  ]
LPTIME_ZONE_INFORMATION = POINTER(_TIME_ZONE_INFORMATION)
PTIME_ZONE_INFORMATION = POINTER(_TIME_ZONE_INFORMATION)
TIME_ZONE_INFORMATION = _TIME_ZONE_INFORMATION

SetTimeZoneInformation = kernel32.SetTimeZoneInformation
SetTimeZoneInformation.restype = BOOL
SetTimeZoneInformation.argtype = LPTIME_ZONE_INFORMATION

# LPVOID WINAPI VirtualAllocEx(
#   _In_      HANDLE hProcess,
#   _In_opt_  LPVOID lpAddress,
#   _In_      SIZE_T dwSize,
#   _In_      DWORD flAllocationType,
#   _In_      DWORD flProtect
# );
#
# See: http://pygarlic.googlecode.com/svn-history/r5/trunk/Garlic.py
VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.restype = LPVOID # error if not zero
#VirtualAllocEx.argtypes = HANDLE, LPVOID, SIZE_T, DWORD, DWORD
VirtualAllocEx.argtypes = ULONG, LPVOID, SIZE_T, DWORD, DWORD

# BOOL WINAPI VirtualFreeEx(
#   _In_  HANDLE hProcess,
#   _In_  LPVOID lpAddress,
#   _In_  SIZE_T dwSize,
#   _In_  DWORD dwFreeType
# );
#
# See: pywinauto: http://pywinauto.googlecode.com/hg-history/badf679f1d09af7bf45add1dec55e98a8b92fbbf/pywinauto/win32functions.py
VirtualFreeEx = kernel32.VirtualFreeEx
VirtualFreeEx.restype = BOOL
#VirtualFreeEx.argtypes = HANDLE, LPVOID, SIZE_T, DWORD
VirtualFreeEx.argtypes = ULONG, LPVOID, SIZE_T, DWORD

# http://stackoverflow.com/questions/1872480/use-python-to-extract-listview-items-from-another-application
#BOOL WINAPI WriteProcessMemory(
#  _In_   HANDLE hProcess,
#  _In_   LPVOID lpBaseAddress,
#  _In_   LPCVOID lpBuffer,
#  _In_   SIZE_T nSize,
#  _Out_  SIZE_T *lpNumberOfBytesWritten
#);
WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.restype = BOOL
#WriteProcessMemory.argtypes = HANDLE, LPVOID, LPCVOID, SIZE_T, LPSIZE_T
WriteProcessMemory.argtypes = ULONG, LPVOID, LPCVOID, SIZE_T, LPSIZE_T

# DWORD WINAPI WaitForSingleObject(
#   _In_  HANDLE hHandle,
#   _In_  DWORD dwMilliseconds
# );
WaitForSingleObject = kernel32.WaitForSingleObject
WaitForSingleObject.restype = DWORD
#WaitForSingleObject.argtypes = HANDLE, DWORD
WaitForSingleObject.argtypes = ULONG, DWORD

PTHREAD_START_ROUTINE = WINFUNCTYPE(DWORD, c_void_p)
LPTHREAD_START_ROUTINE = PTHREAD_START_ROUTINE

# HANDLE WINAPI CreateRemoteThread(
#   _In_   HANDLE hProcess,
#   _In_   LPSECURITY_ATTRIBUTES lpThreadAttributes,
#   _In_   SIZE_T dwStackSize,
#   _In_   LPTHREAD_START_ROUTINE lpStartAddress,
#   _In_   LPVOID lpParameter,
#   _In_   DWORD dwCreationFlags,
#   _Out_  LPDWORD lpThreadId
# );
CreateRemoteThread = kernel32.CreateRemoteThread
CreateRemoteThread.restype = ULONG
CreateRemoteThread.argtypes = ULONG, LPSECURITY_ATTRIBUTES, SIZE_T, LPTHREAD_START_ROUTINE, LPVOID, DWORD, LPDWORD

# EOF

# See: http://nullege.com/codes/show/src@jaraco.mysql-1.1.1@root@_mysql_windows@api.py

#from ctypes import *
#
#STRING = c_char_p
#from ctypes.wintypes import ULONG
#from ctypes.wintypes import HKL
#from ctypes.wintypes import UINT
#from ctypes.wintypes import DWORD
#from ctypes.wintypes import tagPOINT
#from ctypes.wintypes import POINT
#from ctypes.wintypes import tagRECT
#from ctypes.wintypes import RECT
#from ctypes.wintypes import LPSTR
#from ctypes.wintypes import WCHAR
#from ctypes.wintypes import LPWSTR
#from ctypes.wintypes import HBITMAP
#from ctypes.wintypes import BOOL
#WSTRING = c_wchar_p
#from ctypes.wintypes import BYTE
#from ctypes.wintypes import HANDLE
#from ctypes.wintypes import WORD
#from ctypes.wintypes import LONG
#from ctypes.wintypes import _FILETIME
#from ctypes.wintypes import FILETIME
#from ctypes.wintypes import _LARGE_INTEGER
#from ctypes.wintypes import LARGE_INTEGER
#from ctypes.wintypes import WIN32_FIND_DATAA
#from ctypes.wintypes import WIN32_FIND_DATAW
#from ctypes.wintypes import _COORD
#from ctypes.wintypes import _SMALL_RECT
#from ctypes.wintypes import SMALL_RECT
#from ctypes.wintypes import WPARAM
#from ctypes.wintypes import LPARAM
#from ctypes.wintypes import HWND
#from ctypes.wintypes import HHOOK
#from ctypes.wintypes import ATOM
#from ctypes.wintypes import HGLOBAL
#from ctypes.wintypes import HLOCAL
#from ctypes.wintypes import HGDIOBJ
#from ctypes.wintypes import HKEY
#from ctypes.wintypes import HACCEL
#from ctypes.wintypes import HBRUSH
#from ctypes.wintypes import HCOLORSPACE
#from ctypes.wintypes import HDC
#from ctypes.wintypes import HDESK
#from ctypes.wintypes import HENHMETAFILE
#from ctypes.wintypes import HFONT
#from ctypes.wintypes import HICON
#from ctypes.wintypes import HMENU
#from ctypes.wintypes import HMETAFILE
#from ctypes.wintypes import HINSTANCE
#from ctypes.wintypes import HMODULE
#from ctypes.wintypes import HPALETTE
#from ctypes.wintypes import HPEN
#from ctypes.wintypes import HRGN
#from ctypes.wintypes import HRSRC
#from ctypes.wintypes import HSTR
#from ctypes.wintypes import HTASK
#from ctypes.wintypes import HWINSTA
#from ctypes.wintypes import HMONITOR
#from ctypes.wintypes import COLORREF
#from ctypes.wintypes import _RECTL
#from ctypes.wintypes import RECTL
#from ctypes.wintypes import _POINTL
#from ctypes.wintypes import POINTL
#from ctypes.wintypes import tagSIZE
#from ctypes.wintypes import SIZE
#from ctypes.wintypes import SIZEL
#from ctypes.wintypes import LPCSTR
#from ctypes.wintypes import LPCWSTR
#from ctypes.wintypes import LGRPID
#from ctypes.wintypes import LCTYPE
#from ctypes.wintypes import SC_HANDLE
#from ctypes.wintypes import SERVICE_STATUS_HANDLE
#from ctypes.wintypes import HDWP
#from ctypes.wintypes import tagMSG
#from ctypes.wintypes import MSG
#from _mysql_api_util import get_lib_path
#_libraries = {}
#_libraries['libmysql.dll'] = CDLL(get_lib_path())
#_stdcall_libraries = {}
#_stdcall_libraries['libmysql.dll'] = WinDLL(get_lib_path())
#from ctypes import HRESULT
#from ctypes.wintypes import LCID
#from ctypes.wintypes import LANGID
#from ctypes.wintypes import _ULARGE_INTEGER
#from ctypes.wintypes import ULARGE_INTEGER
#from ctypes.wintypes import BOOLEAN
#
#
#MYSQL_TYPE_NEWDATE = 14
#COMP_EQUAL = 0
#COM_SHUTDOWN = 8
#SC_STATUS_PROCESS_INFO = 0
#KILL_QUERY = 254
#IMPORT_OBJECT_CONST = 2
#LT_LOWEST_LATENCY = 1
#DECIMAL_RESULT = 4
#ProcessorPowerPolicyCurrent = 22
#COM_QUERY = 3
#STMT_ATTR_UPDATE_MAX_LENGTH = 0
#MYSQL_OPT_RECONNECT = 20
#GEO_ISO2 = 4
#AuditEventDirectoryServiceAccess = 1
#MYSQL_INIT_COMMAND = 3
#PowerDeviceUnspecified = 0
#PowerDeviceD3 = 4
#PowerSystemWorking = 1
#WinDigestAuthenticationSid = 52
#IMAGE_COR_MIH_BASICBLOCK = 8
#FileSystemType = 2
#KILL_CONNECTION = 255
#CURSOR_TYPE_FOR_UPDATE = 2
#WinWorldSid = 1
#TokenPrimaryGroup = 5
#COM_TABLE_DUMP = 19
#GEO_ISO3 = 5
#TapeDriveWriteError = 6
#MYSQL_STMT_INIT_DONE = 1
#NSP_NOTIFY_HWND = 1
#WinCreatorGroupServerSid = 6
#SidTypeDeletedAccount = 6
#COM_QUIT = 1
#COM_SLEEP = 0
#IMPORT_OBJECT_DATA = 1
#WinEnterpriseControllersSid = 15
#PowerSystemSleeping2 = 3
#SystemReserveHiberFile = 10
#ROW_RESULT = 3
#MYSQL_OPT_SSL_VERIFY_SERVER_CERT = 21
#GEO_RFC1766 = 6
#WinAccountKrbtgtSid = 40
#IMAGE_COR_MIH_EHRVA = 2
#TokenDefaultDacl = 6
#COM_BINLOG_DUMP = 18
#TokenOwner = 4
#COM_PING = 14
#VerifyProcessorPowerPolicyDc = 21
#ExceptionCollidedUnwind = 3
#TapeDriveReadError = 5
#WinNTLMAuthenticationSid = 51
#PowerActionNone = 0
#COM_STMT_RESET = 26
#FindExSearchLimitToDevices = 2
#FileInformationInAssemblyOfAssemblyInActivationContext = 4
#MYSQL_TIMESTAMP_DATE = 0
#MaxTokenInfoClass = 17
#INT_RESULT = 2
#GEO_LCID = 7
#NormalError = 1
#TapeDriveScsiConnectionError = 9
#SecurityImpersonation = 2
#SC_ACTION_RUN_COMMAND = 3
#MYSQL_TYPE_TIME = 11
#WinBuiltinGuestsSid = 28
#SidTypeInvalid = 7
#PowerActionShutdownOff = 6
#IMAGE_COR_MIH_METHODRVA = 1
#COM_CONNECT = 11
#MYSQL_OPT_LOCAL_INFILE = 8
#AdapterType = 4
#WinProxySid = 14
#TokenPrivileges = 3
#SystemPowerPolicyCurrent = 8
#MYSQL_TYPE_GEOMETRY = 255
#FindExSearchMaxSearchOp = 3
#SHUTDOWN_WAIT_ALL_BUFFERS = 16
#MYSQL_OPT_READ_TIMEOUT = 11
#NSP_NOTIFY_EVENT = 2
#JobObjectBasicAndIoAccountingInformation = 8
#COM_INIT_DB = 2
#CURSOR_TYPE_READ_ONLY = 1
#COM_STMT_CLOSE = 25
#FindExSearchLimitToDirectories = 1
#WinBuiltinDomainSid = 25
#WinNullSid = 0
#VerifyProcessorPowerPolicyAc = 20
#SHUTDOWN_WAIT_UPDATES = 8
#COM_CONNECT_OUT = 20
#MYSQL_TIMESTAMP_TIME = 2
#SecurityIdentification = 1
#MYSQL_OPTION_MULTI_STATEMENTS_ON = 0
#SC_ACTION_REBOOT = 2
#COMP_NOTLESS = 1
#ProcessorStateHandler = 7
#TokenAuditPolicy = 16
#CURSOR_TYPE_NO_CURSOR = 0
#AclRevisionInformation = 1
#NATIVE_TYPE_MAX_CB = 1
#COR_ILMETHOD_SECT_SMALL_MAX_DATASIZE = 255
#MYSQL_STATUS_READY = 0
#PowerDeviceD1 = 2
#DisableLoad = 4
#GEO_FRIENDLYNAME = 8
#COR_DELETED_NAME_LENGTH = 8
#STMT_ATTR_CURSOR_TYPE = 1
#GEOCLASS_NATION = 16
#TapeDriveReadWarning = 3
#MYSQL_SET_CHARSET_DIR = 6
#MYSQL_TYPE_LONG_BLOB = 251
#GEO_NATION = 1
#TapeDriveProblemNone = 0
#GEO_LONGITUDE = 3
#WinAccountAdministratorSid = 38
#TokenImpersonation = 2
#MYSQL_TIMESTAMP_DATETIME = 1
#WinAccountGuestSid = 39
#MYSQL_TYPE_VARCHAR = 15
#MYSQL_TYPE_TINY = 1
#MYSQL_TYPE_LONGLONG = 8
#MYSQL_STATUS_USE_RESULT = 2
#ActivationContextDetailedInformation = 2
#COM_STMT_PREPARE = 22
#SC_ACTION_RESTART = 1
#SystemPowerStateHandler = 6
#WinNetworkServiceSid = 24
#ProcessorPowerPolicyDc = 19
#GEO_TIMEZONES = 10
#MYSQL_SET_CHARSET_NAME = 7
#JobObjectBasicAccountingInformation = 1
#REAL_RESULT = 1
#WinAccountPolicyAdminsSid = 49
#COM_CHANGE_USER = 17
#Win32ServiceShareProcess = 32
#PowerSystemUnspecified = 0
#TokenSandBoxInert = 15
#GEO_OFFICIALNAME = 9
#TapeDriveReadWriteError = 2
#Win32ServiceOwnProcess = 16
#MYSQL_RPL_MASTER = 0
#MYSQL_STMT_FETCH_DONE = 4
#SidTypeComputer = 9
#MYSQL_PROTOCOL_MEMORY = 4
#COM_DROP_DB = 6
#WinServiceSid = 12
#SystemBatteryState = 5
#HeapCompatibilityInformation = 0
#IgnoreError = 0
#MYSQL_TYPE_SET = 248
#WinBuiltinNetworkConfigurationOperatorsSid = 37
#GetFileExMaxInfoLevel = 1
#MYSQL_TYPE_INT24 = 9
#AdministratorPowerPolicy = 9
#WinLocalServiceSid = 23
#TapeDriveReadWriteWarning = 1
#MYSQL_OPT_PROTOCOL = 9
#WinDialupSid = 8
#MaxJobObjectInfoClass = 11
#MYSQL_STMT_EXECUTE_DONE = 3
#WinAccountEnterpriseAdminsSid = 48
#MYSQL_PROTOCOL_PIPE = 3
#PowerActionWarmEject = 7
#AclSizeInformation = 2
#TokenSessionReference = 14
#TokenPrimary = 1
#NSP_NOTIFY_PORT = 3
#NSP_NOTIFY_IMMEDIATELY = 0
#SidTypeGroup = 2
#MYSQL_TIMESTAMP_ERROR = -1
#COM_REGISTER_SLAVE = 21
#COMIMAGE_FLAGS_ILONLY = 1
#WinRestrictedCodeSid = 18
#IMPORT_OBJECT_CODE = 0
#RNRSERVICE_DELETE = 2
#FindExInfoMaxInfoLevel = 1
#RecognizerType = 8
#SystemPowerCapabilities = 4
#WinAccountRasAndIasServersSid = 50
#GEO_OFFICIALLANGUAGES = 11
#WinAccountSchemaAdminsSid = 47
#WinBuiltinRemoteDesktopUsersSid = 36
#WinAccountControllersSid = 45
#COR_VERSION_MINOR = 0
#COM_SET_OPTION = 27
#DriverType = 1
#WinAccountDomainAdminsSid = 41
#JobObjectBasicProcessIdList = 3
#RNRSERVICE_DEREGISTER = 1
#AuditEventObjectAccess = 0
#WinBuiltinSystemOperatorsSid = 31
#WinBuiltinPowerUsersSid = 29
#WinBuiltinUsersSid = 27
#AssemblyDetailedInformationInActivationContext = 3
#COR_VERSION_MAJOR = 2
#MYSQL_TYPE_TIMESTAMP = 7
#MYSQL_PROTOCOL_TCP = 1
#IMPORT_OBJECT_ORDINAL = 0
#WinBuiltinPerfLoggingUsersSid = 58
#COM_FIELD_LIST = 4
#PowerActionShutdownReset = 5
#WinBatchSid = 10
#SidTypeWellKnownGroup = 5
#CURSOR_TYPE_SCROLLABLE = 4
#MYSQL_OPTION_MULTI_STATEMENTS_OFF = 1
#MYSQL_SET_CLIENT_IP = 17
#WinBuiltinPreWindows2000CompatibleAccessSid = 35
#COM_END = 30
#COR_VTABLE_32BIT = 1
#MYSQL_TYPE_LONG = 3
#MYSQL_STATUS_GET_RESULT = 1
#MAX_PACKAGE_NAME = 1024
#MYSQL_TYPE_DOUBLE = 5
#SC_ENUM_PROCESS_INFO = 0
#FindExSearchNameMatch = 0
#GEOCLASS_REGION = 14
#COM_DELAYED_INSERT = 16
#VerifySystemPolicyAc = 2
#WinLogonIdsSid = 21
#SevereError = 2
#STRING_RESULT = 0
#SystemExecutionState = 16
#MYSQL_SHARED_MEMORY_BASE_NAME = 10
#MYSQL_TYPE_MEDIUM_BLOB = 250
#MYSQL_TYPE_DECIMAL = 0
#WinAccountCertAdminsSid = 46
#MYSQL_TYPE_DATE = 10
#SecurityAnonymous = 0
#COR_VERSION_MAJOR_V2 = 2
#MYSQL_TYPE_FLOAT = 4
#COM_STATISTICS = 9
#SHUTDOWN_WAIT_CRITICAL_BUFFERS = 17
#JobObjectExtendedLimitInformation = 9
#TokenUser = 1
#JobObjectJobSetInformation = 10
#SidTypeUnknown = 8
#TokenSessionId = 12
#JobObjectBasicUIRestrictions = 4
#ExceptionContinueExecution = 0
#MYSQL_OPT_GUESS_CONNECTION = 16
#TapeDriveSnappedTape = 13
#RelationNumaNode = 1
#MYSQL_TYPE_YEAR = 13
#COR_VTABLEGAP_NAME_LENGTH = 8
#MYSQL_TYPE_DATETIME = 12
#WinBuiltinPerfMonitoringUsersSid = 57
#PowerActionShutdown = 4
#MYSQL_TYPE_TINY_BLOB = 249
#SystemPowerPolicyDc = 1
#BootLoad = 0
#SystemLoad = 1
#RelationProcessorCore = 0
#JobObjectAssociateCompletionPortInformation = 7
#WinBuiltinReplicatorSid = 34
#MYSQL_TYPE_NEWDECIMAL = 246
#AutoLoad = 2
#MYSQL_OPT_WRITE_TIMEOUT = 12
#MYSQL_TYPE_ENUM = 247
#SidTypeUser = 1
#MAX_CLASS_NAME = 1024
#ActivationContextBasicInformation = 1
#COM_CREATE_DB = 5
#WinRemoteLogonIdSid = 20
#COM_DEBUG = 13
#COMPARE_STRING = 1
#LastSleepTime = 15
#MYSQL_OPT_USE_REMOTE_CONNECTION = 14
#MYSQL_OPT_USE_RESULT = 13
#ProcessorPowerPolicyAc = 18
#PowerActionHibernate = 3
#MYSQL_TYPE_BLOB = 252
#WinNtAuthoritySid = 7
#LastWakeTime = 14
#TokenRestrictedSids = 11
#WinAnonymousSid = 13
#WinInteractiveSid = 11
#TapeDriveMediaLifeExpired = 12
#JobObjectEndOfJobTimeInformation = 6
#TokenType = 8
#WinBuiltinIncomingForestTrustBuildersSid = 56
#SHUTDOWN_DEFAULT = 0
#VerifySystemPolicyDc = 3
#WinLocalSid = 2
#TokenGroups = 2
#MYSQL_SECURE_AUTH = 18
#MYSQL_TYPE_VAR_STRING = 253
#COM_REFRESH = 7
#WinBuiltinBackupOperatorsSid = 33
#PowerDeviceD0 = 1
#DemandLoad = 3
#IMAGE_COR_EATJ_THUNK_SIZE = 32
#SHUTDOWN_WAIT_CONNECTIONS = 1
#COM_STMT_EXECUTE = 23
#IMPORT_OBJECT_NAME_UNDECORATE = 3
#WinTerminalServerSid = 19
#TapeDriveHardwareError = 7
#TapeDriveWriteWarning = 4
#WinAccountComputersSid = 44
#COMIMAGE_FLAGS_STRONGNAMESIGNED = 8
#NSP_NOTIFY_APC = 4
#MaxActivationContextInfoClass = 5
#TapeDriveCleanDriveNow = 11
#JobObjectSecurityLimitInformation = 5
#ExceptionNestedException = 2
#ExceptionContinueSearch = 1
#PowerSystemHibernate = 5
#WinOtherOrganizationSid = 55
#COM_PROCESS_INFO = 10
#SHUTDOWN_WAIT_TRANSACTIONS = 2
#PowerActionReserved = 1
#IMPORT_OBJECT_NAME_NO_PREFIX = 2
#COM_STMT_SEND_LONG_DATA = 24
#WinCreatorOwnerServerSid = 5
#FindExInfoStandard = 0
#TokenImpersonationLevel = 9
#CriticalError = 3
#WinBuiltinPrintOperatorsSid = 32
#MYSQL_TIMESTAMP_NONE = -2
#COMIMAGE_FLAGS_IL_LIBRARY = 4
#SidTypeDomain = 3
#COR_VTABLE_CALL_MOST_DERIVED = 16
#COM_PROCESS_KILL = 12
#MYSQL_PROTOCOL_SOCKET = 2
#COMIMAGE_FLAGS_TRACKDEBUGDATA = 65536
#WinNetworkSid = 9
#WinLocalSystemSid = 22
#ProcessorStateHandler2 = 13
#MYSQL_READ_DEFAULT_GROUP = 5
#RNRSERVICE_REGISTER = 0
#WinAccountDomainGuestsSid = 43
#PowerDeviceMaximum = 5
#PowerActionSleep = 2
#MYSQL_TYPE_NULL = 6
#IMPORT_OBJECT_NAME = 1
#PowerSystemMaximum = 7
#PowerSystemShutdown = 6
#SystemPowerLoggingEntry = 24
#COM_STMT_FETCH = 28
#PowerSystemSleeping3 = 4
#TapeDriveTimetoClean = 10
#SecurityDelegation = 3
#PowerSystemSleeping1 = 2
#COMIMAGE_FLAGS_32BITREQUIRED = 2
#MYSQL_PROTOCOL_DEFAULT = 0
#WinThisOrganizationSid = 54
#COR_VTABLE_FROM_UNMANAGED = 4
#COM_DAEMON = 29
#WinCreatorGroupSid = 4
#MYSQL_STMT_PREPARE_DONE = 2
#TokenSource = 7
#COM_TIME = 15
#MYSQL_READ_DEFAULT_FILE = 4
#SidTypeAlias = 4
#SystemPowerStateNotifyHandler = 17
#WinAuthenticatedUserSid = 17
#SystemPowerInformation = 12
#SC_ACTION_NONE = 0
#GEO_LATITUDE = 2
#MYSQL_OPT_CONNECT_TIMEOUT = 0
#WinBuiltinAccountOperatorsSid = 30
#WinAccountDomainUsersSid = 42
#MYSQL_RPL_ADMIN = 2
#MYSQL_OPT_NAMED_PIPE = 2
#COR_VTABLE_64BIT = 2
#MYSQL_TYPE_SHORT = 2
#GetFileExInfoStandard = 0
#WinCreatorOwnerSid = 3
#FileInformationInAssemblyOfAssemblyInActivationContxt = 4
#SystemPowerStateLogging = 23
#TapeDriveUnsupportedMedia = 8
#MYSQL_OPT_COMPRESS = 1
#JobObjectBasicLimitInformation = 2
#PowerDeviceD2 = 3
#MYSQL_TYPE_BIT = 16
#MYSQL_OPT_USE_EMBEDDED_CONNECTION = 15
#WinSChannelAuthenticationSid = 53
#SystemPowerPolicyAc = 0
#AssemblyDetailedInformationInActivationContxt = 3
#MYSQL_RPL_SLAVE = 1
#WinBuiltinAdministratorsSid = 26
#WinSelfSid = 16
#TokenStatistics = 10
#ProcessorInformation = 11
#MYSQL_TYPE_STRING = 254
#LT_DONT_CARE = 0
#MYSQL_REPORT_DATA_TRUNCATION = 19
#STMT_ATTR_PREFETCH_ROWS = 2
#IMAGE_AUX_SYMBOL_TYPE_TOKEN_DEF = 1
#TokenGroupsAndPrivileges = 13
#wint_t = c_ushort
#wctype_t = c_ushort
#
## values for enumeration '_EXCEPTION_DISPOSITION'
#_EXCEPTION_DISPOSITION = c_int # enum
#EXCEPTION_DISPOSITION = _EXCEPTION_DISPOSITION
#intptr_t = c_int
#time_t = c_long
#__time64_t = c_longlong
#_fsize_t = c_ulong
#class _finddata_t(Structure):
#    pass
#_finddata_t._fields_ = [
#    ('attrib', c_uint),
#    ('time_create', time_t),
#    ('time_access', time_t),
#    ('time_write', time_t),
#    ('size', _fsize_t),
#    ('name', c_char * 260),
#]
#class _finddatai64_t(Structure):
#    pass
#_finddatai64_t._fields_ = [
#    ('attrib', c_uint),
#    ('time_create', time_t),
#    ('time_access', time_t),
#    ('time_write', time_t),
#    ('size', c_longlong),
#    ('name', c_char * 260),
#]
#class __finddata64_t(Structure):
#    pass
#__finddata64_t._fields_ = [
#    ('attrib', c_uint),
#    ('time_create', __time64_t),
#    ('time_access', __time64_t),
#    ('time_write', __time64_t),
#    ('size', c_longlong),
#    ('name', c_char * 260),
#]
#class _wfinddata_t(Structure):
#    pass
#_wfinddata_t._fields_ = [
#    ('attrib', c_uint),
#    ('time_create', time_t),
#    ('time_access', time_t),
#    ('time_write', time_t),
#    ('size', _fsize_t),
#    ('name', c_wchar * 260),
#]
#class _wfinddatai64_t(Structure):
#    pass
#_wfinddatai64_t._fields_ = [
#    ('attrib', c_uint),
#    ('time_create', time_t),
#    ('time_access', time_t),
#    ('time_write', time_t),
#    ('size', c_longlong),
#    ('name', c_wchar * 260),
#]
#class __wfinddata64_t(Structure):
#    pass
#__wfinddata64_t._fields_ = [
#    ('attrib', c_uint),
#    ('time_create', __time64_t),
#    ('time_access', __time64_t),
#    ('time_write', __time64_t),
#    ('size', c_longlong),
#    ('name', c_wchar * 260),
#]
#class _heapinfo(Structure):
#    pass
#size_t = c_uint
#_heapinfo._fields_ = [
#    ('_pentry', POINTER(c_int)),
#    ('_size', size_t),
#    ('_useflag', c_int),
#]
#_HEAPINFO = _heapinfo
#class _exception(Structure):
#    pass
#_exception._fields_ = [
#    ('type', c_int),
#    ('name', STRING),
#    ('arg1', c_double),
#    ('arg2', c_double),
#    ('retval', c_double),
#]
#class _complex(Structure):
#    pass
#_complex._fields_ = [
#    ('x', c_double),
#    ('y', c_double),
#]
#uintptr_t = c_uint
#va_list = STRING
#_ino_t = c_ushort
#ino_t = c_ushort
#_dev_t = c_uint
#dev_t = c_uint
#_off_t = c_long
#off_t = c_long
#class _VIDEOPARAMETERS(Structure):
#    pass
#class _GUID(Structure):
#    pass
#_GUID._fields_ = [
#    ('Data1', c_ulong),
#    ('Data2', c_ushort),
#    ('Data3', c_ushort),
#    ('Data4', c_ubyte * 8),
#]
#GUID = _GUID
#UCHAR = c_ubyte
#_VIDEOPARAMETERS._fields_ = [
#    ('Guid', GUID),
#    ('dwOffset', ULONG),
#    ('dwCommand', ULONG),
#    ('dwFlags', ULONG),
#    ('dwMode', ULONG),
#    ('dwTVStandard', ULONG),
#    ('dwAvailableModes', ULONG),
#    ('dwAvailableTVStandard', ULONG),
#    ('dwFlickerFilter', ULONG),
#    ('dwOverScanX', ULONG),
#    ('dwOverScanY', ULONG),
#    ('dwMaxUnscaledX', ULONG),
#    ('dwMaxUnscaledY', ULONG),
#    ('dwPositionX', ULONG),
#    ('dwPositionY', ULONG),
#    ('dwBrightness', ULONG),
#    ('dwContrast', ULONG),
#    ('dwCPType', ULONG),
#    ('dwCPCommand', ULONG),
#    ('dwCPStandard', ULONG),
#    ('dwCPKey', ULONG),
#    ('bCP_APSTriggerBits', ULONG),
#    ('bOEMCopyProtection', UCHAR * 256),
#]
#PVIDEOPARAMETERS = POINTER(_VIDEOPARAMETERS)
#VIDEOPARAMETERS = _VIDEOPARAMETERS
#LPVIDEOPARAMETERS = POINTER(_VIDEOPARAMETERS)
#INT8 = c_byte
#PINT8 = POINTER(c_byte)
#PINT16 = POINTER(c_short)
#INT16 = c_short
#INT32 = c_int
#PINT32 = POINTER(c_int)
#PINT64 = POINTER(c_longlong)
#INT64 = c_longlong
#UINT8 = c_ubyte
#PUINT8 = POINTER(c_ubyte)
#PUINT16 = POINTER(c_ushort)
#UINT16 = c_ushort
#UINT32 = c_uint
#PUINT32 = POINTER(c_uint)
#PUINT64 = POINTER(c_ulonglong)
#UINT64 = c_ulonglong
#PLONG32 = POINTER(c_int)
#LONG32 = c_int
#PULONG32 = POINTER(c_uint)
#ULONG32 = c_uint
#PDWORD32 = POINTER(c_uint)
#DWORD32 = c_uint
#PINT_PTR = POINTER(c_int)
#INT_PTR = c_int
#PUINT_PTR = POINTER(c_uint)
#UINT_PTR = c_uint
#LONG_PTR = c_long
#PLONG_PTR = POINTER(c_long)
#PULONG_PTR = POINTER(c_ulong)
#ULONG_PTR = c_ulong
#PUHALF_PTR = POINTER(c_ushort)
#UHALF_PTR = c_ushort
#PHALF_PTR = POINTER(c_short)
#HALF_PTR = c_short
#SHANDLE_PTR = c_long
#HANDLE_PTR = c_ulong
#PSIZE_T = POINTER(ULONG_PTR)
#SIZE_T = ULONG_PTR
#SSIZE_T = LONG_PTR
#PSSIZE_T = POINTER(LONG_PTR)
#DWORD_PTR = ULONG_PTR
#PDWORD_PTR = POINTER(ULONG_PTR)
#LONG64 = c_longlong
#PLONG64 = POINTER(c_longlong)
#PULONG64 = POINTER(c_ulonglong)
#ULONG64 = c_ulonglong
#DWORD64 = c_ulonglong
#PDWORD64 = POINTER(c_ulonglong)
#KAFFINITY = ULONG_PTR
#PKAFFINITY = POINTER(KAFFINITY)
#LPGUID = POINTER(GUID)
#LPCGUID = POINTER(GUID)
#IID = GUID
#LPIID = POINTER(IID)
#CLSID = GUID
#LPCLSID = POINTER(CLSID)
#FMTID = GUID
#LPFMTID = POINTER(FMTID)
#class HIMC__(Structure):
#    pass
#HIMC__._fields_ = [
#    ('unused', c_int),
#]
#HIMC = POINTER(HIMC__)
#class HIMCC__(Structure):
#    pass
#HIMCC = POINTER(HIMCC__)
#HIMCC__._fields_ = [
#    ('unused', c_int),
#]
#LPHKL = POINTER(HKL)
#LPUINT = POINTER(UINT)
#class tagCOMPOSITIONFORM(Structure):
#    pass
#tagCOMPOSITIONFORM._fields_ = [
#    ('dwStyle', DWORD),
#    ('ptCurrentPos', POINT),
#    ('rcArea', RECT),
#]
#PCOMPOSITIONFORM = POINTER(tagCOMPOSITIONFORM)
#COMPOSITIONFORM = tagCOMPOSITIONFORM
#LPCOMPOSITIONFORM = POINTER(tagCOMPOSITIONFORM)
#NPCOMPOSITIONFORM = POINTER(tagCOMPOSITIONFORM)
#class tagCANDIDATEFORM(Structure):
#    pass
#tagCANDIDATEFORM._fields_ = [
#    ('dwIndex', DWORD),
#    ('dwStyle', DWORD),
#    ('ptCurrentPos', POINT),
#    ('rcArea', RECT),
#]
#PCANDIDATEFORM = POINTER(tagCANDIDATEFORM)
#LPCANDIDATEFORM = POINTER(tagCANDIDATEFORM)
#NPCANDIDATEFORM = POINTER(tagCANDIDATEFORM)
#CANDIDATEFORM = tagCANDIDATEFORM
#class tagCANDIDATELIST(Structure):
#    pass
#tagCANDIDATELIST._fields_ = [
#    ('dwSize', DWORD),
#    ('dwStyle', DWORD),
#    ('dwCount', DWORD),
#    ('dwSelection', DWORD),
#    ('dwPageStart', DWORD),
#    ('dwPageSize', DWORD),
#    ('dwOffset', DWORD * 1),
#]
#CANDIDATELIST = tagCANDIDATELIST
#LPCANDIDATELIST = POINTER(tagCANDIDATELIST)
#PCANDIDATELIST = POINTER(tagCANDIDATELIST)
#NPCANDIDATELIST = POINTER(tagCANDIDATELIST)
#class tagREGISTERWORDA(Structure):
#    pass
#CHAR = c_char
#tagREGISTERWORDA._fields_ = [
#    ('lpReading', LPSTR),
#    ('lpWord', LPSTR),
#]
#NPREGISTERWORDA = POINTER(tagREGISTERWORDA)
#PREGISTERWORDA = POINTER(tagREGISTERWORDA)
#LPREGISTERWORDA = POINTER(tagREGISTERWORDA)
#REGISTERWORDA = tagREGISTERWORDA
#class tagREGISTERWORDW(Structure):
#    pass
#tagREGISTERWORDW._fields_ = [
#    ('lpReading', LPWSTR),
#    ('lpWord', LPWSTR),
#]
#LPREGISTERWORDW = POINTER(tagREGISTERWORDW)
#NPREGISTERWORDW = POINTER(tagREGISTERWORDW)
#PREGISTERWORDW = POINTER(tagREGISTERWORDW)
#REGISTERWORDW = tagREGISTERWORDW
#REGISTERWORD = REGISTERWORDA
#PREGISTERWORD = PREGISTERWORDA
#NPREGISTERWORD = NPREGISTERWORDA
#LPREGISTERWORD = LPREGISTERWORDA
#class tagRECONVERTSTRING(Structure):
#    pass
#tagRECONVERTSTRING._fields_ = [
#    ('dwSize', DWORD),
#    ('dwVersion', DWORD),
#    ('dwStrLen', DWORD),
#    ('dwStrOffset', DWORD),
#    ('dwCompStrLen', DWORD),
#    ('dwCompStrOffset', DWORD),
#    ('dwTargetStrLen', DWORD),
#    ('dwTargetStrOffset', DWORD),
#]
#NPRECONVERTSTRING = POINTER(tagRECONVERTSTRING)
#PRECONVERTSTRING = POINTER(tagRECONVERTSTRING)
#LPRECONVERTSTRING = POINTER(tagRECONVERTSTRING)
#RECONVERTSTRING = tagRECONVERTSTRING
#class tagSTYLEBUFA(Structure):
#    pass
#tagSTYLEBUFA._fields_ = [
#    ('dwStyle', DWORD),
#    ('szDescription', CHAR * 32),
#]
#STYLEBUFA = tagSTYLEBUFA
#LPSTYLEBUFA = POINTER(tagSTYLEBUFA)
#NPSTYLEBUFA = POINTER(tagSTYLEBUFA)
#PSTYLEBUFA = POINTER(tagSTYLEBUFA)
#class tagSTYLEBUFW(Structure):
#    pass
#tagSTYLEBUFW._fields_ = [
#    ('dwStyle', DWORD),
#    ('szDescription', WCHAR * 32),
#]
#STYLEBUFW = tagSTYLEBUFW
#LPSTYLEBUFW = POINTER(tagSTYLEBUFW)
#NPSTYLEBUFW = POINTER(tagSTYLEBUFW)
#PSTYLEBUFW = POINTER(tagSTYLEBUFW)
#STYLEBUF = STYLEBUFA
#PSTYLEBUF = PSTYLEBUFA
#NPSTYLEBUF = NPSTYLEBUFA
#LPSTYLEBUF = LPSTYLEBUFA
#class tagIMEMENUITEMINFOA(Structure):
#    pass
#class HBITMAP__(Structure):
#    pass
#tagIMEMENUITEMINFOA._fields_ = [
#    ('cbSize', UINT),
#    ('fType', UINT),
#    ('fState', UINT),
#    ('wID', UINT),
#    ('hbmpChecked', HBITMAP),
#    ('hbmpUnchecked', HBITMAP),
#    ('dwItemData', DWORD),
#    ('szString', CHAR * 80),
#    ('hbmpItem', HBITMAP),
#]
#NPIMEMENUITEMINFOA = POINTER(tagIMEMENUITEMINFOA)
#LPIMEMENUITEMINFOA = POINTER(tagIMEMENUITEMINFOA)
#IMEMENUITEMINFOA = tagIMEMENUITEMINFOA
#PIMEMENUITEMINFOA = POINTER(tagIMEMENUITEMINFOA)
#class tagIMEMENUITEMINFOW(Structure):
#    pass
#tagIMEMENUITEMINFOW._fields_ = [
#    ('cbSize', UINT),
#    ('fType', UINT),
#    ('fState', UINT),
#    ('wID', UINT),
#    ('hbmpChecked', HBITMAP),
#    ('hbmpUnchecked', HBITMAP),
#    ('dwItemData', DWORD),
#    ('szString', WCHAR * 80),
#    ('hbmpItem', HBITMAP),
#]
#PIMEMENUITEMINFOW = POINTER(tagIMEMENUITEMINFOW)
#NPIMEMENUITEMINFOW = POINTER(tagIMEMENUITEMINFOW)
#LPIMEMENUITEMINFOW = POINTER(tagIMEMENUITEMINFOW)
#IMEMENUITEMINFOW = tagIMEMENUITEMINFOW
#IMEMENUITEMINFO = IMEMENUITEMINFOA
#PIMEMENUITEMINFO = PIMEMENUITEMINFOA
#NPIMEMENUITEMINFO = NPIMEMENUITEMINFOA
#LPIMEMENUITEMINFO = LPIMEMENUITEMINFOA
#class tagIMECHARPOSITION(Structure):
#    pass
#tagIMECHARPOSITION._fields_ = [
#    ('dwSize', DWORD),
#    ('dwCharPos', DWORD),
#    ('pt', POINT),
#    ('cLineHeight', UINT),
#    ('rcDocument', RECT),
#]
#IMECHARPOSITION = tagIMECHARPOSITION
#LPIMECHARPOSITION = POINTER(tagIMECHARPOSITION)
#NPIMECHARPOSITION = POINTER(tagIMECHARPOSITION)
#PIMECHARPOSITION = POINTER(tagIMECHARPOSITION)
#IMCENUMPROC = WINFUNCTYPE(BOOL, POINTER(HIMC__), c_long)
#REGISTERWORDENUMPROCA = WINFUNCTYPE(c_int, STRING, c_ulong, STRING, c_void_p)
#REGISTERWORDENUMPROCW = WINFUNCTYPE(c_int, WSTRING, c_ulong, WSTRING, c_void_p)
#class _MODEMDEVCAPS(Structure):
#    pass
#_MODEMDEVCAPS._fields_ = [
#    ('dwActualSize', DWORD),
#    ('dwRequiredSize', DWORD),
#    ('dwDevSpecificOffset', DWORD),
#    ('dwDevSpecificSize', DWORD),
#    ('dwModemProviderVersion', DWORD),
#    ('dwModemManufacturerOffset', DWORD),
#    ('dwModemManufacturerSize', DWORD),
#    ('dwModemModelOffset', DWORD),
#    ('dwModemModelSize', DWORD),
#    ('dwModemVersionOffset', DWORD),
#    ('dwModemVersionSize', DWORD),
#    ('dwDialOptions', DWORD),
#    ('dwCallSetupFailTimer', DWORD),
#    ('dwInactivityTimeout', DWORD),
#    ('dwSpeakerVolume', DWORD),
#    ('dwSpeakerMode', DWORD),
#    ('dwModemOptions', DWORD),
#    ('dwMaxDTERate', DWORD),
#    ('dwMaxDCERate', DWORD),
#    ('abVariablePortion', BYTE * 1),
#]
#LPMODEMDEVCAPS = POINTER(_MODEMDEVCAPS)
#PMODEMDEVCAPS = POINTER(_MODEMDEVCAPS)
#MODEMDEVCAPS = _MODEMDEVCAPS
#class _MODEMSETTINGS(Structure):
#    pass
#_MODEMSETTINGS._fields_ = [
#    ('dwActualSize', DWORD),
#    ('dwRequiredSize', DWORD),
#    ('dwDevSpecificOffset', DWORD),
#    ('dwDevSpecificSize', DWORD),
#    ('dwCallSetupFailTimer', DWORD),
#    ('dwInactivityTimeout', DWORD),
#    ('dwSpeakerVolume', DWORD),
#    ('dwSpeakerMode', DWORD),
#    ('dwPreferredModemOptions', DWORD),
#    ('dwNegotiatedModemOptions', DWORD),
#    ('dwNegotiatedDCERate', DWORD),
#    ('abVariablePortion', BYTE * 1),
#]
#PMODEMSETTINGS = POINTER(_MODEMSETTINGS)
#LPMODEMSETTINGS = POINTER(_MODEMSETTINGS)
#MODEMSETTINGS = _MODEMSETTINGS
#SERVICETYPE = ULONG
#class _flowspec(Structure):
#    pass
#_flowspec._fields_ = [
#    ('TokenRate', ULONG),
#    ('TokenBucketSize', ULONG),
#    ('PeakBandwidth', ULONG),
#    ('Latency', ULONG),
#    ('DelayVariation', ULONG),
#    ('ServiceType', SERVICETYPE),
#    ('MaxSduSize', ULONG),
#    ('MinimumPolicedSize', ULONG),
#]
#PFLOWSPEC = POINTER(_flowspec)
#LPFLOWSPEC = POINTER(_flowspec)
#FLOWSPEC = _flowspec
#class QOS_OBJECT_HDR(Structure):
#    pass
#LPQOS_OBJECT_HDR = POINTER(QOS_OBJECT_HDR)
#QOS_OBJECT_HDR._fields_ = [
#    ('ObjectType', ULONG),
#    ('ObjectLength', ULONG),
#]
#class _QOS_SD_MODE(Structure):
#    pass
#_QOS_SD_MODE._fields_ = [
#    ('ObjectHdr', QOS_OBJECT_HDR),
#    ('ShapeDiscardMode', ULONG),
#]
#QOS_SD_MODE = _QOS_SD_MODE
#LPQOS_SD_MODE = POINTER(_QOS_SD_MODE)
#class _QOS_SHAPING_RATE(Structure):
#    pass
#_QOS_SHAPING_RATE._fields_ = [
#    ('ObjectHdr', QOS_OBJECT_HDR),
#    ('ShapingRate', ULONG),
#]
#QOS_SHAPING_RATE = _QOS_SHAPING_RATE
#LPQOS_SHAPING_RATE = POINTER(_QOS_SHAPING_RATE)
#class _OVERLAPPED(Structure):
#    pass
#class N11_OVERLAPPED4DOLLAR_48E(Union):
#    pass
#class N11_OVERLAPPED4DOLLAR_484DOLLAR_49E(Structure):
#    pass
#N11_OVERLAPPED4DOLLAR_484DOLLAR_49E._fields_ = [
#    ('Offset', DWORD),
#    ('OffsetHigh', DWORD),
#]
#PVOID = c_void_p
#N11_OVERLAPPED4DOLLAR_48E._anonymous_ = ['_0']
#N11_OVERLAPPED4DOLLAR_48E._fields_ = [
#    ('_0', N11_OVERLAPPED4DOLLAR_484DOLLAR_49E),
#    ('Pointer', PVOID),
#]
#_OVERLAPPED._anonymous_ = ['_0']
#_OVERLAPPED._fields_ = [
#    ('Internal', ULONG_PTR),
#    ('InternalHigh', ULONG_PTR),
#    ('_0', N11_OVERLAPPED4DOLLAR_48E),
#    ('hEvent', HANDLE),
#]
#LPOVERLAPPED = POINTER(_OVERLAPPED)
#OVERLAPPED = _OVERLAPPED
#class _SECURITY_ATTRIBUTES(Structure):
#    pass
#LPVOID = c_void_p
#_SECURITY_ATTRIBUTES._fields_ = [
#    ('nLength', DWORD),
#    ('lpSecurityDescriptor', LPVOID),
#    ('bInheritHandle', BOOL),
#]
#PSECURITY_ATTRIBUTES = POINTER(_SECURITY_ATTRIBUTES)
#SECURITY_ATTRIBUTES = _SECURITY_ATTRIBUTES
#LPSECURITY_ATTRIBUTES = POINTER(_SECURITY_ATTRIBUTES)
#class _PROCESS_INFORMATION(Structure):
#    pass
#_PROCESS_INFORMATION._fields_ = [
#    ('hProcess', HANDLE),
#    ('hThread', HANDLE),
#    ('dwProcessId', DWORD),
#    ('dwThreadId', DWORD),
#]
#PROCESS_INFORMATION = _PROCESS_INFORMATION
#LPPROCESS_INFORMATION = POINTER(_PROCESS_INFORMATION)
#PPROCESS_INFORMATION = POINTER(_PROCESS_INFORMATION)
#class _SYSTEMTIME(Structure):
#    pass
#_SYSTEMTIME._fields_ = [
#    ('wYear', WORD),
#    ('wMonth', WORD),
#    ('wDayOfWeek', WORD),
#    ('wDay', WORD),
#    ('wHour', WORD),
#    ('wMinute', WORD),
#    ('wSecond', WORD),
#    ('wMilliseconds', WORD),
#]
#LPSYSTEMTIME = POINTER(_SYSTEMTIME)
#PSYSTEMTIME = POINTER(_SYSTEMTIME)
#SYSTEMTIME = _SYSTEMTIME
#PTHREAD_START_ROUTINE = WINFUNCTYPE(DWORD, c_void_p)
#LPTHREAD_START_ROUTINE = PTHREAD_START_ROUTINE
#PFIBER_START_ROUTINE = WINFUNCTYPE(None, c_void_p)
#LPFIBER_START_ROUTINE = PFIBER_START_ROUTINE
#class _RTL_CRITICAL_SECTION(Structure):
#    pass
#RTL_CRITICAL_SECTION = _RTL_CRITICAL_SECTION
#CRITICAL_SECTION = RTL_CRITICAL_SECTION
#PRTL_CRITICAL_SECTION = POINTER(_RTL_CRITICAL_SECTION)
#PCRITICAL_SECTION = PRTL_CRITICAL_SECTION
#LPCRITICAL_SECTION = PRTL_CRITICAL_SECTION
#class _RTL_CRITICAL_SECTION_DEBUG(Structure):
#    pass
#RTL_CRITICAL_SECTION_DEBUG = _RTL_CRITICAL_SECTION_DEBUG
#CRITICAL_SECTION_DEBUG = RTL_CRITICAL_SECTION_DEBUG
#PRTL_CRITICAL_SECTION_DEBUG = POINTER(_RTL_CRITICAL_SECTION_DEBUG)
#PCRITICAL_SECTION_DEBUG = PRTL_CRITICAL_SECTION_DEBUG
#LPCRITICAL_SECTION_DEBUG = PRTL_CRITICAL_SECTION_DEBUG
#class _LDT_ENTRY(Structure):
#    pass
#PLDT_ENTRY = POINTER(_LDT_ENTRY)
#LPLDT_ENTRY = PLDT_ENTRY
#class _COMMPROP(Structure):
#    pass
#_COMMPROP._fields_ = [
#    ('wPacketLength', WORD),
#    ('wPacketVersion', WORD),
#    ('dwServiceMask', DWORD),
#    ('dwReserved1', DWORD),
#    ('dwMaxTxQueue', DWORD),
#    ('dwMaxRxQueue', DWORD),
#    ('dwMaxBaud', DWORD),
#    ('dwProvSubType', DWORD),
#    ('dwProvCapabilities', DWORD),
#    ('dwSettableParams', DWORD),
#    ('dwSettableBaud', DWORD),
#    ('wSettableData', WORD),
#    ('wSettableStopParity', WORD),
#    ('dwCurrentTxQueue', DWORD),
#    ('dwCurrentRxQueue', DWORD),
#    ('dwProvSpec1', DWORD),
#    ('dwProvSpec2', DWORD),
#    ('wcProvChar', WCHAR * 1),
#]
#LPCOMMPROP = POINTER(_COMMPROP)
#COMMPROP = _COMMPROP
#class _COMSTAT(Structure):
#    pass
#_COMSTAT._fields_ = [
#    ('fCtsHold', DWORD, 1),
#    ('fDsrHold', DWORD, 1),
#    ('fRlsdHold', DWORD, 1),
#    ('fXoffHold', DWORD, 1),
#    ('fXoffSent', DWORD, 1),
#    ('fEof', DWORD, 1),
#    ('fTxim', DWORD, 1),
#    ('fReserved', DWORD, 25),
#    ('cbInQue', DWORD),
#    ('cbOutQue', DWORD),
#]
#LPCOMSTAT = POINTER(_COMSTAT)
#COMSTAT = _COMSTAT
#class _DCB(Structure):
#    pass
#_DCB._fields_ = [
#    ('DCBlength', DWORD),
#    ('BaudRate', DWORD),
#    ('fBinary', DWORD, 1),
#    ('fParity', DWORD, 1),
#    ('fOutxCtsFlow', DWORD, 1),
#    ('fOutxDsrFlow', DWORD, 1),
#    ('fDtrControl', DWORD, 2),
#    ('fDsrSensitivity', DWORD, 1),
#    ('fTXContinueOnXoff', DWORD, 1),
#    ('fOutX', DWORD, 1),
#    ('fInX', DWORD, 1),
#    ('fErrorChar', DWORD, 1),
#    ('fNull', DWORD, 1),
#    ('fRtsControl', DWORD, 2),
#    ('fAbortOnError', DWORD, 1),
#    ('fDummy2', DWORD, 17),
#    ('wReserved', WORD),
#    ('XonLim', WORD),
#    ('XoffLim', WORD),
#    ('ByteSize', BYTE),
#    ('Parity', BYTE),
#    ('StopBits', BYTE),
#    ('XonChar', c_char),
#    ('XoffChar', c_char),
#    ('ErrorChar', c_char),
#    ('EofChar', c_char),
#    ('EvtChar', c_char),
#    ('wReserved1', WORD),
#]
#DCB = _DCB
#LPDCB = POINTER(_DCB)
#class _COMMTIMEOUTS(Structure):
#    pass
#_COMMTIMEOUTS._fields_ = [
#    ('ReadIntervalTimeout', DWORD),
#    ('ReadTotalTimeoutMultiplier', DWORD),
#    ('ReadTotalTimeoutConstant', DWORD),
#    ('WriteTotalTimeoutMultiplier', DWORD),
#    ('WriteTotalTimeoutConstant', DWORD),
#]
#LPCOMMTIMEOUTS = POINTER(_COMMTIMEOUTS)
#COMMTIMEOUTS = _COMMTIMEOUTS
#class _COMMCONFIG(Structure):
#    pass
#_COMMCONFIG._fields_ = [
#    ('dwSize', DWORD),
#    ('wVersion', WORD),
#    ('wReserved', WORD),
#    ('dcb', DCB),
#    ('dwProviderSubType', DWORD),
#    ('dwProviderOffset', DWORD),
#    ('dwProviderSize', DWORD),
#    ('wcProviderData', WCHAR * 1),
#]
#COMMCONFIG = _COMMCONFIG
#LPCOMMCONFIG = POINTER(_COMMCONFIG)
#class _SYSTEM_INFO(Structure):
#    pass
#class N12_SYSTEM_INFO4DOLLAR_50E(Union):
#    pass
#class N12_SYSTEM_INFO4DOLLAR_504DOLLAR_51E(Structure):
#    pass
#N12_SYSTEM_INFO4DOLLAR_504DOLLAR_51E._fields_ = [
#    ('wProcessorArchitecture', WORD),
#    ('wReserved', WORD),
#]
#N12_SYSTEM_INFO4DOLLAR_50E._anonymous_ = ['_0']
#N12_SYSTEM_INFO4DOLLAR_50E._fields_ = [
#    ('dwOemId', DWORD),
#    ('_0', N12_SYSTEM_INFO4DOLLAR_504DOLLAR_51E),
#]
#_SYSTEM_INFO._anonymous_ = ['_0']
#_SYSTEM_INFO._fields_ = [
#    ('_0', N12_SYSTEM_INFO4DOLLAR_50E),
#    ('dwPageSize', DWORD),
#    ('lpMinimumApplicationAddress', LPVOID),
#    ('lpMaximumApplicationAddress', LPVOID),
#    ('dwActiveProcessorMask', DWORD_PTR),
#    ('dwNumberOfProcessors', DWORD),
#    ('dwProcessorType', DWORD),
#    ('dwAllocationGranularity', DWORD),
#    ('wProcessorLevel', WORD),
#    ('wProcessorRevision', WORD),
#]
#LPSYSTEM_INFO = POINTER(_SYSTEM_INFO)
#SYSTEM_INFO = _SYSTEM_INFO
#class _MEMORYSTATUS(Structure):
#    pass
#_MEMORYSTATUS._fields_ = [
#    ('dwLength', DWORD),
#    ('dwMemoryLoad', DWORD),
#    ('dwTotalPhys', SIZE_T),
#    ('dwAvailPhys', SIZE_T),
#    ('dwTotalPageFile', SIZE_T),
#    ('dwAvailPageFile', SIZE_T),
#    ('dwTotalVirtual', SIZE_T),
#    ('dwAvailVirtual', SIZE_T),
#]
#MEMORYSTATUS = _MEMORYSTATUS
#LPMEMORYSTATUS = POINTER(_MEMORYSTATUS)
#class _EXCEPTION_DEBUG_INFO(Structure):
#    pass
#class _EXCEPTION_RECORD(Structure):
#    pass
#_EXCEPTION_RECORD._fields_ = [
#    ('ExceptionCode', DWORD),
#    ('ExceptionFlags', DWORD),
#    ('ExceptionRecord', POINTER(_EXCEPTION_RECORD)),
#    ('ExceptionAddress', PVOID),
#    ('NumberParameters', DWORD),
#    ('ExceptionInformation', ULONG_PTR * 15),
#]
#EXCEPTION_RECORD = _EXCEPTION_RECORD
#_EXCEPTION_DEBUG_INFO._fields_ = [
#    ('ExceptionRecord', EXCEPTION_RECORD),
#    ('dwFirstChance', DWORD),
#]
#LPEXCEPTION_DEBUG_INFO = POINTER(_EXCEPTION_DEBUG_INFO)
#EXCEPTION_DEBUG_INFO = _EXCEPTION_DEBUG_INFO
#class _CREATE_THREAD_DEBUG_INFO(Structure):
#    pass
#_CREATE_THREAD_DEBUG_INFO._fields_ = [
#    ('hThread', HANDLE),
#    ('lpThreadLocalBase', LPVOID),
#    ('lpStartAddress', LPTHREAD_START_ROUTINE),
#]
#CREATE_THREAD_DEBUG_INFO = _CREATE_THREAD_DEBUG_INFO
#LPCREATE_THREAD_DEBUG_INFO = POINTER(_CREATE_THREAD_DEBUG_INFO)
#class _CREATE_PROCESS_DEBUG_INFO(Structure):
#    pass
#_CREATE_PROCESS_DEBUG_INFO._fields_ = [
#    ('hFile', HANDLE),
#    ('hProcess', HANDLE),
#    ('hThread', HANDLE),
#    ('lpBaseOfImage', LPVOID),
#    ('dwDebugInfoFileOffset', DWORD),
#    ('nDebugInfoSize', DWORD),
#    ('lpThreadLocalBase', LPVOID),
#    ('lpStartAddress', LPTHREAD_START_ROUTINE),
#    ('lpImageName', LPVOID),
#    ('fUnicode', WORD),
#]
#LPCREATE_PROCESS_DEBUG_INFO = POINTER(_CREATE_PROCESS_DEBUG_INFO)
#CREATE_PROCESS_DEBUG_INFO = _CREATE_PROCESS_DEBUG_INFO
#class _EXIT_THREAD_DEBUG_INFO(Structure):
#    pass
#_EXIT_THREAD_DEBUG_INFO._fields_ = [
#    ('dwExitCode', DWORD),
#]
#EXIT_THREAD_DEBUG_INFO = _EXIT_THREAD_DEBUG_INFO
#LPEXIT_THREAD_DEBUG_INFO = POINTER(_EXIT_THREAD_DEBUG_INFO)
#class _EXIT_PROCESS_DEBUG_INFO(Structure):
#    pass
#_EXIT_PROCESS_DEBUG_INFO._fields_ = [
#    ('dwExitCode', DWORD),
#]
#LPEXIT_PROCESS_DEBUG_INFO = POINTER(_EXIT_PROCESS_DEBUG_INFO)
#EXIT_PROCESS_DEBUG_INFO = _EXIT_PROCESS_DEBUG_INFO
#class _LOAD_DLL_DEBUG_INFO(Structure):
#    pass
#_LOAD_DLL_DEBUG_INFO._fields_ = [
#    ('hFile', HANDLE),
#    ('lpBaseOfDll', LPVOID),
#    ('dwDebugInfoFileOffset', DWORD),
#    ('nDebugInfoSize', DWORD),
#    ('lpImageName', LPVOID),
#    ('fUnicode', WORD),
#]
#LOAD_DLL_DEBUG_INFO = _LOAD_DLL_DEBUG_INFO
#LPLOAD_DLL_DEBUG_INFO = POINTER(_LOAD_DLL_DEBUG_INFO)
#class _UNLOAD_DLL_DEBUG_INFO(Structure):
#    pass
#_UNLOAD_DLL_DEBUG_INFO._fields_ = [
#    ('lpBaseOfDll', LPVOID),
#]
#LPUNLOAD_DLL_DEBUG_INFO = POINTER(_UNLOAD_DLL_DEBUG_INFO)
#UNLOAD_DLL_DEBUG_INFO = _UNLOAD_DLL_DEBUG_INFO
#class _OUTPUT_DEBUG_STRING_INFO(Structure):
#    pass
#_OUTPUT_DEBUG_STRING_INFO._fields_ = [
#    ('lpDebugStringData', LPSTR),
#    ('fUnicode', WORD),
#    ('nDebugStringLength', WORD),
#]
#OUTPUT_DEBUG_STRING_INFO = _OUTPUT_DEBUG_STRING_INFO
#LPOUTPUT_DEBUG_STRING_INFO = POINTER(_OUTPUT_DEBUG_STRING_INFO)
#class _RIP_INFO(Structure):
#    pass
#_RIP_INFO._fields_ = [
#    ('dwError', DWORD),
#    ('dwType', DWORD),
#]
#LPRIP_INFO = POINTER(_RIP_INFO)
#RIP_INFO = _RIP_INFO
#class _DEBUG_EVENT(Structure):
#    pass
#class N12_DEBUG_EVENT4DOLLAR_52E(Union):
#    pass
#N12_DEBUG_EVENT4DOLLAR_52E._fields_ = [
#    ('Exception', EXCEPTION_DEBUG_INFO),
#    ('CreateThread', CREATE_THREAD_DEBUG_INFO),
#    ('CreateProcessInfo', CREATE_PROCESS_DEBUG_INFO),
#    ('ExitThread', EXIT_THREAD_DEBUG_INFO),
#    ('ExitProcess', EXIT_PROCESS_DEBUG_INFO),
#    ('LoadDll', LOAD_DLL_DEBUG_INFO),
#    ('UnloadDll', UNLOAD_DLL_DEBUG_INFO),
#    ('DebugString', OUTPUT_DEBUG_STRING_INFO),
#    ('RipInfo', RIP_INFO),
#]
#_DEBUG_EVENT._fields_ = [
#    ('dwDebugEventCode', DWORD),
#    ('dwProcessId', DWORD),
#    ('dwThreadId', DWORD),
#    ('u', N12_DEBUG_EVENT4DOLLAR_52E),
#]
#LPDEBUG_EVENT = POINTER(_DEBUG_EVENT)
#DEBUG_EVENT = _DEBUG_EVENT
#class _CONTEXT(Structure):
#    pass
#CONTEXT = _CONTEXT
#PCONTEXT = POINTER(CONTEXT)
#LPCONTEXT = PCONTEXT
#PEXCEPTION_RECORD = POINTER(EXCEPTION_RECORD)
#LPEXCEPTION_RECORD = PEXCEPTION_RECORD
#class _EXCEPTION_POINTERS(Structure):
#    pass
#PEXCEPTION_POINTERS = POINTER(_EXCEPTION_POINTERS)
#LPEXCEPTION_POINTERS = PEXCEPTION_POINTERS
#class _OFSTRUCT(Structure):
#    pass
#_OFSTRUCT._fields_ = [
#    ('cBytes', BYTE),
#    ('fFixedDisk', BYTE),
#    ('nErrCode', WORD),
#    ('Reserved1', WORD),
#    ('Reserved2', WORD),
#    ('szPathName', CHAR * 128),
#]
#POFSTRUCT = POINTER(_OFSTRUCT)
#LPOFSTRUCT = POINTER(_OFSTRUCT)
#OFSTRUCT = _OFSTRUCT
#class _MEMORYSTATUSEX(Structure):
#    pass
#ULONGLONG = c_ulonglong
#DWORDLONG = ULONGLONG
#_MEMORYSTATUSEX._fields_ = [
#    ('dwLength', DWORD),
#    ('dwMemoryLoad', DWORD),
#    ('ullTotalPhys', DWORDLONG),
#    ('ullAvailPhys', DWORDLONG),
#    ('ullTotalPageFile', DWORDLONG),
#    ('ullAvailPageFile', DWORDLONG),
#    ('ullTotalVirtual', DWORDLONG),
#    ('ullAvailVirtual', DWORDLONG),
#    ('ullAvailExtendedVirtual', DWORDLONG),
#]
#MEMORYSTATUSEX = _MEMORYSTATUSEX
#LPMEMORYSTATUSEX = POINTER(_MEMORYSTATUSEX)
#class _PROCESS_HEAP_ENTRY(Structure):
#    pass
#class N19_PROCESS_HEAP_ENTRY4DOLLAR_53E(Union):
#    pass
#class N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_54E(Structure):
#    pass
#N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_54E._fields_ = [
#    ('hMem', HANDLE),
#    ('dwReserved', DWORD * 3),
#]
#class N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_55E(Structure):
#    pass
#N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_55E._fields_ = [
#    ('dwCommittedSize', DWORD),
#    ('dwUnCommittedSize', DWORD),
#    ('lpFirstBlock', LPVOID),
#    ('lpLastBlock', LPVOID),
#]
#N19_PROCESS_HEAP_ENTRY4DOLLAR_53E._fields_ = [
#    ('Block', N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_54E),
#    ('Region', N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_55E),
#]
#_PROCESS_HEAP_ENTRY._anonymous_ = ['_0']
#_PROCESS_HEAP_ENTRY._fields_ = [
#    ('lpData', PVOID),
#    ('cbData', DWORD),
#    ('cbOverhead', BYTE),
#    ('iRegionIndex', BYTE),
#    ('wFlags', WORD),
#    ('_0', N19_PROCESS_HEAP_ENTRY4DOLLAR_53E),
#]
#PROCESS_HEAP_ENTRY = _PROCESS_HEAP_ENTRY
#LPPROCESS_HEAP_ENTRY = POINTER(_PROCESS_HEAP_ENTRY)
#PPROCESS_HEAP_ENTRY = POINTER(_PROCESS_HEAP_ENTRY)
#PTOP_LEVEL_EXCEPTION_FILTER = WINFUNCTYPE(LONG, POINTER(_EXCEPTION_POINTERS))
#LPTOP_LEVEL_EXCEPTION_FILTER = PTOP_LEVEL_EXCEPTION_FILTER
#PAPCFUNC = WINFUNCTYPE(None, c_ulong)
#class _BY_HANDLE_FILE_INFORMATION(Structure):
#    pass
#_BY_HANDLE_FILE_INFORMATION._fields_ = [
#    ('dwFileAttributes', DWORD),
#    ('ftCreationTime', FILETIME),
#    ('ftLastAccessTime', FILETIME),
#    ('ftLastWriteTime', FILETIME),
#    ('dwVolumeSerialNumber', DWORD),
#    ('nFileSizeHigh', DWORD),
#    ('nFileSizeLow', DWORD),
#    ('nNumberOfLinks', DWORD),
#    ('nFileIndexHigh', DWORD),
#    ('nFileIndexLow', DWORD),
#]
#LPBY_HANDLE_FILE_INFORMATION = POINTER(_BY_HANDLE_FILE_INFORMATION)
#PBY_HANDLE_FILE_INFORMATION = POINTER(_BY_HANDLE_FILE_INFORMATION)
#BY_HANDLE_FILE_INFORMATION = _BY_HANDLE_FILE_INFORMATION
#class _TIME_ZONE_INFORMATION(Structure):
#    pass
#_TIME_ZONE_INFORMATION._fields_ = [
#    ('Bias', LONG),
#    ('StandardName', WCHAR * 32),
#    ('StandardDate', SYSTEMTIME),
#    ('StandardBias', LONG),
#    ('DaylightName', WCHAR * 32),
#    ('DaylightDate', SYSTEMTIME),
#    ('DaylightBias', LONG),
#]
#TIME_ZONE_INFORMATION = _TIME_ZONE_INFORMATION
#LPTIME_ZONE_INFORMATION = POINTER(_TIME_ZONE_INFORMATION)
#PTIME_ZONE_INFORMATION = POINTER(_TIME_ZONE_INFORMATION)
#PFE_EXPORT_FUNC = WINFUNCTYPE(DWORD, POINTER(BYTE), c_void_p, c_ulong)
#PFE_IMPORT_FUNC = WINFUNCTYPE(DWORD, POINTER(BYTE), c_void_p, POINTER(ULONG))
#PFLS_CALLBACK_FUNCTION = WINFUNCTYPE(None, c_void_p)
#LPOVERLAPPED_COMPLETION_ROUTINE = WINFUNCTYPE(None, c_ulong, c_ulong, POINTER(_OVERLAPPED))
#class _WIN32_STREAM_ID(Structure):
#    pass
#_WIN32_STREAM_ID._fields_ = [
#    ('dwStreamId', DWORD),
#    ('dwStreamAttributes', DWORD),
#    ('Size', LARGE_INTEGER),
#    ('dwStreamNameSize', DWORD),
#    ('cStreamName', WCHAR * 1),
#]
#LPWIN32_STREAM_ID = POINTER(_WIN32_STREAM_ID)
#WIN32_STREAM_ID = _WIN32_STREAM_ID
#class _STARTUPINFOA(Structure):
#    pass
#LPBYTE = POINTER(BYTE)
#_STARTUPINFOA._fields_ = [
#    ('cb', DWORD),
#    ('lpReserved', LPSTR),
#    ('lpDesktop', LPSTR),
#    ('lpTitle', LPSTR),
#    ('dwX', DWORD),
#    ('dwY', DWORD),
#    ('dwXSize', DWORD),
#    ('dwYSize', DWORD),
#    ('dwXCountChars', DWORD),
#    ('dwYCountChars', DWORD),
#    ('dwFillAttribute', DWORD),
#    ('dwFlags', DWORD),
#    ('wShowWindow', WORD),
#    ('cbReserved2', WORD),
#    ('lpReserved2', LPBYTE),
#    ('hStdInput', HANDLE),
#    ('hStdOutput', HANDLE),
#    ('hStdError', HANDLE),
#]
#STARTUPINFOA = _STARTUPINFOA
#LPSTARTUPINFOA = POINTER(_STARTUPINFOA)
#class _STARTUPINFOW(Structure):
#    pass
#_STARTUPINFOW._fields_ = [
#    ('cb', DWORD),
#    ('lpReserved', LPWSTR),
#    ('lpDesktop', LPWSTR),
#    ('lpTitle', LPWSTR),
#    ('dwX', DWORD),
#    ('dwY', DWORD),
#    ('dwXSize', DWORD),
#    ('dwYSize', DWORD),
#    ('dwXCountChars', DWORD),
#    ('dwYCountChars', DWORD),
#    ('dwFillAttribute', DWORD),
#    ('dwFlags', DWORD),
#    ('wShowWindow', WORD),
#    ('cbReserved2', WORD),
#    ('lpReserved2', LPBYTE),
#    ('hStdInput', HANDLE),
#    ('hStdOutput', HANDLE),
#    ('hStdError', HANDLE),
#]
#LPSTARTUPINFOW = POINTER(_STARTUPINFOW)
#STARTUPINFOW = _STARTUPINFOW
#STARTUPINFO = STARTUPINFOA
#LPSTARTUPINFO = LPSTARTUPINFOA
#class _WIN32_FIND_DATAA(Structure):
#    pass
#_WIN32_FIND_DATAA._fields_ = [
#    ('dwFileAttributes', DWORD),
#    ('ftCreationTime', FILETIME),
#    ('ftLastAccessTime', FILETIME),
#    ('ftLastWriteTime', FILETIME),
#    ('nFileSizeHigh', DWORD),
#    ('nFileSizeLow', DWORD),
#    ('dwReserved0', DWORD),
#    ('dwReserved1', DWORD),
#    ('cFileName', CHAR * 260),
#    ('cAlternateFileName', CHAR * 14),
#]
#LPWIN32_FIND_DATAA = POINTER(_WIN32_FIND_DATAA)
#PWIN32_FIND_DATAA = POINTER(_WIN32_FIND_DATAA)
#class _WIN32_FIND_DATAW(Structure):
#    pass
#_WIN32_FIND_DATAW._fields_ = [
#    ('dwFileAttributes', DWORD),
#    ('ftCreationTime', FILETIME),
#    ('ftLastAccessTime', FILETIME),
#    ('ftLastWriteTime', FILETIME),
#    ('nFileSizeHigh', DWORD),
#    ('nFileSizeLow', DWORD),
#    ('dwReserved0', DWORD),
#    ('dwReserved1', DWORD),
#    ('cFileName', WCHAR * 260),
#    ('cAlternateFileName', WCHAR * 14),
#]
#LPWIN32_FIND_DATAW = POINTER(_WIN32_FIND_DATAW)
#PWIN32_FIND_DATAW = POINTER(_WIN32_FIND_DATAW)
#WIN32_FIND_DATA = WIN32_FIND_DATAA
#PWIN32_FIND_DATA = PWIN32_FIND_DATAA
#LPWIN32_FIND_DATA = LPWIN32_FIND_DATAA
#class _WIN32_FILE_ATTRIBUTE_DATA(Structure):
#    pass
#_WIN32_FILE_ATTRIBUTE_DATA._fields_ = [
#    ('dwFileAttributes', DWORD),
#    ('ftCreationTime', FILETIME),
#    ('ftLastAccessTime', FILETIME),
#    ('ftLastWriteTime', FILETIME),
#    ('nFileSizeHigh', DWORD),
#    ('nFileSizeLow', DWORD),
#]
#WIN32_FILE_ATTRIBUTE_DATA = _WIN32_FILE_ATTRIBUTE_DATA
#LPWIN32_FILE_ATTRIBUTE_DATA = POINTER(_WIN32_FILE_ATTRIBUTE_DATA)
#PTIMERAPCROUTINE = WINFUNCTYPE(None, c_void_p, c_ulong, c_ulong)
#class HINSTANCE__(Structure):
#    pass
#ENUMRESTYPEPROCA = WINFUNCTYPE(BOOL, POINTER(HINSTANCE__), STRING, c_long)
#ENUMRESTYPEPROCW = WINFUNCTYPE(BOOL, POINTER(HINSTANCE__), WSTRING, c_long)
#ENUMRESNAMEPROCA = WINFUNCTYPE(BOOL, POINTER(HINSTANCE__), STRING, STRING, c_long)
#ENUMRESNAMEPROCW = WINFUNCTYPE(BOOL, POINTER(HINSTANCE__), WSTRING, WSTRING, c_long)
#ENUMRESLANGPROCA = WINFUNCTYPE(BOOL, POINTER(HINSTANCE__), STRING, STRING, c_ushort, c_long)
#ENUMRESLANGPROCW = WINFUNCTYPE(BOOL, POINTER(HINSTANCE__), WSTRING, WSTRING, c_ushort, c_long)
#
## values for enumeration '_GET_FILEEX_INFO_LEVELS'
#_GET_FILEEX_INFO_LEVELS = c_int # enum
#GET_FILEEX_INFO_LEVELS = _GET_FILEEX_INFO_LEVELS
#
## values for enumeration '_FINDEX_INFO_LEVELS'
#_FINDEX_INFO_LEVELS = c_int # enum
#FINDEX_INFO_LEVELS = _FINDEX_INFO_LEVELS
#
## values for enumeration '_FINDEX_SEARCH_OPS'
#_FINDEX_SEARCH_OPS = c_int # enum
#FINDEX_SEARCH_OPS = _FINDEX_SEARCH_OPS
#LPPROGRESS_ROUTINE = WINFUNCTYPE(DWORD, _LARGE_INTEGER, _LARGE_INTEGER, _LARGE_INTEGER, _LARGE_INTEGER, c_ulong, c_ulong, c_void_p, c_void_p, c_void_p)
#class _EVENTLOG_FULL_INFORMATION(Structure):
#    pass
#_EVENTLOG_FULL_INFORMATION._fields_ = [
#    ('dwFull', DWORD),
#]
#EVENTLOG_FULL_INFORMATION = _EVENTLOG_FULL_INFORMATION
#LPEVENTLOG_FULL_INFORMATION = POINTER(_EVENTLOG_FULL_INFORMATION)
#class tagHW_PROFILE_INFOA(Structure):
#    pass
#tagHW_PROFILE_INFOA._fields_ = [
#    ('dwDockInfo', DWORD),
#    ('szHwProfileGuid', CHAR * 39),
#    ('szHwProfileName', CHAR * 80),
#]
#HW_PROFILE_INFOA = tagHW_PROFILE_INFOA
#LPHW_PROFILE_INFOA = POINTER(tagHW_PROFILE_INFOA)
#class tagHW_PROFILE_INFOW(Structure):
#    pass
#tagHW_PROFILE_INFOW._fields_ = [
#    ('dwDockInfo', DWORD),
#    ('szHwProfileGuid', WCHAR * 39),
#    ('szHwProfileName', WCHAR * 80),
#]
#HW_PROFILE_INFOW = tagHW_PROFILE_INFOW
#LPHW_PROFILE_INFOW = POINTER(tagHW_PROFILE_INFOW)
#HW_PROFILE_INFO = HW_PROFILE_INFOA
#LPHW_PROFILE_INFO = LPHW_PROFILE_INFOA
#class _SYSTEM_POWER_STATUS(Structure):
#    pass
#_SYSTEM_POWER_STATUS._fields_ = [
#    ('ACLineStatus', BYTE),
#    ('BatteryFlag', BYTE),
#    ('BatteryLifePercent', BYTE),
#    ('Reserved1', BYTE),
#    ('BatteryLifeTime', DWORD),
#    ('BatteryFullLifeTime', DWORD),
#]
#SYSTEM_POWER_STATUS = _SYSTEM_POWER_STATUS
#LPSYSTEM_POWER_STATUS = POINTER(_SYSTEM_POWER_STATUS)
#COORD = _COORD
#PCOORD = POINTER(_COORD)
#PSMALL_RECT = POINTER(_SMALL_RECT)
#class _KEY_EVENT_RECORD(Structure):
#    pass
#class N17_KEY_EVENT_RECORD4DOLLAR_72E(Union):
#    pass
#N17_KEY_EVENT_RECORD4DOLLAR_72E._fields_ = [
#    ('UnicodeChar', WCHAR),
#    ('AsciiChar', CHAR),
#]
#_KEY_EVENT_RECORD._fields_ = [
#    ('bKeyDown', BOOL),
#    ('wRepeatCount', WORD),
#    ('wVirtualKeyCode', WORD),
#    ('wVirtualScanCode', WORD),
#    ('uChar', N17_KEY_EVENT_RECORD4DOLLAR_72E),
#    ('dwControlKeyState', DWORD),
#]
#KEY_EVENT_RECORD = _KEY_EVENT_RECORD
#PKEY_EVENT_RECORD = POINTER(_KEY_EVENT_RECORD)
#class _MOUSE_EVENT_RECORD(Structure):
#    pass
#_MOUSE_EVENT_RECORD._fields_ = [
#    ('dwMousePosition', COORD),
#    ('dwButtonState', DWORD),
#    ('dwControlKeyState', DWORD),
#    ('dwEventFlags', DWORD),
#]
#PMOUSE_EVENT_RECORD = POINTER(_MOUSE_EVENT_RECORD)
#MOUSE_EVENT_RECORD = _MOUSE_EVENT_RECORD
#class _WINDOW_BUFFER_SIZE_RECORD(Structure):
#    pass
#_WINDOW_BUFFER_SIZE_RECORD._fields_ = [
#    ('dwSize', COORD),
#]
#WINDOW_BUFFER_SIZE_RECORD = _WINDOW_BUFFER_SIZE_RECORD
#PWINDOW_BUFFER_SIZE_RECORD = POINTER(_WINDOW_BUFFER_SIZE_RECORD)
#class _MENU_EVENT_RECORD(Structure):
#    pass
#_MENU_EVENT_RECORD._fields_ = [
#    ('dwCommandId', UINT),
#]
#MENU_EVENT_RECORD = _MENU_EVENT_RECORD
#PMENU_EVENT_RECORD = POINTER(_MENU_EVENT_RECORD)
#class _FOCUS_EVENT_RECORD(Structure):
#    pass
#_FOCUS_EVENT_RECORD._fields_ = [
#    ('bSetFocus', BOOL),
#]
#FOCUS_EVENT_RECORD = _FOCUS_EVENT_RECORD
#PFOCUS_EVENT_RECORD = POINTER(_FOCUS_EVENT_RECORD)
#class _INPUT_RECORD(Structure):
#    pass
#class N13_INPUT_RECORD4DOLLAR_73E(Union):
#    pass
#N13_INPUT_RECORD4DOLLAR_73E._fields_ = [
#    ('KeyEvent', KEY_EVENT_RECORD),
#    ('MouseEvent', MOUSE_EVENT_RECORD),
#    ('WindowBufferSizeEvent', WINDOW_BUFFER_SIZE_RECORD),
#    ('MenuEvent', MENU_EVENT_RECORD),
#    ('FocusEvent', FOCUS_EVENT_RECORD),
#]
#_INPUT_RECORD._fields_ = [
#    ('EventType', WORD),
#    ('Event', N13_INPUT_RECORD4DOLLAR_73E),
#]
#INPUT_RECORD = _INPUT_RECORD
#PINPUT_RECORD = POINTER(_INPUT_RECORD)
#class _CHAR_INFO(Structure):
#    pass
#class N10_CHAR_INFO4DOLLAR_74E(Union):
#    pass
#N10_CHAR_INFO4DOLLAR_74E._fields_ = [
#    ('UnicodeChar', WCHAR),
#    ('AsciiChar', CHAR),
#]
#_CHAR_INFO._fields_ = [
#    ('Char', N10_CHAR_INFO4DOLLAR_74E),
#    ('Attributes', WORD),
#]
#CHAR_INFO = _CHAR_INFO
#PCHAR_INFO = POINTER(_CHAR_INFO)
#class _CONSOLE_SCREEN_BUFFER_INFO(Structure):
#    pass
#_CONSOLE_SCREEN_BUFFER_INFO._fields_ = [
#    ('dwSize', COORD),
#    ('dwCursorPosition', COORD),
#    ('wAttributes', WORD),
#    ('srWindow', SMALL_RECT),
#    ('dwMaximumWindowSize', COORD),
#]
#CONSOLE_SCREEN_BUFFER_INFO = _CONSOLE_SCREEN_BUFFER_INFO
#PCONSOLE_SCREEN_BUFFER_INFO = POINTER(_CONSOLE_SCREEN_BUFFER_INFO)
#class _CONSOLE_CURSOR_INFO(Structure):
#    pass
#_CONSOLE_CURSOR_INFO._fields_ = [
#    ('dwSize', DWORD),
#    ('bVisible', BOOL),
#]
#CONSOLE_CURSOR_INFO = _CONSOLE_CURSOR_INFO
#PCONSOLE_CURSOR_INFO = POINTER(_CONSOLE_CURSOR_INFO)
#class _CONSOLE_FONT_INFO(Structure):
#    pass
#_CONSOLE_FONT_INFO._fields_ = [
#    ('nFont', DWORD),
#    ('dwFontSize', COORD),
#]
#PCONSOLE_FONT_INFO = POINTER(_CONSOLE_FONT_INFO)
#CONSOLE_FONT_INFO = _CONSOLE_FONT_INFO
#PHANDLER_ROUTINE = WINFUNCTYPE(BOOL, c_ulong)
#PULONG = POINTER(ULONG)
#USHORT = c_ushort
#PUSHORT = POINTER(USHORT)
#PUCHAR = POINTER(UCHAR)
#PSZ = STRING
#FLOAT = c_float
#PFLOAT = POINTER(FLOAT)
#PBOOL = POINTER(BOOL)
#LPBOOL = POINTER(BOOL)
#PBYTE = POINTER(BYTE)
#PINT = POINTER(c_int)
#LPINT = POINTER(c_int)
#PWORD = POINTER(WORD)
#LPWORD = POINTER(WORD)
#LPLONG = POINTER(c_long)
#PDWORD = POINTER(DWORD)
#LPDWORD = POINTER(DWORD)
#LPCVOID = c_void_p
#INT = c_int
#PUINT = POINTER(c_uint)
#LRESULT = LONG_PTR
#class HWND__(Structure):
#    pass
#HWND__._fields_ = [
#    ('unused', c_int),
#]
#class HHOOK__(Structure):
#    pass
#HHOOK__._fields_ = [
#    ('unused', c_int),
#]
#SPHANDLE = POINTER(HANDLE)
#LPHANDLE = POINTER(HANDLE)
#GLOBALHANDLE = HANDLE
#LOCALHANDLE = HANDLE
#FARPROC = WINFUNCTYPE(c_int)
#NEARPROC = WINFUNCTYPE(c_int)
#PROC = WINFUNCTYPE(c_int)
#class HKEY__(Structure):
#    pass
#HKEY__._fields_ = [
#    ('unused', c_int),
#]
#PHKEY = POINTER(HKEY)
#class HACCEL__(Structure):
#    pass
#HACCEL__._fields_ = [
#    ('unused', c_int),
#]
#HBITMAP__._fields_ = [
#    ('unused', c_int),
#]
#class HBRUSH__(Structure):
#    pass
#HBRUSH__._fields_ = [
#    ('unused', c_int),
#]
#class HCOLORSPACE__(Structure):
#    pass
#HCOLORSPACE__._fields_ = [
#    ('unused', c_int),
#]
#class HDC__(Structure):
#    pass
#HDC__._fields_ = [
#    ('unused', c_int),
#]
#class HGLRC__(Structure):
#    pass
#HGLRC = POINTER(HGLRC__)
#HGLRC__._fields_ = [
#    ('unused', c_int),
#]
#class HDESK__(Structure):
#    pass
#HDESK__._fields_ = [
#    ('unused', c_int),
#]
#class HENHMETAFILE__(Structure):
#    pass
#HENHMETAFILE__._fields_ = [
#    ('unused', c_int),
#]
#class HFONT__(Structure):
#    pass
#HFONT__._fields_ = [
#    ('unused', c_int),
#]
#class HICON__(Structure):
#    pass
#HICON__._fields_ = [
#    ('unused', c_int),
#]
#class HMENU__(Structure):
#    pass
#HMENU__._fields_ = [
#    ('unused', c_int),
#]
#class HMETAFILE__(Structure):
#    pass
#HMETAFILE__._fields_ = [
#    ('unused', c_int),
#]
#HINSTANCE__._fields_ = [
#    ('unused', c_int),
#]
#class HPALETTE__(Structure):
#    pass
#HPALETTE__._fields_ = [
#    ('unused', c_int),
#]
#class HPEN__(Structure):
#    pass
#HPEN__._fields_ = [
#    ('unused', c_int),
#]
#class HRGN__(Structure):
#    pass
#HRGN__._fields_ = [
#    ('unused', c_int),
#]
#class HRSRC__(Structure):
#    pass
#HRSRC__._fields_ = [
#    ('unused', c_int),
#]
#class HSTR__(Structure):
#    pass
#HSTR__._fields_ = [
#    ('unused', c_int),
#]
#class HTASK__(Structure):
#    pass
#HTASK__._fields_ = [
#    ('unused', c_int),
#]
#class HWINSTA__(Structure):
#    pass
#HWINSTA__._fields_ = [
#    ('unused', c_int),
#]
#class HKL__(Structure):
#    pass
#HKL__._fields_ = [
#    ('unused', c_int),
#]
#class HMONITOR__(Structure):
#    pass
#HMONITOR__._fields_ = [
#    ('unused', c_int),
#]
#class HWINEVENTHOOK__(Structure):
#    pass
#HWINEVENTHOOK__._fields_ = [
#    ('unused', c_int),
#]
#HWINEVENTHOOK = POINTER(HWINEVENTHOOK__)
#class HUMPD__(Structure):
#    pass
#HUMPD = POINTER(HUMPD__)
#HUMPD__._fields_ = [
#    ('unused', c_int),
#]
#HFILE = c_int
#HCURSOR = HICON
#LPCOLORREF = POINTER(DWORD)
#NPRECT = POINTER(tagRECT)
#PRECT = POINTER(tagRECT)
#LPRECT = POINTER(tagRECT)
#LPCRECT = POINTER(RECT)
#PRECTL = POINTER(_RECTL)
#LPRECTL = POINTER(_RECTL)
#LPCRECTL = POINTER(RECTL)
#NPPOINT = POINTER(tagPOINT)
#PPOINT = POINTER(tagPOINT)
#LPPOINT = POINTER(tagPOINT)
#PPOINTL = POINTER(_POINTL)
#PSIZE = POINTER(tagSIZE)
#LPSIZE = POINTER(tagSIZE)
#LPSIZEL = POINTER(SIZE)
#PSIZEL = POINTER(SIZE)
#class tagPOINTS(Structure):
#    pass
#SHORT = c_short
#tagPOINTS._fields_ = [
#    ('x', SHORT),
#    ('y', SHORT),
#]
#POINTS = tagPOINTS
#LPPOINTS = POINTER(tagPOINTS)
#PPOINTS = POINTER(tagPOINTS)
#LPFILETIME = POINTER(_FILETIME)
#PFILETIME = POINTER(_FILETIME)
#class _DRAWPATRECT(Structure):
#    pass
#_DRAWPATRECT._fields_ = [
#    ('ptPosition', POINT),
#    ('ptSize', POINT),
#    ('wStyle', WORD),
#    ('wPattern', WORD),
#]
#PDRAWPATRECT = POINTER(_DRAWPATRECT)
#DRAWPATRECT = _DRAWPATRECT
#class _PSINJECTDATA(Structure):
#    pass
#_PSINJECTDATA._fields_ = [
#    ('DataBytes', DWORD),
#    ('InjectionPoint', WORD),
#    ('PageNumber', WORD),
#]
#PSINJECTDATA = _PSINJECTDATA
#PPSINJECTDATA = POINTER(_PSINJECTDATA)
#class _PSFEATURE_OUTPUT(Structure):
#    pass
#_PSFEATURE_OUTPUT._fields_ = [
#    ('bPageIndependent', BOOL),
#    ('bSetPageDevice', BOOL),
#]
#PPSFEATURE_OUTPUT = POINTER(_PSFEATURE_OUTPUT)
#PSFEATURE_OUTPUT = _PSFEATURE_OUTPUT
#class _PSFEATURE_CUSTPAPER(Structure):
#    pass
#_PSFEATURE_CUSTPAPER._fields_ = [
#    ('lOrientation', LONG),
#    ('lWidth', LONG),
#    ('lHeight', LONG),
#    ('lWidthOffset', LONG),
#    ('lHeightOffset', LONG),
#]
#PPSFEATURE_CUSTPAPER = POINTER(_PSFEATURE_CUSTPAPER)
#PSFEATURE_CUSTPAPER = _PSFEATURE_CUSTPAPER
#class tagXFORM(Structure):
#    pass
#tagXFORM._fields_ = [
#    ('eM11', FLOAT),
#    ('eM12', FLOAT),
#    ('eM21', FLOAT),
#    ('eM22', FLOAT),
#    ('eDx', FLOAT),
#    ('eDy', FLOAT),
#]
#LPXFORM = POINTER(tagXFORM)
#PXFORM = POINTER(tagXFORM)
#XFORM = tagXFORM
#class tagBITMAP(Structure):
#    pass
#tagBITMAP._fields_ = [
#    ('bmType', LONG),
#    ('bmWidth', LONG),
#    ('bmHeight', LONG),
#    ('bmWidthBytes', LONG),
#    ('bmPlanes', WORD),
#    ('bmBitsPixel', WORD),
#    ('bmBits', LPVOID),
#]
#LPBITMAP = POINTER(tagBITMAP)
#PBITMAP = POINTER(tagBITMAP)
#BITMAP = tagBITMAP
#NPBITMAP = POINTER(tagBITMAP)
#class tagRGBTRIPLE(Structure):
#    pass
#tagRGBTRIPLE._fields_ = [
#    ('rgbtBlue', BYTE),
#    ('rgbtGreen', BYTE),
#    ('rgbtRed', BYTE),
#]
#RGBTRIPLE = tagRGBTRIPLE
#class tagRGBQUAD(Structure):
#    pass
#tagRGBQUAD._fields_ = [
#    ('rgbBlue', BYTE),
#    ('rgbGreen', BYTE),
#    ('rgbRed', BYTE),
#    ('rgbReserved', BYTE),
#]
#RGBQUAD = tagRGBQUAD
#LPRGBQUAD = POINTER(RGBQUAD)
#LCSCSTYPE = LONG
#LCSGAMUTMATCH = LONG
#FXPT16DOT16 = c_long
#LPFXPT16DOT16 = POINTER(c_long)
#LPFXPT2DOT30 = POINTER(c_long)
#FXPT2DOT30 = c_long
#class tagCIEXYZ(Structure):
#    pass
#tagCIEXYZ._fields_ = [
#    ('ciexyzX', FXPT2DOT30),
#    ('ciexyzY', FXPT2DOT30),
#    ('ciexyzZ', FXPT2DOT30),
#]
#CIEXYZ = tagCIEXYZ
#LPCIEXYZ = POINTER(CIEXYZ)
#class tagICEXYZTRIPLE(Structure):
#    pass
#tagICEXYZTRIPLE._fields_ = [
#    ('ciexyzRed', CIEXYZ),
#    ('ciexyzGreen', CIEXYZ),
#    ('ciexyzBlue', CIEXYZ),
#]
#CIEXYZTRIPLE = tagICEXYZTRIPLE
#LPCIEXYZTRIPLE = POINTER(CIEXYZTRIPLE)
#class tagLOGCOLORSPACEA(Structure):
#    pass
#tagLOGCOLORSPACEA._fields_ = [
#    ('lcsSignature', DWORD),
#    ('lcsVersion', DWORD),
#    ('lcsSize', DWORD),
#    ('lcsCSType', LCSCSTYPE),
#    ('lcsIntent', LCSGAMUTMATCH),
#    ('lcsEndpoints', CIEXYZTRIPLE),
#    ('lcsGammaRed', DWORD),
#    ('lcsGammaGreen', DWORD),
#    ('lcsGammaBlue', DWORD),
#    ('lcsFilename', CHAR * 260),
#]
#LOGCOLORSPACEA = tagLOGCOLORSPACEA
#LPLOGCOLORSPACEA = POINTER(tagLOGCOLORSPACEA)
#class tagLOGCOLORSPACEW(Structure):
#    pass
#tagLOGCOLORSPACEW._fields_ = [
#    ('lcsSignature', DWORD),
#    ('lcsVersion', DWORD),
#    ('lcsSize', DWORD),
#    ('lcsCSType', LCSCSTYPE),
#    ('lcsIntent', LCSGAMUTMATCH),
#    ('lcsEndpoints', CIEXYZTRIPLE),
#    ('lcsGammaRed', DWORD),
#    ('lcsGammaGreen', DWORD),
#    ('lcsGammaBlue', DWORD),
#    ('lcsFilename', WCHAR * 260),
#]
#LPLOGCOLORSPACEW = POINTER(tagLOGCOLORSPACEW)
#LOGCOLORSPACEW = tagLOGCOLORSPACEW
#LOGCOLORSPACE = LOGCOLORSPACEA
#LPLOGCOLORSPACE = LPLOGCOLORSPACEA
#class tagBITMAPCOREHEADER(Structure):
#    pass
#tagBITMAPCOREHEADER._fields_ = [
#    ('bcSize', DWORD),
#    ('bcWidth', WORD),
#    ('bcHeight', WORD),
#    ('bcPlanes', WORD),
#    ('bcBitCount', WORD),
#]
#BITMAPCOREHEADER = tagBITMAPCOREHEADER
#LPBITMAPCOREHEADER = POINTER(tagBITMAPCOREHEADER)
#PBITMAPCOREHEADER = POINTER(tagBITMAPCOREHEADER)
#class tagBITMAPINFOHEADER(Structure):
#    pass
#tagBITMAPINFOHEADER._fields_ = [
#    ('biSize', DWORD),
#    ('biWidth', LONG),
#    ('biHeight', LONG),
#    ('biPlanes', WORD),
#    ('biBitCount', WORD),
#    ('biCompression', DWORD),
#    ('biSizeImage', DWORD),
#    ('biXPelsPerMeter', LONG),
#    ('biYPelsPerMeter', LONG),
#    ('biClrUsed', DWORD),
#    ('biClrImportant', DWORD),
#]
#PBITMAPINFOHEADER = POINTER(tagBITMAPINFOHEADER)
#BITMAPINFOHEADER = tagBITMAPINFOHEADER
#LPBITMAPINFOHEADER = POINTER(tagBITMAPINFOHEADER)
#class BITMAPV4HEADER(Structure):
#    pass
#BITMAPV4HEADER._fields_ = [
#    ('bV4Size', DWORD),
#    ('bV4Width', LONG),
#    ('bV4Height', LONG),
#    ('bV4Planes', WORD),
#    ('bV4BitCount', WORD),
#    ('bV4V4Compression', DWORD),
#    ('bV4SizeImage', DWORD),
#    ('bV4XPelsPerMeter', LONG),
#    ('bV4YPelsPerMeter', LONG),
#    ('bV4ClrUsed', DWORD),
#    ('bV4ClrImportant', DWORD),
#    ('bV4RedMask', DWORD),
#    ('bV4GreenMask', DWORD),
#    ('bV4BlueMask', DWORD),
#    ('bV4AlphaMask', DWORD),
#    ('bV4CSType', DWORD),
#    ('bV4Endpoints', CIEXYZTRIPLE),
#    ('bV4GammaRed', DWORD),
#    ('bV4GammaGreen', DWORD),
#    ('bV4GammaBlue', DWORD),
#]
#LPBITMAPV4HEADER = POINTER(BITMAPV4HEADER)
#PBITMAPV4HEADER = POINTER(BITMAPV4HEADER)
#class BITMAPV5HEADER(Structure):
#    pass
#LPBITMAPV5HEADER = POINTER(BITMAPV5HEADER)
#PBITMAPV5HEADER = POINTER(BITMAPV5HEADER)
#BITMAPV5HEADER._fields_ = [
#    ('bV5Size', DWORD),
#    ('bV5Width', LONG),
#    ('bV5Height', LONG),
#    ('bV5Planes', WORD),
#    ('bV5BitCount', WORD),
#    ('bV5Compression', DWORD),
#    ('bV5SizeImage', DWORD),
#    ('bV5XPelsPerMeter', LONG),
#    ('bV5YPelsPerMeter', LONG),
#    ('bV5ClrUsed', DWORD),
#    ('bV5ClrImportant', DWORD),
#    ('bV5RedMask', DWORD),
#    ('bV5GreenMask', DWORD),
#    ('bV5BlueMask', DWORD),
#    ('bV5AlphaMask', DWORD),
#    ('bV5CSType', DWORD),
#    ('bV5Endpoints', CIEXYZTRIPLE),
#    ('bV5GammaRed', DWORD),
#    ('bV5GammaGreen', DWORD),
#    ('bV5GammaBlue', DWORD),
#    ('bV5Intent', DWORD),
#    ('bV5ProfileData', DWORD),
#    ('bV5ProfileSize', DWORD),
#    ('bV5Reserved', DWORD),
#]
#class tagBITMAPINFO(Structure):
#    pass
#tagBITMAPINFO._fields_ = [
#    ('bmiHeader', BITMAPINFOHEADER),
#    ('bmiColors', RGBQUAD * 1),
#]
#PBITMAPINFO = POINTER(tagBITMAPINFO)
#LPBITMAPINFO = POINTER(tagBITMAPINFO)
#BITMAPINFO = tagBITMAPINFO
#class tagBITMAPCOREINFO(Structure):
#    pass
#tagBITMAPCOREINFO._fields_ = [
#    ('bmciHeader', BITMAPCOREHEADER),
#    ('bmciColors', RGBTRIPLE * 1),
#]
#PBITMAPCOREINFO = POINTER(tagBITMAPCOREINFO)
#BITMAPCOREINFO = tagBITMAPCOREINFO
#LPBITMAPCOREINFO = POINTER(tagBITMAPCOREINFO)
#class tagBITMAPFILEHEADER(Structure):
#    pass
#tagBITMAPFILEHEADER._pack_ = 2
#tagBITMAPFILEHEADER._fields_ = [
#    ('bfType', WORD),
#    ('bfSize', DWORD),
#    ('bfReserved1', WORD),
#    ('bfReserved2', WORD),
#    ('bfOffBits', DWORD),
#]
#LPBITMAPFILEHEADER = POINTER(tagBITMAPFILEHEADER)
#BITMAPFILEHEADER = tagBITMAPFILEHEADER
#PBITMAPFILEHEADER = POINTER(tagBITMAPFILEHEADER)
#class tagFONTSIGNATURE(Structure):
#    pass
#tagFONTSIGNATURE._fields_ = [
#    ('fsUsb', DWORD * 4),
#    ('fsCsb', DWORD * 2),
#]
#PFONTSIGNATURE = POINTER(tagFONTSIGNATURE)
#LPFONTSIGNATURE = POINTER(tagFONTSIGNATURE)
#FONTSIGNATURE = tagFONTSIGNATURE
#class tagCHARSETINFO(Structure):
#    pass
#tagCHARSETINFO._fields_ = [
#    ('ciCharset', UINT),
#    ('ciACP', UINT),
#    ('fs', FONTSIGNATURE),
#]
#PCHARSETINFO = POINTER(tagCHARSETINFO)
#NPCHARSETINFO = POINTER(tagCHARSETINFO)
#LPCHARSETINFO = POINTER(tagCHARSETINFO)
#CHARSETINFO = tagCHARSETINFO
#class tagLOCALESIGNATURE(Structure):
#    pass
#tagLOCALESIGNATURE._fields_ = [
#    ('lsUsb', DWORD * 4),
#    ('lsCsbDefault', DWORD * 2),
#    ('lsCsbSupported', DWORD * 2),
#]
#PLOCALESIGNATURE = POINTER(tagLOCALESIGNATURE)
#LPLOCALESIGNATURE = POINTER(tagLOCALESIGNATURE)
#LOCALESIGNATURE = tagLOCALESIGNATURE
#class tagHANDLETABLE(Structure):
#    pass
#tagHANDLETABLE._fields_ = [
#    ('objectHandle', HGDIOBJ * 1),
#]
#HANDLETABLE = tagHANDLETABLE
#LPHANDLETABLE = POINTER(tagHANDLETABLE)
#PHANDLETABLE = POINTER(tagHANDLETABLE)
#class tagMETARECORD(Structure):
#    pass
#tagMETARECORD._fields_ = [
#    ('rdSize', DWORD),
#    ('rdFunction', WORD),
#    ('rdParm', WORD * 1),
#]
#METARECORD = tagMETARECORD
#PMETARECORD = POINTER(tagMETARECORD)
#LPMETARECORD = POINTER(tagMETARECORD)
#class tagMETAFILEPICT(Structure):
#    pass
#tagMETAFILEPICT._fields_ = [
#    ('mm', LONG),
#    ('xExt', LONG),
#    ('yExt', LONG),
#    ('hMF', HMETAFILE),
#]
#METAFILEPICT = tagMETAFILEPICT
#LPMETAFILEPICT = POINTER(tagMETAFILEPICT)
#class tagMETAHEADER(Structure):
#    pass
#tagMETAHEADER._pack_ = 2
#tagMETAHEADER._fields_ = [
#    ('mtType', WORD),
#    ('mtHeaderSize', WORD),
#    ('mtVersion', WORD),
#    ('mtSize', DWORD),
#    ('mtNoObjects', WORD),
#    ('mtMaxRecord', DWORD),
#    ('mtNoParameters', WORD),
#]
#METAHEADER = tagMETAHEADER
#PMETAHEADER = POINTER(tagMETAHEADER)
#LPMETAHEADER = POINTER(tagMETAHEADER)
#class tagENHMETARECORD(Structure):
#    pass
#tagENHMETARECORD._fields_ = [
#    ('iType', DWORD),
#    ('nSize', DWORD),
#    ('dParm', DWORD * 1),
#]
#LPENHMETARECORD = POINTER(tagENHMETARECORD)
#PENHMETARECORD = POINTER(tagENHMETARECORD)
#ENHMETARECORD = tagENHMETARECORD
#class tagENHMETAHEADER(Structure):
#    pass
#tagENHMETAHEADER._fields_ = [
#    ('iType', DWORD),
#    ('nSize', DWORD),
#    ('rclBounds', RECTL),
#    ('rclFrame', RECTL),
#    ('dSignature', DWORD),
#    ('nVersion', DWORD),
#    ('nBytes', DWORD),
#    ('nRecords', DWORD),
#    ('nHandles', WORD),
#    ('sReserved', WORD),
#    ('nDescription', DWORD),
#    ('offDescription', DWORD),
#    ('nPalEntries', DWORD),
#    ('szlDevice', SIZEL),
#    ('szlMillimeters', SIZEL),
#    ('cbPixelFormat', DWORD),
#    ('offPixelFormat', DWORD),
#    ('bOpenGL', DWORD),
#    ('szlMicrometers', SIZEL),
#]
#PENHMETAHEADER = POINTER(tagENHMETAHEADER)
#ENHMETAHEADER = tagENHMETAHEADER
#LPENHMETAHEADER = POINTER(tagENHMETAHEADER)
#BCHAR = BYTE
#class tagTEXTMETRICA(Structure):
#    pass
#tagTEXTMETRICA._fields_ = [
#    ('tmHeight', LONG),
#    ('tmAscent', LONG),
#    ('tmDescent', LONG),
#    ('tmInternalLeading', LONG),
#    ('tmExternalLeading', LONG),
#    ('tmAveCharWidth', LONG),
#    ('tmMaxCharWidth', LONG),
#    ('tmWeight', LONG),
#    ('tmOverhang', LONG),
#    ('tmDigitizedAspectX', LONG),
#    ('tmDigitizedAspectY', LONG),
#    ('tmFirstChar', BYTE),
#    ('tmLastChar', BYTE),
#    ('tmDefaultChar', BYTE),
#    ('tmBreakChar', BYTE),
#    ('tmItalic', BYTE),
#    ('tmUnderlined', BYTE),
#    ('tmStruckOut', BYTE),
#    ('tmPitchAndFamily', BYTE),
#    ('tmCharSet', BYTE),
#]
#PTEXTMETRICA = POINTER(tagTEXTMETRICA)
#NPTEXTMETRICA = POINTER(tagTEXTMETRICA)
#LPTEXTMETRICA = POINTER(tagTEXTMETRICA)
#TEXTMETRICA = tagTEXTMETRICA
#class tagTEXTMETRICW(Structure):
#    pass
#tagTEXTMETRICW._fields_ = [
#    ('tmHeight', LONG),
#    ('tmAscent', LONG),
#    ('tmDescent', LONG),
#    ('tmInternalLeading', LONG),
#    ('tmExternalLeading', LONG),
#    ('tmAveCharWidth', LONG),
#    ('tmMaxCharWidth', LONG),
#    ('tmWeight', LONG),
#    ('tmOverhang', LONG),
#    ('tmDigitizedAspectX', LONG),
#    ('tmDigitizedAspectY', LONG),
#    ('tmFirstChar', WCHAR),
#    ('tmLastChar', WCHAR),
#    ('tmDefaultChar', WCHAR),
#    ('tmBreakChar', WCHAR),
#    ('tmItalic', BYTE),
#    ('tmUnderlined', BYTE),
#    ('tmStruckOut', BYTE),
#    ('tmPitchAndFamily', BYTE),
#    ('tmCharSet', BYTE),
#]
#TEXTMETRICW = tagTEXTMETRICW
#LPTEXTMETRICW = POINTER(tagTEXTMETRICW)
#NPTEXTMETRICW = POINTER(tagTEXTMETRICW)
#PTEXTMETRICW = POINTER(tagTEXTMETRICW)
#TEXTMETRIC = TEXTMETRICA
#PTEXTMETRIC = PTEXTMETRICA
#NPTEXTMETRIC = NPTEXTMETRICA
#LPTEXTMETRIC = LPTEXTMETRICA
#class tagNEWTEXTMETRICA(Structure):
#    pass
#tagNEWTEXTMETRICA._fields_ = [
#    ('tmHeight', LONG),
#    ('tmAscent', LONG),
#    ('tmDescent', LONG),
#    ('tmInternalLeading', LONG),
#    ('tmExternalLeading', LONG),
#    ('tmAveCharWidth', LONG),
#    ('tmMaxCharWidth', LONG),
#    ('tmWeight', LONG),
#    ('tmOverhang', LONG),
#    ('tmDigitizedAspectX', LONG),
#    ('tmDigitizedAspectY', LONG),
#    ('tmFirstChar', BYTE),
#    ('tmLastChar', BYTE),
#    ('tmDefaultChar', BYTE),
#    ('tmBreakChar', BYTE),
#    ('tmItalic', BYTE),
#    ('tmUnderlined', BYTE),
#    ('tmStruckOut', BYTE),
#    ('tmPitchAndFamily', BYTE),
#    ('tmCharSet', BYTE),
#    ('ntmFlags', DWORD),
#    ('ntmSizeEM', UINT),
#    ('ntmCellHeight', UINT),
#    ('ntmAvgWidth', UINT),
#]
#PNEWTEXTMETRICA = POINTER(tagNEWTEXTMETRICA)
#NPNEWTEXTMETRICA = POINTER(tagNEWTEXTMETRICA)
#NEWTEXTMETRICA = tagNEWTEXTMETRICA
#LPNEWTEXTMETRICA = POINTER(tagNEWTEXTMETRICA)
#class tagNEWTEXTMETRICW(Structure):
#    pass
#tagNEWTEXTMETRICW._fields_ = [
#    ('tmHeight', LONG),
#    ('tmAscent', LONG),
#    ('tmDescent', LONG),
#    ('tmInternalLeading', LONG),
#    ('tmExternalLeading', LONG),
#    ('tmAveCharWidth', LONG),
#    ('tmMaxCharWidth', LONG),
#    ('tmWeight', LONG),
#    ('tmOverhang', LONG),
#    ('tmDigitizedAspectX', LONG),
#    ('tmDigitizedAspectY', LONG),
#    ('tmFirstChar', WCHAR),
#    ('tmLastChar', WCHAR),
#    ('tmDefaultChar', WCHAR),
#    ('tmBreakChar', WCHAR),
#    ('tmItalic', BYTE),
#    ('tmUnderlined', BYTE),
#    ('tmStruckOut', BYTE),
#    ('tmPitchAndFamily', BYTE),
#    ('tmCharSet', BYTE),
#    ('ntmFlags', DWORD),
#    ('ntmSizeEM', UINT),
#    ('ntmCellHeight', UINT),
#    ('ntmAvgWidth', UINT),
#]
#PNEWTEXTMETRICW = POINTER(tagNEWTEXTMETRICW)
#NEWTEXTMETRICW = tagNEWTEXTMETRICW
#LPNEWTEXTMETRICW = POINTER(tagNEWTEXTMETRICW)
#NPNEWTEXTMETRICW = POINTER(tagNEWTEXTMETRICW)
#NEWTEXTMETRIC = NEWTEXTMETRICA
#PNEWTEXTMETRIC = PNEWTEXTMETRICA
#NPNEWTEXTMETRIC = NPNEWTEXTMETRICA
#LPNEWTEXTMETRIC = LPNEWTEXTMETRICA
#class tagNEWTEXTMETRICEXA(Structure):
#    pass
#tagNEWTEXTMETRICEXA._fields_ = [
#    ('ntmTm', NEWTEXTMETRICA),
#    ('ntmFontSig', FONTSIGNATURE),
#]
#NEWTEXTMETRICEXA = tagNEWTEXTMETRICEXA
#class tagNEWTEXTMETRICEXW(Structure):
#    pass
#tagNEWTEXTMETRICEXW._fields_ = [
#    ('ntmTm', NEWTEXTMETRICW),
#    ('ntmFontSig', FONTSIGNATURE),
#]
#NEWTEXTMETRICEXW = tagNEWTEXTMETRICEXW
#NEWTEXTMETRICEX = NEWTEXTMETRICEXA
#class tagPELARRAY(Structure):
#    pass
#tagPELARRAY._fields_ = [
#    ('paXCount', LONG),
#    ('paYCount', LONG),
#    ('paXExt', LONG),
#    ('paYExt', LONG),
#    ('paRGBs', BYTE),
#]
#LPPELARRAY = POINTER(tagPELARRAY)
#PELARRAY = tagPELARRAY
#PPELARRAY = POINTER(tagPELARRAY)
#NPPELARRAY = POINTER(tagPELARRAY)
#class tagLOGBRUSH(Structure):
#    pass
#tagLOGBRUSH._fields_ = [
#    ('lbStyle', UINT),
#    ('lbColor', COLORREF),
#    ('lbHatch', ULONG_PTR),
#]
#LOGBRUSH = tagLOGBRUSH
#LPLOGBRUSH = POINTER(tagLOGBRUSH)
#NPLOGBRUSH = POINTER(tagLOGBRUSH)
#PLOGBRUSH = POINTER(tagLOGBRUSH)
#class tagLOGBRUSH32(Structure):
#    pass
#tagLOGBRUSH32._fields_ = [
#    ('lbStyle', UINT),
#    ('lbColor', COLORREF),
#    ('lbHatch', ULONG),
#]
#PLOGBRUSH32 = POINTER(tagLOGBRUSH32)
#LOGBRUSH32 = tagLOGBRUSH32
#LPLOGBRUSH32 = POINTER(tagLOGBRUSH32)
#NPLOGBRUSH32 = POINTER(tagLOGBRUSH32)
#PATTERN = LOGBRUSH
#PPATTERN = POINTER(PATTERN)
#NPPATTERN = POINTER(PATTERN)
#LPPATTERN = POINTER(PATTERN)
#class tagLOGPEN(Structure):
#    pass
#tagLOGPEN._fields_ = [
#    ('lopnStyle', UINT),
#    ('lopnWidth', POINT),
#    ('lopnColor', COLORREF),
#]
#PLOGPEN = POINTER(tagLOGPEN)
#NPLOGPEN = POINTER(tagLOGPEN)
#LPLOGPEN = POINTER(tagLOGPEN)
#LOGPEN = tagLOGPEN
#class tagEXTLOGPEN(Structure):
#    pass
#tagEXTLOGPEN._fields_ = [
#    ('elpPenStyle', DWORD),
#    ('elpWidth', DWORD),
#    ('elpBrushStyle', UINT),
#    ('elpColor', COLORREF),
#    ('elpHatch', ULONG_PTR),
#    ('elpNumEntries', DWORD),
#    ('elpStyleEntry', DWORD * 1),
#]
#LPEXTLOGPEN = POINTER(tagEXTLOGPEN)
#PEXTLOGPEN = POINTER(tagEXTLOGPEN)
#NPEXTLOGPEN = POINTER(tagEXTLOGPEN)
#EXTLOGPEN = tagEXTLOGPEN
#class tagPALETTEENTRY(Structure):
#    pass
#tagPALETTEENTRY._fields_ = [
#    ('peRed', BYTE),
#    ('peGreen', BYTE),
#    ('peBlue', BYTE),
#    ('peFlags', BYTE),
#]
#PALETTEENTRY = tagPALETTEENTRY
#PPALETTEENTRY = POINTER(tagPALETTEENTRY)
#LPPALETTEENTRY = POINTER(tagPALETTEENTRY)
#class tagLOGPALETTE(Structure):
#    pass
#tagLOGPALETTE._fields_ = [
#    ('palVersion', WORD),
#    ('palNumEntries', WORD),
#    ('palPalEntry', PALETTEENTRY * 1),
#]
#LOGPALETTE = tagLOGPALETTE
#LPLOGPALETTE = POINTER(tagLOGPALETTE)
#PLOGPALETTE = POINTER(tagLOGPALETTE)
#NPLOGPALETTE = POINTER(tagLOGPALETTE)
#class tagLOGFONTA(Structure):
#    pass
#tagLOGFONTA._fields_ = [
#    ('lfHeight', LONG),
#    ('lfWidth', LONG),
#    ('lfEscapement', LONG),
#    ('lfOrientation', LONG),
#    ('lfWeight', LONG),
#    ('lfItalic', BYTE),
#    ('lfUnderline', BYTE),
#    ('lfStrikeOut', BYTE),
#    ('lfCharSet', BYTE),
#    ('lfOutPrecision', BYTE),
#    ('lfClipPrecision', BYTE),
#    ('lfQuality', BYTE),
#    ('lfPitchAndFamily', BYTE),
#    ('lfFaceName', CHAR * 32),
#]
#PLOGFONTA = POINTER(tagLOGFONTA)
#LOGFONTA = tagLOGFONTA
#NPLOGFONTA = POINTER(tagLOGFONTA)
#LPLOGFONTA = POINTER(tagLOGFONTA)
#class tagLOGFONTW(Structure):
#    pass
#tagLOGFONTW._fields_ = [
#    ('lfHeight', LONG),
#    ('lfWidth', LONG),
#    ('lfEscapement', LONG),
#    ('lfOrientation', LONG),
#    ('lfWeight', LONG),
#    ('lfItalic', BYTE),
#    ('lfUnderline', BYTE),
#    ('lfStrikeOut', BYTE),
#    ('lfCharSet', BYTE),
#    ('lfOutPrecision', BYTE),
#    ('lfClipPrecision', BYTE),
#    ('lfQuality', BYTE),
#    ('lfPitchAndFamily', BYTE),
#    ('lfFaceName', WCHAR * 32),
#]
#LOGFONTW = tagLOGFONTW
#LPLOGFONTW = POINTER(tagLOGFONTW)
#NPLOGFONTW = POINTER(tagLOGFONTW)
#PLOGFONTW = POINTER(tagLOGFONTW)
#LOGFONT = LOGFONTA
#PLOGFONT = PLOGFONTA
#NPLOGFONT = NPLOGFONTA
#LPLOGFONT = LPLOGFONTA
#class tagENUMLOGFONTA(Structure):
#    pass
#tagENUMLOGFONTA._fields_ = [
#    ('elfLogFont', LOGFONTA),
#    ('elfFullName', BYTE * 64),
#    ('elfStyle', BYTE * 32),
#]
#LPENUMLOGFONTA = POINTER(tagENUMLOGFONTA)
#ENUMLOGFONTA = tagENUMLOGFONTA
#class tagENUMLOGFONTW(Structure):
#    pass
#tagENUMLOGFONTW._fields_ = [
#    ('elfLogFont', LOGFONTW),
#    ('elfFullName', WCHAR * 64),
#    ('elfStyle', WCHAR * 32),
#]
#ENUMLOGFONTW = tagENUMLOGFONTW
#LPENUMLOGFONTW = POINTER(tagENUMLOGFONTW)
#ENUMLOGFONT = ENUMLOGFONTA
#LPENUMLOGFONT = LPENUMLOGFONTA
#class tagENUMLOGFONTEXA(Structure):
#    pass
#tagENUMLOGFONTEXA._fields_ = [
#    ('elfLogFont', LOGFONTA),
#    ('elfFullName', BYTE * 64),
#    ('elfStyle', BYTE * 32),
#    ('elfScript', BYTE * 32),
#]
#ENUMLOGFONTEXA = tagENUMLOGFONTEXA
#LPENUMLOGFONTEXA = POINTER(tagENUMLOGFONTEXA)
#class tagENUMLOGFONTEXW(Structure):
#    pass
#tagENUMLOGFONTEXW._fields_ = [
#    ('elfLogFont', LOGFONTW),
#    ('elfFullName', WCHAR * 64),
#    ('elfStyle', WCHAR * 32),
#    ('elfScript', WCHAR * 32),
#]
#ENUMLOGFONTEXW = tagENUMLOGFONTEXW
#LPENUMLOGFONTEXW = POINTER(tagENUMLOGFONTEXW)
#ENUMLOGFONTEX = ENUMLOGFONTEXA
#LPENUMLOGFONTEX = LPENUMLOGFONTEXA
#class tagPANOSE(Structure):
#    pass
#tagPANOSE._fields_ = [
#    ('bFamilyType', BYTE),
#    ('bSerifStyle', BYTE),
#    ('bWeight', BYTE),
#    ('bProportion', BYTE),
#    ('bContrast', BYTE),
#    ('bStrokeVariation', BYTE),
#    ('bArmStyle', BYTE),
#    ('bLetterform', BYTE),
#    ('bMidline', BYTE),
#    ('bXHeight', BYTE),
#]
#PANOSE = tagPANOSE
#LPPANOSE = POINTER(tagPANOSE)
#class tagEXTLOGFONTA(Structure):
#    pass
#tagEXTLOGFONTA._fields_ = [
#    ('elfLogFont', LOGFONTA),
#    ('elfFullName', BYTE * 64),
#    ('elfStyle', BYTE * 32),
#    ('elfVersion', DWORD),
#    ('elfStyleSize', DWORD),
#    ('elfMatch', DWORD),
#    ('elfReserved', DWORD),
#    ('elfVendorId', BYTE * 4),
#    ('elfCulture', DWORD),
#    ('elfPanose', PANOSE),
#]
#NPEXTLOGFONTA = POINTER(tagEXTLOGFONTA)
#LPEXTLOGFONTA = POINTER(tagEXTLOGFONTA)
#PEXTLOGFONTA = POINTER(tagEXTLOGFONTA)
#EXTLOGFONTA = tagEXTLOGFONTA
#class tagEXTLOGFONTW(Structure):
#    pass
#tagEXTLOGFONTW._fields_ = [
#    ('elfLogFont', LOGFONTW),
#    ('elfFullName', WCHAR * 64),
#    ('elfStyle', WCHAR * 32),
#    ('elfVersion', DWORD),
#    ('elfStyleSize', DWORD),
#    ('elfMatch', DWORD),
#    ('elfReserved', DWORD),
#    ('elfVendorId', BYTE * 4),
#    ('elfCulture', DWORD),
#    ('elfPanose', PANOSE),
#]
#EXTLOGFONTW = tagEXTLOGFONTW
#NPEXTLOGFONTW = POINTER(tagEXTLOGFONTW)
#PEXTLOGFONTW = POINTER(tagEXTLOGFONTW)
#LPEXTLOGFONTW = POINTER(tagEXTLOGFONTW)
#EXTLOGFONT = EXTLOGFONTA
#PEXTLOGFONT = PEXTLOGFONTA
#NPEXTLOGFONT = NPEXTLOGFONTA
#LPEXTLOGFONT = LPEXTLOGFONTA
#class _devicemodeA(Structure):
#    pass
#class N12_devicemodeA4DOLLAR_58E(Union):
#    pass
#class N12_devicemodeA4DOLLAR_584DOLLAR_59E(Structure):
#    pass
#N12_devicemodeA4DOLLAR_584DOLLAR_59E._fields_ = [
#    ('dmOrientation', c_short),
#    ('dmPaperSize', c_short),
#    ('dmPaperLength', c_short),
#    ('dmPaperWidth', c_short),
#    ('dmScale', c_short),
#    ('dmCopies', c_short),
#    ('dmDefaultSource', c_short),
#    ('dmPrintQuality', c_short),
#]
#class N12_devicemodeA4DOLLAR_584DOLLAR_60E(Structure):
#    pass
#N12_devicemodeA4DOLLAR_584DOLLAR_60E._fields_ = [
#    ('dmPosition', POINTL),
#    ('dmDisplayOrientation', DWORD),
#    ('dmDisplayFixedOutput', DWORD),
#]
#N12_devicemodeA4DOLLAR_58E._anonymous_ = ['_0', '_1']
#N12_devicemodeA4DOLLAR_58E._fields_ = [
#    ('_0', N12_devicemodeA4DOLLAR_584DOLLAR_59E),
#    ('_1', N12_devicemodeA4DOLLAR_584DOLLAR_60E),
#]
#class N12_devicemodeA4DOLLAR_61E(Union):
#    pass
#N12_devicemodeA4DOLLAR_61E._fields_ = [
#    ('dmDisplayFlags', DWORD),
#    ('dmNup', DWORD),
#]
#_devicemodeA._anonymous_ = ['_0', '_1']
#_devicemodeA._fields_ = [
#    ('dmDeviceName', BYTE * 32),
#    ('dmSpecVersion', WORD),
#    ('dmDriverVersion', WORD),
#    ('dmSize', WORD),
#    ('dmDriverExtra', WORD),
#    ('dmFields', DWORD),
#    ('_0', N12_devicemodeA4DOLLAR_58E),
#    ('dmColor', c_short),
#    ('dmDuplex', c_short),
#    ('dmYResolution', c_short),
#    ('dmTTOption', c_short),
#    ('dmCollate', c_short),
#    ('dmFormName', BYTE * 32),
#    ('dmLogPixels', WORD),
#    ('dmBitsPerPel', DWORD),
#    ('dmPelsWidth', DWORD),
#    ('dmPelsHeight', DWORD),
#    ('_1', N12_devicemodeA4DOLLAR_61E),
#    ('dmDisplayFrequency', DWORD),
#    ('dmICMMethod', DWORD),
#    ('dmICMIntent', DWORD),
#    ('dmMediaType', DWORD),
#    ('dmDitherType', DWORD),
#    ('dmReserved1', DWORD),
#    ('dmReserved2', DWORD),
#    ('dmPanningWidth', DWORD),
#    ('dmPanningHeight', DWORD),
#]
#NPDEVMODEA = POINTER(_devicemodeA)
#PDEVMODEA = POINTER(_devicemodeA)
#DEVMODEA = _devicemodeA
#LPDEVMODEA = POINTER(_devicemodeA)
#class _devicemodeW(Structure):
#    pass
#class N12_devicemodeW4DOLLAR_62E(Union):
#    pass
#class N12_devicemodeW4DOLLAR_624DOLLAR_63E(Structure):
#    pass
#N12_devicemodeW4DOLLAR_624DOLLAR_63E._fields_ = [
#    ('dmOrientation', c_short),
#    ('dmPaperSize', c_short),
#    ('dmPaperLength', c_short),
#    ('dmPaperWidth', c_short),
#    ('dmScale', c_short),
#    ('dmCopies', c_short),
#    ('dmDefaultSource', c_short),
#    ('dmPrintQuality', c_short),
#]
#class N12_devicemodeW4DOLLAR_624DOLLAR_64E(Structure):
#    pass
#N12_devicemodeW4DOLLAR_624DOLLAR_64E._fields_ = [
#    ('dmPosition', POINTL),
#    ('dmDisplayOrientation', DWORD),
#    ('dmDisplayFixedOutput', DWORD),
#]
#N12_devicemodeW4DOLLAR_62E._anonymous_ = ['_0', '_1']
#N12_devicemodeW4DOLLAR_62E._fields_ = [
#    ('_0', N12_devicemodeW4DOLLAR_624DOLLAR_63E),
#    ('_1', N12_devicemodeW4DOLLAR_624DOLLAR_64E),
#]
#class N12_devicemodeW4DOLLAR_65E(Union):
#    pass
#N12_devicemodeW4DOLLAR_65E._fields_ = [
#    ('dmDisplayFlags', DWORD),
#    ('dmNup', DWORD),
#]
#_devicemodeW._anonymous_ = ['_0', '_1']
#_devicemodeW._fields_ = [
#    ('dmDeviceName', WCHAR * 32),
#    ('dmSpecVersion', WORD),
#    ('dmDriverVersion', WORD),
#    ('dmSize', WORD),
#    ('dmDriverExtra', WORD),
#    ('dmFields', DWORD),
#    ('_0', N12_devicemodeW4DOLLAR_62E),
#    ('dmColor', c_short),
#    ('dmDuplex', c_short),
#    ('dmYResolution', c_short),
#    ('dmTTOption', c_short),
#    ('dmCollate', c_short),
#    ('dmFormName', WCHAR * 32),
#    ('dmLogPixels', WORD),
#    ('dmBitsPerPel', DWORD),
#    ('dmPelsWidth', DWORD),
#    ('dmPelsHeight', DWORD),
#    ('_1', N12_devicemodeW4DOLLAR_65E),
#    ('dmDisplayFrequency', DWORD),
#    ('dmICMMethod', DWORD),
#    ('dmICMIntent', DWORD),
#    ('dmMediaType', DWORD),
#    ('dmDitherType', DWORD),
#    ('dmReserved1', DWORD),
#    ('dmReserved2', DWORD),
#    ('dmPanningWidth', DWORD),
#    ('dmPanningHeight', DWORD),
#]
#DEVMODEW = _devicemodeW
#NPDEVMODEW = POINTER(_devicemodeW)
#LPDEVMODEW = POINTER(_devicemodeW)
#PDEVMODEW = POINTER(_devicemodeW)
#DEVMODE = DEVMODEA
#PDEVMODE = PDEVMODEA
#NPDEVMODE = NPDEVMODEA
#LPDEVMODE = LPDEVMODEA
#class _DISPLAY_DEVICEA(Structure):
#    pass
#_DISPLAY_DEVICEA._fields_ = [
#    ('cb', DWORD),
#    ('DeviceName', CHAR * 32),
#    ('DeviceString', CHAR * 128),
#    ('StateFlags', DWORD),
#    ('DeviceID', CHAR * 128),
#    ('DeviceKey', CHAR * 128),
#]
#DISPLAY_DEVICEA = _DISPLAY_DEVICEA
#LPDISPLAY_DEVICEA = POINTER(_DISPLAY_DEVICEA)
#PDISPLAY_DEVICEA = POINTER(_DISPLAY_DEVICEA)
#class _DISPLAY_DEVICEW(Structure):
#    pass
#_DISPLAY_DEVICEW._fields_ = [
#    ('cb', DWORD),
#    ('DeviceName', WCHAR * 32),
#    ('DeviceString', WCHAR * 128),
#    ('StateFlags', DWORD),
#    ('DeviceID', WCHAR * 128),
#    ('DeviceKey', WCHAR * 128),
#]
#PDISPLAY_DEVICEW = POINTER(_DISPLAY_DEVICEW)
#DISPLAY_DEVICEW = _DISPLAY_DEVICEW
#LPDISPLAY_DEVICEW = POINTER(_DISPLAY_DEVICEW)
#DISPLAY_DEVICE = DISPLAY_DEVICEA
#PDISPLAY_DEVICE = PDISPLAY_DEVICEA
#LPDISPLAY_DEVICE = LPDISPLAY_DEVICEA
#class _RGNDATAHEADER(Structure):
#    pass
#_RGNDATAHEADER._fields_ = [
#    ('dwSize', DWORD),
#    ('iType', DWORD),
#    ('nCount', DWORD),
#    ('nRgnSize', DWORD),
#    ('rcBound', RECT),
#]
#PRGNDATAHEADER = POINTER(_RGNDATAHEADER)
#RGNDATAHEADER = _RGNDATAHEADER
#class _RGNDATA(Structure):
#    pass
#_RGNDATA._fields_ = [
#    ('rdh', RGNDATAHEADER),
#    ('Buffer', c_char * 1),
#]
#PRGNDATA = POINTER(_RGNDATA)
#LPRGNDATA = POINTER(_RGNDATA)
#NPRGNDATA = POINTER(_RGNDATA)
#RGNDATA = _RGNDATA
#class _ABC(Structure):
#    pass
#_ABC._fields_ = [
#    ('abcA', c_int),
#    ('abcB', UINT),
#    ('abcC', c_int),
#]
#PABC = POINTER(_ABC)
#LPABC = POINTER(_ABC)
#NPABC = POINTER(_ABC)
#ABC = _ABC
#class _ABCFLOAT(Structure):
#    pass
#_ABCFLOAT._fields_ = [
#    ('abcfA', FLOAT),
#    ('abcfB', FLOAT),
#    ('abcfC', FLOAT),
#]
#LPABCFLOAT = POINTER(_ABCFLOAT)
#PABCFLOAT = POINTER(_ABCFLOAT)
#NPABCFLOAT = POINTER(_ABCFLOAT)
#ABCFLOAT = _ABCFLOAT
#class _OUTLINETEXTMETRICA(Structure):
#    pass
#PSTR = STRING
#_OUTLINETEXTMETRICA._fields_ = [
#    ('otmSize', UINT),
#    ('otmTextMetrics', TEXTMETRICA),
#    ('otmFiller', BYTE),
#    ('otmPanoseNumber', PANOSE),
#    ('otmfsSelection', UINT),
#    ('otmfsType', UINT),
#    ('otmsCharSlopeRise', c_int),
#    ('otmsCharSlopeRun', c_int),
#    ('otmItalicAngle', c_int),
#    ('otmEMSquare', UINT),
#    ('otmAscent', c_int),
#    ('otmDescent', c_int),
#    ('otmLineGap', UINT),
#    ('otmsCapEmHeight', UINT),
#    ('otmsXHeight', UINT),
#    ('otmrcFontBox', RECT),
#    ('otmMacAscent', c_int),
#    ('otmMacDescent', c_int),
#    ('otmMacLineGap', UINT),
#    ('otmusMinimumPPEM', UINT),
#    ('otmptSubscriptSize', POINT),
#    ('otmptSubscriptOffset', POINT),
#    ('otmptSuperscriptSize', POINT),
#    ('otmptSuperscriptOffset', POINT),
#    ('otmsStrikeoutSize', UINT),
#    ('otmsStrikeoutPosition', c_int),
#    ('otmsUnderscoreSize', c_int),
#    ('otmsUnderscorePosition', c_int),
#    ('otmpFamilyName', PSTR),
#    ('otmpFaceName', PSTR),
#    ('otmpStyleName', PSTR),
#    ('otmpFullName', PSTR),
#]
#NPOUTLINETEXTMETRICA = POINTER(_OUTLINETEXTMETRICA)
#POUTLINETEXTMETRICA = POINTER(_OUTLINETEXTMETRICA)
#OUTLINETEXTMETRICA = _OUTLINETEXTMETRICA
#LPOUTLINETEXTMETRICA = POINTER(_OUTLINETEXTMETRICA)
#class _OUTLINETEXTMETRICW(Structure):
#    pass
#_OUTLINETEXTMETRICW._fields_ = [
#    ('otmSize', UINT),
#    ('otmTextMetrics', TEXTMETRICW),
#    ('otmFiller', BYTE),
#    ('otmPanoseNumber', PANOSE),
#    ('otmfsSelection', UINT),
#    ('otmfsType', UINT),
#    ('otmsCharSlopeRise', c_int),
#    ('otmsCharSlopeRun', c_int),
#    ('otmItalicAngle', c_int),
#    ('otmEMSquare', UINT),
#    ('otmAscent', c_int),
#    ('otmDescent', c_int),
#    ('otmLineGap', UINT),
#    ('otmsCapEmHeight', UINT),
#    ('otmsXHeight', UINT),
#    ('otmrcFontBox', RECT),
#    ('otmMacAscent', c_int),
#    ('otmMacDescent', c_int),
#    ('otmMacLineGap', UINT),
#    ('otmusMinimumPPEM', UINT),
#    ('otmptSubscriptSize', POINT),
#    ('otmptSubscriptOffset', POINT),
#    ('otmptSuperscriptSize', POINT),
#    ('otmptSuperscriptOffset', POINT),
#    ('otmsStrikeoutSize', UINT),
#    ('otmsStrikeoutPosition', c_int),
#    ('otmsUnderscoreSize', c_int),
#    ('otmsUnderscorePosition', c_int),
#    ('otmpFamilyName', PSTR),
#    ('otmpFaceName', PSTR),
#    ('otmpStyleName', PSTR),
#    ('otmpFullName', PSTR),
#]
#NPOUTLINETEXTMETRICW = POINTER(_OUTLINETEXTMETRICW)
#OUTLINETEXTMETRICW = _OUTLINETEXTMETRICW
#POUTLINETEXTMETRICW = POINTER(_OUTLINETEXTMETRICW)
#LPOUTLINETEXTMETRICW = POINTER(_OUTLINETEXTMETRICW)
#OUTLINETEXTMETRIC = OUTLINETEXTMETRICA
#POUTLINETEXTMETRIC = POUTLINETEXTMETRICA
#NPOUTLINETEXTMETRIC = NPOUTLINETEXTMETRICA
#LPOUTLINETEXTMETRIC = LPOUTLINETEXTMETRICA
#class tagPOLYTEXTA(Structure):
#    pass
#tagPOLYTEXTA._fields_ = [
#    ('x', c_int),
#    ('y', c_int),
#    ('n', UINT),
#    ('lpstr', LPCSTR),
#    ('uiFlags', UINT),
#    ('rcl', RECT),
#    ('pdx', POINTER(c_int)),
#]
#POLYTEXTA = tagPOLYTEXTA
#LPPOLYTEXTA = POINTER(tagPOLYTEXTA)
#PPOLYTEXTA = POINTER(tagPOLYTEXTA)
#NPPOLYTEXTA = POINTER(tagPOLYTEXTA)
#class tagPOLYTEXTW(Structure):
#    pass
#tagPOLYTEXTW._fields_ = [
#    ('x', c_int),
#    ('y', c_int),
#    ('n', UINT),
#    ('lpstr', LPCWSTR),
#    ('uiFlags', UINT),
#    ('rcl', RECT),
#    ('pdx', POINTER(c_int)),
#]
#NPPOLYTEXTW = POINTER(tagPOLYTEXTW)
#LPPOLYTEXTW = POINTER(tagPOLYTEXTW)
#POLYTEXTW = tagPOLYTEXTW
#PPOLYTEXTW = POINTER(tagPOLYTEXTW)
#POLYTEXT = POLYTEXTA
#PPOLYTEXT = PPOLYTEXTA
#NPPOLYTEXT = NPPOLYTEXTA
#LPPOLYTEXT = LPPOLYTEXTA
#class _FIXED(Structure):
#    pass
#_FIXED._fields_ = [
#    ('fract', WORD),
#    ('value', c_short),
#]
#FIXED = _FIXED
#class _MAT2(Structure):
#    pass
#_MAT2._fields_ = [
#    ('eM11', FIXED),
#    ('eM12', FIXED),
#    ('eM21', FIXED),
#    ('eM22', FIXED),
#]
#LPMAT2 = POINTER(_MAT2)
#MAT2 = _MAT2
#class _GLYPHMETRICS(Structure):
#    pass
#_GLYPHMETRICS._fields_ = [
#    ('gmBlackBoxX', UINT),
#    ('gmBlackBoxY', UINT),
#    ('gmptGlyphOrigin', POINT),
#    ('gmCellIncX', c_short),
#    ('gmCellIncY', c_short),
#]
#LPGLYPHMETRICS = POINTER(_GLYPHMETRICS)
#GLYPHMETRICS = _GLYPHMETRICS
#class tagPOINTFX(Structure):
#    pass
#tagPOINTFX._fields_ = [
#    ('x', FIXED),
#    ('y', FIXED),
#]
#POINTFX = tagPOINTFX
#LPPOINTFX = POINTER(tagPOINTFX)
#class tagTTPOLYCURVE(Structure):
#    pass
#tagTTPOLYCURVE._fields_ = [
#    ('wType', WORD),
#    ('cpfx', WORD),
#    ('apfx', POINTFX * 1),
#]
#LPTTPOLYCURVE = POINTER(tagTTPOLYCURVE)
#TTPOLYCURVE = tagTTPOLYCURVE
#class tagTTPOLYGONHEADER(Structure):
#    pass
#tagTTPOLYGONHEADER._fields_ = [
#    ('cb', DWORD),
#    ('dwType', DWORD),
#    ('pfxStart', POINTFX),
#]
#TTPOLYGONHEADER = tagTTPOLYGONHEADER
#LPTTPOLYGONHEADER = POINTER(tagTTPOLYGONHEADER)
#class tagGCP_RESULTSA(Structure):
#    pass
#tagGCP_RESULTSA._fields_ = [
#    ('lStructSize', DWORD),
#    ('lpOutString', LPSTR),
#    ('lpOrder', POINTER(UINT)),
#    ('lpDx', POINTER(c_int)),
#    ('lpCaretPos', POINTER(c_int)),
#    ('lpClass', LPSTR),
#    ('lpGlyphs', LPWSTR),
#    ('nGlyphs', UINT),
#    ('nMaxFit', c_int),
#]
#LPGCP_RESULTSA = POINTER(tagGCP_RESULTSA)
#GCP_RESULTSA = tagGCP_RESULTSA
#class tagGCP_RESULTSW(Structure):
#    pass
#tagGCP_RESULTSW._fields_ = [
#    ('lStructSize', DWORD),
#    ('lpOutString', LPWSTR),
#    ('lpOrder', POINTER(UINT)),
#    ('lpDx', POINTER(c_int)),
#    ('lpCaretPos', POINTER(c_int)),
#    ('lpClass', LPSTR),
#    ('lpGlyphs', LPWSTR),
#    ('nGlyphs', UINT),
#    ('nMaxFit', c_int),
#]
#GCP_RESULTSW = tagGCP_RESULTSW
#LPGCP_RESULTSW = POINTER(tagGCP_RESULTSW)
#GCP_RESULTS = GCP_RESULTSA
#LPGCP_RESULTS = LPGCP_RESULTSA
#class _RASTERIZER_STATUS(Structure):
#    pass
#_RASTERIZER_STATUS._fields_ = [
#    ('nSize', c_short),
#    ('wFlags', c_short),
#    ('nLanguageID', c_short),
#]
#LPRASTERIZER_STATUS = POINTER(_RASTERIZER_STATUS)
#RASTERIZER_STATUS = _RASTERIZER_STATUS
#class tagPIXELFORMATDESCRIPTOR(Structure):
#    pass
#tagPIXELFORMATDESCRIPTOR._fields_ = [
#    ('nSize', WORD),
#    ('nVersion', WORD),
#    ('dwFlags', DWORD),
#    ('iPixelType', BYTE),
#    ('cColorBits', BYTE),
#    ('cRedBits', BYTE),
#    ('cRedShift', BYTE),
#    ('cGreenBits', BYTE),
#    ('cGreenShift', BYTE),
#    ('cBlueBits', BYTE),
#    ('cBlueShift', BYTE),
#    ('cAlphaBits', BYTE),
#    ('cAlphaShift', BYTE),
#    ('cAccumBits', BYTE),
#    ('cAccumRedBits', BYTE),
#    ('cAccumGreenBits', BYTE),
#    ('cAccumBlueBits', BYTE),
#    ('cAccumAlphaBits', BYTE),
#    ('cDepthBits', BYTE),
#    ('cStencilBits', BYTE),
#    ('cAuxBuffers', BYTE),
#    ('iLayerType', BYTE),
#    ('bReserved', BYTE),
#    ('dwLayerMask', DWORD),
#    ('dwVisibleMask', DWORD),
#    ('dwDamageMask', DWORD),
#]
#PPIXELFORMATDESCRIPTOR = POINTER(tagPIXELFORMATDESCRIPTOR)
#PIXELFORMATDESCRIPTOR = tagPIXELFORMATDESCRIPTOR
#LPPIXELFORMATDESCRIPTOR = POINTER(tagPIXELFORMATDESCRIPTOR)
#OLDFONTENUMPROCA = WINFUNCTYPE(c_int, POINTER(LOGFONTA), POINTER(TEXTMETRICA), c_ulong, c_long)
#OLDFONTENUMPROCW = WINFUNCTYPE(c_int, POINTER(LOGFONTW), POINTER(TEXTMETRICW), c_ulong, c_long)
#FONTENUMPROCA = OLDFONTENUMPROCA
#FONTENUMPROCW = OLDFONTENUMPROCW
#FONTENUMPROC = FONTENUMPROCA
#GOBJENUMPROC = WINFUNCTYPE(c_int, c_void_p, c_long)
#LINEDDAPROC = WINFUNCTYPE(None, c_int, c_int, c_long)
#LPFNDEVMODE = WINFUNCTYPE(UINT, POINTER(HWND__), POINTER(HINSTANCE__), POINTER(_devicemodeA), STRING, STRING, POINTER(_devicemodeA), STRING, c_uint)
#LPFNDEVCAPS = WINFUNCTYPE(DWORD, STRING, STRING, c_uint, STRING, POINTER(_devicemodeA))
#COLOR16 = USHORT
#class _TRIVERTEX(Structure):
#    pass
#_TRIVERTEX._fields_ = [
#    ('x', LONG),
#    ('y', LONG),
#    ('Red', COLOR16),
#    ('Green', COLOR16),
#    ('Blue', COLOR16),
#    ('Alpha', COLOR16),
#]
#PTRIVERTEX = POINTER(_TRIVERTEX)
#TRIVERTEX = _TRIVERTEX
#LPTRIVERTEX = POINTER(_TRIVERTEX)
#class _GRADIENT_TRIANGLE(Structure):
#    pass
#_GRADIENT_TRIANGLE._fields_ = [
#    ('Vertex1', ULONG),
#    ('Vertex2', ULONG),
#    ('Vertex3', ULONG),
#]
#LPGRADIENT_TRIANGLE = POINTER(_GRADIENT_TRIANGLE)
#GRADIENT_TRIANGLE = _GRADIENT_TRIANGLE
#PGRADIENT_TRIANGLE = POINTER(_GRADIENT_TRIANGLE)
#class _GRADIENT_RECT(Structure):
#    pass
#_GRADIENT_RECT._fields_ = [
#    ('UpperLeft', ULONG),
#    ('LowerRight', ULONG),
#]
#PGRADIENT_RECT = POINTER(_GRADIENT_RECT)
#GRADIENT_RECT = _GRADIENT_RECT
#LPGRADIENT_RECT = POINTER(_GRADIENT_RECT)
#class _BLENDFUNCTION(Structure):
#    pass
#_BLENDFUNCTION._fields_ = [
#    ('BlendOp', BYTE),
#    ('BlendFlags', BYTE),
#    ('SourceConstantAlpha', BYTE),
#    ('AlphaFormat', BYTE),
#]
#BLENDFUNCTION = _BLENDFUNCTION
#PBLENDFUNCTION = POINTER(_BLENDFUNCTION)
#MFENUMPROC = WINFUNCTYPE(c_int, POINTER(HDC__), POINTER(HANDLETABLE), POINTER(METARECORD), c_int, c_long)
#ENHMFENUMPROC = WINFUNCTYPE(c_int, POINTER(HDC__), POINTER(HANDLETABLE), POINTER(ENHMETARECORD), c_int, c_long)
#class tagDIBSECTION(Structure):
#    pass
#tagDIBSECTION._fields_ = [
#    ('dsBm', BITMAP),
#    ('dsBmih', BITMAPINFOHEADER),
#    ('dsBitfields', DWORD * 3),
#    ('dshSection', HANDLE),
#    ('dsOffset', DWORD),
#]
#DIBSECTION = tagDIBSECTION
#PDIBSECTION = POINTER(tagDIBSECTION)
#LPDIBSECTION = POINTER(tagDIBSECTION)
#class tagCOLORADJUSTMENT(Structure):
#    pass
#tagCOLORADJUSTMENT._fields_ = [
#    ('caSize', WORD),
#    ('caFlags', WORD),
#    ('caIlluminantIndex', WORD),
#    ('caRedGamma', WORD),
#    ('caGreenGamma', WORD),
#    ('caBlueGamma', WORD),
#    ('caReferenceBlack', WORD),
#    ('caReferenceWhite', WORD),
#    ('caContrast', SHORT),
#    ('caBrightness', SHORT),
#    ('caColorfulness', SHORT),
#    ('caRedGreenTint', SHORT),
#]
#PCOLORADJUSTMENT = POINTER(tagCOLORADJUSTMENT)
#LPCOLORADJUSTMENT = POINTER(tagCOLORADJUSTMENT)
#COLORADJUSTMENT = tagCOLORADJUSTMENT
#ABORTPROC = WINFUNCTYPE(BOOL, POINTER(HDC__), c_int)
#class _DOCINFOA(Structure):
#    pass
#_DOCINFOA._fields_ = [
#    ('cbSize', c_int),
#    ('lpszDocName', LPCSTR),
#    ('lpszOutput', LPCSTR),
#    ('lpszDatatype', LPCSTR),
#    ('fwType', DWORD),
#]
#LPDOCINFOA = POINTER(_DOCINFOA)
#DOCINFOA = _DOCINFOA
#class _DOCINFOW(Structure):
#    pass
#_DOCINFOW._fields_ = [
#    ('cbSize', c_int),
#    ('lpszDocName', LPCWSTR),
#    ('lpszOutput', LPCWSTR),
#    ('lpszDatatype', LPCWSTR),
#    ('fwType', DWORD),
#]
#LPDOCINFOW = POINTER(_DOCINFOW)
#DOCINFOW = _DOCINFOW
#DOCINFO = DOCINFOA
#LPDOCINFO = LPDOCINFOA
#class tagKERNINGPAIR(Structure):
#    pass
#tagKERNINGPAIR._fields_ = [
#    ('wFirst', WORD),
#    ('wSecond', WORD),
#    ('iKernAmount', c_int),
#]
#LPKERNINGPAIR = POINTER(tagKERNINGPAIR)
#KERNINGPAIR = tagKERNINGPAIR
#ICMENUMPROCA = WINFUNCTYPE(c_int, STRING, c_long)
#ICMENUMPROCW = WINFUNCTYPE(c_int, WSTRING, c_long)
#class tagEMR(Structure):
#    pass
#tagEMR._fields_ = [
#    ('iType', DWORD),
#    ('nSize', DWORD),
#]
#PEMR = POINTER(tagEMR)
#EMR = tagEMR
#class tagEMRTEXT(Structure):
#    pass
#tagEMRTEXT._fields_ = [
#    ('ptlReference', POINTL),
#    ('nChars', DWORD),
#    ('offString', DWORD),
#    ('fOptions', DWORD),
#    ('rcl', RECTL),
#    ('offDx', DWORD),
#]
#EMRTEXT = tagEMRTEXT
#PEMRTEXT = POINTER(tagEMRTEXT)
#class tagABORTPATH(Structure):
#    pass
#tagABORTPATH._fields_ = [
#    ('emr', EMR),
#]
#EMRABORTPATH = tagABORTPATH
#PEMRABORTPATH = POINTER(tagABORTPATH)
#PEMRBEGINPATH = POINTER(tagABORTPATH)
#EMRBEGINPATH = tagABORTPATH
#PEMRENDPATH = POINTER(tagABORTPATH)
#EMRENDPATH = tagABORTPATH
#EMRCLOSEFIGURE = tagABORTPATH
#PEMRCLOSEFIGURE = POINTER(tagABORTPATH)
#PEMRFLATTENPATH = POINTER(tagABORTPATH)
#EMRFLATTENPATH = tagABORTPATH
#PEMRWIDENPATH = POINTER(tagABORTPATH)
#EMRWIDENPATH = tagABORTPATH
#PEMRSETMETARGN = POINTER(tagABORTPATH)
#EMRSETMETARGN = tagABORTPATH
#PEMRSAVEDC = POINTER(tagABORTPATH)
#EMRSAVEDC = tagABORTPATH
#PEMRREALIZEPALETTE = POINTER(tagABORTPATH)
#EMRREALIZEPALETTE = tagABORTPATH
#class tagEMRSELECTCLIPPATH(Structure):
#    pass
#tagEMRSELECTCLIPPATH._fields_ = [
#    ('emr', EMR),
#    ('iMode', DWORD),
#]
#PEMRSELECTCLIPPATH = POINTER(tagEMRSELECTCLIPPATH)
#EMRSELECTCLIPPATH = tagEMRSELECTCLIPPATH
#PEMRSETBKMODE = POINTER(tagEMRSELECTCLIPPATH)
#EMRSETBKMODE = tagEMRSELECTCLIPPATH
#PEMRSETMAPMODE = POINTER(tagEMRSELECTCLIPPATH)
#EMRSETMAPMODE = tagEMRSELECTCLIPPATH
#PEMRSETLAYOUT = POINTER(tagEMRSELECTCLIPPATH)
#EMRSETLAYOUT = tagEMRSELECTCLIPPATH
#EMRSETPOLYFILLMODE = tagEMRSELECTCLIPPATH
#PEMRSETPOLYFILLMODE = POINTER(tagEMRSELECTCLIPPATH)
#PEMRSETROP2 = POINTER(tagEMRSELECTCLIPPATH)
#EMRSETROP2 = tagEMRSELECTCLIPPATH
#PEMRSETSTRETCHBLTMODE = POINTER(tagEMRSELECTCLIPPATH)
#EMRSETSTRETCHBLTMODE = tagEMRSELECTCLIPPATH
#PEMRSETICMMODE = POINTER(tagEMRSELECTCLIPPATH)
#EMRSETICMMODE = tagEMRSELECTCLIPPATH
#PEMRSETTEXTALIGN = POINTER(tagEMRSELECTCLIPPATH)
#EMRSETTEXTALIGN = tagEMRSELECTCLIPPATH
#class tagEMRSETMITERLIMIT(Structure):
#    pass
#tagEMRSETMITERLIMIT._fields_ = [
#    ('emr', EMR),
#    ('eMiterLimit', FLOAT),
#]
#EMRSETMITERLIMIT = tagEMRSETMITERLIMIT
#PEMRSETMITERLIMIT = POINTER(tagEMRSETMITERLIMIT)
#class tagEMRRESTOREDC(Structure):
#    pass
#tagEMRRESTOREDC._fields_ = [
#    ('emr', EMR),
#    ('iRelative', LONG),
#]
#EMRRESTOREDC = tagEMRRESTOREDC
#PEMRRESTOREDC = POINTER(tagEMRRESTOREDC)
#class tagEMRSETARCDIRECTION(Structure):
#    pass
#tagEMRSETARCDIRECTION._fields_ = [
#    ('emr', EMR),
#    ('iArcDirection', DWORD),
#]
#EMRSETARCDIRECTION = tagEMRSETARCDIRECTION
#PEMRSETARCDIRECTION = POINTER(tagEMRSETARCDIRECTION)
#class tagEMRSETMAPPERFLAGS(Structure):
#    pass
#tagEMRSETMAPPERFLAGS._fields_ = [
#    ('emr', EMR),
#    ('dwFlags', DWORD),
#]
#EMRSETMAPPERFLAGS = tagEMRSETMAPPERFLAGS
#PEMRSETMAPPERFLAGS = POINTER(tagEMRSETMAPPERFLAGS)
#class tagEMRSETTEXTCOLOR(Structure):
#    pass
#tagEMRSETTEXTCOLOR._fields_ = [
#    ('emr', EMR),
#    ('crColor', COLORREF),
#]
#PEMRSETBKCOLOR = POINTER(tagEMRSETTEXTCOLOR)
#EMRSETBKCOLOR = tagEMRSETTEXTCOLOR
#PEMRSETTEXTCOLOR = POINTER(tagEMRSETTEXTCOLOR)
#EMRSETTEXTCOLOR = tagEMRSETTEXTCOLOR
#class tagEMRSELECTOBJECT(Structure):
#    pass
#tagEMRSELECTOBJECT._fields_ = [
#    ('emr', EMR),
#    ('ihObject', DWORD),
#]
#PEMRSELECTOBJECT = POINTER(tagEMRSELECTOBJECT)
#EMRSELECTOBJECT = tagEMRSELECTOBJECT
#PEMRDELETEOBJECT = POINTER(tagEMRSELECTOBJECT)
#EMRDELETEOBJECT = tagEMRSELECTOBJECT
#class tagEMRSELECTPALETTE(Structure):
#    pass
#tagEMRSELECTPALETTE._fields_ = [
#    ('emr', EMR),
#    ('ihPal', DWORD),
#]
#EMRSELECTPALETTE = tagEMRSELECTPALETTE
#PEMRSELECTPALETTE = POINTER(tagEMRSELECTPALETTE)
#class tagEMRRESIZEPALETTE(Structure):
#    pass
#tagEMRRESIZEPALETTE._fields_ = [
#    ('emr', EMR),
#    ('ihPal', DWORD),
#    ('cEntries', DWORD),
#]
#PEMRRESIZEPALETTE = POINTER(tagEMRRESIZEPALETTE)
#EMRRESIZEPALETTE = tagEMRRESIZEPALETTE
#class tagEMRSETPALETTEENTRIES(Structure):
#    pass
#tagEMRSETPALETTEENTRIES._fields_ = [
#    ('emr', EMR),
#    ('ihPal', DWORD),
#    ('iStart', DWORD),
#    ('cEntries', DWORD),
#    ('aPalEntries', PALETTEENTRY * 1),
#]
#PEMRSETPALETTEENTRIES = POINTER(tagEMRSETPALETTEENTRIES)
#EMRSETPALETTEENTRIES = tagEMRSETPALETTEENTRIES
#class tagEMRSETCOLORADJUSTMENT(Structure):
#    pass
#tagEMRSETCOLORADJUSTMENT._fields_ = [
#    ('emr', EMR),
#    ('ColorAdjustment', COLORADJUSTMENT),
#]
#PEMRSETCOLORADJUSTMENT = POINTER(tagEMRSETCOLORADJUSTMENT)
#EMRSETCOLORADJUSTMENT = tagEMRSETCOLORADJUSTMENT
#class tagEMRGDICOMMENT(Structure):
#    pass
#tagEMRGDICOMMENT._fields_ = [
#    ('emr', EMR),
#    ('cbData', DWORD),
#    ('Data', BYTE * 1),
#]
#EMRGDICOMMENT = tagEMRGDICOMMENT
#PEMRGDICOMMENT = POINTER(tagEMRGDICOMMENT)
#class tagEMREOF(Structure):
#    pass
#tagEMREOF._fields_ = [
#    ('emr', EMR),
#    ('nPalEntries', DWORD),
#    ('offPalEntries', DWORD),
#    ('nSizeLast', DWORD),
#]
#EMREOF = tagEMREOF
#PEMREOF = POINTER(tagEMREOF)
#class tagEMRLINETO(Structure):
#    pass
#tagEMRLINETO._fields_ = [
#    ('emr', EMR),
#    ('ptl', POINTL),
#]
#PEMRLINETO = POINTER(tagEMRLINETO)
#EMRLINETO = tagEMRLINETO
#EMRMOVETOEX = tagEMRLINETO
#PEMRMOVETOEX = POINTER(tagEMRLINETO)
#class tagEMROFFSETCLIPRGN(Structure):
#    pass
#tagEMROFFSETCLIPRGN._fields_ = [
#    ('emr', EMR),
#    ('ptlOffset', POINTL),
#]
#EMROFFSETCLIPRGN = tagEMROFFSETCLIPRGN
#PEMROFFSETCLIPRGN = POINTER(tagEMROFFSETCLIPRGN)
#class tagEMRFILLPATH(Structure):
#    pass
#tagEMRFILLPATH._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#]
#PEMRFILLPATH = POINTER(tagEMRFILLPATH)
#EMRFILLPATH = tagEMRFILLPATH
#EMRSTROKEANDFILLPATH = tagEMRFILLPATH
#PEMRSTROKEANDFILLPATH = POINTER(tagEMRFILLPATH)
#PEMRSTROKEPATH = POINTER(tagEMRFILLPATH)
#EMRSTROKEPATH = tagEMRFILLPATH
#class tagEMREXCLUDECLIPRECT(Structure):
#    pass
#tagEMREXCLUDECLIPRECT._fields_ = [
#    ('emr', EMR),
#    ('rclClip', RECTL),
#]
#PEMREXCLUDECLIPRECT = POINTER(tagEMREXCLUDECLIPRECT)
#EMREXCLUDECLIPRECT = tagEMREXCLUDECLIPRECT
#PEMRINTERSECTCLIPRECT = POINTER(tagEMREXCLUDECLIPRECT)
#EMRINTERSECTCLIPRECT = tagEMREXCLUDECLIPRECT
#class tagEMRSETVIEWPORTORGEX(Structure):
#    pass
#tagEMRSETVIEWPORTORGEX._fields_ = [
#    ('emr', EMR),
#    ('ptlOrigin', POINTL),
#]
#PEMRSETVIEWPORTORGEX = POINTER(tagEMRSETVIEWPORTORGEX)
#EMRSETVIEWPORTORGEX = tagEMRSETVIEWPORTORGEX
#PEMRSETWINDOWORGEX = POINTER(tagEMRSETVIEWPORTORGEX)
#EMRSETWINDOWORGEX = tagEMRSETVIEWPORTORGEX
#EMRSETBRUSHORGEX = tagEMRSETVIEWPORTORGEX
#PEMRSETBRUSHORGEX = POINTER(tagEMRSETVIEWPORTORGEX)
#class tagEMRSETVIEWPORTEXTEX(Structure):
#    pass
#tagEMRSETVIEWPORTEXTEX._fields_ = [
#    ('emr', EMR),
#    ('szlExtent', SIZEL),
#]
#PEMRSETVIEWPORTEXTEX = POINTER(tagEMRSETVIEWPORTEXTEX)
#EMRSETVIEWPORTEXTEX = tagEMRSETVIEWPORTEXTEX
#EMRSETWINDOWEXTEX = tagEMRSETVIEWPORTEXTEX
#PEMRSETWINDOWEXTEX = POINTER(tagEMRSETVIEWPORTEXTEX)
#class tagEMRSCALEVIEWPORTEXTEX(Structure):
#    pass
#tagEMRSCALEVIEWPORTEXTEX._fields_ = [
#    ('emr', EMR),
#    ('xNum', LONG),
#    ('xDenom', LONG),
#    ('yNum', LONG),
#    ('yDenom', LONG),
#]
#PEMRSCALEVIEWPORTEXTEX = POINTER(tagEMRSCALEVIEWPORTEXTEX)
#EMRSCALEVIEWPORTEXTEX = tagEMRSCALEVIEWPORTEXTEX
#PEMRSCALEWINDOWEXTEX = POINTER(tagEMRSCALEVIEWPORTEXTEX)
#EMRSCALEWINDOWEXTEX = tagEMRSCALEVIEWPORTEXTEX
#class tagEMRSETWORLDTRANSFORM(Structure):
#    pass
#tagEMRSETWORLDTRANSFORM._fields_ = [
#    ('emr', EMR),
#    ('xform', XFORM),
#]
#EMRSETWORLDTRANSFORM = tagEMRSETWORLDTRANSFORM
#PEMRSETWORLDTRANSFORM = POINTER(tagEMRSETWORLDTRANSFORM)
#class tagEMRMODIFYWORLDTRANSFORM(Structure):
#    pass
#tagEMRMODIFYWORLDTRANSFORM._fields_ = [
#    ('emr', EMR),
#    ('xform', XFORM),
#    ('iMode', DWORD),
#]
#PEMRMODIFYWORLDTRANSFORM = POINTER(tagEMRMODIFYWORLDTRANSFORM)
#EMRMODIFYWORLDTRANSFORM = tagEMRMODIFYWORLDTRANSFORM
#class tagEMRSETPIXELV(Structure):
#    pass
#tagEMRSETPIXELV._fields_ = [
#    ('emr', EMR),
#    ('ptlPixel', POINTL),
#    ('crColor', COLORREF),
#]
#EMRSETPIXELV = tagEMRSETPIXELV
#PEMRSETPIXELV = POINTER(tagEMRSETPIXELV)
#class tagEMREXTFLOODFILL(Structure):
#    pass
#tagEMREXTFLOODFILL._fields_ = [
#    ('emr', EMR),
#    ('ptlStart', POINTL),
#    ('crColor', COLORREF),
#    ('iMode', DWORD),
#]
#EMREXTFLOODFILL = tagEMREXTFLOODFILL
#PEMREXTFLOODFILL = POINTER(tagEMREXTFLOODFILL)
#class tagEMRELLIPSE(Structure):
#    pass
#tagEMRELLIPSE._fields_ = [
#    ('emr', EMR),
#    ('rclBox', RECTL),
#]
#PEMRELLIPSE = POINTER(tagEMRELLIPSE)
#EMRELLIPSE = tagEMRELLIPSE
#PEMRRECTANGLE = POINTER(tagEMRELLIPSE)
#EMRRECTANGLE = tagEMRELLIPSE
#class tagEMRROUNDRECT(Structure):
#    pass
#tagEMRROUNDRECT._fields_ = [
#    ('emr', EMR),
#    ('rclBox', RECTL),
#    ('szlCorner', SIZEL),
#]
#EMRROUNDRECT = tagEMRROUNDRECT
#PEMRROUNDRECT = POINTER(tagEMRROUNDRECT)
#class tagEMRARC(Structure):
#    pass
#tagEMRARC._fields_ = [
#    ('emr', EMR),
#    ('rclBox', RECTL),
#    ('ptlStart', POINTL),
#    ('ptlEnd', POINTL),
#]
#EMRARC = tagEMRARC
#PEMRARC = POINTER(tagEMRARC)
#PEMRARCTO = POINTER(tagEMRARC)
#EMRARCTO = tagEMRARC
#EMRCHORD = tagEMRARC
#PEMRCHORD = POINTER(tagEMRARC)
#PEMRPIE = POINTER(tagEMRARC)
#EMRPIE = tagEMRARC
#class tagEMRANGLEARC(Structure):
#    pass
#tagEMRANGLEARC._fields_ = [
#    ('emr', EMR),
#    ('ptlCenter', POINTL),
#    ('nRadius', DWORD),
#    ('eStartAngle', FLOAT),
#    ('eSweepAngle', FLOAT),
#]
#PEMRANGLEARC = POINTER(tagEMRANGLEARC)
#EMRANGLEARC = tagEMRANGLEARC
#class tagEMRPOLYLINE(Structure):
#    pass
#tagEMRPOLYLINE._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cptl', DWORD),
#    ('aptl', POINTL * 1),
#]
#PEMRPOLYLINE = POINTER(tagEMRPOLYLINE)
#EMRPOLYLINE = tagEMRPOLYLINE
#PEMRPOLYBEZIER = POINTER(tagEMRPOLYLINE)
#EMRPOLYBEZIER = tagEMRPOLYLINE
#PEMRPOLYGON = POINTER(tagEMRPOLYLINE)
#EMRPOLYGON = tagEMRPOLYLINE
#EMRPOLYBEZIERTO = tagEMRPOLYLINE
#PEMRPOLYBEZIERTO = POINTER(tagEMRPOLYLINE)
#PEMRPOLYLINETO = POINTER(tagEMRPOLYLINE)
#EMRPOLYLINETO = tagEMRPOLYLINE
#class tagEMRPOLYLINE16(Structure):
#    pass
#tagEMRPOLYLINE16._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cpts', DWORD),
#    ('apts', POINTS * 1),
#]
#EMRPOLYLINE16 = tagEMRPOLYLINE16
#PEMRPOLYLINE16 = POINTER(tagEMRPOLYLINE16)
#EMRPOLYBEZIER16 = tagEMRPOLYLINE16
#PEMRPOLYBEZIER16 = POINTER(tagEMRPOLYLINE16)
#EMRPOLYGON16 = tagEMRPOLYLINE16
#PEMRPOLYGON16 = POINTER(tagEMRPOLYLINE16)
#EMRPOLYBEZIERTO16 = tagEMRPOLYLINE16
#PEMRPOLYBEZIERTO16 = POINTER(tagEMRPOLYLINE16)
#PEMRPOLYLINETO16 = POINTER(tagEMRPOLYLINE16)
#EMRPOLYLINETO16 = tagEMRPOLYLINE16
#class tagEMRPOLYDRAW(Structure):
#    pass
#tagEMRPOLYDRAW._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cptl', DWORD),
#    ('aptl', POINTL * 1),
#    ('abTypes', BYTE * 1),
#]
#PEMRPOLYDRAW = POINTER(tagEMRPOLYDRAW)
#EMRPOLYDRAW = tagEMRPOLYDRAW
#class tagEMRPOLYDRAW16(Structure):
#    pass
#tagEMRPOLYDRAW16._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cpts', DWORD),
#    ('apts', POINTS * 1),
#    ('abTypes', BYTE * 1),
#]
#EMRPOLYDRAW16 = tagEMRPOLYDRAW16
#PEMRPOLYDRAW16 = POINTER(tagEMRPOLYDRAW16)
#class tagEMRPOLYPOLYLINE(Structure):
#    pass
#tagEMRPOLYPOLYLINE._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('nPolys', DWORD),
#    ('cptl', DWORD),
#    ('aPolyCounts', DWORD * 1),
#    ('aptl', POINTL * 1),
#]
#PEMRPOLYPOLYLINE = POINTER(tagEMRPOLYPOLYLINE)
#EMRPOLYPOLYLINE = tagEMRPOLYPOLYLINE
#PEMRPOLYPOLYGON = POINTER(tagEMRPOLYPOLYLINE)
#EMRPOLYPOLYGON = tagEMRPOLYPOLYLINE
#class tagEMRPOLYPOLYLINE16(Structure):
#    pass
#tagEMRPOLYPOLYLINE16._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('nPolys', DWORD),
#    ('cpts', DWORD),
#    ('aPolyCounts', DWORD * 1),
#    ('apts', POINTS * 1),
#]
#PEMRPOLYPOLYLINE16 = POINTER(tagEMRPOLYPOLYLINE16)
#EMRPOLYPOLYLINE16 = tagEMRPOLYPOLYLINE16
#EMRPOLYPOLYGON16 = tagEMRPOLYPOLYLINE16
#PEMRPOLYPOLYGON16 = POINTER(tagEMRPOLYPOLYLINE16)
#class tagEMRINVERTRGN(Structure):
#    pass
#tagEMRINVERTRGN._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cbRgnData', DWORD),
#    ('RgnData', BYTE * 1),
#]
#PEMRINVERTRGN = POINTER(tagEMRINVERTRGN)
#EMRINVERTRGN = tagEMRINVERTRGN
#EMRPAINTRGN = tagEMRINVERTRGN
#PEMRPAINTRGN = POINTER(tagEMRINVERTRGN)
#class tagEMRFILLRGN(Structure):
#    pass
#tagEMRFILLRGN._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cbRgnData', DWORD),
#    ('ihBrush', DWORD),
#    ('RgnData', BYTE * 1),
#]
#PEMRFILLRGN = POINTER(tagEMRFILLRGN)
#EMRFILLRGN = tagEMRFILLRGN
#class tagEMRFRAMERGN(Structure):
#    pass
#tagEMRFRAMERGN._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cbRgnData', DWORD),
#    ('ihBrush', DWORD),
#    ('szlStroke', SIZEL),
#    ('RgnData', BYTE * 1),
#]
#EMRFRAMERGN = tagEMRFRAMERGN
#PEMRFRAMERGN = POINTER(tagEMRFRAMERGN)
#class tagEMREXTSELECTCLIPRGN(Structure):
#    pass
#tagEMREXTSELECTCLIPRGN._fields_ = [
#    ('emr', EMR),
#    ('cbRgnData', DWORD),
#    ('iMode', DWORD),
#    ('RgnData', BYTE * 1),
#]
#EMREXTSELECTCLIPRGN = tagEMREXTSELECTCLIPRGN
#PEMREXTSELECTCLIPRGN = POINTER(tagEMREXTSELECTCLIPRGN)
#class tagEMREXTTEXTOUTA(Structure):
#    pass
#tagEMREXTTEXTOUTA._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('iGraphicsMode', DWORD),
#    ('exScale', FLOAT),
#    ('eyScale', FLOAT),
#    ('emrtext', EMRTEXT),
#]
#PEMREXTTEXTOUTA = POINTER(tagEMREXTTEXTOUTA)
#EMREXTTEXTOUTA = tagEMREXTTEXTOUTA
#PEMREXTTEXTOUTW = POINTER(tagEMREXTTEXTOUTA)
#EMREXTTEXTOUTW = tagEMREXTTEXTOUTA
#class tagEMRPOLYTEXTOUTA(Structure):
#    pass
#tagEMRPOLYTEXTOUTA._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('iGraphicsMode', DWORD),
#    ('exScale', FLOAT),
#    ('eyScale', FLOAT),
#    ('cStrings', LONG),
#    ('aemrtext', EMRTEXT * 1),
#]
#PEMRPOLYTEXTOUTA = POINTER(tagEMRPOLYTEXTOUTA)
#EMRPOLYTEXTOUTA = tagEMRPOLYTEXTOUTA
#EMRPOLYTEXTOUTW = tagEMRPOLYTEXTOUTA
#PEMRPOLYTEXTOUTW = POINTER(tagEMRPOLYTEXTOUTA)
#class tagEMRBITBLT(Structure):
#    pass
#tagEMRBITBLT._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('xDest', LONG),
#    ('yDest', LONG),
#    ('cxDest', LONG),
#    ('cyDest', LONG),
#    ('dwRop', DWORD),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('xformSrc', XFORM),
#    ('crBkColorSrc', COLORREF),
#    ('iUsageSrc', DWORD),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#]
#EMRBITBLT = tagEMRBITBLT
#PEMRBITBLT = POINTER(tagEMRBITBLT)
#class tagEMRSTRETCHBLT(Structure):
#    pass
#tagEMRSTRETCHBLT._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('xDest', LONG),
#    ('yDest', LONG),
#    ('cxDest', LONG),
#    ('cyDest', LONG),
#    ('dwRop', DWORD),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('xformSrc', XFORM),
#    ('crBkColorSrc', COLORREF),
#    ('iUsageSrc', DWORD),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#    ('cxSrc', LONG),
#    ('cySrc', LONG),
#]
#EMRSTRETCHBLT = tagEMRSTRETCHBLT
#PEMRSTRETCHBLT = POINTER(tagEMRSTRETCHBLT)
#class tagEMRMASKBLT(Structure):
#    pass
#tagEMRMASKBLT._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('xDest', LONG),
#    ('yDest', LONG),
#    ('cxDest', LONG),
#    ('cyDest', LONG),
#    ('dwRop', DWORD),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('xformSrc', XFORM),
#    ('crBkColorSrc', COLORREF),
#    ('iUsageSrc', DWORD),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#    ('xMask', LONG),
#    ('yMask', LONG),
#    ('iUsageMask', DWORD),
#    ('offBmiMask', DWORD),
#    ('cbBmiMask', DWORD),
#    ('offBitsMask', DWORD),
#    ('cbBitsMask', DWORD),
#]
#PEMRMASKBLT = POINTER(tagEMRMASKBLT)
#EMRMASKBLT = tagEMRMASKBLT
#class tagEMRPLGBLT(Structure):
#    pass
#tagEMRPLGBLT._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('aptlDest', POINTL * 3),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('cxSrc', LONG),
#    ('cySrc', LONG),
#    ('xformSrc', XFORM),
#    ('crBkColorSrc', COLORREF),
#    ('iUsageSrc', DWORD),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#    ('xMask', LONG),
#    ('yMask', LONG),
#    ('iUsageMask', DWORD),
#    ('offBmiMask', DWORD),
#    ('cbBmiMask', DWORD),
#    ('offBitsMask', DWORD),
#    ('cbBitsMask', DWORD),
#]
#EMRPLGBLT = tagEMRPLGBLT
#PEMRPLGBLT = POINTER(tagEMRPLGBLT)
#class tagEMRSETDIBITSTODEVICE(Structure):
#    pass
#tagEMRSETDIBITSTODEVICE._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('xDest', LONG),
#    ('yDest', LONG),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('cxSrc', LONG),
#    ('cySrc', LONG),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#    ('iUsageSrc', DWORD),
#    ('iStartScan', DWORD),
#    ('cScans', DWORD),
#]
#PEMRSETDIBITSTODEVICE = POINTER(tagEMRSETDIBITSTODEVICE)
#EMRSETDIBITSTODEVICE = tagEMRSETDIBITSTODEVICE
#class tagEMRSTRETCHDIBITS(Structure):
#    pass
#tagEMRSTRETCHDIBITS._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('xDest', LONG),
#    ('yDest', LONG),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('cxSrc', LONG),
#    ('cySrc', LONG),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#    ('iUsageSrc', DWORD),
#    ('dwRop', DWORD),
#    ('cxDest', LONG),
#    ('cyDest', LONG),
#]
#PEMRSTRETCHDIBITS = POINTER(tagEMRSTRETCHDIBITS)
#EMRSTRETCHDIBITS = tagEMRSTRETCHDIBITS
#class tagEMREXTCREATEFONTINDIRECTW(Structure):
#    pass
#tagEMREXTCREATEFONTINDIRECTW._fields_ = [
#    ('emr', EMR),
#    ('ihFont', DWORD),
#    ('elfw', EXTLOGFONTW),
#]
#EMREXTCREATEFONTINDIRECTW = tagEMREXTCREATEFONTINDIRECTW
#PEMREXTCREATEFONTINDIRECTW = POINTER(tagEMREXTCREATEFONTINDIRECTW)
#class tagEMRCREATEPALETTE(Structure):
#    pass
#tagEMRCREATEPALETTE._fields_ = [
#    ('emr', EMR),
#    ('ihPal', DWORD),
#    ('lgpl', LOGPALETTE),
#]
#EMRCREATEPALETTE = tagEMRCREATEPALETTE
#PEMRCREATEPALETTE = POINTER(tagEMRCREATEPALETTE)
#class tagEMRCREATEPEN(Structure):
#    pass
#tagEMRCREATEPEN._fields_ = [
#    ('emr', EMR),
#    ('ihPen', DWORD),
#    ('lopn', LOGPEN),
#]
#EMRCREATEPEN = tagEMRCREATEPEN
#PEMRCREATEPEN = POINTER(tagEMRCREATEPEN)
#class tagEMREXTCREATEPEN(Structure):
#    pass
#tagEMREXTCREATEPEN._fields_ = [
#    ('emr', EMR),
#    ('ihPen', DWORD),
#    ('offBmi', DWORD),
#    ('cbBmi', DWORD),
#    ('offBits', DWORD),
#    ('cbBits', DWORD),
#    ('elp', EXTLOGPEN),
#]
#EMREXTCREATEPEN = tagEMREXTCREATEPEN
#PEMREXTCREATEPEN = POINTER(tagEMREXTCREATEPEN)
#class tagEMRCREATEBRUSHINDIRECT(Structure):
#    pass
#tagEMRCREATEBRUSHINDIRECT._fields_ = [
#    ('emr', EMR),
#    ('ihBrush', DWORD),
#    ('lb', LOGBRUSH32),
#]
#EMRCREATEBRUSHINDIRECT = tagEMRCREATEBRUSHINDIRECT
#PEMRCREATEBRUSHINDIRECT = POINTER(tagEMRCREATEBRUSHINDIRECT)
#class tagEMRCREATEMONOBRUSH(Structure):
#    pass
#tagEMRCREATEMONOBRUSH._fields_ = [
#    ('emr', EMR),
#    ('ihBrush', DWORD),
#    ('iUsage', DWORD),
#    ('offBmi', DWORD),
#    ('cbBmi', DWORD),
#    ('offBits', DWORD),
#    ('cbBits', DWORD),
#]
#EMRCREATEMONOBRUSH = tagEMRCREATEMONOBRUSH
#PEMRCREATEMONOBRUSH = POINTER(tagEMRCREATEMONOBRUSH)
#class tagEMRCREATEDIBPATTERNBRUSHPT(Structure):
#    pass
#tagEMRCREATEDIBPATTERNBRUSHPT._fields_ = [
#    ('emr', EMR),
#    ('ihBrush', DWORD),
#    ('iUsage', DWORD),
#    ('offBmi', DWORD),
#    ('cbBmi', DWORD),
#    ('offBits', DWORD),
#    ('cbBits', DWORD),
#]
#EMRCREATEDIBPATTERNBRUSHPT = tagEMRCREATEDIBPATTERNBRUSHPT
#PEMRCREATEDIBPATTERNBRUSHPT = POINTER(tagEMRCREATEDIBPATTERNBRUSHPT)
#class tagEMRFORMAT(Structure):
#    pass
#tagEMRFORMAT._fields_ = [
#    ('dSignature', DWORD),
#    ('nVersion', DWORD),
#    ('cbData', DWORD),
#    ('offData', DWORD),
#]
#EMRFORMAT = tagEMRFORMAT
#PEMRFORMAT = POINTER(tagEMRFORMAT)
#class tagEMRGLSRECORD(Structure):
#    pass
#tagEMRGLSRECORD._fields_ = [
#    ('emr', EMR),
#    ('cbData', DWORD),
#    ('Data', BYTE * 1),
#]
#PEMRGLSRECORD = POINTER(tagEMRGLSRECORD)
#EMRGLSRECORD = tagEMRGLSRECORD
#class tagEMRGLSBOUNDEDRECORD(Structure):
#    pass
#tagEMRGLSBOUNDEDRECORD._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('cbData', DWORD),
#    ('Data', BYTE * 1),
#]
#PEMRGLSBOUNDEDRECORD = POINTER(tagEMRGLSBOUNDEDRECORD)
#EMRGLSBOUNDEDRECORD = tagEMRGLSBOUNDEDRECORD
#class tagEMRPIXELFORMAT(Structure):
#    pass
#tagEMRPIXELFORMAT._fields_ = [
#    ('emr', EMR),
#    ('pfd', PIXELFORMATDESCRIPTOR),
#]
#PEMRPIXELFORMAT = POINTER(tagEMRPIXELFORMAT)
#EMRPIXELFORMAT = tagEMRPIXELFORMAT
#class tagEMRCREATECOLORSPACE(Structure):
#    pass
#tagEMRCREATECOLORSPACE._fields_ = [
#    ('emr', EMR),
#    ('ihCS', DWORD),
#    ('lcs', LOGCOLORSPACEA),
#]
#EMRCREATECOLORSPACE = tagEMRCREATECOLORSPACE
#PEMRCREATECOLORSPACE = POINTER(tagEMRCREATECOLORSPACE)
#class tagEMRSETCOLORSPACE(Structure):
#    pass
#tagEMRSETCOLORSPACE._fields_ = [
#    ('emr', EMR),
#    ('ihCS', DWORD),
#]
#EMRSETCOLORSPACE = tagEMRSETCOLORSPACE
#PEMRSETCOLORSPACE = POINTER(tagEMRSETCOLORSPACE)
#EMRSELECTCOLORSPACE = tagEMRSETCOLORSPACE
#PEMRSELECTCOLORSPACE = POINTER(tagEMRSETCOLORSPACE)
#PEMRDELETECOLORSPACE = POINTER(tagEMRSETCOLORSPACE)
#EMRDELETECOLORSPACE = tagEMRSETCOLORSPACE
#class tagEMREXTESCAPE(Structure):
#    pass
#tagEMREXTESCAPE._fields_ = [
#    ('emr', EMR),
#    ('iEscape', INT),
#    ('cbEscData', INT),
#    ('EscData', BYTE * 1),
#]
#PEMREXTESCAPE = POINTER(tagEMREXTESCAPE)
#EMREXTESCAPE = tagEMREXTESCAPE
#PEMRDRAWESCAPE = POINTER(tagEMREXTESCAPE)
#EMRDRAWESCAPE = tagEMREXTESCAPE
#class tagEMRNAMEDESCAPE(Structure):
#    pass
#tagEMRNAMEDESCAPE._fields_ = [
#    ('emr', EMR),
#    ('iEscape', INT),
#    ('cbDriver', INT),
#    ('cbEscData', INT),
#    ('EscData', BYTE * 1),
#]
#EMRNAMEDESCAPE = tagEMRNAMEDESCAPE
#PEMRNAMEDESCAPE = POINTER(tagEMRNAMEDESCAPE)
#class tagEMRSETICMPROFILE(Structure):
#    pass
#tagEMRSETICMPROFILE._fields_ = [
#    ('emr', EMR),
#    ('dwFlags', DWORD),
#    ('cbName', DWORD),
#    ('cbData', DWORD),
#    ('Data', BYTE * 1),
#]
#EMRSETICMPROFILE = tagEMRSETICMPROFILE
#PEMRSETICMPROFILE = POINTER(tagEMRSETICMPROFILE)
#PEMRSETICMPROFILEA = POINTER(tagEMRSETICMPROFILE)
#EMRSETICMPROFILEA = tagEMRSETICMPROFILE
#EMRSETICMPROFILEW = tagEMRSETICMPROFILE
#PEMRSETICMPROFILEW = POINTER(tagEMRSETICMPROFILE)
#class tagEMRCREATECOLORSPACEW(Structure):
#    pass
#tagEMRCREATECOLORSPACEW._fields_ = [
#    ('emr', EMR),
#    ('ihCS', DWORD),
#    ('lcs', LOGCOLORSPACEW),
#    ('dwFlags', DWORD),
#    ('cbData', DWORD),
#    ('Data', BYTE * 1),
#]
#PEMRCREATECOLORSPACEW = POINTER(tagEMRCREATECOLORSPACEW)
#EMRCREATECOLORSPACEW = tagEMRCREATECOLORSPACEW
#class tagCOLORMATCHTOTARGET(Structure):
#    pass
#tagCOLORMATCHTOTARGET._fields_ = [
#    ('emr', EMR),
#    ('dwAction', DWORD),
#    ('dwFlags', DWORD),
#    ('cbName', DWORD),
#    ('cbData', DWORD),
#    ('Data', BYTE * 1),
#]
#PEMRCOLORMATCHTOTARGET = POINTER(tagCOLORMATCHTOTARGET)
#EMRCOLORMATCHTOTARGET = tagCOLORMATCHTOTARGET
#class tagCOLORCORRECTPALETTE(Structure):
#    pass
#tagCOLORCORRECTPALETTE._fields_ = [
#    ('emr', EMR),
#    ('ihPalette', DWORD),
#    ('nFirstEntry', DWORD),
#    ('nPalEntries', DWORD),
#    ('nReserved', DWORD),
#]
#PEMRCOLORCORRECTPALETTE = POINTER(tagCOLORCORRECTPALETTE)
#EMRCOLORCORRECTPALETTE = tagCOLORCORRECTPALETTE
#class tagEMRALPHABLEND(Structure):
#    pass
#tagEMRALPHABLEND._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('xDest', LONG),
#    ('yDest', LONG),
#    ('cxDest', LONG),
#    ('cyDest', LONG),
#    ('dwRop', DWORD),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('xformSrc', XFORM),
#    ('crBkColorSrc', COLORREF),
#    ('iUsageSrc', DWORD),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#    ('cxSrc', LONG),
#    ('cySrc', LONG),
#]
#PEMRALPHABLEND = POINTER(tagEMRALPHABLEND)
#EMRALPHABLEND = tagEMRALPHABLEND
#class tagEMRGRADIENTFILL(Structure):
#    pass
#tagEMRGRADIENTFILL._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('nVer', DWORD),
#    ('nTri', DWORD),
#    ('ulMode', ULONG),
#    ('Ver', TRIVERTEX * 1),
#]
#EMRGRADIENTFILL = tagEMRGRADIENTFILL
#PEMRGRADIENTFILL = POINTER(tagEMRGRADIENTFILL)
#class tagEMRTRANSPARENTBLT(Structure):
#    pass
#tagEMRTRANSPARENTBLT._fields_ = [
#    ('emr', EMR),
#    ('rclBounds', RECTL),
#    ('xDest', LONG),
#    ('yDest', LONG),
#    ('cxDest', LONG),
#    ('cyDest', LONG),
#    ('dwRop', DWORD),
#    ('xSrc', LONG),
#    ('ySrc', LONG),
#    ('xformSrc', XFORM),
#    ('crBkColorSrc', COLORREF),
#    ('iUsageSrc', DWORD),
#    ('offBmiSrc', DWORD),
#    ('cbBmiSrc', DWORD),
#    ('offBitsSrc', DWORD),
#    ('cbBitsSrc', DWORD),
#    ('cxSrc', LONG),
#    ('cySrc', LONG),
#]
#EMRTRANSPARENTBLT = tagEMRTRANSPARENTBLT
#PEMRTRANSPARENTBLT = POINTER(tagEMRTRANSPARENTBLT)
#class _POINTFLOAT(Structure):
#    pass
#_POINTFLOAT._fields_ = [
#    ('x', FLOAT),
#    ('y', FLOAT),
#]
#PPOINTFLOAT = POINTER(_POINTFLOAT)
#POINTFLOAT = _POINTFLOAT
#class _GLYPHMETRICSFLOAT(Structure):
#    pass
#_GLYPHMETRICSFLOAT._fields_ = [
#    ('gmfBlackBoxX', FLOAT),
#    ('gmfBlackBoxY', FLOAT),
#    ('gmfptGlyphOrigin', POINTFLOAT),
#    ('gmfCellIncX', FLOAT),
#    ('gmfCellIncY', FLOAT),
#]
#PGLYPHMETRICSFLOAT = POINTER(_GLYPHMETRICSFLOAT)
#GLYPHMETRICSFLOAT = _GLYPHMETRICSFLOAT
#LPGLYPHMETRICSFLOAT = POINTER(_GLYPHMETRICSFLOAT)
#class tagLAYERPLANEDESCRIPTOR(Structure):
#    pass
#tagLAYERPLANEDESCRIPTOR._fields_ = [
#    ('nSize', WORD),
#    ('nVersion', WORD),
#    ('dwFlags', DWORD),
#    ('iPixelType', BYTE),
#    ('cColorBits', BYTE),
#    ('cRedBits', BYTE),
#    ('cRedShift', BYTE),
#    ('cGreenBits', BYTE),
#    ('cGreenShift', BYTE),
#    ('cBlueBits', BYTE),
#    ('cBlueShift', BYTE),
#    ('cAlphaBits', BYTE),
#    ('cAlphaShift', BYTE),
#    ('cAccumBits', BYTE),
#    ('cAccumRedBits', BYTE),
#    ('cAccumGreenBits', BYTE),
#    ('cAccumBlueBits', BYTE),
#    ('cAccumAlphaBits', BYTE),
#    ('cDepthBits', BYTE),
#    ('cStencilBits', BYTE),
#    ('cAuxBuffers', BYTE),
#    ('iLayerPlane', BYTE),
#    ('bReserved', BYTE),
#    ('crTransparent', COLORREF),
#]
#LAYERPLANEDESCRIPTOR = tagLAYERPLANEDESCRIPTOR
#LPLAYERPLANEDESCRIPTOR = POINTER(tagLAYERPLANEDESCRIPTOR)
#PLAYERPLANEDESCRIPTOR = POINTER(tagLAYERPLANEDESCRIPTOR)
#class _WGLSWAP(Structure):
#    pass
#_WGLSWAP._fields_ = [
#    ('hdc', HDC),
#    ('uiFlags', UINT),
#]
#WGLSWAP = _WGLSWAP
#PWGLSWAP = POINTER(_WGLSWAP)
#LPWGLSWAP = POINTER(_WGLSWAP)
#class _NETRESOURCEA(Structure):
#    pass
#_NETRESOURCEA._fields_ = [
#    ('dwScope', DWORD),
#    ('dwType', DWORD),
#    ('dwDisplayType', DWORD),
#    ('dwUsage', DWORD),
#    ('lpLocalName', LPSTR),
#    ('lpRemoteName', LPSTR),
#    ('lpComment', LPSTR),
#    ('lpProvider', LPSTR),
#]
#LPNETRESOURCEA = POINTER(_NETRESOURCEA)
#NETRESOURCEA = _NETRESOURCEA
#class _NETRESOURCEW(Structure):
#    pass
#_NETRESOURCEW._fields_ = [
#    ('dwScope', DWORD),
#    ('dwType', DWORD),
#    ('dwDisplayType', DWORD),
#    ('dwUsage', DWORD),
#    ('lpLocalName', LPWSTR),
#    ('lpRemoteName', LPWSTR),
#    ('lpComment', LPWSTR),
#    ('lpProvider', LPWSTR),
#]
#LPNETRESOURCEW = POINTER(_NETRESOURCEW)
#NETRESOURCEW = _NETRESOURCEW
#NETRESOURCE = NETRESOURCEA
#LPNETRESOURCE = LPNETRESOURCEA
#class _CONNECTDLGSTRUCTA(Structure):
#    pass
#_CONNECTDLGSTRUCTA._fields_ = [
#    ('cbStructure', DWORD),
#    ('hwndOwner', HWND),
#    ('lpConnRes', LPNETRESOURCEA),
#    ('dwFlags', DWORD),
#    ('dwDevNum', DWORD),
#]
#LPCONNECTDLGSTRUCTA = POINTER(_CONNECTDLGSTRUCTA)
#CONNECTDLGSTRUCTA = _CONNECTDLGSTRUCTA
#class _CONNECTDLGSTRUCTW(Structure):
#    pass
#_CONNECTDLGSTRUCTW._fields_ = [
#    ('cbStructure', DWORD),
#    ('hwndOwner', HWND),
#    ('lpConnRes', LPNETRESOURCEW),
#    ('dwFlags', DWORD),
#    ('dwDevNum', DWORD),
#]
#CONNECTDLGSTRUCTW = _CONNECTDLGSTRUCTW
#LPCONNECTDLGSTRUCTW = POINTER(_CONNECTDLGSTRUCTW)
#CONNECTDLGSTRUCT = CONNECTDLGSTRUCTA
#LPCONNECTDLGSTRUCT = LPCONNECTDLGSTRUCTA
#class _DISCDLGSTRUCTA(Structure):
#    pass
#_DISCDLGSTRUCTA._fields_ = [
#    ('cbStructure', DWORD),
#    ('hwndOwner', HWND),
#    ('lpLocalName', LPSTR),
#    ('lpRemoteName', LPSTR),
#    ('dwFlags', DWORD),
#]
#LPDISCDLGSTRUCTA = POINTER(_DISCDLGSTRUCTA)
#DISCDLGSTRUCTA = _DISCDLGSTRUCTA
#class _DISCDLGSTRUCTW(Structure):
#    pass
#_DISCDLGSTRUCTW._fields_ = [
#    ('cbStructure', DWORD),
#    ('hwndOwner', HWND),
#    ('lpLocalName', LPWSTR),
#    ('lpRemoteName', LPWSTR),
#    ('dwFlags', DWORD),
#]
#DISCDLGSTRUCTW = _DISCDLGSTRUCTW
#LPDISCDLGSTRUCTW = POINTER(_DISCDLGSTRUCTW)
#DISCDLGSTRUCT = DISCDLGSTRUCTA
#LPDISCDLGSTRUCT = LPDISCDLGSTRUCTA
#class _UNIVERSAL_NAME_INFOA(Structure):
#    pass
#_UNIVERSAL_NAME_INFOA._fields_ = [
#    ('lpUniversalName', LPSTR),
#]
#LPUNIVERSAL_NAME_INFOA = POINTER(_UNIVERSAL_NAME_INFOA)
#UNIVERSAL_NAME_INFOA = _UNIVERSAL_NAME_INFOA
#class _UNIVERSAL_NAME_INFOW(Structure):
#    pass
#_UNIVERSAL_NAME_INFOW._fields_ = [
#    ('lpUniversalName', LPWSTR),
#]
#LPUNIVERSAL_NAME_INFOW = POINTER(_UNIVERSAL_NAME_INFOW)
#UNIVERSAL_NAME_INFOW = _UNIVERSAL_NAME_INFOW
#UNIVERSAL_NAME_INFO = UNIVERSAL_NAME_INFOA
#LPUNIVERSAL_NAME_INFO = LPUNIVERSAL_NAME_INFOA
#class _REMOTE_NAME_INFOA(Structure):
#    pass
#_REMOTE_NAME_INFOA._fields_ = [
#    ('lpUniversalName', LPSTR),
#    ('lpConnectionName', LPSTR),
#    ('lpRemainingPath', LPSTR),
#]
#LPREMOTE_NAME_INFOA = POINTER(_REMOTE_NAME_INFOA)
#REMOTE_NAME_INFOA = _REMOTE_NAME_INFOA
#class _REMOTE_NAME_INFOW(Structure):
#    pass
#_REMOTE_NAME_INFOW._fields_ = [
#    ('lpUniversalName', LPWSTR),
#    ('lpConnectionName', LPWSTR),
#    ('lpRemainingPath', LPWSTR),
#]
#REMOTE_NAME_INFOW = _REMOTE_NAME_INFOW
#LPREMOTE_NAME_INFOW = POINTER(_REMOTE_NAME_INFOW)
#REMOTE_NAME_INFO = REMOTE_NAME_INFOA
#LPREMOTE_NAME_INFO = LPREMOTE_NAME_INFOA
#class _NETINFOSTRUCT(Structure):
#    pass
#_NETINFOSTRUCT._fields_ = [
#    ('cbStructure', DWORD),
#    ('dwProviderVersion', DWORD),
#    ('dwStatus', DWORD),
#    ('dwCharacteristics', DWORD),
#    ('dwHandle', ULONG_PTR),
#    ('wNetType', WORD),
#    ('dwPrinters', DWORD),
#    ('dwDrives', DWORD),
#]
#LPNETINFOSTRUCT = POINTER(_NETINFOSTRUCT)
#NETINFOSTRUCT = _NETINFOSTRUCT
#PFNGETPROFILEPATHA = WINFUNCTYPE(UINT, STRING, STRING, c_uint)
#PFNGETPROFILEPATHW = WINFUNCTYPE(UINT, WSTRING, WSTRING, c_uint)
#PFNRECONCILEPROFILEA = WINFUNCTYPE(UINT, STRING, STRING, c_ulong)
#PFNRECONCILEPROFILEW = WINFUNCTYPE(UINT, WSTRING, WSTRING, c_ulong)
#PFNPROCESSPOLICIESA = WINFUNCTYPE(BOOL, POINTER(HWND__), STRING, STRING, STRING, c_ulong)
#PFNPROCESSPOLICIESW = WINFUNCTYPE(BOOL, POINTER(HWND__), WSTRING, WSTRING, WSTRING, c_ulong)
#class _NETCONNECTINFOSTRUCT(Structure):
#    pass
#_NETCONNECTINFOSTRUCT._fields_ = [
#    ('cbStructure', DWORD),
#    ('dwFlags', DWORD),
#    ('dwSpeed', DWORD),
#    ('dwDelay', DWORD),
#    ('dwOptDataSize', DWORD),
#]
#LPNETCONNECTINFOSTRUCT = POINTER(_NETCONNECTINFOSTRUCT)
#NETCONNECTINFOSTRUCT = _NETCONNECTINFOSTRUCT
#CALTYPE = DWORD
#CALID = DWORD
#class _cpinfo(Structure):
#    pass
#_cpinfo._fields_ = [
#    ('MaxCharSize', UINT),
#    ('DefaultChar', BYTE * 2),
#    ('LeadByte', BYTE * 12),
#]
#LPCPINFO = POINTER(_cpinfo)
#CPINFO = _cpinfo
#class _cpinfoexA(Structure):
#    pass
#_cpinfoexA._fields_ = [
#    ('MaxCharSize', UINT),
#    ('DefaultChar', BYTE * 2),
#    ('LeadByte', BYTE * 12),
#    ('UnicodeDefaultChar', WCHAR),
#    ('CodePage', UINT),
#    ('CodePageName', CHAR * 260),
#]
#LPCPINFOEXA = POINTER(_cpinfoexA)
#CPINFOEXA = _cpinfoexA
#class _cpinfoexW(Structure):
#    pass
#_cpinfoexW._fields_ = [
#    ('MaxCharSize', UINT),
#    ('DefaultChar', BYTE * 2),
#    ('LeadByte', BYTE * 12),
#    ('UnicodeDefaultChar', WCHAR),
#    ('CodePage', UINT),
#    ('CodePageName', WCHAR * 260),
#]
#CPINFOEXW = _cpinfoexW
#LPCPINFOEXW = POINTER(_cpinfoexW)
#CPINFOEX = CPINFOEXA
#LPCPINFOEX = LPCPINFOEXA
#class _numberfmtA(Structure):
#    pass
#_numberfmtA._fields_ = [
#    ('NumDigits', UINT),
#    ('LeadingZero', UINT),
#    ('Grouping', UINT),
#    ('lpDecimalSep', LPSTR),
#    ('lpThousandSep', LPSTR),
#    ('NegativeOrder', UINT),
#]
#LPNUMBERFMTA = POINTER(_numberfmtA)
#NUMBERFMTA = _numberfmtA
#class _numberfmtW(Structure):
#    pass
#_numberfmtW._fields_ = [
#    ('NumDigits', UINT),
#    ('LeadingZero', UINT),
#    ('Grouping', UINT),
#    ('lpDecimalSep', LPWSTR),
#    ('lpThousandSep', LPWSTR),
#    ('NegativeOrder', UINT),
#]
#NUMBERFMTW = _numberfmtW
#LPNUMBERFMTW = POINTER(_numberfmtW)
#NUMBERFMT = NUMBERFMTA
#LPNUMBERFMT = LPNUMBERFMTA
#class _currencyfmtA(Structure):
#    pass
#_currencyfmtA._fields_ = [
#    ('NumDigits', UINT),
#    ('LeadingZero', UINT),
#    ('Grouping', UINT),
#    ('lpDecimalSep', LPSTR),
#    ('lpThousandSep', LPSTR),
#    ('NegativeOrder', UINT),
#    ('PositiveOrder', UINT),
#    ('lpCurrencySymbol', LPSTR),
#]
#LPCURRENCYFMTA = POINTER(_currencyfmtA)
#CURRENCYFMTA = _currencyfmtA
#class _currencyfmtW(Structure):
#    pass
#_currencyfmtW._fields_ = [
#    ('NumDigits', UINT),
#    ('LeadingZero', UINT),
#    ('Grouping', UINT),
#    ('lpDecimalSep', LPWSTR),
#    ('lpThousandSep', LPWSTR),
#    ('NegativeOrder', UINT),
#    ('PositiveOrder', UINT),
#    ('lpCurrencySymbol', LPWSTR),
#]
#LPCURRENCYFMTW = POINTER(_currencyfmtW)
#CURRENCYFMTW = _currencyfmtW
#CURRENCYFMT = CURRENCYFMTA
#LPCURRENCYFMT = LPCURRENCYFMTA
#
## values for enumeration 'SYSNLS_FUNCTION'
#SYSNLS_FUNCTION = c_int # enum
#NLS_FUNCTION = DWORD
#class _nlsversioninfo(Structure):
#    pass
#_nlsversioninfo._fields_ = [
#    ('dwNLSVersionInfoSize', DWORD),
#    ('dwNLSVersion', DWORD),
#    ('dwDefinedVersion', DWORD),
#]
#LPNLSVERSIONINFO = POINTER(_nlsversioninfo)
#NLSVERSIONINFO = _nlsversioninfo
#GEOID = LONG
#GEOTYPE = DWORD
#GEOCLASS = DWORD
#
## values for enumeration 'SYSGEOTYPE'
#SYSGEOTYPE = c_int # enum
#
## values for enumeration 'SYSGEOCLASS'
#SYSGEOCLASS = c_int # enum
#LANGUAGEGROUP_ENUMPROCA = WINFUNCTYPE(BOOL, c_ulong, STRING, STRING, c_ulong, c_long)
#LANGGROUPLOCALE_ENUMPROCA = WINFUNCTYPE(BOOL, c_ulong, c_ulong, STRING, c_long)
#UILANGUAGE_ENUMPROCA = WINFUNCTYPE(BOOL, STRING, c_long)
#LOCALE_ENUMPROCA = WINFUNCTYPE(BOOL, STRING)
#CODEPAGE_ENUMPROCA = WINFUNCTYPE(BOOL, STRING)
#DATEFMT_ENUMPROCA = WINFUNCTYPE(BOOL, STRING)
#DATEFMT_ENUMPROCEXA = WINFUNCTYPE(BOOL, STRING, c_ulong)
#TIMEFMT_ENUMPROCA = WINFUNCTYPE(BOOL, STRING)
#CALINFO_ENUMPROCA = WINFUNCTYPE(BOOL, STRING)
#CALINFO_ENUMPROCEXA = WINFUNCTYPE(BOOL, STRING, c_ulong)
#LANGUAGEGROUP_ENUMPROCW = WINFUNCTYPE(BOOL, c_ulong, WSTRING, WSTRING, c_ulong, c_long)
#LANGGROUPLOCALE_ENUMPROCW = WINFUNCTYPE(BOOL, c_ulong, c_ulong, WSTRING, c_long)
#UILANGUAGE_ENUMPROCW = WINFUNCTYPE(BOOL, WSTRING, c_long)
#LOCALE_ENUMPROCW = WINFUNCTYPE(BOOL, WSTRING)
#CODEPAGE_ENUMPROCW = WINFUNCTYPE(BOOL, WSTRING)
#DATEFMT_ENUMPROCW = WINFUNCTYPE(BOOL, WSTRING)
#DATEFMT_ENUMPROCEXW = WINFUNCTYPE(BOOL, WSTRING, c_ulong)
#TIMEFMT_ENUMPROCW = WINFUNCTYPE(BOOL, WSTRING)
#CALINFO_ENUMPROCW = WINFUNCTYPE(BOOL, WSTRING)
#CALINFO_ENUMPROCEXW = WINFUNCTYPE(BOOL, WSTRING, c_ulong)
#GEO_ENUMPROC = WINFUNCTYPE(BOOL, c_long)
#ACCESS_MASK = DWORD
#REGSAM = ACCESS_MASK
#class val_context(Structure):
#    pass
#val_context._fields_ = [
#    ('valuelen', c_int),
#    ('value_context', LPVOID),
#    ('val_buff_ptr', LPVOID),
#]
#PVALCONTEXT = POINTER(val_context)
#class pvalueA(Structure):
#    pass
#pvalueA._fields_ = [
#    ('pv_valuename', LPSTR),
#    ('pv_valuelen', c_int),
#    ('pv_value_context', LPVOID),
#    ('pv_type', DWORD),
#]
#PPVALUEA = POINTER(pvalueA)
#PVALUEA = pvalueA
#class pvalueW(Structure):
#    pass
#pvalueW._fields_ = [
#    ('pv_valuename', LPWSTR),
#    ('pv_valuelen', c_int),
#    ('pv_value_context', LPVOID),
#    ('pv_type', DWORD),
#]
#PVALUEW = pvalueW
#PPVALUEW = POINTER(pvalueW)
#PVALUE = PVALUEA
#PPVALUE = PPVALUEA
#QUERYHANDLER = CFUNCTYPE(DWORD, c_void_p, POINTER(val_context), c_ulong, c_void_p, POINTER(DWORD), c_ulong)
#PQUERYHANDLER = POINTER(QUERYHANDLER)
#class provider_info(Structure):
#    pass
#provider_info._fields_ = [
#    ('pi_R0_1val', PQUERYHANDLER),
#    ('pi_R0_allvals', PQUERYHANDLER),
#    ('pi_R3_1val', PQUERYHANDLER),
#    ('pi_R3_allvals', PQUERYHANDLER),
#    ('pi_flags', DWORD),
#    ('pi_key_context', LPVOID),
#]
#REG_PROVIDER = provider_info
#PPROVIDER = POINTER(provider_info)
#class value_entA(Structure):
#    pass
#value_entA._fields_ = [
#    ('ve_valuename', LPSTR),
#    ('ve_valuelen', DWORD),
#    ('ve_valueptr', DWORD_PTR),
#    ('ve_type', DWORD),
#]
#PVALENTA = POINTER(value_entA)
#VALENTA = value_entA
#class value_entW(Structure):
#    pass
#value_entW._fields_ = [
#    ('ve_valuename', LPWSTR),
#    ('ve_valuelen', DWORD),
#    ('ve_valueptr', DWORD_PTR),
#    ('ve_type', DWORD),
#]
#PVALENTW = POINTER(value_entW)
#VALENTW = value_entW
#VALENT = VALENTA
#PVALENT = PVALENTA
#u_char = c_ubyte
#u_short = c_ushort
#u_int = c_uint
#u_long = c_ulong
#u_int64 = c_ulonglong
#SOCKET = UINT_PTR
#class fd_set(Structure):
#    pass
#fd_set._fields_ = [
#    ('fd_count', u_int),
#    ('fd_array', SOCKET * 64),
#]
#class timeval(Structure):
#    pass
#timeval._fields_ = [
#    ('tv_sec', c_long),
#    ('tv_usec', c_long),
#]
#class hostent(Structure):
#    pass
#hostent._fields_ = [
#    ('h_name', STRING),
#    ('h_aliases', POINTER(STRING)),
#    ('h_addrtype', c_short),
#    ('h_length', c_short),
#    ('h_addr_list', POINTER(STRING)),
#]
#class netent(Structure):
#    pass
#netent._fields_ = [
#    ('n_name', STRING),
#    ('n_aliases', POINTER(STRING)),
#    ('n_addrtype', c_short),
#    ('n_net', u_long),
#]
#class servent(Structure):
#    pass
#servent._fields_ = [
#    ('s_name', STRING),
#    ('s_aliases', POINTER(STRING)),
#    ('s_port', c_short),
#    ('s_proto', STRING),
#]
#class protoent(Structure):
#    pass
#protoent._fields_ = [
#    ('p_name', STRING),
#    ('p_aliases', POINTER(STRING)),
#    ('p_proto', c_short),
#]
#class in_addr(Structure):
#    pass
#class N7in_addr4DOLLAR_75E(Union):
#    pass
#class N7in_addr4DOLLAR_754DOLLAR_76E(Structure):
#    pass
#N7in_addr4DOLLAR_754DOLLAR_76E._fields_ = [
#    ('s_b1', u_char),
#    ('s_b2', u_char),
#    ('s_b3', u_char),
#    ('s_b4', u_char),
#]
#class N7in_addr4DOLLAR_754DOLLAR_77E(Structure):
#    pass
#N7in_addr4DOLLAR_754DOLLAR_77E._fields_ = [
#    ('s_w1', u_short),
#    ('s_w2', u_short),
#]
#N7in_addr4DOLLAR_75E._fields_ = [
#    ('S_un_b', N7in_addr4DOLLAR_754DOLLAR_76E),
#    ('S_un_w', N7in_addr4DOLLAR_754DOLLAR_77E),
#    ('S_addr', u_long),
#]
#in_addr._fields_ = [
#    ('S_un', N7in_addr4DOLLAR_75E),
#]
#class sockaddr_in(Structure):
#    pass
#sockaddr_in._fields_ = [
#    ('sin_family', c_short),
#    ('sin_port', u_short),
#    ('sin_addr', in_addr),
#    ('sin_zero', c_char * 8),
#]
#class WSAData(Structure):
#    pass
#WSAData._fields_ = [
#    ('wVersion', WORD),
#    ('wHighVersion', WORD),
#    ('szDescription', c_char * 257),
#    ('szSystemStatus', c_char * 129),
#    ('iMaxSockets', c_ushort),
#    ('iMaxUdpDg', c_ushort),
#    ('lpVendorInfo', STRING),
#]
#LPWSADATA = POINTER(WSAData)
#WSADATA = WSAData
#class sockaddr(Structure):
#    pass
#sockaddr._fields_ = [
#    ('sa_family', u_short),
#    ('sa_data', c_char * 14),
#]
#class sockaddr_storage(Structure):
#    pass
#sockaddr_storage._fields_ = [
#    ('ss_family', c_short),
#    ('__ss_pad1', c_char * 6),
#    ('__ss_align', c_longlong),
#    ('__ss_pad2', c_char * 112),
#]
#class sockproto(Structure):
#    pass
#sockproto._fields_ = [
#    ('sp_family', u_short),
#    ('sp_protocol', u_short),
#]
#class linger(Structure):
#    pass
#linger._fields_ = [
#    ('l_onoff', u_short),
#    ('l_linger', u_short),
#]
#LPWSAOVERLAPPED = POINTER(_OVERLAPPED)
#class _WSABUF(Structure):
#    pass
#_WSABUF._fields_ = [
#    ('len', u_long),
#    ('buf', STRING),
#]
#LPWSABUF = POINTER(_WSABUF)
#WSABUF = _WSABUF
#class _QualityOfService(Structure):
#    pass
#_QualityOfService._fields_ = [
#    ('SendingFlowspec', FLOWSPEC),
#    ('ReceivingFlowspec', FLOWSPEC),
#    ('ProviderSpecific', WSABUF),
#]
#QOS = _QualityOfService
#LPQOS = POINTER(_QualityOfService)
#GROUP = c_uint
#class _WSANETWORKEVENTS(Structure):
#    pass
#_WSANETWORKEVENTS._fields_ = [
#    ('lNetworkEvents', c_long),
#    ('iErrorCode', c_int * 10),
#]
#WSANETWORKEVENTS = _WSANETWORKEVENTS
#LPWSANETWORKEVENTS = POINTER(_WSANETWORKEVENTS)
#class _WSAPROTOCOLCHAIN(Structure):
#    pass
#_WSAPROTOCOLCHAIN._fields_ = [
#    ('ChainLen', c_int),
#    ('ChainEntries', DWORD * 7),
#]
#WSAPROTOCOLCHAIN = _WSAPROTOCOLCHAIN
#LPWSAPROTOCOLCHAIN = POINTER(_WSAPROTOCOLCHAIN)
#class _WSAPROTOCOL_INFOA(Structure):
#    pass
#_WSAPROTOCOL_INFOA._fields_ = [
#    ('dwServiceFlags1', DWORD),
#    ('dwServiceFlags2', DWORD),
#    ('dwServiceFlags3', DWORD),
#    ('dwServiceFlags4', DWORD),
#    ('dwProviderFlags', DWORD),
#    ('ProviderId', GUID),
#    ('dwCatalogEntryId', DWORD),
#    ('ProtocolChain', WSAPROTOCOLCHAIN),
#    ('iVersion', c_int),
#    ('iAddressFamily', c_int),
#    ('iMaxSockAddr', c_int),
#    ('iMinSockAddr', c_int),
#    ('iSocketType', c_int),
#    ('iProtocol', c_int),
#    ('iProtocolMaxOffset', c_int),
#    ('iNetworkByteOrder', c_int),
#    ('iSecurityScheme', c_int),
#    ('dwMessageSize', DWORD),
#    ('dwProviderReserved', DWORD),
#    ('szProtocol', CHAR * 256),
#]
#LPWSAPROTOCOL_INFOA = POINTER(_WSAPROTOCOL_INFOA)
#WSAPROTOCOL_INFOA = _WSAPROTOCOL_INFOA
#class _WSAPROTOCOL_INFOW(Structure):
#    pass
#_WSAPROTOCOL_INFOW._fields_ = [
#    ('dwServiceFlags1', DWORD),
#    ('dwServiceFlags2', DWORD),
#    ('dwServiceFlags3', DWORD),
#    ('dwServiceFlags4', DWORD),
#    ('dwProviderFlags', DWORD),
#    ('ProviderId', GUID),
#    ('dwCatalogEntryId', DWORD),
#    ('ProtocolChain', WSAPROTOCOLCHAIN),
#    ('iVersion', c_int),
#    ('iAddressFamily', c_int),
#    ('iMaxSockAddr', c_int),
#    ('iMinSockAddr', c_int),
#    ('iSocketType', c_int),
#    ('iProtocol', c_int),
#    ('iProtocolMaxOffset', c_int),
#    ('iNetworkByteOrder', c_int),
#    ('iSecurityScheme', c_int),
#    ('dwMessageSize', DWORD),
#    ('dwProviderReserved', DWORD),
#    ('szProtocol', WCHAR * 256),
#]
#WSAPROTOCOL_INFOW = _WSAPROTOCOL_INFOW
#LPWSAPROTOCOL_INFOW = POINTER(_WSAPROTOCOL_INFOW)
#WSAPROTOCOL_INFO = WSAPROTOCOL_INFOA
#LPWSAPROTOCOL_INFO = LPWSAPROTOCOL_INFOA
#LPCONDITIONPROC = WINFUNCTYPE(c_int, POINTER(_WSABUF), POINTER(_WSABUF), POINTER(_QualityOfService), POINTER(_QualityOfService), POINTER(_WSABUF), POINTER(_WSABUF), POINTER(GROUP), c_ulong)
#LPWSAOVERLAPPED_COMPLETION_ROUTINE = WINFUNCTYPE(None, c_ulong, c_ulong, POINTER(_OVERLAPPED), c_ulong)
#
## values for enumeration '_WSACOMPLETIONTYPE'
#_WSACOMPLETIONTYPE = c_int # enum
#PWSACOMPLETIONTYPE = POINTER(_WSACOMPLETIONTYPE)
#LPWSACOMPLETIONTYPE = POINTER(_WSACOMPLETIONTYPE)
#WSACOMPLETIONTYPE = _WSACOMPLETIONTYPE
#class _WSACOMPLETION(Structure):
#    pass
#class N14_WSACOMPLETION4DOLLAR_79E(Union):
#    pass
#class N14_WSACOMPLETION4DOLLAR_794DOLLAR_80E(Structure):
#    pass
#N14_WSACOMPLETION4DOLLAR_794DOLLAR_80E._fields_ = [
#    ('hWnd', HWND),
#    ('uMsg', UINT),
#    ('context', WPARAM),
#]
#class N14_WSACOMPLETION4DOLLAR_794DOLLAR_81E(Structure):
#    pass
#N14_WSACOMPLETION4DOLLAR_794DOLLAR_81E._fields_ = [
#    ('lpOverlapped', LPWSAOVERLAPPED),
#]
#class N14_WSACOMPLETION4DOLLAR_794DOLLAR_82E(Structure):
#    pass
#N14_WSACOMPLETION4DOLLAR_794DOLLAR_82E._fields_ = [
#    ('lpOverlapped', LPWSAOVERLAPPED),
#    ('lpfnCompletionProc', LPWSAOVERLAPPED_COMPLETION_ROUTINE),
#]
#class N14_WSACOMPLETION4DOLLAR_794DOLLAR_83E(Structure):
#    pass
#N14_WSACOMPLETION4DOLLAR_794DOLLAR_83E._fields_ = [
#    ('lpOverlapped', LPWSAOVERLAPPED),
#    ('hPort', HANDLE),
#    ('Key', ULONG_PTR),
#]
#N14_WSACOMPLETION4DOLLAR_79E._fields_ = [
#    ('WindowMessage', N14_WSACOMPLETION4DOLLAR_794DOLLAR_80E),
#    ('Event', N14_WSACOMPLETION4DOLLAR_794DOLLAR_81E),
#    ('Apc', N14_WSACOMPLETION4DOLLAR_794DOLLAR_82E),
#    ('Port', N14_WSACOMPLETION4DOLLAR_794DOLLAR_83E),
#]
#_WSACOMPLETION._fields_ = [
#    ('Type', WSACOMPLETIONTYPE),
#    ('Parameters', N14_WSACOMPLETION4DOLLAR_79E),
#]
#WSACOMPLETION = _WSACOMPLETION
#LPWSACOMPLETION = POINTER(_WSACOMPLETION)
#PWSACOMPLETION = POINTER(_WSACOMPLETION)
#SOCKADDR = sockaddr
#PSOCKADDR = POINTER(sockaddr)
#LPSOCKADDR = POINTER(sockaddr)
#SOCKADDR_STORAGE = sockaddr_storage
#PSOCKADDR_STORAGE = POINTER(sockaddr_storage)
#LPSOCKADDR_STORAGE = POINTER(sockaddr_storage)
#class _BLOB(Structure):
#    pass
#_BLOB._fields_ = [
#    ('cbSize', ULONG),
#    ('pBlobData', POINTER(BYTE)),
#]
#LPBLOB = POINTER(_BLOB)
#BLOB = _BLOB
#class _SOCKET_ADDRESS(Structure):
#    pass
#_SOCKET_ADDRESS._fields_ = [
#    ('lpSockaddr', LPSOCKADDR),
#    ('iSockaddrLength', INT),
#]
#SOCKET_ADDRESS = _SOCKET_ADDRESS
#PSOCKET_ADDRESS = POINTER(_SOCKET_ADDRESS)
#LPSOCKET_ADDRESS = POINTER(_SOCKET_ADDRESS)
#class _CSADDR_INFO(Structure):
#    pass
#_CSADDR_INFO._fields_ = [
#    ('LocalAddr', SOCKET_ADDRESS),
#    ('RemoteAddr', SOCKET_ADDRESS),
#    ('iSocketType', INT),
#    ('iProtocol', INT),
#]
#PCSADDR_INFO = POINTER(_CSADDR_INFO)
#LPCSADDR_INFO = POINTER(_CSADDR_INFO)
#CSADDR_INFO = _CSADDR_INFO
#class _SOCKET_ADDRESS_LIST(Structure):
#    pass
#_SOCKET_ADDRESS_LIST._fields_ = [
#    ('iAddressCount', INT),
#    ('Address', SOCKET_ADDRESS * 1),
#]
#LPSOCKET_ADDRESS_LIST = POINTER(_SOCKET_ADDRESS_LIST)
#SOCKET_ADDRESS_LIST = _SOCKET_ADDRESS_LIST
#class _AFPROTOCOLS(Structure):
#    pass
#_AFPROTOCOLS._fields_ = [
#    ('iAddressFamily', INT),
#    ('iProtocol', INT),
#]
#LPAFPROTOCOLS = POINTER(_AFPROTOCOLS)
#PAFPROTOCOLS = POINTER(_AFPROTOCOLS)
#AFPROTOCOLS = _AFPROTOCOLS
#
## values for enumeration '_WSAEcomparator'
#_WSAEcomparator = c_int # enum
#WSAECOMPARATOR = _WSAEcomparator
#LPWSAECOMPARATOR = POINTER(_WSAEcomparator)
#PWSAECOMPARATOR = POINTER(_WSAEcomparator)
#class _WSAVersion(Structure):
#    pass
#_WSAVersion._fields_ = [
#    ('dwVersion', DWORD),
#    ('ecHow', WSAECOMPARATOR),
#]
#WSAVERSION = _WSAVersion
#LPWSAVERSION = POINTER(_WSAVersion)
#PWSAVERSION = POINTER(_WSAVersion)
#class _WSAQuerySetA(Structure):
#    pass
#_WSAQuerySetA._fields_ = [
#    ('dwSize', DWORD),
#    ('lpszServiceInstanceName', LPSTR),
#    ('lpServiceClassId', LPGUID),
#    ('lpVersion', LPWSAVERSION),
#    ('lpszComment', LPSTR),
#    ('dwNameSpace', DWORD),
#    ('lpNSProviderId', LPGUID),
#    ('lpszContext', LPSTR),
#    ('dwNumberOfProtocols', DWORD),
#    ('lpafpProtocols', LPAFPROTOCOLS),
#    ('lpszQueryString', LPSTR),
#    ('dwNumberOfCsAddrs', DWORD),
#    ('lpcsaBuffer', LPCSADDR_INFO),
#    ('dwOutputFlags', DWORD),
#    ('lpBlob', LPBLOB),
#]
#WSAQUERYSETA = _WSAQuerySetA
#LPWSAQUERYSETA = POINTER(_WSAQuerySetA)
#PWSAQUERYSETA = POINTER(_WSAQuerySetA)
#class _WSAQuerySetW(Structure):
#    pass
#_WSAQuerySetW._fields_ = [
#    ('dwSize', DWORD),
#    ('lpszServiceInstanceName', LPWSTR),
#    ('lpServiceClassId', LPGUID),
#    ('lpVersion', LPWSAVERSION),
#    ('lpszComment', LPWSTR),
#    ('dwNameSpace', DWORD),
#    ('lpNSProviderId', LPGUID),
#    ('lpszContext', LPWSTR),
#    ('dwNumberOfProtocols', DWORD),
#    ('lpafpProtocols', LPAFPROTOCOLS),
#    ('lpszQueryString', LPWSTR),
#    ('dwNumberOfCsAddrs', DWORD),
#    ('lpcsaBuffer', LPCSADDR_INFO),
#    ('dwOutputFlags', DWORD),
#    ('lpBlob', LPBLOB),
#]
#LPWSAQUERYSETW = POINTER(_WSAQuerySetW)
#WSAQUERYSETW = _WSAQuerySetW
#PWSAQUERYSETW = POINTER(_WSAQuerySetW)
#WSAQUERYSET = WSAQUERYSETA
#PWSAQUERYSET = PWSAQUERYSETA
#LPWSAQUERYSET = LPWSAQUERYSETA
#
## values for enumeration '_WSAESETSERVICEOP'
#_WSAESETSERVICEOP = c_int # enum
#WSAESETSERVICEOP = _WSAESETSERVICEOP
#LPWSAESETSERVICEOP = POINTER(_WSAESETSERVICEOP)
#PWSAESETSERVICEOP = POINTER(_WSAESETSERVICEOP)
#class _WSANSClassInfoA(Structure):
#    pass
#_WSANSClassInfoA._fields_ = [
#    ('lpszName', LPSTR),
#    ('dwNameSpace', DWORD),
#    ('dwValueType', DWORD),
#    ('dwValueSize', DWORD),
#    ('lpValue', LPVOID),
#]
#WSANSCLASSINFOA = _WSANSClassInfoA
#PWSANSCLASSINFOA = POINTER(_WSANSClassInfoA)
#LPWSANSCLASSINFOA = POINTER(_WSANSClassInfoA)
#class _WSANSClassInfoW(Structure):
#    pass
#_WSANSClassInfoW._fields_ = [
#    ('lpszName', LPWSTR),
#    ('dwNameSpace', DWORD),
#    ('dwValueType', DWORD),
#    ('dwValueSize', DWORD),
#    ('lpValue', LPVOID),
#]
#PWSANSCLASSINFOW = POINTER(_WSANSClassInfoW)
#WSANSCLASSINFOW = _WSANSClassInfoW
#LPWSANSCLASSINFOW = POINTER(_WSANSClassInfoW)
#WSANSCLASSINFO = WSANSCLASSINFOA
#PWSANSCLASSINFO = PWSANSCLASSINFOA
#LPWSANSCLASSINFO = LPWSANSCLASSINFOA
#class _WSAServiceClassInfoA(Structure):
#    pass
#_WSAServiceClassInfoA._fields_ = [
#    ('lpServiceClassId', LPGUID),
#    ('lpszServiceClassName', LPSTR),
#    ('dwCount', DWORD),
#    ('lpClassInfos', LPWSANSCLASSINFOA),
#]
#PWSASERVICECLASSINFOA = POINTER(_WSAServiceClassInfoA)
#WSASERVICECLASSINFOA = _WSAServiceClassInfoA
#LPWSASERVICECLASSINFOA = POINTER(_WSAServiceClassInfoA)
#class _WSAServiceClassInfoW(Structure):
#    pass
#_WSAServiceClassInfoW._fields_ = [
#    ('lpServiceClassId', LPGUID),
#    ('lpszServiceClassName', LPWSTR),
#    ('dwCount', DWORD),
#    ('lpClassInfos', LPWSANSCLASSINFOW),
#]
#LPWSASERVICECLASSINFOW = POINTER(_WSAServiceClassInfoW)
#WSASERVICECLASSINFOW = _WSAServiceClassInfoW
#PWSASERVICECLASSINFOW = POINTER(_WSAServiceClassInfoW)
#WSASERVICECLASSINFO = WSASERVICECLASSINFOA
#PWSASERVICECLASSINFO = PWSASERVICECLASSINFOA
#LPWSASERVICECLASSINFO = LPWSASERVICECLASSINFOA
#class _WSANAMESPACE_INFOA(Structure):
#    pass
#_WSANAMESPACE_INFOA._fields_ = [
#    ('NSProviderId', GUID),
#    ('dwNameSpace', DWORD),
#    ('fActive', BOOL),
#    ('dwVersion', DWORD),
#    ('lpszIdentifier', LPSTR),
#]
#PWSANAMESPACE_INFOA = POINTER(_WSANAMESPACE_INFOA)
#WSANAMESPACE_INFOA = _WSANAMESPACE_INFOA
#LPWSANAMESPACE_INFOA = POINTER(_WSANAMESPACE_INFOA)
#class _WSANAMESPACE_INFOW(Structure):
#    pass
#_WSANAMESPACE_INFOW._fields_ = [
#    ('NSProviderId', GUID),
#    ('dwNameSpace', DWORD),
#    ('fActive', BOOL),
#    ('dwVersion', DWORD),
#    ('lpszIdentifier', LPWSTR),
#]
#WSANAMESPACE_INFOW = _WSANAMESPACE_INFOW
#LPWSANAMESPACE_INFOW = POINTER(_WSANAMESPACE_INFOW)
#PWSANAMESPACE_INFOW = POINTER(_WSANAMESPACE_INFOW)
#WSANAMESPACE_INFO = WSANAMESPACE_INFOA
#PWSANAMESPACE_INFO = PWSANAMESPACE_INFOA
#LPWSANAMESPACE_INFO = LPWSANAMESPACE_INFOA
#SOCKADDR_IN = sockaddr_in
#PSOCKADDR_IN = POINTER(sockaddr_in)
#LPSOCKADDR_IN = POINTER(sockaddr_in)
#LINGER = linger
#PLINGER = POINTER(linger)
#LPLINGER = POINTER(linger)
#IN_ADDR = in_addr
#PIN_ADDR = POINTER(in_addr)
#LPIN_ADDR = POINTER(in_addr)
#FD_SET = fd_set
#PFD_SET = POINTER(fd_set)
#LPFD_SET = POINTER(fd_set)
#HOSTENT = hostent
#PHOSTENT = POINTER(hostent)
#LPHOSTENT = POINTER(hostent)
#SERVENT = servent
#PSERVENT = POINTER(servent)
#LPSERVENT = POINTER(servent)
#PROTOENT = protoent
#PPROTOENT = POINTER(protoent)
#LPPROTOENT = POINTER(protoent)
#TIMEVAL = timeval
#PTIMEVAL = POINTER(timeval)
#LPTIMEVAL = POINTER(timeval)
#class _SERVICE_DESCRIPTIONA(Structure):
#    pass
#_SERVICE_DESCRIPTIONA._fields_ = [
#    ('lpDescription', LPSTR),
#]
#SERVICE_DESCRIPTIONA = _SERVICE_DESCRIPTIONA
#LPSERVICE_DESCRIPTIONA = POINTER(_SERVICE_DESCRIPTIONA)
#class _SERVICE_DESCRIPTIONW(Structure):
#    pass
#_SERVICE_DESCRIPTIONW._fields_ = [
#    ('lpDescription', LPWSTR),
#]
#LPSERVICE_DESCRIPTIONW = POINTER(_SERVICE_DESCRIPTIONW)
#SERVICE_DESCRIPTIONW = _SERVICE_DESCRIPTIONW
#SERVICE_DESCRIPTION = SERVICE_DESCRIPTIONA
#LPSERVICE_DESCRIPTION = LPSERVICE_DESCRIPTIONA
#
## values for enumeration '_SC_ACTION_TYPE'
#_SC_ACTION_TYPE = c_int # enum
#SC_ACTION_TYPE = _SC_ACTION_TYPE
#class _SC_ACTION(Structure):
#    pass
#_SC_ACTION._fields_ = [
#    ('Type', SC_ACTION_TYPE),
#    ('Delay', DWORD),
#]
#SC_ACTION = _SC_ACTION
#LPSC_ACTION = POINTER(_SC_ACTION)
#class _SERVICE_FAILURE_ACTIONSA(Structure):
#    pass
#_SERVICE_FAILURE_ACTIONSA._fields_ = [
#    ('dwResetPeriod', DWORD),
#    ('lpRebootMsg', LPSTR),
#    ('lpCommand', LPSTR),
#    ('cActions', DWORD),
#    ('lpsaActions', POINTER(SC_ACTION)),
#]
#LPSERVICE_FAILURE_ACTIONSA = POINTER(_SERVICE_FAILURE_ACTIONSA)
#SERVICE_FAILURE_ACTIONSA = _SERVICE_FAILURE_ACTIONSA
#class _SERVICE_FAILURE_ACTIONSW(Structure):
#    pass
#_SERVICE_FAILURE_ACTIONSW._fields_ = [
#    ('dwResetPeriod', DWORD),
#    ('lpRebootMsg', LPWSTR),
#    ('lpCommand', LPWSTR),
#    ('cActions', DWORD),
#    ('lpsaActions', POINTER(SC_ACTION)),
#]
#SERVICE_FAILURE_ACTIONSW = _SERVICE_FAILURE_ACTIONSW
#LPSERVICE_FAILURE_ACTIONSW = POINTER(_SERVICE_FAILURE_ACTIONSW)
#SERVICE_FAILURE_ACTIONS = SERVICE_FAILURE_ACTIONSA
#LPSERVICE_FAILURE_ACTIONS = LPSERVICE_FAILURE_ACTIONSA
#class SC_HANDLE__(Structure):
#    pass
#SC_HANDLE__._fields_ = [
#    ('unused', c_int),
#]
#LPSC_HANDLE = POINTER(SC_HANDLE)
#class SERVICE_STATUS_HANDLE__(Structure):
#    pass
#SERVICE_STATUS_HANDLE__._fields_ = [
#    ('unused', c_int),
#]
#
## values for enumeration '_SC_STATUS_TYPE'
#_SC_STATUS_TYPE = c_int # enum
#SC_STATUS_TYPE = _SC_STATUS_TYPE
#
## values for enumeration '_SC_ENUM_TYPE'
#_SC_ENUM_TYPE = c_int # enum
#SC_ENUM_TYPE = _SC_ENUM_TYPE
#class _SERVICE_STATUS(Structure):
#    pass
#_SERVICE_STATUS._fields_ = [
#    ('dwServiceType', DWORD),
#    ('dwCurrentState', DWORD),
#    ('dwControlsAccepted', DWORD),
#    ('dwWin32ExitCode', DWORD),
#    ('dwServiceSpecificExitCode', DWORD),
#    ('dwCheckPoint', DWORD),
#    ('dwWaitHint', DWORD),
#]
#SERVICE_STATUS = _SERVICE_STATUS
#LPSERVICE_STATUS = POINTER(_SERVICE_STATUS)
#class _SERVICE_STATUS_PROCESS(Structure):
#    pass
#_SERVICE_STATUS_PROCESS._fields_ = [
#    ('dwServiceType', DWORD),
#    ('dwCurrentState', DWORD),
#    ('dwControlsAccepted', DWORD),
#    ('dwWin32ExitCode', DWORD),
#    ('dwServiceSpecificExitCode', DWORD),
#    ('dwCheckPoint', DWORD),
#    ('dwWaitHint', DWORD),
#    ('dwProcessId', DWORD),
#    ('dwServiceFlags', DWORD),
#]
#LPSERVICE_STATUS_PROCESS = POINTER(_SERVICE_STATUS_PROCESS)
#SERVICE_STATUS_PROCESS = _SERVICE_STATUS_PROCESS
#class _ENUM_SERVICE_STATUSA(Structure):
#    pass
#_ENUM_SERVICE_STATUSA._fields_ = [
#    ('lpServiceName', LPSTR),
#    ('lpDisplayName', LPSTR),
#    ('ServiceStatus', SERVICE_STATUS),
#]
#ENUM_SERVICE_STATUSA = _ENUM_SERVICE_STATUSA
#LPENUM_SERVICE_STATUSA = POINTER(_ENUM_SERVICE_STATUSA)
#class _ENUM_SERVICE_STATUSW(Structure):
#    pass
#_ENUM_SERVICE_STATUSW._fields_ = [
#    ('lpServiceName', LPWSTR),
#    ('lpDisplayName', LPWSTR),
#    ('ServiceStatus', SERVICE_STATUS),
#]
#ENUM_SERVICE_STATUSW = _ENUM_SERVICE_STATUSW
#LPENUM_SERVICE_STATUSW = POINTER(_ENUM_SERVICE_STATUSW)
#ENUM_SERVICE_STATUS = ENUM_SERVICE_STATUSA
#LPENUM_SERVICE_STATUS = LPENUM_SERVICE_STATUSA
#class _ENUM_SERVICE_STATUS_PROCESSA(Structure):
#    pass
#_ENUM_SERVICE_STATUS_PROCESSA._fields_ = [
#    ('lpServiceName', LPSTR),
#    ('lpDisplayName', LPSTR),
#    ('ServiceStatusProcess', SERVICE_STATUS_PROCESS),
#]
#LPENUM_SERVICE_STATUS_PROCESSA = POINTER(_ENUM_SERVICE_STATUS_PROCESSA)
#ENUM_SERVICE_STATUS_PROCESSA = _ENUM_SERVICE_STATUS_PROCESSA
#class _ENUM_SERVICE_STATUS_PROCESSW(Structure):
#    pass
#_ENUM_SERVICE_STATUS_PROCESSW._fields_ = [
#    ('lpServiceName', LPWSTR),
#    ('lpDisplayName', LPWSTR),
#    ('ServiceStatusProcess', SERVICE_STATUS_PROCESS),
#]
#LPENUM_SERVICE_STATUS_PROCESSW = POINTER(_ENUM_SERVICE_STATUS_PROCESSW)
#ENUM_SERVICE_STATUS_PROCESSW = _ENUM_SERVICE_STATUS_PROCESSW
#ENUM_SERVICE_STATUS_PROCESS = ENUM_SERVICE_STATUS_PROCESSA
#LPENUM_SERVICE_STATUS_PROCESS = LPENUM_SERVICE_STATUS_PROCESSA
#SC_LOCK = LPVOID
#class _QUERY_SERVICE_LOCK_STATUSA(Structure):
#    pass
#_QUERY_SERVICE_LOCK_STATUSA._fields_ = [
#    ('fIsLocked', DWORD),
#    ('lpLockOwner', LPSTR),
#    ('dwLockDuration', DWORD),
#]
#LPQUERY_SERVICE_LOCK_STATUSA = POINTER(_QUERY_SERVICE_LOCK_STATUSA)
#QUERY_SERVICE_LOCK_STATUSA = _QUERY_SERVICE_LOCK_STATUSA
#class _QUERY_SERVICE_LOCK_STATUSW(Structure):
#    pass
#_QUERY_SERVICE_LOCK_STATUSW._fields_ = [
#    ('fIsLocked', DWORD),
#    ('lpLockOwner', LPWSTR),
#    ('dwLockDuration', DWORD),
#]
#LPQUERY_SERVICE_LOCK_STATUSW = POINTER(_QUERY_SERVICE_LOCK_STATUSW)
#QUERY_SERVICE_LOCK_STATUSW = _QUERY_SERVICE_LOCK_STATUSW
#QUERY_SERVICE_LOCK_STATUS = QUERY_SERVICE_LOCK_STATUSA
#LPQUERY_SERVICE_LOCK_STATUS = LPQUERY_SERVICE_LOCK_STATUSA
#class _QUERY_SERVICE_CONFIGA(Structure):
#    pass
#_QUERY_SERVICE_CONFIGA._fields_ = [
#    ('dwServiceType', DWORD),
#    ('dwStartType', DWORD),
#    ('dwErrorControl', DWORD),
#    ('lpBinaryPathName', LPSTR),
#    ('lpLoadOrderGroup', LPSTR),
#    ('dwTagId', DWORD),
#    ('lpDependencies', LPSTR),
#    ('lpServiceStartName', LPSTR),
#    ('lpDisplayName', LPSTR),
#]
#LPQUERY_SERVICE_CONFIGA = POINTER(_QUERY_SERVICE_CONFIGA)
#QUERY_SERVICE_CONFIGA = _QUERY_SERVICE_CONFIGA
#class _QUERY_SERVICE_CONFIGW(Structure):
#    pass
#_QUERY_SERVICE_CONFIGW._fields_ = [
#    ('dwServiceType', DWORD),
#    ('dwStartType', DWORD),
#    ('dwErrorControl', DWORD),
#    ('lpBinaryPathName', LPWSTR),
#    ('lpLoadOrderGroup', LPWSTR),
#    ('dwTagId', DWORD),
#    ('lpDependencies', LPWSTR),
#    ('lpServiceStartName', LPWSTR),
#    ('lpDisplayName', LPWSTR),
#]
#LPQUERY_SERVICE_CONFIGW = POINTER(_QUERY_SERVICE_CONFIGW)
#QUERY_SERVICE_CONFIGW = _QUERY_SERVICE_CONFIGW
#QUERY_SERVICE_CONFIG = QUERY_SERVICE_CONFIGA
#LPQUERY_SERVICE_CONFIG = LPQUERY_SERVICE_CONFIGA
#LPSERVICE_MAIN_FUNCTIONW = WINFUNCTYPE(None, c_ulong, POINTER(LPWSTR))
#LPSERVICE_MAIN_FUNCTIONA = WINFUNCTYPE(None, c_ulong, POINTER(LPSTR))
#class _SERVICE_TABLE_ENTRYA(Structure):
#    pass
#_SERVICE_TABLE_ENTRYA._fields_ = [
#    ('lpServiceName', LPSTR),
#    ('lpServiceProc', LPSERVICE_MAIN_FUNCTIONA),
#]
#SERVICE_TABLE_ENTRYA = _SERVICE_TABLE_ENTRYA
#LPSERVICE_TABLE_ENTRYA = POINTER(_SERVICE_TABLE_ENTRYA)
#class _SERVICE_TABLE_ENTRYW(Structure):
#    pass
#_SERVICE_TABLE_ENTRYW._fields_ = [
#    ('lpServiceName', LPWSTR),
#    ('lpServiceProc', LPSERVICE_MAIN_FUNCTIONW),
#]
#SERVICE_TABLE_ENTRYW = _SERVICE_TABLE_ENTRYW
#LPSERVICE_TABLE_ENTRYW = POINTER(_SERVICE_TABLE_ENTRYW)
#SERVICE_TABLE_ENTRY = SERVICE_TABLE_ENTRYA
#LPSERVICE_TABLE_ENTRY = LPSERVICE_TABLE_ENTRYA
#LPHANDLER_FUNCTION = WINFUNCTYPE(None, c_ulong)
#LPHANDLER_FUNCTION_EX = WINFUNCTYPE(DWORD, c_ulong, c_ulong, c_void_p, c_void_p)
#MENUTEMPLATEA = None
#MENUTEMPLATEW = None
#MENUTEMPLATE = MENUTEMPLATEA
#LPMENUTEMPLATEA = PVOID
#LPMENUTEMPLATEW = PVOID
#LPMENUTEMPLATE = LPMENUTEMPLATEA
#WNDPROC = WINFUNCTYPE(LRESULT, POINTER(HWND__), c_uint, c_uint, c_long)
#DLGPROC = WINFUNCTYPE(INT_PTR, POINTER(HWND__), c_uint, c_uint, c_long)
#TIMERPROC = WINFUNCTYPE(None, POINTER(HWND__), c_uint, c_uint, c_ulong)
#GRAYSTRINGPROC = WINFUNCTYPE(BOOL, POINTER(HDC__), c_long, c_int)
#WNDENUMPROC = WINFUNCTYPE(BOOL, POINTER(HWND__), c_long)
#HOOKPROC = WINFUNCTYPE(LRESULT, c_int, c_uint, c_long)
#SENDASYNCPROC = WINFUNCTYPE(None, POINTER(HWND__), c_uint, c_ulong, c_long)
#PROPENUMPROCA = WINFUNCTYPE(BOOL, POINTER(HWND__), STRING, c_void_p)
#PROPENUMPROCW = WINFUNCTYPE(BOOL, POINTER(HWND__), WSTRING, c_void_p)
#PROPENUMPROCEXA = WINFUNCTYPE(BOOL, POINTER(HWND__), STRING, c_void_p, c_ulong)
#PROPENUMPROCEXW = WINFUNCTYPE(BOOL, POINTER(HWND__), WSTRING, c_void_p, c_ulong)
#EDITWORDBREAKPROCA = WINFUNCTYPE(c_int, STRING, c_int, c_int, c_int)
#EDITWORDBREAKPROCW = WINFUNCTYPE(c_int, WSTRING, c_int, c_int, c_int)
#DRAWSTATEPROC = WINFUNCTYPE(BOOL, POINTER(HDC__), c_long, c_uint, c_int, c_int)
#PROPENUMPROC = PROPENUMPROCA
#PROPENUMPROCEX = PROPENUMPROCEXA
#EDITWORDBREAKPROC = EDITWORDBREAKPROCA
#NAMEENUMPROCA = WINFUNCTYPE(BOOL, STRING, c_long)
#NAMEENUMPROCW = WINFUNCTYPE(BOOL, WSTRING, c_long)
#WINSTAENUMPROCA = NAMEENUMPROCA
#DESKTOPENUMPROCA = NAMEENUMPROCA
#WINSTAENUMPROCW = NAMEENUMPROCW
#DESKTOPENUMPROCW = NAMEENUMPROCW
#WINSTAENUMPROC = WINSTAENUMPROCA
#DESKTOPENUMPROC = DESKTOPENUMPROCA
#class tagCBT_CREATEWNDA(Structure):
#    pass
#class tagCREATESTRUCTA(Structure):
#    pass
#tagCBT_CREATEWNDA._fields_ = [
#    ('lpcs', POINTER(tagCREATESTRUCTA)),
#    ('hwndInsertAfter', HWND),
#]
#CBT_CREATEWNDA = tagCBT_CREATEWNDA
#LPCBT_CREATEWNDA = POINTER(tagCBT_CREATEWNDA)
#class tagCBT_CREATEWNDW(Structure):
#    pass
#class tagCREATESTRUCTW(Structure):
#    pass
#tagCBT_CREATEWNDW._fields_ = [
#    ('lpcs', POINTER(tagCREATESTRUCTW)),
#    ('hwndInsertAfter', HWND),
#]
#CBT_CREATEWNDW = tagCBT_CREATEWNDW
#LPCBT_CREATEWNDW = POINTER(tagCBT_CREATEWNDW)
#CBT_CREATEWND = CBT_CREATEWNDA
#LPCBT_CREATEWND = LPCBT_CREATEWNDA
#class tagCBTACTIVATESTRUCT(Structure):
#    pass
#tagCBTACTIVATESTRUCT._fields_ = [
#    ('fMouse', BOOL),
#    ('hWndActive', HWND),
#]
#LPCBTACTIVATESTRUCT = POINTER(tagCBTACTIVATESTRUCT)
#CBTACTIVATESTRUCT = tagCBTACTIVATESTRUCT
#class SHELLHOOKINFO(Structure):
#    pass
#LPSHELLHOOKINFO = POINTER(SHELLHOOKINFO)
#SHELLHOOKINFO._fields_ = [
#    ('hwnd', HWND),
#    ('rc', RECT),
#]
#class tagEVENTMSG(Structure):
#    pass
#tagEVENTMSG._fields_ = [
#    ('message', UINT),
#    ('paramL', UINT),
#    ('paramH', UINT),
#    ('time', DWORD),
#    ('hwnd', HWND),
#]
#EVENTMSG = tagEVENTMSG
#LPEVENTMSGMSG = POINTER(tagEVENTMSG)
#NPEVENTMSGMSG = POINTER(tagEVENTMSG)
#PEVENTMSGMSG = POINTER(tagEVENTMSG)
#PEVENTMSG = POINTER(tagEVENTMSG)
#LPEVENTMSG = POINTER(tagEVENTMSG)
#NPEVENTMSG = POINTER(tagEVENTMSG)
#class tagCWPSTRUCT(Structure):
#    pass
#tagCWPSTRUCT._fields_ = [
#    ('lParam', LPARAM),
#    ('wParam', WPARAM),
#    ('message', UINT),
#    ('hwnd', HWND),
#]
#LPCWPSTRUCT = POINTER(tagCWPSTRUCT)
#NPCWPSTRUCT = POINTER(tagCWPSTRUCT)
#PCWPSTRUCT = POINTER(tagCWPSTRUCT)
#CWPSTRUCT = tagCWPSTRUCT
#class tagCWPRETSTRUCT(Structure):
#    pass
#tagCWPRETSTRUCT._fields_ = [
#    ('lResult', LRESULT),
#    ('lParam', LPARAM),
#    ('wParam', WPARAM),
#    ('message', UINT),
#    ('hwnd', HWND),
#]
#LPCWPRETSTRUCT = POINTER(tagCWPRETSTRUCT)
#NPCWPRETSTRUCT = POINTER(tagCWPRETSTRUCT)
#CWPRETSTRUCT = tagCWPRETSTRUCT
#PCWPRETSTRUCT = POINTER(tagCWPRETSTRUCT)
#class tagKBDLLHOOKSTRUCT(Structure):
#    pass
#tagKBDLLHOOKSTRUCT._fields_ = [
#    ('vkCode', DWORD),
#    ('scanCode', DWORD),
#    ('flags', DWORD),
#    ('time', DWORD),
#    ('dwExtraInfo', ULONG_PTR),
#]
#LPKBDLLHOOKSTRUCT = POINTER(tagKBDLLHOOKSTRUCT)
#KBDLLHOOKSTRUCT = tagKBDLLHOOKSTRUCT
#PKBDLLHOOKSTRUCT = POINTER(tagKBDLLHOOKSTRUCT)
#class tagMSLLHOOKSTRUCT(Structure):
#    pass
#tagMSLLHOOKSTRUCT._fields_ = [
#    ('pt', POINT),
#    ('mouseData', DWORD),
#    ('flags', DWORD),
#    ('time', DWORD),
#    ('dwExtraInfo', ULONG_PTR),
#]
#MSLLHOOKSTRUCT = tagMSLLHOOKSTRUCT
#PMSLLHOOKSTRUCT = POINTER(tagMSLLHOOKSTRUCT)
#LPMSLLHOOKSTRUCT = POINTER(tagMSLLHOOKSTRUCT)
#class tagDEBUGHOOKINFO(Structure):
#    pass
#tagDEBUGHOOKINFO._fields_ = [
#    ('idThread', DWORD),
#    ('idThreadInstaller', DWORD),
#    ('lParam', LPARAM),
#    ('wParam', WPARAM),
#    ('code', c_int),
#]
#LPDEBUGHOOKINFO = POINTER(tagDEBUGHOOKINFO)
#DEBUGHOOKINFO = tagDEBUGHOOKINFO
#NPDEBUGHOOKINFO = POINTER(tagDEBUGHOOKINFO)
#PDEBUGHOOKINFO = POINTER(tagDEBUGHOOKINFO)
#class tagMOUSEHOOKSTRUCT(Structure):
#    pass
#tagMOUSEHOOKSTRUCT._fields_ = [
#    ('pt', POINT),
#    ('hwnd', HWND),
#    ('wHitTestCode', UINT),
#    ('dwExtraInfo', ULONG_PTR),
#]
#MOUSEHOOKSTRUCT = tagMOUSEHOOKSTRUCT
#PMOUSEHOOKSTRUCT = POINTER(tagMOUSEHOOKSTRUCT)
#LPMOUSEHOOKSTRUCT = POINTER(tagMOUSEHOOKSTRUCT)
#class tagHARDWAREHOOKSTRUCT(Structure):
#    pass
#tagHARDWAREHOOKSTRUCT._fields_ = [
#    ('hwnd', HWND),
#    ('message', UINT),
#    ('wParam', WPARAM),
#    ('lParam', LPARAM),
#]
#HARDWAREHOOKSTRUCT = tagHARDWAREHOOKSTRUCT
#PHARDWAREHOOKSTRUCT = POINTER(tagHARDWAREHOOKSTRUCT)
#LPHARDWAREHOOKSTRUCT = POINTER(tagHARDWAREHOOKSTRUCT)
#class tagMOUSEMOVEPOINT(Structure):
#    pass
#tagMOUSEMOVEPOINT._fields_ = [
#    ('x', c_int),
#    ('y', c_int),
#    ('time', DWORD),
#    ('dwExtraInfo', ULONG_PTR),
#]
#PMOUSEMOVEPOINT = POINTER(tagMOUSEMOVEPOINT)
#MOUSEMOVEPOINT = tagMOUSEMOVEPOINT
#LPMOUSEMOVEPOINT = POINTER(tagMOUSEMOVEPOINT)
#class tagUSEROBJECTFLAGS(Structure):
#    pass
#tagUSEROBJECTFLAGS._fields_ = [
#    ('fInherit', BOOL),
#    ('fReserved', BOOL),
#    ('dwFlags', DWORD),
#]
#USEROBJECTFLAGS = tagUSEROBJECTFLAGS
#PUSEROBJECTFLAGS = POINTER(tagUSEROBJECTFLAGS)
#class tagWNDCLASSEXA(Structure):
#    pass
#tagWNDCLASSEXA._fields_ = [
#    ('cbSize', UINT),
#    ('style', UINT),
#    ('lpfnWndProc', WNDPROC),
#    ('cbClsExtra', c_int),
#    ('cbWndExtra', c_int),
#    ('hInstance', HINSTANCE),
#    ('hIcon', HICON),
#    ('hCursor', HCURSOR),
#    ('hbrBackground', HBRUSH),
#    ('lpszMenuName', LPCSTR),
#    ('lpszClassName', LPCSTR),
#    ('hIconSm', HICON),
#]
#NPWNDCLASSEXA = POINTER(tagWNDCLASSEXA)
#LPWNDCLASSEXA = POINTER(tagWNDCLASSEXA)
#WNDCLASSEXA = tagWNDCLASSEXA
#PWNDCLASSEXA = POINTER(tagWNDCLASSEXA)
#class tagWNDCLASSEXW(Structure):
#    pass
#tagWNDCLASSEXW._fields_ = [
#    ('cbSize', UINT),
#    ('style', UINT),
#    ('lpfnWndProc', WNDPROC),
#    ('cbClsExtra', c_int),
#    ('cbWndExtra', c_int),
#    ('hInstance', HINSTANCE),
#    ('hIcon', HICON),
#    ('hCursor', HCURSOR),
#    ('hbrBackground', HBRUSH),
#    ('lpszMenuName', LPCWSTR),
#    ('lpszClassName', LPCWSTR),
#    ('hIconSm', HICON),
#]
#PWNDCLASSEXW = POINTER(tagWNDCLASSEXW)
#WNDCLASSEXW = tagWNDCLASSEXW
#LPWNDCLASSEXW = POINTER(tagWNDCLASSEXW)
#NPWNDCLASSEXW = POINTER(tagWNDCLASSEXW)
#WNDCLASSEX = WNDCLASSEXA
#PWNDCLASSEX = PWNDCLASSEXA
#NPWNDCLASSEX = NPWNDCLASSEXA
#LPWNDCLASSEX = LPWNDCLASSEXA
#class tagWNDCLASSA(Structure):
#    pass
#tagWNDCLASSA._fields_ = [
#    ('style', UINT),
#    ('lpfnWndProc', WNDPROC),
#    ('cbClsExtra', c_int),
#    ('cbWndExtra', c_int),
#    ('hInstance', HINSTANCE),
#    ('hIcon', HICON),
#    ('hCursor', HCURSOR),
#    ('hbrBackground', HBRUSH),
#    ('lpszMenuName', LPCSTR),
#    ('lpszClassName', LPCSTR),
#]
#PWNDCLASSA = POINTER(tagWNDCLASSA)
#LPWNDCLASSA = POINTER(tagWNDCLASSA)
#WNDCLASSA = tagWNDCLASSA
#NPWNDCLASSA = POINTER(tagWNDCLASSA)
#class tagWNDCLASSW(Structure):
#    pass
#tagWNDCLASSW._fields_ = [
#    ('style', UINT),
#    ('lpfnWndProc', WNDPROC),
#    ('cbClsExtra', c_int),
#    ('cbWndExtra', c_int),
#    ('hInstance', HINSTANCE),
#    ('hIcon', HICON),
#    ('hCursor', HCURSOR),
#    ('hbrBackground', HBRUSH),
#    ('lpszMenuName', LPCWSTR),
#    ('lpszClassName', LPCWSTR),
#]
#WNDCLASSW = tagWNDCLASSW
#LPWNDCLASSW = POINTER(tagWNDCLASSW)
#NPWNDCLASSW = POINTER(tagWNDCLASSW)
#PWNDCLASSW = POINTER(tagWNDCLASSW)
#WNDCLASS = WNDCLASSA
#PWNDCLASS = PWNDCLASSA
#NPWNDCLASS = NPWNDCLASSA
#LPWNDCLASS = LPWNDCLASSA
#LPMSG = POINTER(tagMSG)
#NPMSG = POINTER(tagMSG)
#PMSG = POINTER(tagMSG)
#class tagMINMAXINFO(Structure):
#    pass
#tagMINMAXINFO._fields_ = [
#    ('ptReserved', POINT),
#    ('ptMaxSize', POINT),
#    ('ptMaxPosition', POINT),
#    ('ptMinTrackSize', POINT),
#    ('ptMaxTrackSize', POINT),
#]
#MINMAXINFO = tagMINMAXINFO
#PMINMAXINFO = POINTER(tagMINMAXINFO)
#LPMINMAXINFO = POINTER(tagMINMAXINFO)
#class tagCOPYDATASTRUCT(Structure):
#    pass
#tagCOPYDATASTRUCT._fields_ = [
#    ('dwData', ULONG_PTR),
#    ('cbData', DWORD),
#    ('lpData', PVOID),
#]
#COPYDATASTRUCT = tagCOPYDATASTRUCT
#PCOPYDATASTRUCT = POINTER(tagCOPYDATASTRUCT)
#class tagMDINEXTMENU(Structure):
#    pass
#tagMDINEXTMENU._fields_ = [
#    ('hmenuIn', HMENU),
#    ('hmenuNext', HMENU),
#    ('hwndNext', HWND),
#]
#PMDINEXTMENU = POINTER(tagMDINEXTMENU)
#LPMDINEXTMENU = POINTER(tagMDINEXTMENU)
#MDINEXTMENU = tagMDINEXTMENU
#class tagWINDOWPOS(Structure):
#    pass
#tagWINDOWPOS._fields_ = [
#    ('hwnd', HWND),
#    ('hwndInsertAfter', HWND),
#    ('x', c_int),
#    ('y', c_int),
#    ('cx', c_int),
#    ('cy', c_int),
#    ('flags', UINT),
#]
#LPWINDOWPOS = POINTER(tagWINDOWPOS)
#PWINDOWPOS = POINTER(tagWINDOWPOS)
#WINDOWPOS = tagWINDOWPOS
#class tagNCCALCSIZE_PARAMS(Structure):
#    pass
#tagNCCALCSIZE_PARAMS._fields_ = [
#    ('rgrc', RECT * 3),
#    ('lppos', PWINDOWPOS),
#]
#NCCALCSIZE_PARAMS = tagNCCALCSIZE_PARAMS
#LPNCCALCSIZE_PARAMS = POINTER(tagNCCALCSIZE_PARAMS)
#class tagTRACKMOUSEEVENT(Structure):
#    pass
#tagTRACKMOUSEEVENT._fields_ = [
#    ('cbSize', DWORD),
#    ('dwFlags', DWORD),
#    ('hwndTrack', HWND),
#    ('dwHoverTime', DWORD),
#]
#LPTRACKMOUSEEVENT = POINTER(tagTRACKMOUSEEVENT)
#TRACKMOUSEEVENT = tagTRACKMOUSEEVENT
#class tagACCEL(Structure):
#    pass
#tagACCEL._fields_ = [
#    ('fVirt', BYTE),
#    ('key', WORD),
#    ('cmd', WORD),
#]
#LPACCEL = POINTER(tagACCEL)
#ACCEL = tagACCEL
#class tagPAINTSTRUCT(Structure):
#    pass
#tagPAINTSTRUCT._fields_ = [
#    ('hdc', HDC),
#    ('fErase', BOOL),
#    ('rcPaint', RECT),
#    ('fRestore', BOOL),
#    ('fIncUpdate', BOOL),
#    ('rgbReserved', BYTE * 32),
#]
#LPPAINTSTRUCT = POINTER(tagPAINTSTRUCT)
#PPAINTSTRUCT = POINTER(tagPAINTSTRUCT)
#NPPAINTSTRUCT = POINTER(tagPAINTSTRUCT)
#PAINTSTRUCT = tagPAINTSTRUCT
#tagCREATESTRUCTA._fields_ = [
#    ('lpCreateParams', LPVOID),
#    ('hInstance', HINSTANCE),
#    ('hMenu', HMENU),
#    ('hwndParent', HWND),
#    ('cy', c_int),
#    ('cx', c_int),
#    ('y', c_int),
#    ('x', c_int),
#    ('style', LONG),
#    ('lpszName', LPCSTR),
#    ('lpszClass', LPCSTR),
#    ('dwExStyle', DWORD),
#]
#LPCREATESTRUCTA = POINTER(tagCREATESTRUCTA)
#CREATESTRUCTA = tagCREATESTRUCTA
#tagCREATESTRUCTW._fields_ = [
#    ('lpCreateParams', LPVOID),
#    ('hInstance', HINSTANCE),
#    ('hMenu', HMENU),
#    ('hwndParent', HWND),
#    ('cy', c_int),
#    ('cx', c_int),
#    ('y', c_int),
#    ('x', c_int),
#    ('style', LONG),
#    ('lpszName', LPCWSTR),
#    ('lpszClass', LPCWSTR),
#    ('dwExStyle', DWORD),
#]
#LPCREATESTRUCTW = POINTER(tagCREATESTRUCTW)
#CREATESTRUCTW = tagCREATESTRUCTW
#CREATESTRUCT = CREATESTRUCTA
#LPCREATESTRUCT = LPCREATESTRUCTA
#class tagWINDOWPLACEMENT(Structure):
#    pass
#tagWINDOWPLACEMENT._fields_ = [
#    ('length', UINT),
#    ('flags', UINT),
#    ('showCmd', UINT),
#    ('ptMinPosition', POINT),
#    ('ptMaxPosition', POINT),
#    ('rcNormalPosition', RECT),
#]
#WINDOWPLACEMENT = tagWINDOWPLACEMENT
#LPWINDOWPLACEMENT = POINTER(WINDOWPLACEMENT)
#PWINDOWPLACEMENT = POINTER(WINDOWPLACEMENT)
#class tagNMHDR(Structure):
#    pass
#tagNMHDR._fields_ = [
#    ('hwndFrom', HWND),
#    ('idFrom', UINT_PTR),
#    ('code', UINT),
#]
#NMHDR = tagNMHDR
#LPNMHDR = POINTER(NMHDR)
#class tagSTYLESTRUCT(Structure):
#    pass
#tagSTYLESTRUCT._fields_ = [
#    ('styleOld', DWORD),
#    ('styleNew', DWORD),
#]
#LPSTYLESTRUCT = POINTER(tagSTYLESTRUCT)
#STYLESTRUCT = tagSTYLESTRUCT
#class tagMEASUREITEMSTRUCT(Structure):
#    pass
#tagMEASUREITEMSTRUCT._fields_ = [
#    ('CtlType', UINT),
#    ('CtlID', UINT),
#    ('itemID', UINT),
#    ('itemWidth', UINT),
#    ('itemHeight', UINT),
#    ('itemData', ULONG_PTR),
#]
#LPMEASUREITEMSTRUCT = POINTER(tagMEASUREITEMSTRUCT)
#PMEASUREITEMSTRUCT = POINTER(tagMEASUREITEMSTRUCT)
#MEASUREITEMSTRUCT = tagMEASUREITEMSTRUCT
#class tagDRAWITEMSTRUCT(Structure):
#    pass
#tagDRAWITEMSTRUCT._fields_ = [
#    ('CtlType', UINT),
#    ('CtlID', UINT),
#    ('itemID', UINT),
#    ('itemAction', UINT),
#    ('itemState', UINT),
#    ('hwndItem', HWND),
#    ('hDC', HDC),
#    ('rcItem', RECT),
#    ('itemData', ULONG_PTR),
#]
#PDRAWITEMSTRUCT = POINTER(tagDRAWITEMSTRUCT)
#LPDRAWITEMSTRUCT = POINTER(tagDRAWITEMSTRUCT)
#DRAWITEMSTRUCT = tagDRAWITEMSTRUCT
#class tagDELETEITEMSTRUCT(Structure):
#    pass
#tagDELETEITEMSTRUCT._fields_ = [
#    ('CtlType', UINT),
#    ('CtlID', UINT),
#    ('itemID', UINT),
#    ('hwndItem', HWND),
#    ('itemData', ULONG_PTR),
#]
#PDELETEITEMSTRUCT = POINTER(tagDELETEITEMSTRUCT)
#DELETEITEMSTRUCT = tagDELETEITEMSTRUCT
#LPDELETEITEMSTRUCT = POINTER(tagDELETEITEMSTRUCT)
#class tagCOMPAREITEMSTRUCT(Structure):
#    pass
#tagCOMPAREITEMSTRUCT._fields_ = [
#    ('CtlType', UINT),
#    ('CtlID', UINT),
#    ('hwndItem', HWND),
#    ('itemID1', UINT),
#    ('itemData1', ULONG_PTR),
#    ('itemID2', UINT),
#    ('itemData2', ULONG_PTR),
#    ('dwLocaleId', DWORD),
#]
#COMPAREITEMSTRUCT = tagCOMPAREITEMSTRUCT
#LPCOMPAREITEMSTRUCT = POINTER(tagCOMPAREITEMSTRUCT)
#PCOMPAREITEMSTRUCT = POINTER(tagCOMPAREITEMSTRUCT)
#HDEVNOTIFY = PVOID
#PHDEVNOTIFY = POINTER(HDEVNOTIFY)
#class FLASHWINFO(Structure):
#    pass
#PFLASHWINFO = POINTER(FLASHWINFO)
#FLASHWINFO._fields_ = [
#    ('cbSize', UINT),
#    ('hwnd', HWND),
#    ('dwFlags', DWORD),
#    ('uCount', UINT),
#    ('dwTimeout', DWORD),
#]
#class DLGTEMPLATE(Structure):
#    pass
#DLGTEMPLATE._pack_ = 2
#DLGTEMPLATE._fields_ = [
#    ('style', DWORD),
#    ('dwExtendedStyle', DWORD),
#    ('cdit', WORD),
#    ('x', c_short),
#    ('y', c_short),
#    ('cx', c_short),
#    ('cy', c_short),
#]
#LPDLGTEMPLATEA = POINTER(DLGTEMPLATE)
#LPDLGTEMPLATEW = POINTER(DLGTEMPLATE)
#LPDLGTEMPLATE = LPDLGTEMPLATEA
#LPCDLGTEMPLATEA = POINTER(DLGTEMPLATE)
#LPCDLGTEMPLATEW = POINTER(DLGTEMPLATE)
#LPCDLGTEMPLATE = LPCDLGTEMPLATEA
#class DLGITEMTEMPLATE(Structure):
#    pass
#DLGITEMTEMPLATE._pack_ = 2
#DLGITEMTEMPLATE._fields_ = [
#    ('style', DWORD),
#    ('dwExtendedStyle', DWORD),
#    ('x', c_short),
#    ('y', c_short),
#    ('cx', c_short),
#    ('cy', c_short),
#    ('id', WORD),
#]
#PDLGITEMTEMPLATEA = POINTER(DLGITEMTEMPLATE)
#PDLGITEMTEMPLATEW = POINTER(DLGITEMTEMPLATE)
#PDLGITEMTEMPLATE = PDLGITEMTEMPLATEA
#LPDLGITEMTEMPLATEA = POINTER(DLGITEMTEMPLATE)
#LPDLGITEMTEMPLATEW = POINTER(DLGITEMTEMPLATE)
#LPDLGITEMTEMPLATE = LPDLGITEMTEMPLATEA
#class tagTPMPARAMS(Structure):
#    pass
#tagTPMPARAMS._fields_ = [
#    ('cbSize', UINT),
#    ('rcExclude', RECT),
#]
#TPMPARAMS = tagTPMPARAMS
#LPTPMPARAMS = POINTER(TPMPARAMS)
#class tagMENUINFO(Structure):
#    pass
#tagMENUINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('fMask', DWORD),
#    ('dwStyle', DWORD),
#    ('cyMax', UINT),
#    ('hbrBack', HBRUSH),
#    ('dwContextHelpID', DWORD),
#    ('dwMenuData', ULONG_PTR),
#]
#MENUINFO = tagMENUINFO
#LPMENUINFO = POINTER(tagMENUINFO)
#LPCMENUINFO = POINTER(MENUINFO)
#class tagMENUGETOBJECTINFO(Structure):
#    pass
#tagMENUGETOBJECTINFO._fields_ = [
#    ('dwFlags', DWORD),
#    ('uPos', UINT),
#    ('hmenu', HMENU),
#    ('riid', PVOID),
#    ('pvObj', PVOID),
#]
#PMENUGETOBJECTINFO = POINTER(tagMENUGETOBJECTINFO)
#MENUGETOBJECTINFO = tagMENUGETOBJECTINFO
#class tagMENUITEMINFOA(Structure):
#    pass
#tagMENUITEMINFOA._fields_ = [
#    ('cbSize', UINT),
#    ('fMask', UINT),
#    ('fType', UINT),
#    ('fState', UINT),
#    ('wID', UINT),
#    ('hSubMenu', HMENU),
#    ('hbmpChecked', HBITMAP),
#    ('hbmpUnchecked', HBITMAP),
#    ('dwItemData', ULONG_PTR),
#    ('dwTypeData', LPSTR),
#    ('cch', UINT),
#    ('hbmpItem', HBITMAP),
#]
#LPMENUITEMINFOA = POINTER(tagMENUITEMINFOA)
#MENUITEMINFOA = tagMENUITEMINFOA
#class tagMENUITEMINFOW(Structure):
#    pass
#tagMENUITEMINFOW._fields_ = [
#    ('cbSize', UINT),
#    ('fMask', UINT),
#    ('fType', UINT),
#    ('fState', UINT),
#    ('wID', UINT),
#    ('hSubMenu', HMENU),
#    ('hbmpChecked', HBITMAP),
#    ('hbmpUnchecked', HBITMAP),
#    ('dwItemData', ULONG_PTR),
#    ('dwTypeData', LPWSTR),
#    ('cch', UINT),
#    ('hbmpItem', HBITMAP),
#]
#LPMENUITEMINFOW = POINTER(tagMENUITEMINFOW)
#MENUITEMINFOW = tagMENUITEMINFOW
#MENUITEMINFO = MENUITEMINFOA
#LPMENUITEMINFO = LPMENUITEMINFOA
#LPCMENUITEMINFOA = POINTER(MENUITEMINFOA)
#LPCMENUITEMINFOW = POINTER(MENUITEMINFOW)
#LPCMENUITEMINFO = LPCMENUITEMINFOA
#class tagDROPSTRUCT(Structure):
#    pass
#tagDROPSTRUCT._fields_ = [
#    ('hwndSource', HWND),
#    ('hwndSink', HWND),
#    ('wFmt', DWORD),
#    ('dwData', ULONG_PTR),
#    ('ptDrop', POINT),
#    ('dwControlData', DWORD),
#]
#DROPSTRUCT = tagDROPSTRUCT
#PDROPSTRUCT = POINTER(tagDROPSTRUCT)
#LPDROPSTRUCT = POINTER(tagDROPSTRUCT)
#class tagDRAWTEXTPARAMS(Structure):
#    pass
#tagDRAWTEXTPARAMS._fields_ = [
#    ('cbSize', UINT),
#    ('iTabLength', c_int),
#    ('iLeftMargin', c_int),
#    ('iRightMargin', c_int),
#    ('uiLengthDrawn', UINT),
#]
#LPDRAWTEXTPARAMS = POINTER(tagDRAWTEXTPARAMS)
#DRAWTEXTPARAMS = tagDRAWTEXTPARAMS
#class tagHELPINFO(Structure):
#    pass
#tagHELPINFO._fields_ = [
#    ('cbSize', UINT),
#    ('iContextType', c_int),
#    ('iCtrlId', c_int),
#    ('hItemHandle', HANDLE),
#    ('dwContextId', DWORD_PTR),
#    ('MousePos', POINT),
#]
#LPHELPINFO = POINTER(tagHELPINFO)
#HELPINFO = tagHELPINFO
#MSGBOXCALLBACK = WINFUNCTYPE(None, POINTER(tagHELPINFO))
#class tagMSGBOXPARAMSA(Structure):
#    pass
#tagMSGBOXPARAMSA._fields_ = [
#    ('cbSize', UINT),
#    ('hwndOwner', HWND),
#    ('hInstance', HINSTANCE),
#    ('lpszText', LPCSTR),
#    ('lpszCaption', LPCSTR),
#    ('dwStyle', DWORD),
#    ('lpszIcon', LPCSTR),
#    ('dwContextHelpId', DWORD_PTR),
#    ('lpfnMsgBoxCallback', MSGBOXCALLBACK),
#    ('dwLanguageId', DWORD),
#]
#LPMSGBOXPARAMSA = POINTER(tagMSGBOXPARAMSA)
#PMSGBOXPARAMSA = POINTER(tagMSGBOXPARAMSA)
#MSGBOXPARAMSA = tagMSGBOXPARAMSA
#class tagMSGBOXPARAMSW(Structure):
#    pass
#tagMSGBOXPARAMSW._fields_ = [
#    ('cbSize', UINT),
#    ('hwndOwner', HWND),
#    ('hInstance', HINSTANCE),
#    ('lpszText', LPCWSTR),
#    ('lpszCaption', LPCWSTR),
#    ('dwStyle', DWORD),
#    ('lpszIcon', LPCWSTR),
#    ('dwContextHelpId', DWORD_PTR),
#    ('lpfnMsgBoxCallback', MSGBOXCALLBACK),
#    ('dwLanguageId', DWORD),
#]
#PMSGBOXPARAMSW = POINTER(tagMSGBOXPARAMSW)
#LPMSGBOXPARAMSW = POINTER(tagMSGBOXPARAMSW)
#MSGBOXPARAMSW = tagMSGBOXPARAMSW
#MSGBOXPARAMS = MSGBOXPARAMSA
#PMSGBOXPARAMS = PMSGBOXPARAMSA
#LPMSGBOXPARAMS = LPMSGBOXPARAMSA
#class MENUITEMTEMPLATEHEADER(Structure):
#    pass
#PMENUITEMTEMPLATEHEADER = POINTER(MENUITEMTEMPLATEHEADER)
#MENUITEMTEMPLATEHEADER._fields_ = [
#    ('versionNumber', WORD),
#    ('offset', WORD),
#]
#class MENUITEMTEMPLATE(Structure):
#    pass
#MENUITEMTEMPLATE._fields_ = [
#    ('mtOption', WORD),
#    ('mtID', WORD),
#    ('mtString', WCHAR * 1),
#]
#PMENUITEMTEMPLATE = POINTER(MENUITEMTEMPLATE)
#class _ICONINFO(Structure):
#    pass
#_ICONINFO._fields_ = [
#    ('fIcon', BOOL),
#    ('xHotspot', DWORD),
#    ('yHotspot', DWORD),
#    ('hbmMask', HBITMAP),
#    ('hbmColor', HBITMAP),
#]
#ICONINFO = _ICONINFO
#PICONINFO = POINTER(ICONINFO)
#class tagCURSORSHAPE(Structure):
#    pass
#tagCURSORSHAPE._fields_ = [
#    ('xHotSpot', c_int),
#    ('yHotSpot', c_int),
#    ('cx', c_int),
#    ('cy', c_int),
#    ('cbWidth', c_int),
#    ('Planes', BYTE),
#    ('BitsPixel', BYTE),
#]
#LPCURSORSHAPE = POINTER(tagCURSORSHAPE)
#CURSORSHAPE = tagCURSORSHAPE
#class tagSCROLLINFO(Structure):
#    pass
#tagSCROLLINFO._fields_ = [
#    ('cbSize', UINT),
#    ('fMask', UINT),
#    ('nMin', c_int),
#    ('nMax', c_int),
#    ('nPage', UINT),
#    ('nPos', c_int),
#    ('nTrackPos', c_int),
#]
#LPSCROLLINFO = POINTER(tagSCROLLINFO)
#SCROLLINFO = tagSCROLLINFO
#LPCSCROLLINFO = POINTER(SCROLLINFO)
#class tagMDICREATESTRUCTA(Structure):
#    pass
#tagMDICREATESTRUCTA._fields_ = [
#    ('szClass', LPCSTR),
#    ('szTitle', LPCSTR),
#    ('hOwner', HANDLE),
#    ('x', c_int),
#    ('y', c_int),
#    ('cx', c_int),
#    ('cy', c_int),
#    ('style', DWORD),
#    ('lParam', LPARAM),
#]
#LPMDICREATESTRUCTA = POINTER(tagMDICREATESTRUCTA)
#MDICREATESTRUCTA = tagMDICREATESTRUCTA
#class tagMDICREATESTRUCTW(Structure):
#    pass
#tagMDICREATESTRUCTW._fields_ = [
#    ('szClass', LPCWSTR),
#    ('szTitle', LPCWSTR),
#    ('hOwner', HANDLE),
#    ('x', c_int),
#    ('y', c_int),
#    ('cx', c_int),
#    ('cy', c_int),
#    ('style', DWORD),
#    ('lParam', LPARAM),
#]
#MDICREATESTRUCTW = tagMDICREATESTRUCTW
#LPMDICREATESTRUCTW = POINTER(tagMDICREATESTRUCTW)
#MDICREATESTRUCT = MDICREATESTRUCTA
#LPMDICREATESTRUCT = LPMDICREATESTRUCTA
#class tagCLIENTCREATESTRUCT(Structure):
#    pass
#tagCLIENTCREATESTRUCT._fields_ = [
#    ('hWindowMenu', HANDLE),
#    ('idFirstChild', UINT),
#]
#LPCLIENTCREATESTRUCT = POINTER(tagCLIENTCREATESTRUCT)
#CLIENTCREATESTRUCT = tagCLIENTCREATESTRUCT
#HELPPOLY = DWORD
#class tagMULTIKEYHELPA(Structure):
#    pass
#tagMULTIKEYHELPA._fields_ = [
#    ('mkSize', DWORD),
#    ('mkKeylist', CHAR),
#    ('szKeyphrase', CHAR * 1),
#]
#LPMULTIKEYHELPA = POINTER(tagMULTIKEYHELPA)
#PMULTIKEYHELPA = POINTER(tagMULTIKEYHELPA)
#MULTIKEYHELPA = tagMULTIKEYHELPA
#class tagMULTIKEYHELPW(Structure):
#    pass
#tagMULTIKEYHELPW._fields_ = [
#    ('mkSize', DWORD),
#    ('mkKeylist', WCHAR),
#    ('szKeyphrase', WCHAR * 1),
#]
#LPMULTIKEYHELPW = POINTER(tagMULTIKEYHELPW)
#MULTIKEYHELPW = tagMULTIKEYHELPW
#PMULTIKEYHELPW = POINTER(tagMULTIKEYHELPW)
#MULTIKEYHELP = MULTIKEYHELPA
#PMULTIKEYHELP = PMULTIKEYHELPA
#LPMULTIKEYHELP = LPMULTIKEYHELPA
#class tagHELPWININFOA(Structure):
#    pass
#tagHELPWININFOA._fields_ = [
#    ('wStructSize', c_int),
#    ('x', c_int),
#    ('y', c_int),
#    ('dx', c_int),
#    ('dy', c_int),
#    ('wMax', c_int),
#    ('rgchMember', CHAR * 2),
#]
#HELPWININFOA = tagHELPWININFOA
#LPHELPWININFOA = POINTER(tagHELPWININFOA)
#PHELPWININFOA = POINTER(tagHELPWININFOA)
#class tagHELPWININFOW(Structure):
#    pass
#tagHELPWININFOW._fields_ = [
#    ('wStructSize', c_int),
#    ('x', c_int),
#    ('y', c_int),
#    ('dx', c_int),
#    ('dy', c_int),
#    ('wMax', c_int),
#    ('rgchMember', WCHAR * 2),
#]
#PHELPWININFOW = POINTER(tagHELPWININFOW)
#LPHELPWININFOW = POINTER(tagHELPWININFOW)
#HELPWININFOW = tagHELPWININFOW
#HELPWININFO = HELPWININFOA
#PHELPWININFO = PHELPWININFOA
#LPHELPWININFO = LPHELPWININFOA
#class tagNONCLIENTMETRICSA(Structure):
#    pass
#tagNONCLIENTMETRICSA._fields_ = [
#    ('cbSize', UINT),
#    ('iBorderWidth', c_int),
#    ('iScrollWidth', c_int),
#    ('iScrollHeight', c_int),
#    ('iCaptionWidth', c_int),
#    ('iCaptionHeight', c_int),
#    ('lfCaptionFont', LOGFONTA),
#    ('iSmCaptionWidth', c_int),
#    ('iSmCaptionHeight', c_int),
#    ('lfSmCaptionFont', LOGFONTA),
#    ('iMenuWidth', c_int),
#    ('iMenuHeight', c_int),
#    ('lfMenuFont', LOGFONTA),
#    ('lfStatusFont', LOGFONTA),
#    ('lfMessageFont', LOGFONTA),
#]
#LPNONCLIENTMETRICSA = POINTER(tagNONCLIENTMETRICSA)
#NONCLIENTMETRICSA = tagNONCLIENTMETRICSA
#PNONCLIENTMETRICSA = POINTER(tagNONCLIENTMETRICSA)
#class tagNONCLIENTMETRICSW(Structure):
#    pass
#tagNONCLIENTMETRICSW._fields_ = [
#    ('cbSize', UINT),
#    ('iBorderWidth', c_int),
#    ('iScrollWidth', c_int),
#    ('iScrollHeight', c_int),
#    ('iCaptionWidth', c_int),
#    ('iCaptionHeight', c_int),
#    ('lfCaptionFont', LOGFONTW),
#    ('iSmCaptionWidth', c_int),
#    ('iSmCaptionHeight', c_int),
#    ('lfSmCaptionFont', LOGFONTW),
#    ('iMenuWidth', c_int),
#    ('iMenuHeight', c_int),
#    ('lfMenuFont', LOGFONTW),
#    ('lfStatusFont', LOGFONTW),
#    ('lfMessageFont', LOGFONTW),
#]
#NONCLIENTMETRICSW = tagNONCLIENTMETRICSW
#PNONCLIENTMETRICSW = POINTER(tagNONCLIENTMETRICSW)
#LPNONCLIENTMETRICSW = POINTER(tagNONCLIENTMETRICSW)
#NONCLIENTMETRICS = NONCLIENTMETRICSA
#PNONCLIENTMETRICS = PNONCLIENTMETRICSA
#LPNONCLIENTMETRICS = LPNONCLIENTMETRICSA
#class tagMINIMIZEDMETRICS(Structure):
#    pass
#tagMINIMIZEDMETRICS._fields_ = [
#    ('cbSize', UINT),
#    ('iWidth', c_int),
#    ('iHorzGap', c_int),
#    ('iVertGap', c_int),
#    ('iArrange', c_int),
#]
#PMINIMIZEDMETRICS = POINTER(tagMINIMIZEDMETRICS)
#LPMINIMIZEDMETRICS = POINTER(tagMINIMIZEDMETRICS)
#MINIMIZEDMETRICS = tagMINIMIZEDMETRICS
#class tagICONMETRICSA(Structure):
#    pass
#tagICONMETRICSA._fields_ = [
#    ('cbSize', UINT),
#    ('iHorzSpacing', c_int),
#    ('iVertSpacing', c_int),
#    ('iTitleWrap', c_int),
#    ('lfFont', LOGFONTA),
#]
#PICONMETRICSA = POINTER(tagICONMETRICSA)
#ICONMETRICSA = tagICONMETRICSA
#LPICONMETRICSA = POINTER(tagICONMETRICSA)
#class tagICONMETRICSW(Structure):
#    pass
#tagICONMETRICSW._fields_ = [
#    ('cbSize', UINT),
#    ('iHorzSpacing', c_int),
#    ('iVertSpacing', c_int),
#    ('iTitleWrap', c_int),
#    ('lfFont', LOGFONTW),
#]
#PICONMETRICSW = POINTER(tagICONMETRICSW)
#ICONMETRICSW = tagICONMETRICSW
#LPICONMETRICSW = POINTER(tagICONMETRICSW)
#ICONMETRICS = ICONMETRICSA
#PICONMETRICS = PICONMETRICSA
#LPICONMETRICS = LPICONMETRICSA
#class tagANIMATIONINFO(Structure):
#    pass
#tagANIMATIONINFO._fields_ = [
#    ('cbSize', UINT),
#    ('iMinAnimate', c_int),
#]
#ANIMATIONINFO = tagANIMATIONINFO
#LPANIMATIONINFO = POINTER(tagANIMATIONINFO)
#class tagSERIALKEYSA(Structure):
#    pass
#tagSERIALKEYSA._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('lpszActivePort', LPSTR),
#    ('lpszPort', LPSTR),
#    ('iBaudRate', UINT),
#    ('iPortState', UINT),
#    ('iActive', UINT),
#]
#LPSERIALKEYSA = POINTER(tagSERIALKEYSA)
#SERIALKEYSA = tagSERIALKEYSA
#class tagSERIALKEYSW(Structure):
#    pass
#tagSERIALKEYSW._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('lpszActivePort', LPWSTR),
#    ('lpszPort', LPWSTR),
#    ('iBaudRate', UINT),
#    ('iPortState', UINT),
#    ('iActive', UINT),
#]
#SERIALKEYSW = tagSERIALKEYSW
#LPSERIALKEYSW = POINTER(tagSERIALKEYSW)
#SERIALKEYS = SERIALKEYSA
#LPSERIALKEYS = LPSERIALKEYSA
#class tagHIGHCONTRASTA(Structure):
#    pass
#tagHIGHCONTRASTA._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('lpszDefaultScheme', LPSTR),
#]
#LPHIGHCONTRASTA = POINTER(tagHIGHCONTRASTA)
#HIGHCONTRASTA = tagHIGHCONTRASTA
#class tagHIGHCONTRASTW(Structure):
#    pass
#tagHIGHCONTRASTW._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('lpszDefaultScheme', LPWSTR),
#]
#HIGHCONTRASTW = tagHIGHCONTRASTW
#LPHIGHCONTRASTW = POINTER(tagHIGHCONTRASTW)
#HIGHCONTRAST = HIGHCONTRASTA
#LPHIGHCONTRAST = LPHIGHCONTRASTA
#class tagFILTERKEYS(Structure):
#    pass
#tagFILTERKEYS._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('iWaitMSec', DWORD),
#    ('iDelayMSec', DWORD),
#    ('iRepeatMSec', DWORD),
#    ('iBounceMSec', DWORD),
#]
#LPFILTERKEYS = POINTER(tagFILTERKEYS)
#FILTERKEYS = tagFILTERKEYS
#class tagSTICKYKEYS(Structure):
#    pass
#tagSTICKYKEYS._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#]
#STICKYKEYS = tagSTICKYKEYS
#LPSTICKYKEYS = POINTER(tagSTICKYKEYS)
#class tagMOUSEKEYS(Structure):
#    pass
#tagMOUSEKEYS._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('iMaxSpeed', DWORD),
#    ('iTimeToMaxSpeed', DWORD),
#    ('iCtrlSpeed', DWORD),
#    ('dwReserved1', DWORD),
#    ('dwReserved2', DWORD),
#]
#LPMOUSEKEYS = POINTER(tagMOUSEKEYS)
#MOUSEKEYS = tagMOUSEKEYS
#class tagACCESSTIMEOUT(Structure):
#    pass
#tagACCESSTIMEOUT._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('iTimeOutMSec', DWORD),
#]
#ACCESSTIMEOUT = tagACCESSTIMEOUT
#LPACCESSTIMEOUT = POINTER(tagACCESSTIMEOUT)
#class tagSOUNDSENTRYA(Structure):
#    pass
#tagSOUNDSENTRYA._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('iFSTextEffect', DWORD),
#    ('iFSTextEffectMSec', DWORD),
#    ('iFSTextEffectColorBits', DWORD),
#    ('iFSGrafEffect', DWORD),
#    ('iFSGrafEffectMSec', DWORD),
#    ('iFSGrafEffectColor', DWORD),
#    ('iWindowsEffect', DWORD),
#    ('iWindowsEffectMSec', DWORD),
#    ('lpszWindowsEffectDLL', LPSTR),
#    ('iWindowsEffectOrdinal', DWORD),
#]
#SOUNDSENTRYA = tagSOUNDSENTRYA
#LPSOUNDSENTRYA = POINTER(tagSOUNDSENTRYA)
#class tagSOUNDSENTRYW(Structure):
#    pass
#tagSOUNDSENTRYW._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#    ('iFSTextEffect', DWORD),
#    ('iFSTextEffectMSec', DWORD),
#    ('iFSTextEffectColorBits', DWORD),
#    ('iFSGrafEffect', DWORD),
#    ('iFSGrafEffectMSec', DWORD),
#    ('iFSGrafEffectColor', DWORD),
#    ('iWindowsEffect', DWORD),
#    ('iWindowsEffectMSec', DWORD),
#    ('lpszWindowsEffectDLL', LPWSTR),
#    ('iWindowsEffectOrdinal', DWORD),
#]
#SOUNDSENTRYW = tagSOUNDSENTRYW
#LPSOUNDSENTRYW = POINTER(tagSOUNDSENTRYW)
#SOUNDSENTRY = SOUNDSENTRYA
#LPSOUNDSENTRY = LPSOUNDSENTRYA
#class tagTOGGLEKEYS(Structure):
#    pass
#tagTOGGLEKEYS._fields_ = [
#    ('cbSize', UINT),
#    ('dwFlags', DWORD),
#]
#LPTOGGLEKEYS = POINTER(tagTOGGLEKEYS)
#TOGGLEKEYS = tagTOGGLEKEYS
#class tagMONITORINFO(Structure):
#    pass
#tagMONITORINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('rcMonitor', RECT),
#    ('rcWork', RECT),
#    ('dwFlags', DWORD),
#]
#MONITORINFO = tagMONITORINFO
#LPMONITORINFO = POINTER(tagMONITORINFO)
#class tagMONITORINFOEXA(tagMONITORINFO):
#    pass
#tagMONITORINFOEXA._fields_ = [
#    ('szDevice', CHAR * 32),
#]
#MONITORINFOEXA = tagMONITORINFOEXA
#LPMONITORINFOEXA = POINTER(tagMONITORINFOEXA)
#class tagMONITORINFOEXW(tagMONITORINFO):
#    pass
#tagMONITORINFOEXW._fields_ = [
#    ('szDevice', WCHAR * 32),
#]
#MONITORINFOEXW = tagMONITORINFOEXW
#LPMONITORINFOEXW = POINTER(tagMONITORINFOEXW)
#MONITORINFOEX = MONITORINFOEXA
#LPMONITORINFOEX = LPMONITORINFOEXA
#MONITORENUMPROC = WINFUNCTYPE(BOOL, POINTER(HMONITOR__), POINTER(HDC__), POINTER(tagRECT), c_long)
#WINEVENTPROC = WINFUNCTYPE(None, POINTER(HWINEVENTHOOK__), c_ulong, POINTER(HWND__), c_long, c_long, c_ulong, c_ulong)
#class tagGUITHREADINFO(Structure):
#    pass
#tagGUITHREADINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('flags', DWORD),
#    ('hwndActive', HWND),
#    ('hwndFocus', HWND),
#    ('hwndCapture', HWND),
#    ('hwndMenuOwner', HWND),
#    ('hwndMoveSize', HWND),
#    ('hwndCaret', HWND),
#    ('rcCaret', RECT),
#]
#PGUITHREADINFO = POINTER(tagGUITHREADINFO)
#LPGUITHREADINFO = POINTER(tagGUITHREADINFO)
#GUITHREADINFO = tagGUITHREADINFO
#class tagCURSORINFO(Structure):
#    pass
#tagCURSORINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('flags', DWORD),
#    ('hCursor', HCURSOR),
#    ('ptScreenPos', POINT),
#]
#PCURSORINFO = POINTER(tagCURSORINFO)
#CURSORINFO = tagCURSORINFO
#LPCURSORINFO = POINTER(tagCURSORINFO)
#class tagWINDOWINFO(Structure):
#    pass
#tagWINDOWINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('rcWindow', RECT),
#    ('rcClient', RECT),
#    ('dwStyle', DWORD),
#    ('dwExStyle', DWORD),
#    ('dwWindowStatus', DWORD),
#    ('cxWindowBorders', UINT),
#    ('cyWindowBorders', UINT),
#    ('atomWindowType', ATOM),
#    ('wCreatorVersion', WORD),
#]
#WINDOWINFO = tagWINDOWINFO
#LPWINDOWINFO = POINTER(tagWINDOWINFO)
#PWINDOWINFO = POINTER(tagWINDOWINFO)
#class tagTITLEBARINFO(Structure):
#    pass
#tagTITLEBARINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('rcTitleBar', RECT),
#    ('rgstate', DWORD * 6),
#]
#PTITLEBARINFO = POINTER(tagTITLEBARINFO)
#LPTITLEBARINFO = POINTER(tagTITLEBARINFO)
#TITLEBARINFO = tagTITLEBARINFO
#class tagMENUBARINFO(Structure):
#    pass
#tagMENUBARINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('rcBar', RECT),
#    ('hMenu', HMENU),
#    ('hwndMenu', HWND),
#    ('fBarFocused', BOOL, 1),
#    ('fFocused', BOOL, 1),
#]
#LPMENUBARINFO = POINTER(tagMENUBARINFO)
#PMENUBARINFO = POINTER(tagMENUBARINFO)
#MENUBARINFO = tagMENUBARINFO
#class tagSCROLLBARINFO(Structure):
#    pass
#tagSCROLLBARINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('rcScrollBar', RECT),
#    ('dxyLineButton', c_int),
#    ('xyThumbTop', c_int),
#    ('xyThumbBottom', c_int),
#    ('reserved', c_int),
#    ('rgstate', DWORD * 6),
#]
#SCROLLBARINFO = tagSCROLLBARINFO
#LPSCROLLBARINFO = POINTER(tagSCROLLBARINFO)
#PSCROLLBARINFO = POINTER(tagSCROLLBARINFO)
#class tagCOMBOBOXINFO(Structure):
#    pass
#tagCOMBOBOXINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('rcItem', RECT),
#    ('rcButton', RECT),
#    ('stateButton', DWORD),
#    ('hwndCombo', HWND),
#    ('hwndItem', HWND),
#    ('hwndList', HWND),
#]
#PCOMBOBOXINFO = POINTER(tagCOMBOBOXINFO)
#LPCOMBOBOXINFO = POINTER(tagCOMBOBOXINFO)
#COMBOBOXINFO = tagCOMBOBOXINFO
#class tagALTTABINFO(Structure):
#    pass
#tagALTTABINFO._fields_ = [
#    ('cbSize', DWORD),
#    ('cItems', c_int),
#    ('cColumns', c_int),
#    ('cRows', c_int),
#    ('iColFocus', c_int),
#    ('iRowFocus', c_int),
#    ('cxItem', c_int),
#    ('cyItem', c_int),
#    ('ptStart', POINT),
#]
#LPALTTABINFO = POINTER(tagALTTABINFO)
#ALTTABINFO = tagALTTABINFO
#PALTTABINFO = POINTER(tagALTTABINFO)
#class tagVS_FIXEDFILEINFO(Structure):
#    pass
#tagVS_FIXEDFILEINFO._fields_ = [
#    ('dwSignature', DWORD),
#    ('dwStrucVersion', DWORD),
#    ('dwFileVersionMS', DWORD),
#    ('dwFileVersionLS', DWORD),
#    ('dwProductVersionMS', DWORD),
#    ('dwProductVersionLS', DWORD),
#    ('dwFileFlagsMask', DWORD),
#    ('dwFileFlags', DWORD),
#    ('dwFileOS', DWORD),
#    ('dwFileType', DWORD),
#    ('dwFileSubtype', DWORD),
#    ('dwFileDateMS', DWORD),
#    ('dwFileDateLS', DWORD),
#]
#VS_FIXEDFILEINFO = tagVS_FIXEDFILEINFO
#ushort = c_ushort
#uint = c_uint
#ulonglong = c_ulonglong
#longlong = c_longlong
#sigset_t = c_int
#os_off_t = c_longlong
#rf_SetTimer = uint
#class st_used_mem(Structure):
#    pass
#st_used_mem._fields_ = [
#    ('next', POINTER(st_used_mem)),
#    ('left', c_uint),
#    ('size', c_uint),
#]
#USED_MEM = st_used_mem
#class st_mem_root(Structure):
#    pass
#st_mem_root._fields_ = [
#    ('free', POINTER(USED_MEM)),
#    ('used', POINTER(USED_MEM)),
#    ('pre_alloc', POINTER(USED_MEM)),
#    ('min_malloc', size_t),
#    ('block_size', size_t),
#    ('block_num', c_uint),
#    ('first_block_usage', c_uint),
#    ('error_handler', CFUNCTYPE(None)),
#]
#MEM_ROOT = st_mem_root
#class st_list(Structure):
#    pass
#st_list._fields_ = [
#    ('prev', POINTER(st_list)),
#    ('next', POINTER(st_list)),
#    ('data', c_void_p),
#]
#LIST = st_list
#list_walk_action = CFUNCTYPE(c_int, c_void_p, c_void_p)
#list_add = _libraries['libmysql.dll'].list_add
#list_add.restype = POINTER(LIST)
#list_add.argtypes = [POINTER(LIST), POINTER(LIST)]
#list_delete = _libraries['libmysql.dll'].list_delete
#list_delete.restype = POINTER(LIST)
#list_delete.argtypes = [POINTER(LIST), POINTER(LIST)]
#my_bool = c_int8
#class st_mysql_field(Structure):
#    pass
#
## values for enumeration 'enum_field_types'
#enum_field_types = c_int # enum
#st_mysql_field._fields_ = [
#    ('name', STRING),
#    ('org_name', STRING),
#    ('table', STRING),
#    ('org_table', STRING),
#    ('db', STRING),
#    ('catalog', STRING),
#    ('def', STRING),
#    ('length', c_ulong),
#    ('max_length', c_ulong),
#    ('name_length', c_uint),
#    ('org_name_length', c_uint),
#    ('table_length', c_uint),
#    ('org_table_length', c_uint),
#    ('db_length', c_uint),
#    ('catalog_length', c_uint),
#    ('def_length', c_uint),
#    ('flags', c_uint),
#    ('decimals', c_uint),
#    ('charsetnr', c_uint),
#    ('type', enum_field_types),
#    ('extension', c_void_p),
#]
#MYSQL_FIELD = st_mysql_field
#MYSQL_ROW = POINTER(STRING)
#MYSQL_FIELD_OFFSET = c_uint
#my_ulonglong = c_ulonglong
#class st_mysql_rows(Structure):
#    pass
#st_mysql_rows._fields_ = [
#    ('next', POINTER(st_mysql_rows)),
#    ('data', MYSQL_ROW),
#    ('length', c_ulong),
#]
#MYSQL_ROWS = st_mysql_rows
#MYSQL_ROW_OFFSET = POINTER(MYSQL_ROWS)
#class embedded_query_result(Structure):
#    pass
#embedded_query_result._fields_ = [
#]
#EMBEDDED_QUERY_RESULT = embedded_query_result
#class st_mysql_data(Structure):
#    pass
#st_mysql_data._fields_ = [
#    ('data', POINTER(MYSQL_ROWS)),
#    ('embedded_info', POINTER(embedded_query_result)),
#    ('alloc', MEM_ROOT),
#    ('rows', my_ulonglong),
#    ('fields', c_uint),
#    ('extension', c_void_p),
#]
#MYSQL_DATA = st_mysql_data
#
## values for enumeration 'mysql_option'
#mysql_option = c_int # enum
#class st_mysql_options(Structure):
#    pass
#class st_dynamic_array(Structure):
#    pass
#st_mysql_options._fields_ = [
#    ('connect_timeout', c_uint),
#    ('read_timeout', c_uint),
#    ('write_timeout', c_uint),
#    ('port', c_uint),
#    ('protocol', c_uint),
#    ('client_flag', c_ulong),
#    ('host', STRING),
#    ('user', STRING),
#    ('password', STRING),
#    ('unix_socket', STRING),
#    ('db', STRING),
#    ('init_commands', POINTER(st_dynamic_array)),
#    ('my_cnf_file', STRING),
#    ('my_cnf_group', STRING),
#    ('charset_dir', STRING),
#    ('charset_name', STRING),
#    ('ssl_key', STRING),
#    ('ssl_cert', STRING),
#    ('ssl_ca', STRING),
#    ('ssl_capath', STRING),
#    ('ssl_cipher', STRING),
#    ('shared_memory_base_name', STRING),
#    ('max_allowed_packet', c_ulong),
#    ('use_ssl', my_bool),
#    ('compress', my_bool),
#    ('named_pipe', my_bool),
#    ('rpl_probe', my_bool),
#    ('rpl_parse', my_bool),
#    ('no_master_reads', my_bool),
#    ('separate_thread', my_bool),
#    ('methods_to_use', mysql_option),
#    ('client_ip', STRING),
#    ('secure_auth', my_bool),
#    ('report_data_truncation', my_bool),
#    ('local_infile_init', CFUNCTYPE(c_int, POINTER(c_void_p), STRING, c_void_p)),
#    ('local_infile_read', CFUNCTYPE(c_int, c_void_p, STRING, c_uint)),
#    ('local_infile_end', CFUNCTYPE(None, c_void_p)),
#    ('local_infile_error', CFUNCTYPE(c_int, c_void_p, STRING, c_uint)),
#    ('local_infile_userdata', c_void_p),
#    ('extension', c_void_p),
#]
#st_dynamic_array._fields_ = [
#]
#
## values for enumeration 'mysql_status'
#mysql_status = c_int # enum
#
## values for enumeration 'mysql_protocol_type'
#mysql_protocol_type = c_int # enum
#
## values for enumeration 'mysql_rpl_type'
#mysql_rpl_type = c_int # enum
#class character_set(Structure):
#    pass
#character_set._fields_ = [
#    ('number', c_uint),
#    ('state', c_uint),
#    ('csname', STRING),
#    ('name', STRING),
#    ('comment', STRING),
#    ('dir', STRING),
#    ('mbminlen', c_uint),
#    ('mbmaxlen', c_uint),
#]
#MY_CHARSET_INFO = character_set
#class st_mysql(Structure):
#    pass
#class st_net(Structure):
#    pass
#class st_vio(Structure):
#    pass
#Vio = st_vio
#st_net._fields_ = [
#    ('vio', POINTER(Vio)),
#    ('buff', POINTER(c_ubyte)),
#    ('buff_end', POINTER(c_ubyte)),
#    ('write_pos', POINTER(c_ubyte)),
#    ('read_pos', POINTER(c_ubyte)),
#    ('fd', SOCKET),
#    ('remain_in_buf', c_ulong),
#    ('length', c_ulong),
#    ('buf_length', c_ulong),
#    ('where_b', c_ulong),
#    ('max_packet', c_ulong),
#    ('max_packet_size', c_ulong),
#    ('pkt_nr', c_uint),
#    ('compress_pkt_nr', c_uint),
#    ('write_timeout', c_uint),
#    ('read_timeout', c_uint),
#    ('retry_count', c_uint),
#    ('fcntl', c_int),
#    ('return_status', POINTER(c_uint)),
#    ('reading_or_writing', c_ubyte),
#    ('save_char', c_char),
#    ('unused0', my_bool),
#    ('unused', my_bool),
#    ('compress', my_bool),
#    ('unused1', my_bool),
#    ('query_cache_query', POINTER(c_ubyte)),
#    ('last_errno', c_uint),
#    ('error', c_ubyte),
#    ('unused2', my_bool),
#    ('return_errno', my_bool),
#    ('last_error', c_char * 512),
#    ('sqlstate', c_char * 6),
#    ('extension', c_void_p),
#]
#NET = st_net
#class charset_info_st(Structure):
#    pass
#class st_mysql_methods(Structure):
#    pass
#MYSQL = st_mysql
#
## values for enumeration 'enum_server_command'
#enum_server_command = c_int # enum
#class st_mysql_stmt(Structure):
#    pass
#MYSQL_STMT = st_mysql_stmt
#class st_mysql_res(Structure):
#    pass
#MYSQL_RES = st_mysql_res
#st_mysql_methods._fields_ = [
#    ('read_query_result', CFUNCTYPE(my_bool, POINTER(MYSQL))),
#    ('advanced_command', CFUNCTYPE(my_bool, POINTER(MYSQL), enum_server_command, POINTER(c_ubyte), c_ulong, POINTER(c_ubyte), c_ulong, c_char, POINTER(MYSQL_STMT))),
#    ('read_rows', CFUNCTYPE(POINTER(MYSQL_DATA), POINTER(MYSQL), POINTER(MYSQL_FIELD), c_uint)),
#    ('use_result', CFUNCTYPE(POINTER(MYSQL_RES), POINTER(MYSQL))),
#    ('fetch_lengths', CFUNCTYPE(None, POINTER(c_ulong), POINTER(STRING), c_uint)),
#    ('flush_use_result', CFUNCTYPE(None, POINTER(MYSQL))),
#    ('list_fields', CFUNCTYPE(POINTER(MYSQL_FIELD), POINTER(MYSQL))),
#    ('read_prepare_result', CFUNCTYPE(my_bool, POINTER(MYSQL), POINTER(MYSQL_STMT))),
#    ('stmt_execute', CFUNCTYPE(c_int, POINTER(MYSQL_STMT))),
#    ('read_binary_rows', CFUNCTYPE(c_int, POINTER(MYSQL_STMT))),
#    ('unbuffered_fetch', CFUNCTYPE(c_int, POINTER(MYSQL), POINTER(STRING))),
#    ('free_embedded_thd', CFUNCTYPE(None, POINTER(MYSQL))),
#    ('read_statistics', CFUNCTYPE(STRING, POINTER(MYSQL))),
#    ('next_result', CFUNCTYPE(my_bool, POINTER(MYSQL))),
#    ('read_change_user_result', CFUNCTYPE(c_int, POINTER(MYSQL), STRING, STRING)),
#    ('read_rows_from_cursor', CFUNCTYPE(c_int, POINTER(MYSQL_STMT))),
#]
#st_mysql._fields_ = [
#    ('net', NET),
#    ('connector_fd', POINTER(c_ubyte)),
#    ('host', STRING),
#    ('user', STRING),
#    ('passwd', STRING),
#    ('unix_socket', STRING),
#    ('server_version', STRING),
#    ('host_info', STRING),
#    ('info', STRING),
#    ('db', STRING),
#    ('charset', POINTER(charset_info_st)),
#    ('fields', POINTER(MYSQL_FIELD)),
#    ('field_alloc', MEM_ROOT),
#    ('affected_rows', my_ulonglong),
#    ('insert_id', my_ulonglong),
#    ('extra_info', my_ulonglong),
#    ('thread_id', c_ulong),
#    ('packet_length', c_ulong),
#    ('port', c_uint),
#    ('client_flag', c_ulong),
#    ('server_capabilities', c_ulong),
#    ('protocol_version', c_uint),
#    ('field_count', c_uint),
#    ('server_status', c_uint),
#    ('server_language', c_uint),
#    ('warning_count', c_uint),
#    ('options', st_mysql_options),
#    ('status', mysql_status),
#    ('free_me', my_bool),
#    ('reconnect', my_bool),
#    ('scramble', c_char * 21),
#    ('rpl_pivot', my_bool),
#    ('master', POINTER(st_mysql)),
#    ('next_slave', POINTER(st_mysql)),
#    ('last_used_slave', POINTER(st_mysql)),
#    ('last_used_con', POINTER(st_mysql)),
#    ('stmts', POINTER(LIST)),
#    ('methods', POINTER(st_mysql_methods)),
#    ('thd', c_void_p),
#    ('unbuffered_fetch_owner', STRING),
#    ('info_buffer', STRING),
#    ('extension', c_void_p),
#]
#charset_info_st._fields_ = [
#]
#st_mysql_res._fields_ = [
#    ('row_count', my_ulonglong),
#    ('fields', POINTER(MYSQL_FIELD)),
#    ('data', POINTER(MYSQL_DATA)),
#    ('data_cursor', POINTER(MYSQL_ROWS)),
#    ('lengths', POINTER(c_ulong)),
#    ('handle', POINTER(MYSQL)),
#    ('methods', POINTER(st_mysql_methods)),
#    ('row', MYSQL_ROW),
#    ('current_row', MYSQL_ROW),
#    ('field_alloc', MEM_ROOT),
#    ('field_count', c_uint),
#    ('current_field', c_uint),
#    ('eof', my_bool),
#    ('unbuffered_fetch_cancelled', my_bool),
#    ('extension', c_void_p),
#]
#class st_mysql_manager(Structure):
#    pass
#st_mysql_manager._fields_ = [
#    ('net', NET),
#    ('host', STRING),
#    ('user', STRING),
#    ('passwd', STRING),
#    ('net_buf', STRING),
#    ('net_buf_pos', STRING),
#    ('net_data_end', STRING),
#    ('port', c_uint),
#    ('cmd_status', c_int),
#    ('last_errno', c_int),
#    ('net_buf_size', c_int),
#    ('free_me', my_bool),
#    ('eof', my_bool),
#    ('last_error', c_char * 256),
#    ('extension', c_void_p),
#]
#MYSQL_MANAGER = st_mysql_manager
#class st_mysql_parameters(Structure):
#    pass
#st_mysql_parameters._fields_ = [
#    ('p_max_allowed_packet', POINTER(c_ulong)),
#    ('p_net_buffer_length', POINTER(c_ulong)),
#    ('extension', c_void_p),
#]
#MYSQL_PARAMETERS = st_mysql_parameters
#mysql_server_init = _stdcall_libraries['libmysql.dll'].mysql_server_init
#mysql_server_init.restype = c_int
#mysql_server_init.argtypes = [c_int, POINTER(STRING), POINTER(STRING)]
#mysql_server_end = _stdcall_libraries['libmysql.dll'].mysql_server_end
#mysql_server_end.restype = None
#mysql_server_end.argtypes = []
#mysql_get_parameters = _stdcall_libraries['libmysql.dll'].mysql_get_parameters
#mysql_get_parameters.restype = POINTER(MYSQL_PARAMETERS)
#mysql_get_parameters.argtypes = []
#mysql_thread_init = _stdcall_libraries['libmysql.dll'].mysql_thread_init
#mysql_thread_init.restype = my_bool
#mysql_thread_init.argtypes = []
#mysql_thread_end = _stdcall_libraries['libmysql.dll'].mysql_thread_end
#mysql_thread_end.restype = None
#mysql_thread_end.argtypes = []
#mysql_num_rows = _stdcall_libraries['libmysql.dll'].mysql_num_rows
#mysql_num_rows.restype = my_ulonglong
#mysql_num_rows.argtypes = [POINTER(MYSQL_RES)]
#mysql_num_fields = _stdcall_libraries['libmysql.dll'].mysql_num_fields
#mysql_num_fields.restype = c_uint
#mysql_num_fields.argtypes = [POINTER(MYSQL_RES)]
#mysql_eof = _stdcall_libraries['libmysql.dll'].mysql_eof
#mysql_eof.restype = my_bool
#mysql_eof.argtypes = [POINTER(MYSQL_RES)]
#mysql_fetch_field_direct = _stdcall_libraries['libmysql.dll'].mysql_fetch_field_direct
#mysql_fetch_field_direct.restype = POINTER(MYSQL_FIELD)
#mysql_fetch_field_direct.argtypes = [POINTER(MYSQL_RES), c_uint]
#mysql_fetch_fields = _stdcall_libraries['libmysql.dll'].mysql_fetch_fields
#mysql_fetch_fields.restype = POINTER(MYSQL_FIELD)
#mysql_fetch_fields.argtypes = [POINTER(MYSQL_RES)]
#mysql_row_tell = _stdcall_libraries['libmysql.dll'].mysql_row_tell
#mysql_row_tell.restype = MYSQL_ROW_OFFSET
#mysql_row_tell.argtypes = [POINTER(MYSQL_RES)]
#mysql_field_tell = _stdcall_libraries['libmysql.dll'].mysql_field_tell
#mysql_field_tell.restype = MYSQL_FIELD_OFFSET
#mysql_field_tell.argtypes = [POINTER(MYSQL_RES)]
#mysql_field_count = _stdcall_libraries['libmysql.dll'].mysql_field_count
#mysql_field_count.restype = c_uint
#mysql_field_count.argtypes = [POINTER(MYSQL)]
#mysql_affected_rows = _stdcall_libraries['libmysql.dll'].mysql_affected_rows
#mysql_affected_rows.restype = my_ulonglong
#mysql_affected_rows.argtypes = [POINTER(MYSQL)]
#mysql_insert_id = _stdcall_libraries['libmysql.dll'].mysql_insert_id
#mysql_insert_id.restype = my_ulonglong
#mysql_insert_id.argtypes = [POINTER(MYSQL)]
#mysql_errno = _stdcall_libraries['libmysql.dll'].mysql_errno
#mysql_errno.restype = c_uint
#mysql_errno.argtypes = [POINTER(MYSQL)]
#mysql_error = _stdcall_libraries['libmysql.dll'].mysql_error
#mysql_error.restype = STRING
#mysql_error.argtypes = [POINTER(MYSQL)]
#mysql_sqlstate = _stdcall_libraries['libmysql.dll'].mysql_sqlstate
#mysql_sqlstate.restype = STRING
#mysql_sqlstate.argtypes = [POINTER(MYSQL)]
#mysql_warning_count = _stdcall_libraries['libmysql.dll'].mysql_warning_count
#mysql_warning_count.restype = c_uint
#mysql_warning_count.argtypes = [POINTER(MYSQL)]
#mysql_info = _stdcall_libraries['libmysql.dll'].mysql_info
#mysql_info.restype = STRING
#mysql_info.argtypes = [POINTER(MYSQL)]
#mysql_thread_id = _stdcall_libraries['libmysql.dll'].mysql_thread_id
#mysql_thread_id.restype = c_ulong
#mysql_thread_id.argtypes = [POINTER(MYSQL)]
#mysql_character_set_name = _stdcall_libraries['libmysql.dll'].mysql_character_set_name
#mysql_character_set_name.restype = STRING
#mysql_character_set_name.argtypes = [POINTER(MYSQL)]
#mysql_set_character_set = _stdcall_libraries['libmysql.dll'].mysql_set_character_set
#mysql_set_character_set.restype = c_int
#mysql_set_character_set.argtypes = [POINTER(MYSQL), STRING]
#mysql_init = _stdcall_libraries['libmysql.dll'].mysql_init
#mysql_init.restype = POINTER(MYSQL)
#mysql_init.argtypes = [POINTER(MYSQL)]
#mysql_ssl_set = _stdcall_libraries['libmysql.dll'].mysql_ssl_set
#mysql_ssl_set.restype = my_bool
#mysql_ssl_set.argtypes = [POINTER(MYSQL), STRING, STRING, STRING, STRING, STRING]
#mysql_get_ssl_cipher = _stdcall_libraries['libmysql.dll'].mysql_get_ssl_cipher
#mysql_get_ssl_cipher.restype = STRING
#mysql_get_ssl_cipher.argtypes = [POINTER(MYSQL)]
#mysql_change_user = _stdcall_libraries['libmysql.dll'].mysql_change_user
#mysql_change_user.restype = my_bool
#mysql_change_user.argtypes = [POINTER(MYSQL), STRING, STRING, STRING]
#mysql_real_connect = _stdcall_libraries['libmysql.dll'].mysql_real_connect
#mysql_real_connect.restype = POINTER(MYSQL)
#mysql_real_connect.argtypes = [POINTER(MYSQL), STRING, STRING, STRING, STRING, c_uint, STRING, c_ulong]
#mysql_select_db = _stdcall_libraries['libmysql.dll'].mysql_select_db
#mysql_select_db.restype = c_int
#mysql_select_db.argtypes = [POINTER(MYSQL), STRING]
#mysql_query = _stdcall_libraries['libmysql.dll'].mysql_query
#mysql_query.restype = c_int
#mysql_query.argtypes = [POINTER(MYSQL), STRING]
#mysql_send_query = _stdcall_libraries['libmysql.dll'].mysql_send_query
#mysql_send_query.restype = c_int
#mysql_send_query.argtypes = [POINTER(MYSQL), STRING, c_ulong]
#mysql_real_query = _stdcall_libraries['libmysql.dll'].mysql_real_query
#mysql_real_query.restype = c_int
#mysql_real_query.argtypes = [POINTER(MYSQL), STRING, c_ulong]
#mysql_store_result = _stdcall_libraries['libmysql.dll'].mysql_store_result
#mysql_store_result.restype = POINTER(MYSQL_RES)
#mysql_store_result.argtypes = [POINTER(MYSQL)]
#mysql_use_result = _stdcall_libraries['libmysql.dll'].mysql_use_result
#mysql_use_result.restype = POINTER(MYSQL_RES)
#mysql_use_result.argtypes = [POINTER(MYSQL)]
#mysql_master_query = _stdcall_libraries['libmysql.dll'].mysql_master_query
#mysql_master_query.restype = my_bool
#mysql_master_query.argtypes = [POINTER(MYSQL), STRING, c_ulong]
#mysql_slave_query = _stdcall_libraries['libmysql.dll'].mysql_slave_query
#mysql_slave_query.restype = my_bool
#mysql_slave_query.argtypes = [POINTER(MYSQL), STRING, c_ulong]
#mysql_get_character_set_info = _stdcall_libraries['libmysql.dll'].mysql_get_character_set_info
#mysql_get_character_set_info.restype = None
#mysql_get_character_set_info.argtypes = [POINTER(MYSQL), POINTER(MY_CHARSET_INFO)]
#mysql_set_local_infile_handler = _libraries['libmysql.dll'].mysql_set_local_infile_handler
#mysql_set_local_infile_handler.restype = None
#mysql_set_local_infile_handler.argtypes = [POINTER(MYSQL), CFUNCTYPE(c_int, POINTER(c_void_p), STRING, c_void_p), CFUNCTYPE(c_int, c_void_p, STRING, c_uint), CFUNCTYPE(None, c_void_p), CFUNCTYPE(c_int, c_void_p, STRING, c_uint), c_void_p]
#mysql_set_local_infile_default = _libraries['libmysql.dll'].mysql_set_local_infile_default
#mysql_set_local_infile_default.restype = None
#mysql_set_local_infile_default.argtypes = [POINTER(MYSQL)]
#mysql_enable_rpl_parse = _stdcall_libraries['libmysql.dll'].mysql_enable_rpl_parse
#mysql_enable_rpl_parse.restype = None
#mysql_enable_rpl_parse.argtypes = [POINTER(MYSQL)]
#mysql_disable_rpl_parse = _stdcall_libraries['libmysql.dll'].mysql_disable_rpl_parse
#mysql_disable_rpl_parse.restype = None
#mysql_disable_rpl_parse.argtypes = [POINTER(MYSQL)]
#mysql_rpl_parse_enabled = _stdcall_libraries['libmysql.dll'].mysql_rpl_parse_enabled
#mysql_rpl_parse_enabled.restype = c_int
#mysql_rpl_parse_enabled.argtypes = [POINTER(MYSQL)]
#mysql_enable_reads_from_master = _stdcall_libraries['libmysql.dll'].mysql_enable_reads_from_master
#mysql_enable_reads_from_master.restype = None
#mysql_enable_reads_from_master.argtypes = [POINTER(MYSQL)]
#mysql_disable_reads_from_master = _stdcall_libraries['libmysql.dll'].mysql_disable_reads_from_master
#mysql_disable_reads_from_master.restype = None
#mysql_disable_reads_from_master.argtypes = [POINTER(MYSQL)]
#mysql_rpl_query_type = _stdcall_libraries['libmysql.dll'].mysql_rpl_query_type
#mysql_rpl_query_type.restype = mysql_rpl_type
#mysql_rpl_query_type.argtypes = [STRING, c_int]
#mysql_rpl_probe = _stdcall_libraries['libmysql.dll'].mysql_rpl_probe
#mysql_rpl_probe.restype = my_bool
#mysql_rpl_probe.argtypes = [POINTER(MYSQL)]
#
## values for enumeration 'mysql_enum_shutdown_level'
#mysql_enum_shutdown_level = c_int # enum
#mysql_shutdown = _stdcall_libraries['libmysql.dll'].mysql_shutdown
#mysql_shutdown.restype = c_int
#mysql_shutdown.argtypes = [POINTER(MYSQL), mysql_enum_shutdown_level]
#mysql_dump_debug_info = _stdcall_libraries['libmysql.dll'].mysql_dump_debug_info
#mysql_dump_debug_info.restype = c_int
#mysql_dump_debug_info.argtypes = [POINTER(MYSQL)]
#mysql_refresh = _stdcall_libraries['libmysql.dll'].mysql_refresh
#mysql_refresh.restype = c_int
#mysql_refresh.argtypes = [POINTER(MYSQL), c_uint]
#mysql_kill = _stdcall_libraries['libmysql.dll'].mysql_kill
#mysql_kill.restype = c_int
#mysql_kill.argtypes = [POINTER(MYSQL), c_ulong]
#
## values for enumeration 'enum_mysql_set_option'
#enum_mysql_set_option = c_int # enum
#mysql_set_server_option = _stdcall_libraries['libmysql.dll'].mysql_set_server_option
#mysql_set_server_option.restype = c_int
#mysql_set_server_option.argtypes = [POINTER(MYSQL), enum_mysql_set_option]
#mysql_ping = _stdcall_libraries['libmysql.dll'].mysql_ping
#mysql_ping.restype = c_int
#mysql_ping.argtypes = [POINTER(MYSQL)]
#mysql_stat = _stdcall_libraries['libmysql.dll'].mysql_stat
#mysql_stat.restype = STRING
#mysql_stat.argtypes = [POINTER(MYSQL)]
#mysql_get_server_info = _stdcall_libraries['libmysql.dll'].mysql_get_server_info
#mysql_get_server_info.restype = STRING
#mysql_get_server_info.argtypes = [POINTER(MYSQL)]
#mysql_get_client_info = _stdcall_libraries['libmysql.dll'].mysql_get_client_info
#mysql_get_client_info.restype = STRING
#mysql_get_client_info.argtypes = []
#mysql_get_client_version = _stdcall_libraries['libmysql.dll'].mysql_get_client_version
#mysql_get_client_version.restype = c_ulong
#mysql_get_client_version.argtypes = []
#mysql_get_host_info = _stdcall_libraries['libmysql.dll'].mysql_get_host_info
#mysql_get_host_info.restype = STRING
#mysql_get_host_info.argtypes = [POINTER(MYSQL)]
#mysql_get_server_version = _stdcall_libraries['libmysql.dll'].mysql_get_server_version
#mysql_get_server_version.restype = c_ulong
#mysql_get_server_version.argtypes = [POINTER(MYSQL)]
#mysql_get_proto_info = _stdcall_libraries['libmysql.dll'].mysql_get_proto_info
#mysql_get_proto_info.restype = c_uint
#mysql_get_proto_info.argtypes = [POINTER(MYSQL)]
#mysql_list_dbs = _stdcall_libraries['libmysql.dll'].mysql_list_dbs
#mysql_list_dbs.restype = POINTER(MYSQL_RES)
#mysql_list_dbs.argtypes = [POINTER(MYSQL), STRING]
#mysql_list_tables = _stdcall_libraries['libmysql.dll'].mysql_list_tables
#mysql_list_tables.restype = POINTER(MYSQL_RES)
#mysql_list_tables.argtypes = [POINTER(MYSQL), STRING]
#mysql_list_processes = _stdcall_libraries['libmysql.dll'].mysql_list_processes
#mysql_list_processes.restype = POINTER(MYSQL_RES)
#mysql_list_processes.argtypes = [POINTER(MYSQL)]
#mysql_options = _stdcall_libraries['libmysql.dll'].mysql_options
#mysql_options.restype = c_int
#mysql_options.argtypes = [POINTER(MYSQL), mysql_option, c_void_p]
#mysql_free_result = _stdcall_libraries['libmysql.dll'].mysql_free_result
#mysql_free_result.restype = None
#mysql_free_result.argtypes = [POINTER(MYSQL_RES)]
#mysql_data_seek = _stdcall_libraries['libmysql.dll'].mysql_data_seek
#mysql_data_seek.restype = None
#mysql_data_seek.argtypes = [POINTER(MYSQL_RES), c_ulonglong]
#mysql_row_seek = _stdcall_libraries['libmysql.dll'].mysql_row_seek
#mysql_row_seek.restype = MYSQL_ROW_OFFSET
#mysql_row_seek.argtypes = [POINTER(MYSQL_RES), POINTER(MYSQL_ROWS)]
#mysql_field_seek = _stdcall_libraries['libmysql.dll'].mysql_field_seek
#mysql_field_seek.restype = MYSQL_FIELD_OFFSET
#mysql_field_seek.argtypes = [POINTER(MYSQL_RES), c_uint]
#mysql_fetch_row = _stdcall_libraries['libmysql.dll'].mysql_fetch_row
#mysql_fetch_row.restype = MYSQL_ROW
#mysql_fetch_row.argtypes = [POINTER(MYSQL_RES)]
#mysql_fetch_lengths = _stdcall_libraries['libmysql.dll'].mysql_fetch_lengths
#mysql_fetch_lengths.restype = POINTER(c_ulong)
#mysql_fetch_lengths.argtypes = [POINTER(MYSQL_RES)]
#mysql_fetch_field = _stdcall_libraries['libmysql.dll'].mysql_fetch_field
#mysql_fetch_field.restype = POINTER(MYSQL_FIELD)
#mysql_fetch_field.argtypes = [POINTER(MYSQL_RES)]
#mysql_list_fields = _stdcall_libraries['libmysql.dll'].mysql_list_fields
#mysql_list_fields.restype = POINTER(MYSQL_RES)
#mysql_list_fields.argtypes = [POINTER(MYSQL), STRING, STRING]
#mysql_escape_string = _stdcall_libraries['libmysql.dll'].mysql_escape_string
#mysql_escape_string.restype = c_ulong
#mysql_escape_string.argtypes = [STRING, STRING, c_ulong]
#mysql_hex_string = _stdcall_libraries['libmysql.dll'].mysql_hex_string
#mysql_hex_string.restype = c_ulong
#mysql_hex_string.argtypes = [STRING, STRING, c_ulong]
#mysql_real_escape_string = _stdcall_libraries['libmysql.dll'].mysql_real_escape_string
#mysql_real_escape_string.restype = c_ulong
#mysql_real_escape_string.argtypes = [POINTER(MYSQL), STRING, STRING, c_ulong]
#mysql_debug = _stdcall_libraries['libmysql.dll'].mysql_debug
#mysql_debug.restype = None
#mysql_debug.argtypes = [STRING]
#myodbc_remove_escape = _stdcall_libraries['libmysql.dll'].myodbc_remove_escape
#myodbc_remove_escape.restype = None
#myodbc_remove_escape.argtypes = [POINTER(MYSQL), STRING]
#mysql_thread_safe = _stdcall_libraries['libmysql.dll'].mysql_thread_safe
#mysql_thread_safe.restype = c_uint
#mysql_thread_safe.argtypes = []
#mysql_embedded = _stdcall_libraries['libmysql.dll'].mysql_embedded
#mysql_embedded.restype = my_bool
#mysql_embedded.argtypes = []
#mysql_read_query_result = _stdcall_libraries['libmysql.dll'].mysql_read_query_result
#mysql_read_query_result.restype = my_bool
#mysql_read_query_result.argtypes = [POINTER(MYSQL)]
#
## values for enumeration 'enum_mysql_stmt_state'
#enum_mysql_stmt_state = c_int # enum
#class st_mysql_bind(Structure):
#    pass
#st_mysql_bind._fields_ = [
#    ('length', POINTER(c_ulong)),
#    ('is_null', STRING),
#    ('buffer', c_void_p),
#    ('error', STRING),
#    ('row_ptr', POINTER(c_ubyte)),
#    ('store_param_func', CFUNCTYPE(None, POINTER(NET), POINTER(st_mysql_bind))),
#    ('fetch_result', CFUNCTYPE(None, POINTER(st_mysql_bind), POINTER(MYSQL_FIELD), POINTER(POINTER(c_ubyte)))),
#    ('skip_result', CFUNCTYPE(None, POINTER(st_mysql_bind), POINTER(MYSQL_FIELD), POINTER(POINTER(c_ubyte)))),
#    ('buffer_length', c_ulong),
#    ('offset', c_ulong),
#    ('length_value', c_ulong),
#    ('param_number', c_uint),
#    ('pack_length', c_uint),
#    ('buffer_type', enum_field_types),
#    ('error_value', my_bool),
#    ('is_unsigned', my_bool),
#    ('long_data_used', my_bool),
#    ('is_null_value', my_bool),
#    ('extension', c_void_p),
#]
#MYSQL_BIND = st_mysql_bind
#st_mysql_stmt._fields_ = [
#    ('mem_root', MEM_ROOT),
#    ('list', LIST),
#    ('mysql', POINTER(MYSQL)),
#    ('params', POINTER(MYSQL_BIND)),
#    ('bind', POINTER(MYSQL_BIND)),
#    ('fields', POINTER(MYSQL_FIELD)),
#    ('result', MYSQL_DATA),
#    ('data_cursor', POINTER(MYSQL_ROWS)),
#    ('read_row_func', CFUNCTYPE(c_int, POINTER(st_mysql_stmt), POINTER(POINTER(c_ubyte)))),
#    ('affected_rows', my_ulonglong),
#    ('insert_id', my_ulonglong),
#    ('stmt_id', c_ulong),
#    ('flags', c_ulong),
#    ('prefetch_rows', c_ulong),
#    ('server_status', c_uint),
#    ('last_errno', c_uint),
#    ('param_count', c_uint),
#    ('field_count', c_uint),
#    ('state', enum_mysql_stmt_state),
#    ('last_error', c_char * 512),
#    ('sqlstate', c_char * 6),
#    ('send_types_to_server', my_bool),
#    ('bind_param_done', my_bool),
#    ('bind_result_done', c_ubyte),
#    ('unbuffered_fetch_cancelled', my_bool),
#    ('update_max_length', my_bool),
#    ('extension', c_void_p),
#]
#
## values for enumeration 'enum_stmt_attr_type'
#enum_stmt_attr_type = c_int # enum
#MYSQL_METHODS = st_mysql_methods
#mysql_stmt_init = _stdcall_libraries['libmysql.dll'].mysql_stmt_init
#mysql_stmt_init.restype = POINTER(MYSQL_STMT)
#mysql_stmt_init.argtypes = [POINTER(MYSQL)]
#mysql_stmt_prepare = _stdcall_libraries['libmysql.dll'].mysql_stmt_prepare
#mysql_stmt_prepare.restype = c_int
#mysql_stmt_prepare.argtypes = [POINTER(MYSQL_STMT), STRING, c_ulong]
#mysql_stmt_execute = _stdcall_libraries['libmysql.dll'].mysql_stmt_execute
#mysql_stmt_execute.restype = c_int
#mysql_stmt_execute.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_fetch = _stdcall_libraries['libmysql.dll'].mysql_stmt_fetch
#mysql_stmt_fetch.restype = c_int
#mysql_stmt_fetch.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_fetch_column = _stdcall_libraries['libmysql.dll'].mysql_stmt_fetch_column
#mysql_stmt_fetch_column.restype = c_int
#mysql_stmt_fetch_column.argtypes = [POINTER(MYSQL_STMT), POINTER(MYSQL_BIND), c_uint, c_ulong]
#mysql_stmt_store_result = _stdcall_libraries['libmysql.dll'].mysql_stmt_store_result
#mysql_stmt_store_result.restype = c_int
#mysql_stmt_store_result.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_param_count = _stdcall_libraries['libmysql.dll'].mysql_stmt_param_count
#mysql_stmt_param_count.restype = c_ulong
#mysql_stmt_param_count.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_attr_set = _stdcall_libraries['libmysql.dll'].mysql_stmt_attr_set
#mysql_stmt_attr_set.restype = my_bool
#mysql_stmt_attr_set.argtypes = [POINTER(MYSQL_STMT), enum_stmt_attr_type, c_void_p]
#mysql_stmt_attr_get = _stdcall_libraries['libmysql.dll'].mysql_stmt_attr_get
#mysql_stmt_attr_get.restype = my_bool
#mysql_stmt_attr_get.argtypes = [POINTER(MYSQL_STMT), enum_stmt_attr_type, c_void_p]
#mysql_stmt_bind_param = _stdcall_libraries['libmysql.dll'].mysql_stmt_bind_param
#mysql_stmt_bind_param.restype = my_bool
#mysql_stmt_bind_param.argtypes = [POINTER(MYSQL_STMT), POINTER(MYSQL_BIND)]
#mysql_stmt_bind_result = _stdcall_libraries['libmysql.dll'].mysql_stmt_bind_result
#mysql_stmt_bind_result.restype = my_bool
#mysql_stmt_bind_result.argtypes = [POINTER(MYSQL_STMT), POINTER(MYSQL_BIND)]
#mysql_stmt_close = _stdcall_libraries['libmysql.dll'].mysql_stmt_close
#mysql_stmt_close.restype = my_bool
#mysql_stmt_close.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_reset = _stdcall_libraries['libmysql.dll'].mysql_stmt_reset
#mysql_stmt_reset.restype = my_bool
#mysql_stmt_reset.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_free_result = _stdcall_libraries['libmysql.dll'].mysql_stmt_free_result
#mysql_stmt_free_result.restype = my_bool
#mysql_stmt_free_result.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_send_long_data = _stdcall_libraries['libmysql.dll'].mysql_stmt_send_long_data
#mysql_stmt_send_long_data.restype = my_bool
#mysql_stmt_send_long_data.argtypes = [POINTER(MYSQL_STMT), c_uint, STRING, c_ulong]
#mysql_stmt_result_metadata = _stdcall_libraries['libmysql.dll'].mysql_stmt_result_metadata
#mysql_stmt_result_metadata.restype = POINTER(MYSQL_RES)
#mysql_stmt_result_metadata.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_param_metadata = _stdcall_libraries['libmysql.dll'].mysql_stmt_param_metadata
#mysql_stmt_param_metadata.restype = POINTER(MYSQL_RES)
#mysql_stmt_param_metadata.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_errno = _stdcall_libraries['libmysql.dll'].mysql_stmt_errno
#mysql_stmt_errno.restype = c_uint
#mysql_stmt_errno.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_error = _stdcall_libraries['libmysql.dll'].mysql_stmt_error
#mysql_stmt_error.restype = STRING
#mysql_stmt_error.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_sqlstate = _stdcall_libraries['libmysql.dll'].mysql_stmt_sqlstate
#mysql_stmt_sqlstate.restype = STRING
#mysql_stmt_sqlstate.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_row_seek = _stdcall_libraries['libmysql.dll'].mysql_stmt_row_seek
#mysql_stmt_row_seek.restype = MYSQL_ROW_OFFSET
#mysql_stmt_row_seek.argtypes = [POINTER(MYSQL_STMT), POINTER(MYSQL_ROWS)]
#mysql_stmt_row_tell = _stdcall_libraries['libmysql.dll'].mysql_stmt_row_tell
#mysql_stmt_row_tell.restype = MYSQL_ROW_OFFSET
#mysql_stmt_row_tell.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_data_seek = _stdcall_libraries['libmysql.dll'].mysql_stmt_data_seek
#mysql_stmt_data_seek.restype = None
#mysql_stmt_data_seek.argtypes = [POINTER(MYSQL_STMT), c_ulonglong]
#mysql_stmt_num_rows = _stdcall_libraries['libmysql.dll'].mysql_stmt_num_rows
#mysql_stmt_num_rows.restype = my_ulonglong
#mysql_stmt_num_rows.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_affected_rows = _stdcall_libraries['libmysql.dll'].mysql_stmt_affected_rows
#mysql_stmt_affected_rows.restype = my_ulonglong
#mysql_stmt_affected_rows.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_insert_id = _stdcall_libraries['libmysql.dll'].mysql_stmt_insert_id
#mysql_stmt_insert_id.restype = my_ulonglong
#mysql_stmt_insert_id.argtypes = [POINTER(MYSQL_STMT)]
#mysql_stmt_field_count = _stdcall_libraries['libmysql.dll'].mysql_stmt_field_count
#mysql_stmt_field_count.restype = c_uint
#mysql_stmt_field_count.argtypes = [POINTER(MYSQL_STMT)]
#mysql_commit = _stdcall_libraries['libmysql.dll'].mysql_commit
#mysql_commit.restype = my_bool
#mysql_commit.argtypes = [POINTER(MYSQL)]
#mysql_rollback = _stdcall_libraries['libmysql.dll'].mysql_rollback
#mysql_rollback.restype = my_bool
#mysql_rollback.argtypes = [POINTER(MYSQL)]
#mysql_autocommit = _stdcall_libraries['libmysql.dll'].mysql_autocommit
#mysql_autocommit.restype = my_bool
#mysql_autocommit.argtypes = [POINTER(MYSQL), my_bool]
#mysql_more_results = _stdcall_libraries['libmysql.dll'].mysql_more_results
#mysql_more_results.restype = my_bool
#mysql_more_results.argtypes = [POINTER(MYSQL)]
#mysql_next_result = _stdcall_libraries['libmysql.dll'].mysql_next_result
#mysql_next_result.restype = c_int
#mysql_next_result.argtypes = [POINTER(MYSQL)]
#mysql_close = _stdcall_libraries['libmysql.dll'].mysql_close
#mysql_close.restype = None
#mysql_close.argtypes = [POINTER(MYSQL)]
#st_vio._fields_ = [
#]
#
## values for enumeration 'enum_cursor_type'
#enum_cursor_type = c_int # enum
#class rand_struct(Structure):
#    pass
#rand_struct._fields_ = [
#    ('seed1', c_ulong),
#    ('seed2', c_ulong),
#    ('max_value', c_ulong),
#    ('max_value_dbl', c_double),
#]
#
## values for enumeration 'Item_result'
#Item_result = c_int # enum
#class st_udf_args(Structure):
#    pass
#st_udf_args._fields_ = [
#    ('arg_count', c_uint),
#    ('arg_type', POINTER(Item_result)),
#    ('args', POINTER(STRING)),
#    ('lengths', POINTER(c_ulong)),
#    ('maybe_null', STRING),
#    ('attributes', POINTER(STRING)),
#    ('attribute_lengths', POINTER(c_ulong)),
#    ('extension', c_void_p),
#]
#UDF_ARGS = st_udf_args
#class st_udf_init(Structure):
#    pass
#st_udf_init._fields_ = [
#    ('maybe_null', my_bool),
#    ('decimals', c_uint),
#    ('max_length', c_ulong),
#    ('ptr', STRING),
#    ('const_item', my_bool),
#    ('extension', c_void_p),
#]
#UDF_INIT = st_udf_init
#
## values for enumeration 'enum_mysql_timestamp_type'
#enum_mysql_timestamp_type = c_int # enum
#class st_mysql_time(Structure):
#    pass
#st_mysql_time._fields_ = [
#    ('year', c_uint),
#    ('month', c_uint),
#    ('day', c_uint),
#    ('hour', c_uint),
#    ('minute', c_uint),
#    ('second', c_uint),
#    ('second_part', c_ulong),
#    ('neg', my_bool),
#    ('time_type', enum_mysql_timestamp_type),
#]
#MYSQL_TIME = st_mysql_time
#class st_typelib(Structure):
#    pass
#st_typelib._fields_ = [
#    ('count', c_uint),
#    ('name', STRING),
#    ('type_names', POINTER(STRING)),
#    ('type_lengths', POINTER(c_uint)),
#]
#TYPELIB = st_typelib
#POINTER_64_INT = c_ulong
#PVOID64 = c_void_p
#PWCHAR = WSTRING
#PWCH = WSTRING
#LPWCH = WSTRING
#PCWCH = WSTRING
#LPCWCH = WSTRING
#NWPSTR = WSTRING
#PWSTR = WSTRING
#LPUWSTR = WSTRING
#PUWSTR = WSTRING
#PCWSTR = WSTRING
#PCUWSTR = WSTRING
#LPCUWSTR = WSTRING
#PCHAR = STRING
#PCH = STRING
#LPCH = STRING
#PCCH = STRING
#LPCCH = STRING
#NPSTR = STRING
#PCSTR = STRING
#TCHAR = c_char
#PTCHAR = STRING
#PTBYTE = POINTER(c_ubyte)
#TBYTE = c_ubyte
#PTCH = LPSTR
#LPTCH = LPSTR
#LPTSTR = LPSTR
#PUTSTR = LPSTR
#PTSTR = LPSTR
#LPUTSTR = LPSTR
#LPCUTSTR = LPCSTR
#LPCTSTR = LPCSTR
#PCTSTR = LPCSTR
#PCUTSTR = LPCSTR
#PSHORT = POINTER(SHORT)
#PLONG = POINTER(LONG)
#PHANDLE = POINTER(HANDLE)
#FCHAR = BYTE
#FSHORT = WORD
#FLONG = DWORD
#CCHAR = c_char
#PLCID = PDWORD
#class _FLOAT128(Structure):
#    pass
#_FLOAT128._fields_ = [
#    ('LowPart', c_longlong),
#    ('HighPart', c_longlong),
#]
#FLOAT128 = _FLOAT128
#PFLOAT128 = POINTER(FLOAT128)
#LONGLONG = c_longlong
#PLONGLONG = POINTER(LONGLONG)
#PULONGLONG = POINTER(ULONGLONG)
#USN = LONGLONG
#class N14_LARGE_INTEGER3DOLLAR_0E(Structure):
#    pass
#N14_LARGE_INTEGER3DOLLAR_0E._fields_ = [
#    ('LowPart', DWORD),
#    ('HighPart', LONG),
#]
#class N14_LARGE_INTEGER3DOLLAR_1E(Structure):
#    pass
#N14_LARGE_INTEGER3DOLLAR_1E._fields_ = [
#    ('LowPart', DWORD),
#    ('HighPart', LONG),
#]
#PLARGE_INTEGER = POINTER(LARGE_INTEGER)
#class N15_ULARGE_INTEGER3DOLLAR_2E(Structure):
#    pass
#N15_ULARGE_INTEGER3DOLLAR_2E._fields_ = [
#    ('LowPart', DWORD),
#    ('HighPart', DWORD),
#]
#class N15_ULARGE_INTEGER3DOLLAR_3E(Structure):
#    pass
#N15_ULARGE_INTEGER3DOLLAR_3E._fields_ = [
#    ('LowPart', DWORD),
#    ('HighPart', DWORD),
#]
#PULARGE_INTEGER = POINTER(ULARGE_INTEGER)
#class _LUID(Structure):
#    pass
#_LUID._fields_ = [
#    ('LowPart', DWORD),
#    ('HighPart', LONG),
#]
#PLUID = POINTER(_LUID)
#LUID = _LUID
#PDWORDLONG = POINTER(DWORDLONG)
#PBOOLEAN = POINTER(BOOLEAN)
#class _LIST_ENTRY(Structure):
#    pass
#_LIST_ENTRY._fields_ = [
#    ('Flink', POINTER(_LIST_ENTRY)),
#    ('Blink', POINTER(_LIST_ENTRY)),
#]
#LIST_ENTRY = _LIST_ENTRY
#PRLIST_ENTRY = POINTER(_LIST_ENTRY)
#PLIST_ENTRY = POINTER(_LIST_ENTRY)
#class _SINGLE_LIST_ENTRY(Structure):
#    pass
#_SINGLE_LIST_ENTRY._fields_ = [
#    ('Next', POINTER(_SINGLE_LIST_ENTRY)),
#]
#PSINGLE_LIST_ENTRY = POINTER(_SINGLE_LIST_ENTRY)
#SINGLE_LIST_ENTRY = _SINGLE_LIST_ENTRY
#class LIST_ENTRY32(Structure):
#    pass
#LIST_ENTRY32._fields_ = [
#    ('Flink', DWORD),
#    ('Blink', DWORD),
#]
#PLIST_ENTRY32 = POINTER(LIST_ENTRY32)
#class LIST_ENTRY64(Structure):
#    pass
#LIST_ENTRY64._fields_ = [
#    ('Flink', ULONGLONG),
#    ('Blink', ULONGLONG),
#]
#PLIST_ENTRY64 = POINTER(LIST_ENTRY64)
#class _OBJECTID(Structure):
#    pass
#_OBJECTID._fields_ = [
#    ('Lineage', GUID),
#    ('Uniquifier', DWORD),
#]
#OBJECTID = _OBJECTID
#KSPIN_LOCK = ULONG_PTR
#PKSPIN_LOCK = POINTER(KSPIN_LOCK)
#class _TEB(Structure):
#    pass
#_TEB._fields_ = [
#]
#class _FLOATING_SAVE_AREA(Structure):
#    pass
#_FLOATING_SAVE_AREA._fields_ = [
#    ('ControlWord', DWORD),
#    ('StatusWord', DWORD),
#    ('TagWord', DWORD),
#    ('ErrorOffset', DWORD),
#    ('ErrorSelector', DWORD),
#    ('DataOffset', DWORD),
#    ('DataSelector', DWORD),
#    ('RegisterArea', BYTE * 80),
#    ('Cr0NpxState', DWORD),
#]
#FLOATING_SAVE_AREA = _FLOATING_SAVE_AREA
#PFLOATING_SAVE_AREA = POINTER(FLOATING_SAVE_AREA)
#_CONTEXT._fields_ = [
#    ('ContextFlags', DWORD),
#    ('Dr0', DWORD),
#    ('Dr1', DWORD),
#    ('Dr2', DWORD),
#    ('Dr3', DWORD),
#    ('Dr6', DWORD),
#    ('Dr7', DWORD),
#    ('FloatSave', FLOATING_SAVE_AREA),
#    ('SegGs', DWORD),
#    ('SegFs', DWORD),
#    ('SegEs', DWORD),
#    ('SegDs', DWORD),
#    ('Edi', DWORD),
#    ('Esi', DWORD),
#    ('Ebx', DWORD),
#    ('Edx', DWORD),
#    ('Ecx', DWORD),
#    ('Eax', DWORD),
#    ('Ebp', DWORD),
#    ('Eip', DWORD),
#    ('SegCs', DWORD),
#    ('EFlags', DWORD),
#    ('Esp', DWORD),
#    ('SegSs', DWORD),
#    ('ExtendedRegisters', BYTE * 512),
#]
#class N10_LDT_ENTRY3DOLLAR_4E(Union):
#    pass
#class N10_LDT_ENTRY3DOLLAR_43DOLLAR_5E(Structure):
#    pass
#N10_LDT_ENTRY3DOLLAR_43DOLLAR_5E._fields_ = [
#    ('BaseMid', BYTE),
#    ('Flags1', BYTE),
#    ('Flags2', BYTE),
#    ('BaseHi', BYTE),
#]
#class N10_LDT_ENTRY3DOLLAR_43DOLLAR_6E(Structure):
#    pass
#N10_LDT_ENTRY3DOLLAR_43DOLLAR_6E._fields_ = [
#    ('BaseMid', DWORD, 8),
#    ('Type', DWORD, 5),
#    ('Dpl', DWORD, 2),
#    ('Pres', DWORD, 1),
#    ('LimitHi', DWORD, 4),
#    ('Sys', DWORD, 1),
#    ('Reserved_0', DWORD, 1),
#    ('Default_Big', DWORD, 1),
#    ('Granularity', DWORD, 1),
#    ('BaseHi', DWORD, 8),
#]
#N10_LDT_ENTRY3DOLLAR_4E._fields_ = [
#    ('Bytes', N10_LDT_ENTRY3DOLLAR_43DOLLAR_5E),
#    ('Bits', N10_LDT_ENTRY3DOLLAR_43DOLLAR_6E),
#]
#_LDT_ENTRY._fields_ = [
#    ('LimitLow', WORD),
#    ('BaseLow', WORD),
#    ('HighWord', N10_LDT_ENTRY3DOLLAR_4E),
#]
#LDT_ENTRY = _LDT_ENTRY
#class _EXCEPTION_RECORD32(Structure):
#    pass
#_EXCEPTION_RECORD32._fields_ = [
#    ('ExceptionCode', DWORD),
#    ('ExceptionFlags', DWORD),
#    ('ExceptionRecord', DWORD),
#    ('ExceptionAddress', DWORD),
#    ('NumberParameters', DWORD),
#    ('ExceptionInformation', DWORD * 15),
#]
#PEXCEPTION_RECORD32 = POINTER(_EXCEPTION_RECORD32)
#EXCEPTION_RECORD32 = _EXCEPTION_RECORD32
#class _EXCEPTION_RECORD64(Structure):
#    pass
#_EXCEPTION_RECORD64._fields_ = [
#    ('ExceptionCode', DWORD),
#    ('ExceptionFlags', DWORD),
#    ('ExceptionRecord', DWORD64),
#    ('ExceptionAddress', DWORD64),
#    ('NumberParameters', DWORD),
#    ('__unusedAlignment', DWORD),
#    ('ExceptionInformation', DWORD64 * 15),
#]
#PEXCEPTION_RECORD64 = POINTER(_EXCEPTION_RECORD64)
#EXCEPTION_RECORD64 = _EXCEPTION_RECORD64
#_EXCEPTION_POINTERS._fields_ = [
#    ('ExceptionRecord', PEXCEPTION_RECORD),
#    ('ContextRecord', PCONTEXT),
#]
#EXCEPTION_POINTERS = _EXCEPTION_POINTERS
#PACCESS_TOKEN = PVOID
#PSECURITY_DESCRIPTOR = PVOID
#PSID = PVOID
#PACCESS_MASK = POINTER(ACCESS_MASK)
#class _GENERIC_MAPPING(Structure):
#    pass
#_GENERIC_MAPPING._fields_ = [
#    ('GenericRead', ACCESS_MASK),
#    ('GenericWrite', ACCESS_MASK),
#    ('GenericExecute', ACCESS_MASK),
#    ('GenericAll', ACCESS_MASK),
#]
#GENERIC_MAPPING = _GENERIC_MAPPING
#PGENERIC_MAPPING = POINTER(GENERIC_MAPPING)
#class _LUID_AND_ATTRIBUTES(Structure):
#    pass
#_LUID_AND_ATTRIBUTES._fields_ = [
#    ('Luid', LUID),
#    ('Attributes', DWORD),
#]
#PLUID_AND_ATTRIBUTES = POINTER(_LUID_AND_ATTRIBUTES)
#LUID_AND_ATTRIBUTES = _LUID_AND_ATTRIBUTES
#LUID_AND_ATTRIBUTES_ARRAY = LUID_AND_ATTRIBUTES * 1
#PLUID_AND_ATTRIBUTES_ARRAY = POINTER(LUID_AND_ATTRIBUTES_ARRAY)
#class _SID_IDENTIFIER_AUTHORITY(Structure):
#    pass
#_SID_IDENTIFIER_AUTHORITY._fields_ = [
#    ('Value', BYTE * 6),
#]
#SID_IDENTIFIER_AUTHORITY = _SID_IDENTIFIER_AUTHORITY
#PSID_IDENTIFIER_AUTHORITY = POINTER(_SID_IDENTIFIER_AUTHORITY)
#class _SID(Structure):
#    pass
#_SID._fields_ = [
#    ('Revision', BYTE),
#    ('SubAuthorityCount', BYTE),
#    ('IdentifierAuthority', SID_IDENTIFIER_AUTHORITY),
#    ('SubAuthority', DWORD * 1),
#]
#SID = _SID
#PISID = POINTER(_SID)
#
## values for enumeration '_SID_NAME_USE'
#_SID_NAME_USE = c_int # enum
#SID_NAME_USE = _SID_NAME_USE
#PSID_NAME_USE = POINTER(_SID_NAME_USE)
#class _SID_AND_ATTRIBUTES(Structure):
#    pass
#_SID_AND_ATTRIBUTES._fields_ = [
#    ('Sid', PSID),
#    ('Attributes', DWORD),
#]
#PSID_AND_ATTRIBUTES = POINTER(_SID_AND_ATTRIBUTES)
#SID_AND_ATTRIBUTES = _SID_AND_ATTRIBUTES
#SID_AND_ATTRIBUTES_ARRAY = SID_AND_ATTRIBUTES * 1
#PSID_AND_ATTRIBUTES_ARRAY = POINTER(SID_AND_ATTRIBUTES_ARRAY)
#
## values for enumeration 'WELL_KNOWN_SID_TYPE'
#WELL_KNOWN_SID_TYPE = c_int # enum
#class _ACL(Structure):
#    pass
#_ACL._fields_ = [
#    ('AclRevision', BYTE),
#    ('Sbz1', BYTE),
#    ('AclSize', WORD),
#    ('AceCount', WORD),
#    ('Sbz2', WORD),
#]
#ACL = _ACL
#PACL = POINTER(ACL)
#class _ACE_HEADER(Structure):
#    pass
#_ACE_HEADER._fields_ = [
#    ('AceType', BYTE),
#    ('AceFlags', BYTE),
#    ('AceSize', WORD),
#]
#ACE_HEADER = _ACE_HEADER
#PACE_HEADER = POINTER(ACE_HEADER)
#class _ACCESS_ALLOWED_ACE(Structure):
#    pass
#_ACCESS_ALLOWED_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#ACCESS_ALLOWED_ACE = _ACCESS_ALLOWED_ACE
#PACCESS_ALLOWED_ACE = POINTER(ACCESS_ALLOWED_ACE)
#class _ACCESS_DENIED_ACE(Structure):
#    pass
#_ACCESS_DENIED_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#ACCESS_DENIED_ACE = _ACCESS_DENIED_ACE
#PACCESS_DENIED_ACE = POINTER(ACCESS_DENIED_ACE)
#class _SYSTEM_AUDIT_ACE(Structure):
#    pass
#_SYSTEM_AUDIT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#SYSTEM_AUDIT_ACE = _SYSTEM_AUDIT_ACE
#PSYSTEM_AUDIT_ACE = POINTER(SYSTEM_AUDIT_ACE)
#class _SYSTEM_ALARM_ACE(Structure):
#    pass
#_SYSTEM_ALARM_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#SYSTEM_ALARM_ACE = _SYSTEM_ALARM_ACE
#PSYSTEM_ALARM_ACE = POINTER(SYSTEM_ALARM_ACE)
#class _ACCESS_ALLOWED_OBJECT_ACE(Structure):
#    pass
#_ACCESS_ALLOWED_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#PACCESS_ALLOWED_OBJECT_ACE = POINTER(_ACCESS_ALLOWED_OBJECT_ACE)
#ACCESS_ALLOWED_OBJECT_ACE = _ACCESS_ALLOWED_OBJECT_ACE
#class _ACCESS_DENIED_OBJECT_ACE(Structure):
#    pass
#_ACCESS_DENIED_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#ACCESS_DENIED_OBJECT_ACE = _ACCESS_DENIED_OBJECT_ACE
#PACCESS_DENIED_OBJECT_ACE = POINTER(_ACCESS_DENIED_OBJECT_ACE)
#class _SYSTEM_AUDIT_OBJECT_ACE(Structure):
#    pass
#_SYSTEM_AUDIT_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#PSYSTEM_AUDIT_OBJECT_ACE = POINTER(_SYSTEM_AUDIT_OBJECT_ACE)
#SYSTEM_AUDIT_OBJECT_ACE = _SYSTEM_AUDIT_OBJECT_ACE
#class _SYSTEM_ALARM_OBJECT_ACE(Structure):
#    pass
#_SYSTEM_ALARM_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#PSYSTEM_ALARM_OBJECT_ACE = POINTER(_SYSTEM_ALARM_OBJECT_ACE)
#SYSTEM_ALARM_OBJECT_ACE = _SYSTEM_ALARM_OBJECT_ACE
#class _ACCESS_ALLOWED_CALLBACK_ACE(Structure):
#    pass
#_ACCESS_ALLOWED_CALLBACK_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#ACCESS_ALLOWED_CALLBACK_ACE = _ACCESS_ALLOWED_CALLBACK_ACE
#PACCESS_ALLOWED_CALLBACK_ACE = POINTER(_ACCESS_ALLOWED_CALLBACK_ACE)
#class _ACCESS_DENIED_CALLBACK_ACE(Structure):
#    pass
#_ACCESS_DENIED_CALLBACK_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#PACCESS_DENIED_CALLBACK_ACE = POINTER(_ACCESS_DENIED_CALLBACK_ACE)
#ACCESS_DENIED_CALLBACK_ACE = _ACCESS_DENIED_CALLBACK_ACE
#class _SYSTEM_AUDIT_CALLBACK_ACE(Structure):
#    pass
#_SYSTEM_AUDIT_CALLBACK_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#SYSTEM_AUDIT_CALLBACK_ACE = _SYSTEM_AUDIT_CALLBACK_ACE
#PSYSTEM_AUDIT_CALLBACK_ACE = POINTER(_SYSTEM_AUDIT_CALLBACK_ACE)
#class _SYSTEM_ALARM_CALLBACK_ACE(Structure):
#    pass
#_SYSTEM_ALARM_CALLBACK_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('SidStart', DWORD),
#]
#PSYSTEM_ALARM_CALLBACK_ACE = POINTER(_SYSTEM_ALARM_CALLBACK_ACE)
#SYSTEM_ALARM_CALLBACK_ACE = _SYSTEM_ALARM_CALLBACK_ACE
#class _ACCESS_ALLOWED_CALLBACK_OBJECT_ACE(Structure):
#    pass
#_ACCESS_ALLOWED_CALLBACK_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#PACCESS_ALLOWED_CALLBACK_OBJECT_ACE = POINTER(_ACCESS_ALLOWED_CALLBACK_OBJECT_ACE)
#ACCESS_ALLOWED_CALLBACK_OBJECT_ACE = _ACCESS_ALLOWED_CALLBACK_OBJECT_ACE
#class _ACCESS_DENIED_CALLBACK_OBJECT_ACE(Structure):
#    pass
#_ACCESS_DENIED_CALLBACK_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#ACCESS_DENIED_CALLBACK_OBJECT_ACE = _ACCESS_DENIED_CALLBACK_OBJECT_ACE
#PACCESS_DENIED_CALLBACK_OBJECT_ACE = POINTER(_ACCESS_DENIED_CALLBACK_OBJECT_ACE)
#class _SYSTEM_AUDIT_CALLBACK_OBJECT_ACE(Structure):
#    pass
#_SYSTEM_AUDIT_CALLBACK_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#SYSTEM_AUDIT_CALLBACK_OBJECT_ACE = _SYSTEM_AUDIT_CALLBACK_OBJECT_ACE
#PSYSTEM_AUDIT_CALLBACK_OBJECT_ACE = POINTER(_SYSTEM_AUDIT_CALLBACK_OBJECT_ACE)
#class _SYSTEM_ALARM_CALLBACK_OBJECT_ACE(Structure):
#    pass
#_SYSTEM_ALARM_CALLBACK_OBJECT_ACE._fields_ = [
#    ('Header', ACE_HEADER),
#    ('Mask', ACCESS_MASK),
#    ('Flags', DWORD),
#    ('ObjectType', GUID),
#    ('InheritedObjectType', GUID),
#    ('SidStart', DWORD),
#]
#PSYSTEM_ALARM_CALLBACK_OBJECT_ACE = POINTER(_SYSTEM_ALARM_CALLBACK_OBJECT_ACE)
#SYSTEM_ALARM_CALLBACK_OBJECT_ACE = _SYSTEM_ALARM_CALLBACK_OBJECT_ACE
#
## values for enumeration '_ACL_INFORMATION_CLASS'
#_ACL_INFORMATION_CLASS = c_int # enum
#ACL_INFORMATION_CLASS = _ACL_INFORMATION_CLASS
#class _ACL_REVISION_INFORMATION(Structure):
#    pass
#_ACL_REVISION_INFORMATION._fields_ = [
#    ('AclRevision', DWORD),
#]
#ACL_REVISION_INFORMATION = _ACL_REVISION_INFORMATION
#PACL_REVISION_INFORMATION = POINTER(ACL_REVISION_INFORMATION)
#class _ACL_SIZE_INFORMATION(Structure):
#    pass
#_ACL_SIZE_INFORMATION._fields_ = [
#    ('AceCount', DWORD),
#    ('AclBytesInUse', DWORD),
#    ('AclBytesFree', DWORD),
#]
#ACL_SIZE_INFORMATION = _ACL_SIZE_INFORMATION
#PACL_SIZE_INFORMATION = POINTER(ACL_SIZE_INFORMATION)
#SECURITY_DESCRIPTOR_CONTROL = WORD
#PSECURITY_DESCRIPTOR_CONTROL = POINTER(WORD)
#class _SECURITY_DESCRIPTOR_RELATIVE(Structure):
#    pass
#_SECURITY_DESCRIPTOR_RELATIVE._fields_ = [
#    ('Revision', BYTE),
#    ('Sbz1', BYTE),
#    ('Control', SECURITY_DESCRIPTOR_CONTROL),
#    ('Owner', DWORD),
#    ('Group', DWORD),
#    ('Sacl', DWORD),
#    ('Dacl', DWORD),
#]
#SECURITY_DESCRIPTOR_RELATIVE = _SECURITY_DESCRIPTOR_RELATIVE
#PISECURITY_DESCRIPTOR_RELATIVE = POINTER(_SECURITY_DESCRIPTOR_RELATIVE)
#class _SECURITY_DESCRIPTOR(Structure):
#    pass
#_SECURITY_DESCRIPTOR._fields_ = [
#    ('Revision', BYTE),
#    ('Sbz1', BYTE),
#    ('Control', SECURITY_DESCRIPTOR_CONTROL),
#    ('Owner', PSID),
#    ('Group', PSID),
#    ('Sacl', PACL),
#    ('Dacl', PACL),
#]
#SECURITY_DESCRIPTOR = _SECURITY_DESCRIPTOR
#PISECURITY_DESCRIPTOR = POINTER(_SECURITY_DESCRIPTOR)
#class _OBJECT_TYPE_LIST(Structure):
#    pass
#_OBJECT_TYPE_LIST._fields_ = [
#    ('Level', WORD),
#    ('Sbz', WORD),
#    ('ObjectType', POINTER(GUID)),
#]
#POBJECT_TYPE_LIST = POINTER(_OBJECT_TYPE_LIST)
#OBJECT_TYPE_LIST = _OBJECT_TYPE_LIST
#
## values for enumeration '_AUDIT_EVENT_TYPE'
#_AUDIT_EVENT_TYPE = c_int # enum
#PAUDIT_EVENT_TYPE = POINTER(_AUDIT_EVENT_TYPE)
#AUDIT_EVENT_TYPE = _AUDIT_EVENT_TYPE
#class _PRIVILEGE_SET(Structure):
#    pass
#_PRIVILEGE_SET._fields_ = [
#    ('PrivilegeCount', DWORD),
#    ('Control', DWORD),
#    ('Privilege', LUID_AND_ATTRIBUTES * 1),
#]
#PRIVILEGE_SET = _PRIVILEGE_SET
#PPRIVILEGE_SET = POINTER(_PRIVILEGE_SET)
#
## values for enumeration '_SECURITY_IMPERSONATION_LEVEL'
#_SECURITY_IMPERSONATION_LEVEL = c_int # enum
#PSECURITY_IMPERSONATION_LEVEL = POINTER(_SECURITY_IMPERSONATION_LEVEL)
#SECURITY_IMPERSONATION_LEVEL = _SECURITY_IMPERSONATION_LEVEL
#
## values for enumeration '_TOKEN_TYPE'
#_TOKEN_TYPE = c_int # enum
#TOKEN_TYPE = _TOKEN_TYPE
#PTOKEN_TYPE = POINTER(TOKEN_TYPE)
#
## values for enumeration '_TOKEN_INFORMATION_CLASS'
#_TOKEN_INFORMATION_CLASS = c_int # enum
#PTOKEN_INFORMATION_CLASS = POINTER(_TOKEN_INFORMATION_CLASS)
#TOKEN_INFORMATION_CLASS = _TOKEN_INFORMATION_CLASS
#class _TOKEN_USER(Structure):
#    pass
#_TOKEN_USER._fields_ = [
#    ('User', SID_AND_ATTRIBUTES),
#]
#PTOKEN_USER = POINTER(_TOKEN_USER)
#TOKEN_USER = _TOKEN_USER
#class _TOKEN_GROUPS(Structure):
#    pass
#_TOKEN_GROUPS._fields_ = [
#    ('GroupCount', DWORD),
#    ('Groups', SID_AND_ATTRIBUTES * 1),
#]
#PTOKEN_GROUPS = POINTER(_TOKEN_GROUPS)
#TOKEN_GROUPS = _TOKEN_GROUPS
#class _TOKEN_PRIVILEGES(Structure):
#    pass
#_TOKEN_PRIVILEGES._fields_ = [
#    ('PrivilegeCount', DWORD),
#    ('Privileges', LUID_AND_ATTRIBUTES * 1),
#]
#PTOKEN_PRIVILEGES = POINTER(_TOKEN_PRIVILEGES)
#TOKEN_PRIVILEGES = _TOKEN_PRIVILEGES
#class _TOKEN_OWNER(Structure):
#    pass
#_TOKEN_OWNER._fields_ = [
#    ('Owner', PSID),
#]
#TOKEN_OWNER = _TOKEN_OWNER
#PTOKEN_OWNER = POINTER(_TOKEN_OWNER)
#class _TOKEN_PRIMARY_GROUP(Structure):
#    pass
#_TOKEN_PRIMARY_GROUP._fields_ = [
#    ('PrimaryGroup', PSID),
#]
#TOKEN_PRIMARY_GROUP = _TOKEN_PRIMARY_GROUP
#PTOKEN_PRIMARY_GROUP = POINTER(_TOKEN_PRIMARY_GROUP)
#class _TOKEN_DEFAULT_DACL(Structure):
#    pass
#_TOKEN_DEFAULT_DACL._fields_ = [
#    ('DefaultDacl', PACL),
#]
#TOKEN_DEFAULT_DACL = _TOKEN_DEFAULT_DACL
#PTOKEN_DEFAULT_DACL = POINTER(_TOKEN_DEFAULT_DACL)
#class _TOKEN_GROUPS_AND_PRIVILEGES(Structure):
#    pass
#_TOKEN_GROUPS_AND_PRIVILEGES._fields_ = [
#    ('SidCount', DWORD),
#    ('SidLength', DWORD),
#    ('Sids', PSID_AND_ATTRIBUTES),
#    ('RestrictedSidCount', DWORD),
#    ('RestrictedSidLength', DWORD),
#    ('RestrictedSids', PSID_AND_ATTRIBUTES),
#    ('PrivilegeCount', DWORD),
#    ('PrivilegeLength', DWORD),
#    ('Privileges', PLUID_AND_ATTRIBUTES),
#    ('AuthenticationId', LUID),
#]
#TOKEN_GROUPS_AND_PRIVILEGES = _TOKEN_GROUPS_AND_PRIVILEGES
#PTOKEN_GROUPS_AND_PRIVILEGES = POINTER(_TOKEN_GROUPS_AND_PRIVILEGES)
#class _TOKEN_AUDIT_POLICY_ELEMENT(Structure):
#    pass
#_TOKEN_AUDIT_POLICY_ELEMENT._fields_ = [
#    ('Category', DWORD),
#    ('PolicyMask', DWORD),
#]
#TOKEN_AUDIT_POLICY_ELEMENT = _TOKEN_AUDIT_POLICY_ELEMENT
#PTOKEN_AUDIT_POLICY_ELEMENT = POINTER(_TOKEN_AUDIT_POLICY_ELEMENT)
#class _TOKEN_AUDIT_POLICY(Structure):
#    pass
#_TOKEN_AUDIT_POLICY._fields_ = [
#    ('PolicyCount', DWORD),
#    ('Policy', TOKEN_AUDIT_POLICY_ELEMENT * 1),
#]
#PTOKEN_AUDIT_POLICY = POINTER(_TOKEN_AUDIT_POLICY)
#TOKEN_AUDIT_POLICY = _TOKEN_AUDIT_POLICY
#class _TOKEN_SOURCE(Structure):
#    pass
#_TOKEN_SOURCE._fields_ = [
#    ('SourceName', CHAR * 8),
#    ('SourceIdentifier', LUID),
#]
#PTOKEN_SOURCE = POINTER(_TOKEN_SOURCE)
#TOKEN_SOURCE = _TOKEN_SOURCE
#class _TOKEN_STATISTICS(Structure):
#    pass
#_TOKEN_STATISTICS._fields_ = [
#    ('TokenId', LUID),
#    ('AuthenticationId', LUID),
#    ('ExpirationTime', LARGE_INTEGER),
#    ('TokenType', TOKEN_TYPE),
#    ('ImpersonationLevel', SECURITY_IMPERSONATION_LEVEL),
#    ('DynamicCharged', DWORD),
#    ('DynamicAvailable', DWORD),
#    ('GroupCount', DWORD),
#    ('PrivilegeCount', DWORD),
#    ('ModifiedId', LUID),
#]
#PTOKEN_STATISTICS = POINTER(_TOKEN_STATISTICS)
#TOKEN_STATISTICS = _TOKEN_STATISTICS
#class _TOKEN_CONTROL(Structure):
#    pass
#_TOKEN_CONTROL._fields_ = [
#    ('TokenId', LUID),
#    ('AuthenticationId', LUID),
#    ('ModifiedId', LUID),
#    ('TokenSource', TOKEN_SOURCE),
#]
#TOKEN_CONTROL = _TOKEN_CONTROL
#PTOKEN_CONTROL = POINTER(_TOKEN_CONTROL)
#SECURITY_CONTEXT_TRACKING_MODE = BOOLEAN
#PSECURITY_CONTEXT_TRACKING_MODE = POINTER(BOOLEAN)
#class _SECURITY_QUALITY_OF_SERVICE(Structure):
#    pass
#_SECURITY_QUALITY_OF_SERVICE._fields_ = [
#    ('Length', DWORD),
#    ('ImpersonationLevel', SECURITY_IMPERSONATION_LEVEL),
#    ('ContextTrackingMode', SECURITY_CONTEXT_TRACKING_MODE),
#    ('EffectiveOnly', BOOLEAN),
#]
#PSECURITY_QUALITY_OF_SERVICE = POINTER(_SECURITY_QUALITY_OF_SERVICE)
#SECURITY_QUALITY_OF_SERVICE = _SECURITY_QUALITY_OF_SERVICE
#class _SE_IMPERSONATION_STATE(Structure):
#    pass
#_SE_IMPERSONATION_STATE._fields_ = [
#    ('Token', PACCESS_TOKEN),
#    ('CopyOnOpen', BOOLEAN),
#    ('EffectiveOnly', BOOLEAN),
#    ('Level', SECURITY_IMPERSONATION_LEVEL),
#]
#SE_IMPERSONATION_STATE = _SE_IMPERSONATION_STATE
#PSE_IMPERSONATION_STATE = POINTER(_SE_IMPERSONATION_STATE)
#PSECURITY_INFORMATION = POINTER(DWORD)
#SECURITY_INFORMATION = DWORD
#class _JOB_SET_ARRAY(Structure):
#    pass
#_JOB_SET_ARRAY._fields_ = [
#    ('JobHandle', HANDLE),
#    ('MemberLevel', DWORD),
#    ('Flags', DWORD),
#]
#JOB_SET_ARRAY = _JOB_SET_ARRAY
#PJOB_SET_ARRAY = POINTER(_JOB_SET_ARRAY)
#class _NT_TIB(Structure):
#    pass
#class _EXCEPTION_REGISTRATION_RECORD(Structure):
#    pass
#class N7_NT_TIB3DOLLAR_8E(Union):
#    pass
#N7_NT_TIB3DOLLAR_8E._fields_ = [
#    ('FiberData', PVOID),
#    ('Version', DWORD),
#]
#_NT_TIB._anonymous_ = ['_0']
#_NT_TIB._fields_ = [
#    ('ExceptionList', POINTER(_EXCEPTION_REGISTRATION_RECORD)),
#    ('StackBase', PVOID),
#    ('StackLimit', PVOID),
#    ('SubSystemTib', PVOID),
#    ('_0', N7_NT_TIB3DOLLAR_8E),
#    ('ArbitraryUserPointer', PVOID),
#    ('Self', POINTER(_NT_TIB)),
#]
#_EXCEPTION_REGISTRATION_RECORD._fields_ = [
#]
#NT_TIB = _NT_TIB
#PNT_TIB = POINTER(NT_TIB)
#class _NT_TIB32(Structure):
#    pass
#class N9_NT_TIB323DOLLAR_9E(Union):
#    pass
#N9_NT_TIB323DOLLAR_9E._fields_ = [
#    ('FiberData', DWORD),
#    ('Version', DWORD),
#]
#_NT_TIB32._anonymous_ = ['_0']
#_NT_TIB32._fields_ = [
#    ('ExceptionList', DWORD),
#    ('StackBase', DWORD),
#    ('StackLimit', DWORD),
#    ('SubSystemTib', DWORD),
#    ('_0', N9_NT_TIB323DOLLAR_9E),
#    ('ArbitraryUserPointer', DWORD),
#    ('Self', DWORD),
#]
#PNT_TIB32 = POINTER(_NT_TIB32)
#NT_TIB32 = _NT_TIB32
#class _NT_TIB64(Structure):
#    pass
#class N9_NT_TIB644DOLLAR_10E(Union):
#    pass
#N9_NT_TIB644DOLLAR_10E._fields_ = [
#    ('FiberData', DWORD64),
#    ('Version', DWORD),
#]
#_NT_TIB64._anonymous_ = ['_0']
#_NT_TIB64._fields_ = [
#    ('ExceptionList', DWORD64),
#    ('StackBase', DWORD64),
#    ('StackLimit', DWORD64),
#    ('SubSystemTib', DWORD64),
#    ('_0', N9_NT_TIB644DOLLAR_10E),
#    ('ArbitraryUserPointer', DWORD64),
#    ('Self', DWORD64),
#]
#PNT_TIB64 = POINTER(_NT_TIB64)
#NT_TIB64 = _NT_TIB64
#class _QUOTA_LIMITS(Structure):
#    pass
#_QUOTA_LIMITS._fields_ = [
#    ('PagedPoolLimit', SIZE_T),
#    ('NonPagedPoolLimit', SIZE_T),
#    ('MinimumWorkingSetSize', SIZE_T),
#    ('MaximumWorkingSetSize', SIZE_T),
#    ('PagefileLimit', SIZE_T),
#    ('TimeLimit', LARGE_INTEGER),
#]
#QUOTA_LIMITS = _QUOTA_LIMITS
#PQUOTA_LIMITS = POINTER(_QUOTA_LIMITS)
#class _QUOTA_LIMITS_EX(Structure):
#    pass
#_QUOTA_LIMITS_EX._fields_ = [
#    ('PagedPoolLimit', SIZE_T),
#    ('NonPagedPoolLimit', SIZE_T),
#    ('MinimumWorkingSetSize', SIZE_T),
#    ('MaximumWorkingSetSize', SIZE_T),
#    ('PagefileLimit', SIZE_T),
#    ('TimeLimit', LARGE_INTEGER),
#    ('Reserved1', SIZE_T),
#    ('Reserved2', SIZE_T),
#    ('Reserved3', SIZE_T),
#    ('Reserved4', SIZE_T),
#    ('Flags', DWORD),
#    ('Reserved5', DWORD),
#]
#QUOTA_LIMITS_EX = _QUOTA_LIMITS_EX
#PQUOTA_LIMITS_EX = POINTER(_QUOTA_LIMITS_EX)
#class _IO_COUNTERS(Structure):
#    pass
#_IO_COUNTERS._fields_ = [
#    ('ReadOperationCount', ULONGLONG),
#    ('WriteOperationCount', ULONGLONG),
#    ('OtherOperationCount', ULONGLONG),
#    ('ReadTransferCount', ULONGLONG),
#    ('WriteTransferCount', ULONGLONG),
#    ('OtherTransferCount', ULONGLONG),
#]
#IO_COUNTERS = _IO_COUNTERS
#PIO_COUNTERS = POINTER(IO_COUNTERS)
#class _JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(Structure):
#    pass
#_JOBOBJECT_BASIC_ACCOUNTING_INFORMATION._fields_ = [
#    ('TotalUserTime', LARGE_INTEGER),
#    ('TotalKernelTime', LARGE_INTEGER),
#    ('ThisPeriodTotalUserTime', LARGE_INTEGER),
#    ('ThisPeriodTotalKernelTime', LARGE_INTEGER),
#    ('TotalPageFaultCount', DWORD),
#    ('TotalProcesses', DWORD),
#    ('ActiveProcesses', DWORD),
#    ('TotalTerminatedProcesses', DWORD),
#]
#JOBOBJECT_BASIC_ACCOUNTING_INFORMATION = _JOBOBJECT_BASIC_ACCOUNTING_INFORMATION
#PJOBOBJECT_BASIC_ACCOUNTING_INFORMATION = POINTER(_JOBOBJECT_BASIC_ACCOUNTING_INFORMATION)
#class _JOBOBJECT_BASIC_LIMIT_INFORMATION(Structure):
#    pass
#_JOBOBJECT_BASIC_LIMIT_INFORMATION._fields_ = [
#    ('PerProcessUserTimeLimit', LARGE_INTEGER),
#    ('PerJobUserTimeLimit', LARGE_INTEGER),
#    ('LimitFlags', DWORD),
#    ('MinimumWorkingSetSize', SIZE_T),
#    ('MaximumWorkingSetSize', SIZE_T),
#    ('ActiveProcessLimit', DWORD),
#    ('Affinity', ULONG_PTR),
#    ('PriorityClass', DWORD),
#    ('SchedulingClass', DWORD),
#]
#JOBOBJECT_BASIC_LIMIT_INFORMATION = _JOBOBJECT_BASIC_LIMIT_INFORMATION
#PJOBOBJECT_BASIC_LIMIT_INFORMATION = POINTER(_JOBOBJECT_BASIC_LIMIT_INFORMATION)
#class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(Structure):
#    pass
#_JOBOBJECT_EXTENDED_LIMIT_INFORMATION._fields_ = [
#    ('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION),
#    ('IoInfo', IO_COUNTERS),
#    ('ProcessMemoryLimit', SIZE_T),
#    ('JobMemoryLimit', SIZE_T),
#    ('PeakProcessMemoryUsed', SIZE_T),
#    ('PeakJobMemoryUsed', SIZE_T),
#]
#JOBOBJECT_EXTENDED_LIMIT_INFORMATION = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION
#PJOBOBJECT_EXTENDED_LIMIT_INFORMATION = POINTER(_JOBOBJECT_EXTENDED_LIMIT_INFORMATION)
#class _JOBOBJECT_BASIC_PROCESS_ID_LIST(Structure):
#    pass
#_JOBOBJECT_BASIC_PROCESS_ID_LIST._fields_ = [
#    ('NumberOfAssignedProcesses', DWORD),
#    ('NumberOfProcessIdsInList', DWORD),
#    ('ProcessIdList', ULONG_PTR * 1),
#]
#PJOBOBJECT_BASIC_PROCESS_ID_LIST = POINTER(_JOBOBJECT_BASIC_PROCESS_ID_LIST)
#JOBOBJECT_BASIC_PROCESS_ID_LIST = _JOBOBJECT_BASIC_PROCESS_ID_LIST
#class _JOBOBJECT_BASIC_UI_RESTRICTIONS(Structure):
#    pass
#_JOBOBJECT_BASIC_UI_RESTRICTIONS._fields_ = [
#    ('UIRestrictionsClass', DWORD),
#]
#JOBOBJECT_BASIC_UI_RESTRICTIONS = _JOBOBJECT_BASIC_UI_RESTRICTIONS
#PJOBOBJECT_BASIC_UI_RESTRICTIONS = POINTER(_JOBOBJECT_BASIC_UI_RESTRICTIONS)
#class _JOBOBJECT_SECURITY_LIMIT_INFORMATION(Structure):
#    pass
#_JOBOBJECT_SECURITY_LIMIT_INFORMATION._fields_ = [
#    ('SecurityLimitFlags', DWORD),
#    ('JobToken', HANDLE),
#    ('SidsToDisable', PTOKEN_GROUPS),
#    ('PrivilegesToDelete', PTOKEN_PRIVILEGES),
#    ('RestrictedSids', PTOKEN_GROUPS),
#]
#PJOBOBJECT_SECURITY_LIMIT_INFORMATION = POINTER(_JOBOBJECT_SECURITY_LIMIT_INFORMATION)
#JOBOBJECT_SECURITY_LIMIT_INFORMATION = _JOBOBJECT_SECURITY_LIMIT_INFORMATION
#class _JOBOBJECT_END_OF_JOB_TIME_INFORMATION(Structure):
#    pass
#_JOBOBJECT_END_OF_JOB_TIME_INFORMATION._fields_ = [
#    ('EndOfJobTimeAction', DWORD),
#]
#JOBOBJECT_END_OF_JOB_TIME_INFORMATION = _JOBOBJECT_END_OF_JOB_TIME_INFORMATION
#PJOBOBJECT_END_OF_JOB_TIME_INFORMATION = POINTER(_JOBOBJECT_END_OF_JOB_TIME_INFORMATION)
#class _JOBOBJECT_ASSOCIATE_COMPLETION_PORT(Structure):
#    pass
#_JOBOBJECT_ASSOCIATE_COMPLETION_PORT._fields_ = [
#    ('CompletionKey', PVOID),
#    ('CompletionPort', HANDLE),
#]
#PJOBOBJECT_ASSOCIATE_COMPLETION_PORT = POINTER(_JOBOBJECT_ASSOCIATE_COMPLETION_PORT)
#JOBOBJECT_ASSOCIATE_COMPLETION_PORT = _JOBOBJECT_ASSOCIATE_COMPLETION_PORT
#class _JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION(Structure):
#    pass
#_JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION._fields_ = [
#    ('BasicInfo', JOBOBJECT_BASIC_ACCOUNTING_INFORMATION),
#    ('IoInfo', IO_COUNTERS),
#]
#PJOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION = POINTER(_JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION)
#JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION = _JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION
#class _JOBOBJECT_JOBSET_INFORMATION(Structure):
#    pass
#_JOBOBJECT_JOBSET_INFORMATION._fields_ = [
#    ('MemberLevel', DWORD),
#]
#JOBOBJECT_JOBSET_INFORMATION = _JOBOBJECT_JOBSET_INFORMATION
#PJOBOBJECT_JOBSET_INFORMATION = POINTER(_JOBOBJECT_JOBSET_INFORMATION)
#
## values for enumeration '_JOBOBJECTINFOCLASS'
#_JOBOBJECTINFOCLASS = c_int # enum
#JOBOBJECTINFOCLASS = _JOBOBJECTINFOCLASS
#
## values for enumeration '_LOGICAL_PROCESSOR_RELATIONSHIP'
#_LOGICAL_PROCESSOR_RELATIONSHIP = c_int # enum
#LOGICAL_PROCESSOR_RELATIONSHIP = _LOGICAL_PROCESSOR_RELATIONSHIP
#class _SYSTEM_LOGICAL_PROCESSOR_INFORMATION(Structure):
#    pass
#class N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_11E(Union):
#    pass
#class N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_12E(Structure):
#    pass
#N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_12E._fields_ = [
#    ('Flags', BYTE),
#]
#class N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_13E(Structure):
#    pass
#N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_13E._fields_ = [
#    ('NodeNumber', DWORD),
#]
#N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_11E._fields_ = [
#    ('ProcessorCore', N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_12E),
#    ('NumaNode', N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_13E),
#    ('Reserved', ULONGLONG * 2),
#]
#_SYSTEM_LOGICAL_PROCESSOR_INFORMATION._anonymous_ = ['_0']
#_SYSTEM_LOGICAL_PROCESSOR_INFORMATION._fields_ = [
#    ('ProcessorMask', ULONG_PTR),
#    ('Relationship', LOGICAL_PROCESSOR_RELATIONSHIP),
#    ('_0', N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_11E),
#]
#PSYSTEM_LOGICAL_PROCESSOR_INFORMATION = POINTER(_SYSTEM_LOGICAL_PROCESSOR_INFORMATION)
#SYSTEM_LOGICAL_PROCESSOR_INFORMATION = _SYSTEM_LOGICAL_PROCESSOR_INFORMATION
#class _MEMORY_BASIC_INFORMATION(Structure):
#    pass
#_MEMORY_BASIC_INFORMATION._fields_ = [
#    ('BaseAddress', PVOID),
#    ('AllocationBase', PVOID),
#    ('AllocationProtect', DWORD),
#    ('RegionSize', SIZE_T),
#    ('State', DWORD),
#    ('Protect', DWORD),
#    ('Type', DWORD),
#]
#PMEMORY_BASIC_INFORMATION = POINTER(_MEMORY_BASIC_INFORMATION)
#MEMORY_BASIC_INFORMATION = _MEMORY_BASIC_INFORMATION
#class _MEMORY_BASIC_INFORMATION32(Structure):
#    pass
#_MEMORY_BASIC_INFORMATION32._fields_ = [
#    ('BaseAddress', DWORD),
#    ('AllocationBase', DWORD),
#    ('AllocationProtect', DWORD),
#    ('RegionSize', DWORD),
#    ('State', DWORD),
#    ('Protect', DWORD),
#    ('Type', DWORD),
#]
#PMEMORY_BASIC_INFORMATION32 = POINTER(_MEMORY_BASIC_INFORMATION32)
#MEMORY_BASIC_INFORMATION32 = _MEMORY_BASIC_INFORMATION32
#class _MEMORY_BASIC_INFORMATION64(Structure):
#    pass
#_MEMORY_BASIC_INFORMATION64._fields_ = [
#    ('BaseAddress', ULONGLONG),
#    ('AllocationBase', ULONGLONG),
#    ('AllocationProtect', DWORD),
#    ('__alignment1', DWORD),
#    ('RegionSize', ULONGLONG),
#    ('State', DWORD),
#    ('Protect', DWORD),
#    ('Type', DWORD),
#    ('__alignment2', DWORD),
#]
#MEMORY_BASIC_INFORMATION64 = _MEMORY_BASIC_INFORMATION64
#PMEMORY_BASIC_INFORMATION64 = POINTER(_MEMORY_BASIC_INFORMATION64)
#class _FILE_NOTIFY_INFORMATION(Structure):
#    pass
#_FILE_NOTIFY_INFORMATION._fields_ = [
#    ('NextEntryOffset', DWORD),
#    ('Action', DWORD),
#    ('FileNameLength', DWORD),
#    ('FileName', WCHAR * 1),
#]
#FILE_NOTIFY_INFORMATION = _FILE_NOTIFY_INFORMATION
#PFILE_NOTIFY_INFORMATION = POINTER(_FILE_NOTIFY_INFORMATION)
#class _FILE_SEGMENT_ELEMENT(Union):
#    pass
#_FILE_SEGMENT_ELEMENT._fields_ = [
#    ('Buffer', PVOID64),
#    ('Alignment', ULONGLONG),
#]
#PFILE_SEGMENT_ELEMENT = POINTER(_FILE_SEGMENT_ELEMENT)
#FILE_SEGMENT_ELEMENT = _FILE_SEGMENT_ELEMENT
#class _REPARSE_GUID_DATA_BUFFER(Structure):
#    pass
#class N25_REPARSE_GUID_DATA_BUFFER4DOLLAR_14E(Structure):
#    pass
#N25_REPARSE_GUID_DATA_BUFFER4DOLLAR_14E._fields_ = [
#    ('DataBuffer', BYTE * 1),
#]
#_REPARSE_GUID_DATA_BUFFER._fields_ = [
#    ('ReparseTag', DWORD),
#    ('ReparseDataLength', WORD),
#    ('Reserved', WORD),
#    ('ReparseGuid', GUID),
#    ('GenericReparseBuffer', N25_REPARSE_GUID_DATA_BUFFER4DOLLAR_14E),
#]
#REPARSE_GUID_DATA_BUFFER = _REPARSE_GUID_DATA_BUFFER
#PREPARSE_GUID_DATA_BUFFER = POINTER(_REPARSE_GUID_DATA_BUFFER)
#
## values for enumeration '_SYSTEM_POWER_STATE'
#_SYSTEM_POWER_STATE = c_int # enum
#SYSTEM_POWER_STATE = _SYSTEM_POWER_STATE
#PSYSTEM_POWER_STATE = POINTER(_SYSTEM_POWER_STATE)
#
## values for enumeration 'POWER_ACTION'
#POWER_ACTION = c_int # enum
#PPOWER_ACTION = POINTER(POWER_ACTION)
#
## values for enumeration '_DEVICE_POWER_STATE'
#_DEVICE_POWER_STATE = c_int # enum
#DEVICE_POWER_STATE = _DEVICE_POWER_STATE
#PDEVICE_POWER_STATE = POINTER(_DEVICE_POWER_STATE)
#EXECUTION_STATE = DWORD
#
## values for enumeration 'LATENCY_TIME'
#LATENCY_TIME = c_int # enum
#class CM_Power_Data_s(Structure):
#    pass
#CM_Power_Data_s._fields_ = [
#    ('PD_Size', DWORD),
#    ('PD_MostRecentPowerState', DEVICE_POWER_STATE),
#    ('PD_Capabilities', DWORD),
#    ('PD_D1Latency', DWORD),
#    ('PD_D2Latency', DWORD),
#    ('PD_D3Latency', DWORD),
#    ('PD_PowerStateMapping', DEVICE_POWER_STATE * 7),
#    ('PD_DeepestSystemWake', SYSTEM_POWER_STATE),
#]
#PCM_POWER_DATA = POINTER(CM_Power_Data_s)
#CM_POWER_DATA = CM_Power_Data_s
#
## values for enumeration 'POWER_INFORMATION_LEVEL'
#POWER_INFORMATION_LEVEL = c_int # enum
#class BATTERY_REPORTING_SCALE(Structure):
#    pass
#BATTERY_REPORTING_SCALE._fields_ = [
#    ('Granularity', DWORD),
#    ('Capacity', DWORD),
#]
#PBATTERY_REPORTING_SCALE = POINTER(BATTERY_REPORTING_SCALE)
#class POWER_ACTION_POLICY(Structure):
#    pass
#POWER_ACTION_POLICY._fields_ = [
#    ('Action', POWER_ACTION),
#    ('Flags', DWORD),
#    ('EventCode', DWORD),
#]
#PPOWER_ACTION_POLICY = POINTER(POWER_ACTION_POLICY)
#class SYSTEM_POWER_LEVEL(Structure):
#    pass
#SYSTEM_POWER_LEVEL._fields_ = [
#    ('Enable', BOOLEAN),
#    ('Spare', BYTE * 3),
#    ('BatteryLevel', DWORD),
#    ('PowerPolicy', POWER_ACTION_POLICY),
#    ('MinSystemState', SYSTEM_POWER_STATE),
#]
#PSYSTEM_POWER_LEVEL = POINTER(SYSTEM_POWER_LEVEL)
#class _SYSTEM_POWER_POLICY(Structure):
#    pass
#_SYSTEM_POWER_POLICY._fields_ = [
#    ('Revision', DWORD),
#    ('PowerButton', POWER_ACTION_POLICY),
#    ('SleepButton', POWER_ACTION_POLICY),
#    ('LidClose', POWER_ACTION_POLICY),
#    ('LidOpenWake', SYSTEM_POWER_STATE),
#    ('Reserved', DWORD),
#    ('Idle', POWER_ACTION_POLICY),
#    ('IdleTimeout', DWORD),
#    ('IdleSensitivity', BYTE),
#    ('DynamicThrottle', BYTE),
#    ('Spare2', BYTE * 2),
#    ('MinSleep', SYSTEM_POWER_STATE),
#    ('MaxSleep', SYSTEM_POWER_STATE),
#    ('ReducedLatencySleep', SYSTEM_POWER_STATE),
#    ('WinLogonFlags', DWORD),
#    ('Spare3', DWORD),
#    ('DozeS4Timeout', DWORD),
#    ('BroadcastCapacityResolution', DWORD),
#    ('DischargePolicy', SYSTEM_POWER_LEVEL * 4),
#    ('VideoTimeout', DWORD),
#    ('VideoDimDisplay', BOOLEAN),
#    ('VideoReserved', DWORD * 3),
#    ('SpindownTimeout', DWORD),
#    ('OptimizeForPower', BOOLEAN),
#    ('FanThrottleTolerance', BYTE),
#    ('ForcedThrottle', BYTE),
#    ('MinThrottle', BYTE),
#    ('OverThrottled', POWER_ACTION_POLICY),
#]
#SYSTEM_POWER_POLICY = _SYSTEM_POWER_POLICY
#PSYSTEM_POWER_POLICY = POINTER(_SYSTEM_POWER_POLICY)
#class _PROCESSOR_POWER_POLICY_INFO(Structure):
#    pass
#_PROCESSOR_POWER_POLICY_INFO._fields_ = [
#    ('TimeCheck', DWORD),
#    ('DemoteLimit', DWORD),
#    ('PromoteLimit', DWORD),
#    ('DemotePercent', BYTE),
#    ('PromotePercent', BYTE),
#    ('Spare', BYTE * 2),
#    ('AllowDemotion', DWORD, 1),
#    ('AllowPromotion', DWORD, 1),
#    ('Reserved', DWORD, 30),
#]
#PROCESSOR_POWER_POLICY_INFO = _PROCESSOR_POWER_POLICY_INFO
#PPROCESSOR_POWER_POLICY_INFO = POINTER(_PROCESSOR_POWER_POLICY_INFO)
#class _PROCESSOR_POWER_POLICY(Structure):
#    pass
#_PROCESSOR_POWER_POLICY._fields_ = [
#    ('Revision', DWORD),
#    ('DynamicThrottle', BYTE),
#    ('Spare', BYTE * 3),
#    ('DisableCStates', DWORD, 1),
#    ('Reserved', DWORD, 31),
#    ('PolicyCount', DWORD),
#    ('Policy', PROCESSOR_POWER_POLICY_INFO * 3),
#]
#PROCESSOR_POWER_POLICY = _PROCESSOR_POWER_POLICY
#PPROCESSOR_POWER_POLICY = POINTER(_PROCESSOR_POWER_POLICY)
#class _ADMINISTRATOR_POWER_POLICY(Structure):
#    pass
#_ADMINISTRATOR_POWER_POLICY._fields_ = [
#    ('MinSleep', SYSTEM_POWER_STATE),
#    ('MaxSleep', SYSTEM_POWER_STATE),
#    ('MinVideoTimeout', DWORD),
#    ('MaxVideoTimeout', DWORD),
#    ('MinSpindownTimeout', DWORD),
#    ('MaxSpindownTimeout', DWORD),
#]
#PADMINISTRATOR_POWER_POLICY = POINTER(_ADMINISTRATOR_POWER_POLICY)
#ADMINISTRATOR_POWER_POLICY = _ADMINISTRATOR_POWER_POLICY
#class SYSTEM_POWER_CAPABILITIES(Structure):
#    pass
#PSYSTEM_POWER_CAPABILITIES = POINTER(SYSTEM_POWER_CAPABILITIES)
#SYSTEM_POWER_CAPABILITIES._fields_ = [
#    ('PowerButtonPresent', BOOLEAN),
#    ('SleepButtonPresent', BOOLEAN),
#    ('LidPresent', BOOLEAN),
#    ('SystemS1', BOOLEAN),
#    ('SystemS2', BOOLEAN),
#    ('SystemS3', BOOLEAN),
#    ('SystemS4', BOOLEAN),
#    ('SystemS5', BOOLEAN),
#    ('HiberFilePresent', BOOLEAN),
#    ('FullWake', BOOLEAN),
#    ('VideoDimPresent', BOOLEAN),
#    ('ApmPresent', BOOLEAN),
#    ('UpsPresent', BOOLEAN),
#    ('ThermalControl', BOOLEAN),
#    ('ProcessorThrottle', BOOLEAN),
#    ('ProcessorMinThrottle', BYTE),
#    ('ProcessorMaxThrottle', BYTE),
#    ('spare2', BYTE * 4),
#    ('DiskSpinDown', BOOLEAN),
#    ('spare3', BYTE * 8),
#    ('SystemBatteriesPresent', BOOLEAN),
#    ('BatteriesAreShortTerm', BOOLEAN),
#    ('BatteryScale', BATTERY_REPORTING_SCALE * 3),
#    ('AcOnLineWake', SYSTEM_POWER_STATE),
#    ('SoftLidWake', SYSTEM_POWER_STATE),
#    ('RtcWake', SYSTEM_POWER_STATE),
#    ('MinDeviceWakeState', SYSTEM_POWER_STATE),
#    ('DefaultLowLatencyWake', SYSTEM_POWER_STATE),
#]
#class SYSTEM_BATTERY_STATE(Structure):
#    pass
#SYSTEM_BATTERY_STATE._fields_ = [
#    ('AcOnLine', BOOLEAN),
#    ('BatteryPresent', BOOLEAN),
#    ('Charging', BOOLEAN),
#    ('Discharging', BOOLEAN),
#    ('Spare1', BOOLEAN * 4),
#    ('MaxCapacity', DWORD),
#    ('RemainingCapacity', DWORD),
#    ('Rate', DWORD),
#    ('EstimatedTime', DWORD),
#    ('DefaultAlert1', DWORD),
#    ('DefaultAlert2', DWORD),
#]
#PSYSTEM_BATTERY_STATE = POINTER(SYSTEM_BATTERY_STATE)
#class _IMAGE_DOS_HEADER(Structure):
#    pass
#_IMAGE_DOS_HEADER._pack_ = 2
#_IMAGE_DOS_HEADER._fields_ = [
#    ('e_magic', WORD),
#    ('e_cblp', WORD),
#    ('e_cp', WORD),
#    ('e_crlc', WORD),
#    ('e_cparhdr', WORD),
#    ('e_minalloc', WORD),
#    ('e_maxalloc', WORD),
#    ('e_ss', WORD),
#    ('e_sp', WORD),
#    ('e_csum', WORD),
#    ('e_ip', WORD),
#    ('e_cs', WORD),
#    ('e_lfarlc', WORD),
#    ('e_ovno', WORD),
#    ('e_res', WORD * 4),
#    ('e_oemid', WORD),
#    ('e_oeminfo', WORD),
#    ('e_res2', WORD * 10),
#    ('e_lfanew', LONG),
#]
#PIMAGE_DOS_HEADER = POINTER(_IMAGE_DOS_HEADER)
#IMAGE_DOS_HEADER = _IMAGE_DOS_HEADER
#class _IMAGE_OS2_HEADER(Structure):
#    pass
#_IMAGE_OS2_HEADER._pack_ = 2
#_IMAGE_OS2_HEADER._fields_ = [
#    ('ne_magic', WORD),
#    ('ne_ver', CHAR),
#    ('ne_rev', CHAR),
#    ('ne_enttab', WORD),
#    ('ne_cbenttab', WORD),
#    ('ne_crc', LONG),
#    ('ne_flags', WORD),
#    ('ne_autodata', WORD),
#    ('ne_heap', WORD),
#    ('ne_stack', WORD),
#    ('ne_csip', LONG),
#    ('ne_sssp', LONG),
#    ('ne_cseg', WORD),
#    ('ne_cmod', WORD),
#    ('ne_cbnrestab', WORD),
#    ('ne_segtab', WORD),
#    ('ne_rsrctab', WORD),
#    ('ne_restab', WORD),
#    ('ne_modtab', WORD),
#    ('ne_imptab', WORD),
#    ('ne_nrestab', LONG),
#    ('ne_cmovent', WORD),
#    ('ne_align', WORD),
#    ('ne_cres', WORD),
#    ('ne_exetyp', BYTE),
#    ('ne_flagsothers', BYTE),
#    ('ne_pretthunks', WORD),
#    ('ne_psegrefbytes', WORD),
#    ('ne_swaparea', WORD),
#    ('ne_expver', WORD),
#]
#IMAGE_OS2_HEADER = _IMAGE_OS2_HEADER
#PIMAGE_OS2_HEADER = POINTER(_IMAGE_OS2_HEADER)
#class _IMAGE_VXD_HEADER(Structure):
#    pass
#_IMAGE_VXD_HEADER._pack_ = 2
#_IMAGE_VXD_HEADER._fields_ = [
#    ('e32_magic', WORD),
#    ('e32_border', BYTE),
#    ('e32_worder', BYTE),
#    ('e32_level', DWORD),
#    ('e32_cpu', WORD),
#    ('e32_os', WORD),
#    ('e32_ver', DWORD),
#    ('e32_mflags', DWORD),
#    ('e32_mpages', DWORD),
#    ('e32_startobj', DWORD),
#    ('e32_eip', DWORD),
#    ('e32_stackobj', DWORD),
#    ('e32_esp', DWORD),
#    ('e32_pagesize', DWORD),
#    ('e32_lastpagesize', DWORD),
#    ('e32_fixupsize', DWORD),
#    ('e32_fixupsum', DWORD),
#    ('e32_ldrsize', DWORD),
#    ('e32_ldrsum', DWORD),
#    ('e32_objtab', DWORD),
#    ('e32_objcnt', DWORD),
#    ('e32_objmap', DWORD),
#    ('e32_itermap', DWORD),
#    ('e32_rsrctab', DWORD),
#    ('e32_rsrccnt', DWORD),
#    ('e32_restab', DWORD),
#    ('e32_enttab', DWORD),
#    ('e32_dirtab', DWORD),
#    ('e32_dircnt', DWORD),
#    ('e32_fpagetab', DWORD),
#    ('e32_frectab', DWORD),
#    ('e32_impmod', DWORD),
#    ('e32_impmodcnt', DWORD),
#    ('e32_impproc', DWORD),
#    ('e32_pagesum', DWORD),
#    ('e32_datapage', DWORD),
#    ('e32_preload', DWORD),
#    ('e32_nrestab', DWORD),
#    ('e32_cbnrestab', DWORD),
#    ('e32_nressum', DWORD),
#    ('e32_autodata', DWORD),
#    ('e32_debuginfo', DWORD),
#    ('e32_debuglen', DWORD),
#    ('e32_instpreload', DWORD),
#    ('e32_instdemand', DWORD),
#    ('e32_heapsize', DWORD),
#    ('e32_res3', BYTE * 12),
#    ('e32_winresoff', DWORD),
#    ('e32_winreslen', DWORD),
#    ('e32_devid', WORD),
#    ('e32_ddkver', WORD),
#]
#IMAGE_VXD_HEADER = _IMAGE_VXD_HEADER
#PIMAGE_VXD_HEADER = POINTER(_IMAGE_VXD_HEADER)
#class _IMAGE_FILE_HEADER(Structure):
#    pass
#_IMAGE_FILE_HEADER._fields_ = [
#    ('Machine', WORD),
#    ('NumberOfSections', WORD),
#    ('TimeDateStamp', DWORD),
#    ('PointerToSymbolTable', DWORD),
#    ('NumberOfSymbols', DWORD),
#    ('SizeOfOptionalHeader', WORD),
#    ('Characteristics', WORD),
#]
#IMAGE_FILE_HEADER = _IMAGE_FILE_HEADER
#PIMAGE_FILE_HEADER = POINTER(_IMAGE_FILE_HEADER)
#class _IMAGE_DATA_DIRECTORY(Structure):
#    pass
#_IMAGE_DATA_DIRECTORY._fields_ = [
#    ('VirtualAddress', DWORD),
#    ('Size', DWORD),
#]
#PIMAGE_DATA_DIRECTORY = POINTER(_IMAGE_DATA_DIRECTORY)
#IMAGE_DATA_DIRECTORY = _IMAGE_DATA_DIRECTORY
#class _IMAGE_OPTIONAL_HEADER(Structure):
#    pass
#_IMAGE_OPTIONAL_HEADER._fields_ = [
#    ('Magic', WORD),
#    ('MajorLinkerVersion', BYTE),
#    ('MinorLinkerVersion', BYTE),
#    ('SizeOfCode', DWORD),
#    ('SizeOfInitializedData', DWORD),
#    ('SizeOfUninitializedData', DWORD),
#    ('AddressOfEntryPoint', DWORD),
#    ('BaseOfCode', DWORD),
#    ('BaseOfData', DWORD),
#    ('ImageBase', DWORD),
#    ('SectionAlignment', DWORD),
#    ('FileAlignment', DWORD),
#    ('MajorOperatingSystemVersion', WORD),
#    ('MinorOperatingSystemVersion', WORD),
#    ('MajorImageVersion', WORD),
#    ('MinorImageVersion', WORD),
#    ('MajorSubsystemVersion', WORD),
#    ('MinorSubsystemVersion', WORD),
#    ('Win32VersionValue', DWORD),
#    ('SizeOfImage', DWORD),
#    ('SizeOfHeaders', DWORD),
#    ('CheckSum', DWORD),
#    ('Subsystem', WORD),
#    ('DllCharacteristics', WORD),
#    ('SizeOfStackReserve', DWORD),
#    ('SizeOfStackCommit', DWORD),
#    ('SizeOfHeapReserve', DWORD),
#    ('SizeOfHeapCommit', DWORD),
#    ('LoaderFlags', DWORD),
#    ('NumberOfRvaAndSizes', DWORD),
#    ('DataDirectory', IMAGE_DATA_DIRECTORY * 16),
#]
#PIMAGE_OPTIONAL_HEADER32 = POINTER(_IMAGE_OPTIONAL_HEADER)
#IMAGE_OPTIONAL_HEADER32 = _IMAGE_OPTIONAL_HEADER
#class _IMAGE_ROM_OPTIONAL_HEADER(Structure):
#    pass
#_IMAGE_ROM_OPTIONAL_HEADER._fields_ = [
#    ('Magic', WORD),
#    ('MajorLinkerVersion', BYTE),
#    ('MinorLinkerVersion', BYTE),
#    ('SizeOfCode', DWORD),
#    ('SizeOfInitializedData', DWORD),
#    ('SizeOfUninitializedData', DWORD),
#    ('AddressOfEntryPoint', DWORD),
#    ('BaseOfCode', DWORD),
#    ('BaseOfData', DWORD),
#    ('BaseOfBss', DWORD),
#    ('GprMask', DWORD),
#    ('CprMask', DWORD * 4),
#    ('GpValue', DWORD),
#]
#IMAGE_ROM_OPTIONAL_HEADER = _IMAGE_ROM_OPTIONAL_HEADER
#PIMAGE_ROM_OPTIONAL_HEADER = POINTER(_IMAGE_ROM_OPTIONAL_HEADER)
#class _IMAGE_OPTIONAL_HEADER64(Structure):
#    pass
#_IMAGE_OPTIONAL_HEADER64._pack_ = 4
#_IMAGE_OPTIONAL_HEADER64._fields_ = [
#    ('Magic', WORD),
#    ('MajorLinkerVersion', BYTE),
#    ('MinorLinkerVersion', BYTE),
#    ('SizeOfCode', DWORD),
#    ('SizeOfInitializedData', DWORD),
#    ('SizeOfUninitializedData', DWORD),
#    ('AddressOfEntryPoint', DWORD),
#    ('BaseOfCode', DWORD),
#    ('ImageBase', ULONGLONG),
#    ('SectionAlignment', DWORD),
#    ('FileAlignment', DWORD),
#    ('MajorOperatingSystemVersion', WORD),
#    ('MinorOperatingSystemVersion', WORD),
#    ('MajorImageVersion', WORD),
#    ('MinorImageVersion', WORD),
#    ('MajorSubsystemVersion', WORD),
#    ('MinorSubsystemVersion', WORD),
#    ('Win32VersionValue', DWORD),
#    ('SizeOfImage', DWORD),
#    ('SizeOfHeaders', DWORD),
#    ('CheckSum', DWORD),
#    ('Subsystem', WORD),
#    ('DllCharacteristics', WORD),
#    ('SizeOfStackReserve', ULONGLONG),
#    ('SizeOfStackCommit', ULONGLONG),
#    ('SizeOfHeapReserve', ULONGLONG),
#    ('SizeOfHeapCommit', ULONGLONG),
#    ('LoaderFlags', DWORD),
#    ('NumberOfRvaAndSizes', DWORD),
#    ('DataDirectory', IMAGE_DATA_DIRECTORY * 16),
#]
#IMAGE_OPTIONAL_HEADER64 = _IMAGE_OPTIONAL_HEADER64
#PIMAGE_OPTIONAL_HEADER64 = POINTER(_IMAGE_OPTIONAL_HEADER64)
#IMAGE_OPTIONAL_HEADER = IMAGE_OPTIONAL_HEADER32
#PIMAGE_OPTIONAL_HEADER = PIMAGE_OPTIONAL_HEADER32
#class _IMAGE_NT_HEADERS64(Structure):
#    pass
#_IMAGE_NT_HEADERS64._fields_ = [
#    ('Signature', DWORD),
#    ('FileHeader', IMAGE_FILE_HEADER),
#    ('OptionalHeader', IMAGE_OPTIONAL_HEADER64),
#]
#PIMAGE_NT_HEADERS64 = POINTER(_IMAGE_NT_HEADERS64)
#IMAGE_NT_HEADERS64 = _IMAGE_NT_HEADERS64
#class _IMAGE_NT_HEADERS(Structure):
#    pass
#_IMAGE_NT_HEADERS._fields_ = [
#    ('Signature', DWORD),
#    ('FileHeader', IMAGE_FILE_HEADER),
#    ('OptionalHeader', IMAGE_OPTIONAL_HEADER32),
#]
#PIMAGE_NT_HEADERS32 = POINTER(_IMAGE_NT_HEADERS)
#IMAGE_NT_HEADERS32 = _IMAGE_NT_HEADERS
#class _IMAGE_ROM_HEADERS(Structure):
#    pass
#_IMAGE_ROM_HEADERS._fields_ = [
#    ('FileHeader', IMAGE_FILE_HEADER),
#    ('OptionalHeader', IMAGE_ROM_OPTIONAL_HEADER),
#]
#PIMAGE_ROM_HEADERS = POINTER(_IMAGE_ROM_HEADERS)
#IMAGE_ROM_HEADERS = _IMAGE_ROM_HEADERS
#IMAGE_NT_HEADERS = IMAGE_NT_HEADERS32
#PIMAGE_NT_HEADERS = PIMAGE_NT_HEADERS32
#class ANON_OBJECT_HEADER(Structure):
#    pass
#ANON_OBJECT_HEADER._fields_ = [
#    ('Sig1', WORD),
#    ('Sig2', WORD),
#    ('Version', WORD),
#    ('Machine', WORD),
#    ('TimeDateStamp', DWORD),
#    ('ClassID', CLSID),
#    ('SizeOfData', DWORD),
#]
#class _IMAGE_SECTION_HEADER(Structure):
#    pass
#class N21_IMAGE_SECTION_HEADER4DOLLAR_23E(Union):
#    pass
#N21_IMAGE_SECTION_HEADER4DOLLAR_23E._fields_ = [
#    ('PhysicalAddress', DWORD),
#    ('VirtualSize', DWORD),
#]
#_IMAGE_SECTION_HEADER._fields_ = [
#    ('Name', BYTE * 8),
#    ('Misc', N21_IMAGE_SECTION_HEADER4DOLLAR_23E),
#    ('VirtualAddress', DWORD),
#    ('SizeOfRawData', DWORD),
#    ('PointerToRawData', DWORD),
#    ('PointerToRelocations', DWORD),
#    ('PointerToLinenumbers', DWORD),
#    ('NumberOfRelocations', WORD),
#    ('NumberOfLinenumbers', WORD),
#    ('Characteristics', DWORD),
#]
#IMAGE_SECTION_HEADER = _IMAGE_SECTION_HEADER
#PIMAGE_SECTION_HEADER = POINTER(_IMAGE_SECTION_HEADER)
#class _IMAGE_SYMBOL(Structure):
#    pass
#class N13_IMAGE_SYMBOL4DOLLAR_24E(Union):
#    pass
#class N13_IMAGE_SYMBOL4DOLLAR_244DOLLAR_25E(Structure):
#    pass
#N13_IMAGE_SYMBOL4DOLLAR_244DOLLAR_25E._pack_ = 2
#N13_IMAGE_SYMBOL4DOLLAR_244DOLLAR_25E._fields_ = [
#    ('Short', DWORD),
#    ('Long', DWORD),
#]
#N13_IMAGE_SYMBOL4DOLLAR_24E._pack_ = 2
#N13_IMAGE_SYMBOL4DOLLAR_24E._fields_ = [
#    ('ShortName', BYTE * 8),
#    ('Name', N13_IMAGE_SYMBOL4DOLLAR_244DOLLAR_25E),
#    ('LongName', DWORD * 2),
#]
#_IMAGE_SYMBOL._pack_ = 2
#_IMAGE_SYMBOL._fields_ = [
#    ('N', N13_IMAGE_SYMBOL4DOLLAR_24E),
#    ('Value', DWORD),
#    ('SectionNumber', SHORT),
#    ('Type', WORD),
#    ('StorageClass', BYTE),
#    ('NumberOfAuxSymbols', BYTE),
#]
#IMAGE_SYMBOL = _IMAGE_SYMBOL
#PIMAGE_SYMBOL = POINTER(IMAGE_SYMBOL)
#class _IMAGE_AUX_SYMBOL(Union):
#    pass
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_26E(Structure):
#    pass
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_27E(Union):
#    pass
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_274DOLLAR_28E(Structure):
#    pass
#N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_274DOLLAR_28E._fields_ = [
#    ('Linenumber', WORD),
#    ('Size', WORD),
#]
#N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_27E._pack_ = 2
#N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_27E._fields_ = [
#    ('LnSz', N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_274DOLLAR_28E),
#    ('TotalSize', DWORD),
#]
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_29E(Union):
#    pass
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_30E(Structure):
#    pass
#N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_30E._pack_ = 2
#N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_30E._fields_ = [
#    ('PointerToLinenumber', DWORD),
#    ('PointerToNextFunction', DWORD),
#]
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_31E(Structure):
#    pass
#N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_31E._fields_ = [
#    ('Dimension', WORD * 4),
#]
#N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_29E._fields_ = [
#    ('Function', N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_30E),
#    ('Array', N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_31E),
#]
#N17_IMAGE_AUX_SYMBOL4DOLLAR_26E._pack_ = 2
#N17_IMAGE_AUX_SYMBOL4DOLLAR_26E._fields_ = [
#    ('TagIndex', DWORD),
#    ('Misc', N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_27E),
#    ('FcnAry', N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_29E),
#    ('TvIndex', WORD),
#]
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_32E(Structure):
#    pass
#N17_IMAGE_AUX_SYMBOL4DOLLAR_32E._fields_ = [
#    ('Name', BYTE * 18),
#]
#class N17_IMAGE_AUX_SYMBOL4DOLLAR_33E(Structure):
#    pass
#N17_IMAGE_AUX_SYMBOL4DOLLAR_33E._pack_ = 2
#N17_IMAGE_AUX_SYMBOL4DOLLAR_33E._fields_ = [
#    ('Length', DWORD),
#    ('NumberOfRelocations', WORD),
#    ('NumberOfLinenumbers', WORD),
#    ('CheckSum', DWORD),
#    ('Number', SHORT),
#    ('Selection', BYTE),
#]
#_IMAGE_AUX_SYMBOL._fields_ = [
#    ('Sym', N17_IMAGE_AUX_SYMBOL4DOLLAR_26E),
#    ('File', N17_IMAGE_AUX_SYMBOL4DOLLAR_32E),
#    ('Section', N17_IMAGE_AUX_SYMBOL4DOLLAR_33E),
#]
#IMAGE_AUX_SYMBOL = _IMAGE_AUX_SYMBOL
#PIMAGE_AUX_SYMBOL = POINTER(IMAGE_AUX_SYMBOL)
#
## values for enumeration 'IMAGE_AUX_SYMBOL_TYPE'
#IMAGE_AUX_SYMBOL_TYPE = c_int # enum
#class IMAGE_AUX_SYMBOL_TOKEN_DEF(Structure):
#    pass
#IMAGE_AUX_SYMBOL_TOKEN_DEF._pack_ = 2
#IMAGE_AUX_SYMBOL_TOKEN_DEF._fields_ = [
#    ('bAuxType', BYTE),
#    ('bReserved', BYTE),
#    ('SymbolTableIndex', DWORD),
#    ('rgbReserved', BYTE * 12),
#]
#PIMAGE_AUX_SYMBOL_TOKEN_DEF = POINTER(IMAGE_AUX_SYMBOL_TOKEN_DEF)
#class _IMAGE_RELOCATION(Structure):
#    pass
#class N17_IMAGE_RELOCATION4DOLLAR_34E(Union):
#    pass
#N17_IMAGE_RELOCATION4DOLLAR_34E._pack_ = 2
#N17_IMAGE_RELOCATION4DOLLAR_34E._fields_ = [
#    ('VirtualAddress', DWORD),
#    ('RelocCount', DWORD),
#]
#_IMAGE_RELOCATION._pack_ = 2
#_IMAGE_RELOCATION._anonymous_ = ['_0']
#_IMAGE_RELOCATION._fields_ = [
#    ('_0', N17_IMAGE_RELOCATION4DOLLAR_34E),
#    ('SymbolTableIndex', DWORD),
#    ('Type', WORD),
#]
#IMAGE_RELOCATION = _IMAGE_RELOCATION
#PIMAGE_RELOCATION = POINTER(IMAGE_RELOCATION)
#class _IMAGE_LINENUMBER(Structure):
#    pass
#class N17_IMAGE_LINENUMBER4DOLLAR_35E(Union):
#    pass
#N17_IMAGE_LINENUMBER4DOLLAR_35E._pack_ = 2
#N17_IMAGE_LINENUMBER4DOLLAR_35E._fields_ = [
#    ('SymbolTableIndex', DWORD),
#    ('VirtualAddress', DWORD),
#]
#_IMAGE_LINENUMBER._fields_ = [
#    ('Type', N17_IMAGE_LINENUMBER4DOLLAR_35E),
#    ('Linenumber', WORD),
#]
#IMAGE_LINENUMBER = _IMAGE_LINENUMBER
#PIMAGE_LINENUMBER = POINTER(IMAGE_LINENUMBER)
#class _IMAGE_BASE_RELOCATION(Structure):
#    pass
#_IMAGE_BASE_RELOCATION._fields_ = [
#    ('VirtualAddress', DWORD),
#    ('SizeOfBlock', DWORD),
#]
#IMAGE_BASE_RELOCATION = _IMAGE_BASE_RELOCATION
#PIMAGE_BASE_RELOCATION = POINTER(IMAGE_BASE_RELOCATION)
#class _IMAGE_ARCHIVE_MEMBER_HEADER(Structure):
#    pass
#_IMAGE_ARCHIVE_MEMBER_HEADER._fields_ = [
#    ('Name', BYTE * 16),
#    ('Date', BYTE * 12),
#    ('UserID', BYTE * 6),
#    ('GroupID', BYTE * 6),
#    ('Mode', BYTE * 8),
#    ('Size', BYTE * 10),
#    ('EndHeader', BYTE * 2),
#]
#PIMAGE_ARCHIVE_MEMBER_HEADER = POINTER(_IMAGE_ARCHIVE_MEMBER_HEADER)
#IMAGE_ARCHIVE_MEMBER_HEADER = _IMAGE_ARCHIVE_MEMBER_HEADER
#class _IMAGE_EXPORT_DIRECTORY(Structure):
#    pass
#_IMAGE_EXPORT_DIRECTORY._fields_ = [
#    ('Characteristics', DWORD),
#    ('TimeDateStamp', DWORD),
#    ('MajorVersion', WORD),
#    ('MinorVersion', WORD),
#    ('Name', DWORD),
#    ('Base', DWORD),
#    ('NumberOfFunctions', DWORD),
#    ('NumberOfNames', DWORD),
#    ('AddressOfFunctions', DWORD),
#    ('AddressOfNames', DWORD),
#    ('AddressOfNameOrdinals', DWORD),
#]
#PIMAGE_EXPORT_DIRECTORY = POINTER(_IMAGE_EXPORT_DIRECTORY)
#IMAGE_EXPORT_DIRECTORY = _IMAGE_EXPORT_DIRECTORY
#class _IMAGE_IMPORT_BY_NAME(Structure):
#    pass
#_IMAGE_IMPORT_BY_NAME._fields_ = [
#    ('Hint', WORD),
#    ('Name', BYTE * 1),
#]
#IMAGE_IMPORT_BY_NAME = _IMAGE_IMPORT_BY_NAME
#PIMAGE_IMPORT_BY_NAME = POINTER(_IMAGE_IMPORT_BY_NAME)
#class _IMAGE_THUNK_DATA64(Structure):
#    pass
#class N19_IMAGE_THUNK_DATA644DOLLAR_36E(Union):
#    pass
#N19_IMAGE_THUNK_DATA644DOLLAR_36E._fields_ = [
#    ('ForwarderString', ULONGLONG),
#    ('Function', ULONGLONG),
#    ('Ordinal', ULONGLONG),
#    ('AddressOfData', ULONGLONG),
#]
#_IMAGE_THUNK_DATA64._fields_ = [
#    ('u1', N19_IMAGE_THUNK_DATA644DOLLAR_36E),
#]
#IMAGE_THUNK_DATA64 = _IMAGE_THUNK_DATA64
#PIMAGE_THUNK_DATA64 = POINTER(IMAGE_THUNK_DATA64)
#class _IMAGE_THUNK_DATA32(Structure):
#    pass
#class N19_IMAGE_THUNK_DATA324DOLLAR_37E(Union):
#    pass
#N19_IMAGE_THUNK_DATA324DOLLAR_37E._fields_ = [
#    ('ForwarderString', DWORD),
#    ('Function', DWORD),
#    ('Ordinal', DWORD),
#    ('AddressOfData', DWORD),
#]
#_IMAGE_THUNK_DATA32._fields_ = [
#    ('u1', N19_IMAGE_THUNK_DATA324DOLLAR_37E),
#]
#IMAGE_THUNK_DATA32 = _IMAGE_THUNK_DATA32
#PIMAGE_THUNK_DATA32 = POINTER(IMAGE_THUNK_DATA32)
#PIMAGE_TLS_CALLBACK = WINFUNCTYPE(None, c_void_p, c_ulong, c_void_p)
#class _IMAGE_TLS_DIRECTORY64(Structure):
#    pass
#_IMAGE_TLS_DIRECTORY64._pack_ = 4
#_IMAGE_TLS_DIRECTORY64._fields_ = [
#    ('StartAddressOfRawData', ULONGLONG),
#    ('EndAddressOfRawData', ULONGLONG),
#    ('AddressOfIndex', ULONGLONG),
#    ('AddressOfCallBacks', ULONGLONG),
#    ('SizeOfZeroFill', DWORD),
#    ('Characteristics', DWORD),
#]
#IMAGE_TLS_DIRECTORY64 = _IMAGE_TLS_DIRECTORY64
#PIMAGE_TLS_DIRECTORY64 = POINTER(IMAGE_TLS_DIRECTORY64)
#class _IMAGE_TLS_DIRECTORY32(Structure):
#    pass
#_IMAGE_TLS_DIRECTORY32._fields_ = [
#    ('StartAddressOfRawData', DWORD),
#    ('EndAddressOfRawData', DWORD),
#    ('AddressOfIndex', DWORD),
#    ('AddressOfCallBacks', DWORD),
#    ('SizeOfZeroFill', DWORD),
#    ('Characteristics', DWORD),
#]
#IMAGE_TLS_DIRECTORY32 = _IMAGE_TLS_DIRECTORY32
#PIMAGE_TLS_DIRECTORY32 = POINTER(IMAGE_TLS_DIRECTORY32)
#IMAGE_THUNK_DATA = IMAGE_THUNK_DATA32
#PIMAGE_THUNK_DATA = PIMAGE_THUNK_DATA32
#IMAGE_TLS_DIRECTORY = IMAGE_TLS_DIRECTORY32
#PIMAGE_TLS_DIRECTORY = PIMAGE_TLS_DIRECTORY32
#class _IMAGE_IMPORT_DESCRIPTOR(Structure):
#    pass
#class N24_IMAGE_IMPORT_DESCRIPTOR4DOLLAR_38E(Union):
#    pass
#N24_IMAGE_IMPORT_DESCRIPTOR4DOLLAR_38E._fields_ = [
#    ('Characteristics', DWORD),
#    ('OriginalFirstThunk', DWORD),
#]
#_IMAGE_IMPORT_DESCRIPTOR._anonymous_ = ['_0']
#_IMAGE_IMPORT_DESCRIPTOR._fields_ = [
#    ('_0', N24_IMAGE_IMPORT_DESCRIPTOR4DOLLAR_38E),
#    ('TimeDateStamp', DWORD),
#    ('ForwarderChain', DWORD),
#    ('Name', DWORD),
#    ('FirstThunk', DWORD),
#]
#IMAGE_IMPORT_DESCRIPTOR = _IMAGE_IMPORT_DESCRIPTOR
#PIMAGE_IMPORT_DESCRIPTOR = POINTER(IMAGE_IMPORT_DESCRIPTOR)
#class _IMAGE_BOUND_IMPORT_DESCRIPTOR(Structure):
#    pass
#_IMAGE_BOUND_IMPORT_DESCRIPTOR._fields_ = [
#    ('TimeDateStamp', DWORD),
#    ('OffsetModuleName', WORD),
#    ('NumberOfModuleForwarderRefs', WORD),
#]
#IMAGE_BOUND_IMPORT_DESCRIPTOR = _IMAGE_BOUND_IMPORT_DESCRIPTOR
#PIMAGE_BOUND_IMPORT_DESCRIPTOR = POINTER(_IMAGE_BOUND_IMPORT_DESCRIPTOR)
#class _IMAGE_BOUND_FORWARDER_REF(Structure):
#    pass
#_IMAGE_BOUND_FORWARDER_REF._fields_ = [
#    ('TimeDateStamp', DWORD),
#    ('OffsetModuleName', WORD),
#    ('Reserved', WORD),
#]
#PIMAGE_BOUND_FORWARDER_REF = POINTER(_IMAGE_BOUND_FORWARDER_REF)
#IMAGE_BOUND_FORWARDER_REF = _IMAGE_BOUND_FORWARDER_REF
#class _IMAGE_RESOURCE_DIRECTORY(Structure):
#    pass
#_IMAGE_RESOURCE_DIRECTORY._fields_ = [
#    ('Characteristics', DWORD),
#    ('TimeDateStamp', DWORD),
#    ('MajorVersion', WORD),
#    ('MinorVersion', WORD),
#    ('NumberOfNamedEntries', WORD),
#    ('NumberOfIdEntries', WORD),
#]
#IMAGE_RESOURCE_DIRECTORY = _IMAGE_RESOURCE_DIRECTORY
#PIMAGE_RESOURCE_DIRECTORY = POINTER(_IMAGE_RESOURCE_DIRECTORY)
#class _IMAGE_RESOURCE_DIRECTORY_ENTRY(Structure):
#    pass
#class N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_39E(Union):
#    pass
#class N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_394DOLLAR_40E(Structure):
#    pass
#N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_394DOLLAR_40E._fields_ = [
#    ('NameOffset', DWORD, 31),
#    ('NameIsString', DWORD, 1),
#]
#N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_39E._anonymous_ = ['_0']
#N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_39E._fields_ = [
#    ('_0', N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_394DOLLAR_40E),
#    ('Name', DWORD),
#    ('Id', WORD),
#]
#class N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_41E(Union):
#    pass
#class N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_414DOLLAR_42E(Structure):
#    pass
#N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_414DOLLAR_42E._fields_ = [
#    ('OffsetToDirectory', DWORD, 31),
#    ('DataIsDirectory', DWORD, 1),
#]
#N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_41E._anonymous_ = ['_0']
#N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_41E._fields_ = [
#    ('OffsetToData', DWORD),
#    ('_0', N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_414DOLLAR_42E),
#]
#_IMAGE_RESOURCE_DIRECTORY_ENTRY._anonymous_ = ['_0', '_1']
#_IMAGE_RESOURCE_DIRECTORY_ENTRY._fields_ = [
#    ('_0', N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_39E),
#    ('_1', N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_41E),
#]
#IMAGE_RESOURCE_DIRECTORY_ENTRY = _IMAGE_RESOURCE_DIRECTORY_ENTRY
#PIMAGE_RESOURCE_DIRECTORY_ENTRY = POINTER(_IMAGE_RESOURCE_DIRECTORY_ENTRY)
#class _IMAGE_RESOURCE_DIRECTORY_STRING(Structure):
#    pass
#_IMAGE_RESOURCE_DIRECTORY_STRING._fields_ = [
#    ('Length', WORD),
#    ('NameString', CHAR * 1),
#]
#PIMAGE_RESOURCE_DIRECTORY_STRING = POINTER(_IMAGE_RESOURCE_DIRECTORY_STRING)
#IMAGE_RESOURCE_DIRECTORY_STRING = _IMAGE_RESOURCE_DIRECTORY_STRING
#class _IMAGE_RESOURCE_DIR_STRING_U(Structure):
#    pass
#_IMAGE_RESOURCE_DIR_STRING_U._fields_ = [
#    ('Length', WORD),
#    ('NameString', WCHAR * 1),
#]
#PIMAGE_RESOURCE_DIR_STRING_U = POINTER(_IMAGE_RESOURCE_DIR_STRING_U)
#IMAGE_RESOURCE_DIR_STRING_U = _IMAGE_RESOURCE_DIR_STRING_U
#class _IMAGE_RESOURCE_DATA_ENTRY(Structure):
#    pass
#_IMAGE_RESOURCE_DATA_ENTRY._fields_ = [
#    ('OffsetToData', DWORD),
#    ('Size', DWORD),
#    ('CodePage', DWORD),
#    ('Reserved', DWORD),
#]
#IMAGE_RESOURCE_DATA_ENTRY = _IMAGE_RESOURCE_DATA_ENTRY
#PIMAGE_RESOURCE_DATA_ENTRY = POINTER(_IMAGE_RESOURCE_DATA_ENTRY)
#class IMAGE_LOAD_CONFIG_DIRECTORY32(Structure):
#    pass
#IMAGE_LOAD_CONFIG_DIRECTORY32._fields_ = [
#    ('Size', DWORD),
#    ('TimeDateStamp', DWORD),
#    ('MajorVersion', WORD),
#    ('MinorVersion', WORD),
#    ('GlobalFlagsClear', DWORD),
#    ('GlobalFlagsSet', DWORD),
#    ('CriticalSectionDefaultTimeout', DWORD),
#    ('DeCommitFreeBlockThreshold', DWORD),
#    ('DeCommitTotalFreeThreshold', DWORD),
#    ('LockPrefixTable', DWORD),
#    ('MaximumAllocationSize', DWORD),
#    ('VirtualMemoryThreshold', DWORD),
#    ('ProcessHeapFlags', DWORD),
#    ('ProcessAffinityMask', DWORD),
#    ('CSDVersion', WORD),
#    ('Reserved1', WORD),
#    ('EditList', DWORD),
#    ('SecurityCookie', DWORD),
#    ('SEHandlerTable', DWORD),
#    ('SEHandlerCount', DWORD),
#]
#PIMAGE_LOAD_CONFIG_DIRECTORY32 = POINTER(IMAGE_LOAD_CONFIG_DIRECTORY32)
#class IMAGE_LOAD_CONFIG_DIRECTORY64(Structure):
#    pass
#PIMAGE_LOAD_CONFIG_DIRECTORY64 = POINTER(IMAGE_LOAD_CONFIG_DIRECTORY64)
#IMAGE_LOAD_CONFIG_DIRECTORY64._pack_ = 4
#IMAGE_LOAD_CONFIG_DIRECTORY64._fields_ = [
#    ('Size', DWORD),
#    ('TimeDateStamp', DWORD),
#    ('MajorVersion', WORD),
#    ('MinorVersion', WORD),
#    ('GlobalFlagsClear', DWORD),
#    ('GlobalFlagsSet', DWORD),
#    ('CriticalSectionDefaultTimeout', DWORD),
#    ('DeCommitFreeBlockThreshold', ULONGLONG),
#    ('DeCommitTotalFreeThreshold', ULONGLONG),
#    ('LockPrefixTable', ULONGLONG),
#    ('MaximumAllocationSize', ULONGLONG),
#    ('VirtualMemoryThreshold', ULONGLONG),
#    ('ProcessAffinityMask', ULONGLONG),
#    ('ProcessHeapFlags', DWORD),
#    ('CSDVersion', WORD),
#    ('Reserved1', WORD),
#    ('EditList', ULONGLONG),
#    ('SecurityCookie', ULONGLONG),
#    ('SEHandlerTable', ULONGLONG),
#    ('SEHandlerCount', ULONGLONG),
#]
#IMAGE_LOAD_CONFIG_DIRECTORY = IMAGE_LOAD_CONFIG_DIRECTORY32
#PIMAGE_LOAD_CONFIG_DIRECTORY = PIMAGE_LOAD_CONFIG_DIRECTORY32
#class _IMAGE_CE_RUNTIME_FUNCTION_ENTRY(Structure):
#    pass
#_IMAGE_CE_RUNTIME_FUNCTION_ENTRY._fields_ = [
#    ('FuncStart', DWORD),
#    ('PrologLen', DWORD, 8),
#    ('FuncLen', DWORD, 22),
#    ('ThirtyTwoBit', DWORD, 1),
#    ('ExceptionFlag', DWORD, 1),
#]
#PIMAGE_CE_RUNTIME_FUNCTION_ENTRY = POINTER(_IMAGE_CE_RUNTIME_FUNCTION_ENTRY)
#IMAGE_CE_RUNTIME_FUNCTION_ENTRY = _IMAGE_CE_RUNTIME_FUNCTION_ENTRY
#class _IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY(Structure):
#    pass
#_IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY._pack_ = 4
#_IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY._fields_ = [
#    ('BeginAddress', ULONGLONG),
#    ('EndAddress', ULONGLONG),
#    ('ExceptionHandler', ULONGLONG),
#    ('HandlerData', ULONGLONG),
#    ('PrologEndAddress', ULONGLONG),
#]
#IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY = _IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY
#PIMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY = POINTER(_IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY)
#class _IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY(Structure):
#    pass
#_IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY._fields_ = [
#    ('BeginAddress', DWORD),
#    ('EndAddress', DWORD),
#    ('ExceptionHandler', DWORD),
#    ('HandlerData', DWORD),
#    ('PrologEndAddress', DWORD),
#]
#IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY = _IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY
#PIMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY = POINTER(_IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY)
#class _IMAGE_RUNTIME_FUNCTION_ENTRY(Structure):
#    pass
#_IMAGE_RUNTIME_FUNCTION_ENTRY._fields_ = [
#    ('BeginAddress', DWORD),
#    ('EndAddress', DWORD),
#    ('UnwindInfoAddress', DWORD),
#]
#_PIMAGE_RUNTIME_FUNCTION_ENTRY = POINTER(_IMAGE_RUNTIME_FUNCTION_ENTRY)
#IMAGE_IA64_RUNTIME_FUNCTION_ENTRY = _IMAGE_RUNTIME_FUNCTION_ENTRY
#PIMAGE_IA64_RUNTIME_FUNCTION_ENTRY = _PIMAGE_RUNTIME_FUNCTION_ENTRY
#IMAGE_RUNTIME_FUNCTION_ENTRY = _IMAGE_RUNTIME_FUNCTION_ENTRY
#PIMAGE_RUNTIME_FUNCTION_ENTRY = _PIMAGE_RUNTIME_FUNCTION_ENTRY
#class _IMAGE_DEBUG_DIRECTORY(Structure):
#    pass
#_IMAGE_DEBUG_DIRECTORY._fields_ = [
#    ('Characteristics', DWORD),
#    ('TimeDateStamp', DWORD),
#    ('MajorVersion', WORD),
#    ('MinorVersion', WORD),
#    ('Type', DWORD),
#    ('SizeOfData', DWORD),
#    ('AddressOfRawData', DWORD),
#    ('PointerToRawData', DWORD),
#]
#IMAGE_DEBUG_DIRECTORY = _IMAGE_DEBUG_DIRECTORY
#PIMAGE_DEBUG_DIRECTORY = POINTER(_IMAGE_DEBUG_DIRECTORY)
#class _IMAGE_COFF_SYMBOLS_HEADER(Structure):
#    pass
#_IMAGE_COFF_SYMBOLS_HEADER._fields_ = [
#    ('NumberOfSymbols', DWORD),
#    ('LvaToFirstSymbol', DWORD),
#    ('NumberOfLinenumbers', DWORD),
#    ('LvaToFirstLinenumber', DWORD),
#    ('RvaToFirstByteOfCode', DWORD),
#    ('RvaToLastByteOfCode', DWORD),
#    ('RvaToFirstByteOfData', DWORD),
#    ('RvaToLastByteOfData', DWORD),
#]
#PIMAGE_COFF_SYMBOLS_HEADER = POINTER(_IMAGE_COFF_SYMBOLS_HEADER)
#IMAGE_COFF_SYMBOLS_HEADER = _IMAGE_COFF_SYMBOLS_HEADER
#class _FPO_DATA(Structure):
#    pass
#_FPO_DATA._fields_ = [
#    ('ulOffStart', DWORD),
#    ('cbProcSize', DWORD),
#    ('cdwLocals', DWORD),
#    ('cdwParams', WORD),
#    ('cbProlog', WORD, 8),
#    ('cbRegs', WORD, 3),
#    ('fHasSEH', WORD, 1),
#    ('fUseBP', WORD, 1),
#    ('reserved', WORD, 1),
#    ('cbFrame', WORD, 2),
#]
#PFPO_DATA = POINTER(_FPO_DATA)
#FPO_DATA = _FPO_DATA
#class _IMAGE_DEBUG_MISC(Structure):
#    pass
#_IMAGE_DEBUG_MISC._fields_ = [
#    ('DataType', DWORD),
#    ('Length', DWORD),
#    ('Unicode', BOOLEAN),
#    ('Reserved', BYTE * 3),
#    ('Data', BYTE * 1),
#]
#IMAGE_DEBUG_MISC = _IMAGE_DEBUG_MISC
#PIMAGE_DEBUG_MISC = POINTER(_IMAGE_DEBUG_MISC)
#class _IMAGE_FUNCTION_ENTRY(Structure):
#    pass
#_IMAGE_FUNCTION_ENTRY._fields_ = [
#    ('StartingAddress', DWORD),
#    ('EndingAddress', DWORD),
#    ('EndOfPrologue', DWORD),
#]
#PIMAGE_FUNCTION_ENTRY = POINTER(_IMAGE_FUNCTION_ENTRY)
#IMAGE_FUNCTION_ENTRY = _IMAGE_FUNCTION_ENTRY
#class _IMAGE_FUNCTION_ENTRY64(Structure):
#    pass
#class N23_IMAGE_FUNCTION_ENTRY644DOLLAR_45E(Union):
#    pass
#N23_IMAGE_FUNCTION_ENTRY644DOLLAR_45E._pack_ = 4
#N23_IMAGE_FUNCTION_ENTRY644DOLLAR_45E._fields_ = [
#    ('EndOfPrologue', ULONGLONG),
#    ('UnwindInfoAddress', ULONGLONG),
#]
#_IMAGE_FUNCTION_ENTRY64._pack_ = 4
#_IMAGE_FUNCTION_ENTRY64._anonymous_ = ['_0']
#_IMAGE_FUNCTION_ENTRY64._fields_ = [
#    ('StartingAddress', ULONGLONG),
#    ('EndingAddress', ULONGLONG),
#    ('_0', N23_IMAGE_FUNCTION_ENTRY644DOLLAR_45E),
#]
#PIMAGE_FUNCTION_ENTRY64 = POINTER(_IMAGE_FUNCTION_ENTRY64)
#IMAGE_FUNCTION_ENTRY64 = _IMAGE_FUNCTION_ENTRY64
#class _IMAGE_SEPARATE_DEBUG_HEADER(Structure):
#    pass
#_IMAGE_SEPARATE_DEBUG_HEADER._fields_ = [
#    ('Signature', WORD),
#    ('Flags', WORD),
#    ('Machine', WORD),
#    ('Characteristics', WORD),
#    ('TimeDateStamp', DWORD),
#    ('CheckSum', DWORD),
#    ('ImageBase', DWORD),
#    ('SizeOfImage', DWORD),
#    ('NumberOfSections', DWORD),
#    ('ExportedNamesSize', DWORD),
#    ('DebugDirectorySize', DWORD),
#    ('SectionAlignment', DWORD),
#    ('Reserved', DWORD * 2),
#]
#PIMAGE_SEPARATE_DEBUG_HEADER = POINTER(_IMAGE_SEPARATE_DEBUG_HEADER)
#IMAGE_SEPARATE_DEBUG_HEADER = _IMAGE_SEPARATE_DEBUG_HEADER
#class _NON_PAGED_DEBUG_INFO(Structure):
#    pass
#_NON_PAGED_DEBUG_INFO._pack_ = 4
#_NON_PAGED_DEBUG_INFO._fields_ = [
#    ('Signature', WORD),
#    ('Flags', WORD),
#    ('Size', DWORD),
#    ('Machine', WORD),
#    ('Characteristics', WORD),
#    ('TimeDateStamp', DWORD),
#    ('CheckSum', DWORD),
#    ('SizeOfImage', DWORD),
#    ('ImageBase', ULONGLONG),
#]
#PNON_PAGED_DEBUG_INFO = POINTER(_NON_PAGED_DEBUG_INFO)
#NON_PAGED_DEBUG_INFO = _NON_PAGED_DEBUG_INFO
#class _ImageArchitectureHeader(Structure):
#    pass
#_ImageArchitectureHeader._fields_ = [
#    ('AmaskValue', c_uint, 1),
#    ('', c_int, 7),
#    ('AmaskShift', c_uint, 8),
#    ('', c_int, 16),
#    ('FirstEntryRVA', DWORD),
#]
#IMAGE_ARCHITECTURE_HEADER = _ImageArchitectureHeader
#PIMAGE_ARCHITECTURE_HEADER = POINTER(_ImageArchitectureHeader)
#class _ImageArchitectureEntry(Structure):
#    pass
#_ImageArchitectureEntry._fields_ = [
#    ('FixupInstRVA', DWORD),
#    ('NewInst', DWORD),
#]
#IMAGE_ARCHITECTURE_ENTRY = _ImageArchitectureEntry
#PIMAGE_ARCHITECTURE_ENTRY = POINTER(_ImageArchitectureEntry)
#class IMPORT_OBJECT_HEADER(Structure):
#    pass
#class N20IMPORT_OBJECT_HEADER4DOLLAR_46E(Union):
#    pass
#N20IMPORT_OBJECT_HEADER4DOLLAR_46E._fields_ = [
#    ('Ordinal', WORD),
#    ('Hint', WORD),
#]
#IMPORT_OBJECT_HEADER._anonymous_ = ['_0']
#IMPORT_OBJECT_HEADER._fields_ = [
#    ('Sig1', WORD),
#    ('Sig2', WORD),
#    ('Version', WORD),
#    ('Machine', WORD),
#    ('TimeDateStamp', DWORD),
#    ('SizeOfData', DWORD),
#    ('_0', N20IMPORT_OBJECT_HEADER4DOLLAR_46E),
#    ('Type', WORD, 2),
#    ('NameType', WORD, 3),
#    ('Reserved', WORD, 11),
#]
#
## values for enumeration 'IMPORT_OBJECT_TYPE'
#IMPORT_OBJECT_TYPE = c_int # enum
#
## values for enumeration 'IMPORT_OBJECT_NAME_TYPE'
#IMPORT_OBJECT_NAME_TYPE = c_int # enum
#
## values for enumeration 'ReplacesCorHdrNumericDefines'
#ReplacesCorHdrNumericDefines = c_int # enum
#class IMAGE_COR20_HEADER(Structure):
#    pass
#IMAGE_COR20_HEADER._fields_ = [
#    ('cb', DWORD),
#    ('MajorRuntimeVersion', WORD),
#    ('MinorRuntimeVersion', WORD),
#    ('MetaData', IMAGE_DATA_DIRECTORY),
#    ('Flags', DWORD),
#    ('EntryPointToken', DWORD),
#    ('Resources', IMAGE_DATA_DIRECTORY),
#    ('StrongNameSignature', IMAGE_DATA_DIRECTORY),
#    ('CodeManagerTable', IMAGE_DATA_DIRECTORY),
#    ('VTableFixups', IMAGE_DATA_DIRECTORY),
#    ('ExportAddressTableJumps', IMAGE_DATA_DIRECTORY),
#    ('ManagedNativeHeader', IMAGE_DATA_DIRECTORY),
#]
#PIMAGE_COR20_HEADER = POINTER(IMAGE_COR20_HEADER)
#class _SLIST_HEADER(Union):
#    pass
#class N13_SLIST_HEADER4DOLLAR_47E(Structure):
#    pass
#N13_SLIST_HEADER4DOLLAR_47E._fields_ = [
#    ('Next', SINGLE_LIST_ENTRY),
#    ('Depth', WORD),
#    ('Sequence', WORD),
#]
#_SLIST_HEADER._anonymous_ = ['_0']
#_SLIST_HEADER._fields_ = [
#    ('Alignment', ULONGLONG),
#    ('_0', N13_SLIST_HEADER4DOLLAR_47E),
#]
#PSLIST_HEADER = POINTER(_SLIST_HEADER)
#SLIST_HEADER = _SLIST_HEADER
#class _MESSAGE_RESOURCE_ENTRY(Structure):
#    pass
#_MESSAGE_RESOURCE_ENTRY._fields_ = [
#    ('Length', WORD),
#    ('Flags', WORD),
#    ('Text', BYTE * 1),
#]
#PMESSAGE_RESOURCE_ENTRY = POINTER(_MESSAGE_RESOURCE_ENTRY)
#MESSAGE_RESOURCE_ENTRY = _MESSAGE_RESOURCE_ENTRY
#class _MESSAGE_RESOURCE_BLOCK(Structure):
#    pass
#_MESSAGE_RESOURCE_BLOCK._fields_ = [
#    ('LowId', DWORD),
#    ('HighId', DWORD),
#    ('OffsetToEntries', DWORD),
#]
#MESSAGE_RESOURCE_BLOCK = _MESSAGE_RESOURCE_BLOCK
#PMESSAGE_RESOURCE_BLOCK = POINTER(_MESSAGE_RESOURCE_BLOCK)
#class _MESSAGE_RESOURCE_DATA(Structure):
#    pass
#_MESSAGE_RESOURCE_DATA._fields_ = [
#    ('NumberOfBlocks', DWORD),
#    ('Blocks', MESSAGE_RESOURCE_BLOCK * 1),
#]
#MESSAGE_RESOURCE_DATA = _MESSAGE_RESOURCE_DATA
#PMESSAGE_RESOURCE_DATA = POINTER(_MESSAGE_RESOURCE_DATA)
#class _OSVERSIONINFOA(Structure):
#    pass
#_OSVERSIONINFOA._fields_ = [
#    ('dwOSVersionInfoSize', DWORD),
#    ('dwMajorVersion', DWORD),
#    ('dwMinorVersion', DWORD),
#    ('dwBuildNumber', DWORD),
#    ('dwPlatformId', DWORD),
#    ('szCSDVersion', CHAR * 128),
#]
#LPOSVERSIONINFOA = POINTER(_OSVERSIONINFOA)
#OSVERSIONINFOA = _OSVERSIONINFOA
#POSVERSIONINFOA = POINTER(_OSVERSIONINFOA)
#class _OSVERSIONINFOW(Structure):
#    pass
#_OSVERSIONINFOW._fields_ = [
#    ('dwOSVersionInfoSize', DWORD),
#    ('dwMajorVersion', DWORD),
#    ('dwMinorVersion', DWORD),
#    ('dwBuildNumber', DWORD),
#    ('dwPlatformId', DWORD),
#    ('szCSDVersion', WCHAR * 128),
#]
#POSVERSIONINFOW = POINTER(_OSVERSIONINFOW)
#LPOSVERSIONINFOW = POINTER(_OSVERSIONINFOW)
#PRTL_OSVERSIONINFOW = POINTER(_OSVERSIONINFOW)
#RTL_OSVERSIONINFOW = _OSVERSIONINFOW
#OSVERSIONINFOW = _OSVERSIONINFOW
#OSVERSIONINFO = OSVERSIONINFOA
#POSVERSIONINFO = POSVERSIONINFOA
#LPOSVERSIONINFO = LPOSVERSIONINFOA
#class _OSVERSIONINFOEXA(Structure):
#    pass
#_OSVERSIONINFOEXA._fields_ = [
#    ('dwOSVersionInfoSize', DWORD),
#    ('dwMajorVersion', DWORD),
#    ('dwMinorVersion', DWORD),
#    ('dwBuildNumber', DWORD),
#    ('dwPlatformId', DWORD),
#    ('szCSDVersion', CHAR * 128),
#    ('wServicePackMajor', WORD),
#    ('wServicePackMinor', WORD),
#    ('wSuiteMask', WORD),
#    ('wProductType', BYTE),
#    ('wReserved', BYTE),
#]
#OSVERSIONINFOEXA = _OSVERSIONINFOEXA
#LPOSVERSIONINFOEXA = POINTER(_OSVERSIONINFOEXA)
#POSVERSIONINFOEXA = POINTER(_OSVERSIONINFOEXA)
#class _OSVERSIONINFOEXW(Structure):
#    pass
#_OSVERSIONINFOEXW._fields_ = [
#    ('dwOSVersionInfoSize', DWORD),
#    ('dwMajorVersion', DWORD),
#    ('dwMinorVersion', DWORD),
#    ('dwBuildNumber', DWORD),
#    ('dwPlatformId', DWORD),
#    ('szCSDVersion', WCHAR * 128),
#    ('wServicePackMajor', WORD),
#    ('wServicePackMinor', WORD),
#    ('wSuiteMask', WORD),
#    ('wProductType', BYTE),
#    ('wReserved', BYTE),
#]
#LPOSVERSIONINFOEXW = POINTER(_OSVERSIONINFOEXW)
#OSVERSIONINFOEXW = _OSVERSIONINFOEXW
#POSVERSIONINFOEXW = POINTER(_OSVERSIONINFOEXW)
#PRTL_OSVERSIONINFOEXW = POINTER(_OSVERSIONINFOEXW)
#RTL_OSVERSIONINFOEXW = _OSVERSIONINFOEXW
#OSVERSIONINFOEX = OSVERSIONINFOEXA
#POSVERSIONINFOEX = POSVERSIONINFOEXA
#LPOSVERSIONINFOEX = LPOSVERSIONINFOEXA
#_RTL_CRITICAL_SECTION_DEBUG._fields_ = [
#    ('Type', WORD),
#    ('CreatorBackTraceIndex', WORD),
#    ('CriticalSection', POINTER(_RTL_CRITICAL_SECTION)),
#    ('ProcessLocksList', LIST_ENTRY),
#    ('EntryCount', DWORD),
#    ('ContentionCount', DWORD),
#    ('Spare', DWORD * 2),
#]
#PRTL_RESOURCE_DEBUG = POINTER(_RTL_CRITICAL_SECTION_DEBUG)
#RTL_RESOURCE_DEBUG = _RTL_CRITICAL_SECTION_DEBUG
#_RTL_CRITICAL_SECTION._fields_ = [
#    ('DebugInfo', PRTL_CRITICAL_SECTION_DEBUG),
#    ('LockCount', LONG),
#    ('RecursionCount', LONG),
#    ('OwningThread', HANDLE),
#    ('LockSemaphore', HANDLE),
#    ('SpinCount', ULONG_PTR),
#]
#RTL_VERIFIER_DLL_LOAD_CALLBACK = WINFUNCTYPE(None, WSTRING, c_void_p, c_ulong, c_void_p)
#RTL_VERIFIER_DLL_UNLOAD_CALLBACK = WINFUNCTYPE(None, WSTRING, c_void_p, c_ulong, c_void_p)
#class _RTL_VERIFIER_THUNK_DESCRIPTOR(Structure):
#    pass
#_RTL_VERIFIER_THUNK_DESCRIPTOR._fields_ = [
#    ('ThunkName', PCHAR),
#    ('ThunkOldAddress', PVOID),
#    ('ThunkNewAddress', PVOID),
#]
#PRTL_VERIFIER_THUNK_DESCRIPTOR = POINTER(_RTL_VERIFIER_THUNK_DESCRIPTOR)
#RTL_VERIFIER_THUNK_DESCRIPTOR = _RTL_VERIFIER_THUNK_DESCRIPTOR
#class _RTL_VERIFIER_DLL_DESCRIPTOR(Structure):
#    pass
#_RTL_VERIFIER_DLL_DESCRIPTOR._fields_ = [
#    ('DllName', PWCHAR),
#    ('DllFlags', DWORD),
#    ('DllAddress', PVOID),
#    ('DllThunks', PRTL_VERIFIER_THUNK_DESCRIPTOR),
#]
#RTL_VERIFIER_DLL_DESCRIPTOR = _RTL_VERIFIER_DLL_DESCRIPTOR
#PRTL_VERIFIER_DLL_DESCRIPTOR = POINTER(_RTL_VERIFIER_DLL_DESCRIPTOR)
#class _RTL_VERIFIER_PROVIDER_DESCRIPTOR(Structure):
#    pass
#_RTL_VERIFIER_PROVIDER_DESCRIPTOR._fields_ = [
#    ('Length', DWORD),
#    ('ProviderDlls', PRTL_VERIFIER_DLL_DESCRIPTOR),
#    ('ProviderDllLoadCallback', RTL_VERIFIER_DLL_LOAD_CALLBACK),
#    ('ProviderDllUnloadCallback', RTL_VERIFIER_DLL_UNLOAD_CALLBACK),
#    ('VerifierImage', PWSTR),
#    ('VerifierFlags', DWORD),
#    ('VerifierDebug', DWORD),
#    ('RtlpGetStackTraceAddress', PVOID),
#    ('RtlpDebugPageHeapCreate', PVOID),
#    ('RtlpDebugPageHeapDestroy', PVOID),
#]
#RTL_VERIFIER_PROVIDER_DESCRIPTOR = _RTL_VERIFIER_PROVIDER_DESCRIPTOR
#PRTL_VERIFIER_PROVIDER_DESCRIPTOR = POINTER(_RTL_VERIFIER_PROVIDER_DESCRIPTOR)
#PVECTORED_EXCEPTION_HANDLER = WINFUNCTYPE(LONG, POINTER(_EXCEPTION_POINTERS))
#
## values for enumeration '_HEAP_INFORMATION_CLASS'
#_HEAP_INFORMATION_CLASS = c_int # enum
#HEAP_INFORMATION_CLASS = _HEAP_INFORMATION_CLASS
#WAITORTIMERCALLBACKFUNC = WINFUNCTYPE(None, c_void_p, c_ubyte)
#WORKERCALLBACKFUNC = WINFUNCTYPE(None, c_void_p)
#APC_CALLBACK_FUNCTION = WINFUNCTYPE(None, c_ulong, c_void_p, c_void_p)
#
## values for enumeration '_ACTIVATION_CONTEXT_INFO_CLASS'
#_ACTIVATION_CONTEXT_INFO_CLASS = c_int # enum
#ACTIVATION_CONTEXT_INFO_CLASS = _ACTIVATION_CONTEXT_INFO_CLASS
#class _ACTIVATION_CONTEXT_QUERY_INDEX(Structure):
#    pass
#_ACTIVATION_CONTEXT_QUERY_INDEX._fields_ = [
#    ('ulAssemblyIndex', DWORD),
#    ('ulFileIndexInAssembly', DWORD),
#]
#ACTIVATION_CONTEXT_QUERY_INDEX = _ACTIVATION_CONTEXT_QUERY_INDEX
#PACTIVATION_CONTEXT_QUERY_INDEX = POINTER(_ACTIVATION_CONTEXT_QUERY_INDEX)
#PCACTIVATION_CONTEXT_QUERY_INDEX = POINTER(_ACTIVATION_CONTEXT_QUERY_INDEX)
#class _ASSEMBLY_FILE_DETAILED_INFORMATION(Structure):
#    pass
#_ASSEMBLY_FILE_DETAILED_INFORMATION._fields_ = [
#    ('ulFlags', DWORD),
#    ('ulFilenameLength', DWORD),
#    ('ulPathLength', DWORD),
#    ('lpFileName', PCWSTR),
#    ('lpFilePath', PCWSTR),
#]
#PASSEMBLY_FILE_DETAILED_INFORMATION = POINTER(_ASSEMBLY_FILE_DETAILED_INFORMATION)
#ASSEMBLY_FILE_DETAILED_INFORMATION = _ASSEMBLY_FILE_DETAILED_INFORMATION
#PCASSEMBLY_FILE_DETAILED_INFORMATION = POINTER(ASSEMBLY_FILE_DETAILED_INFORMATION)
#class _ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION(Structure):
#    pass
#_ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION._fields_ = [
#    ('ulFlags', DWORD),
#    ('ulEncodedAssemblyIdentityLength', DWORD),
#    ('ulManifestPathType', DWORD),
#    ('ulManifestPathLength', DWORD),
#    ('liManifestLastWriteTime', LARGE_INTEGER),
#    ('ulPolicyPathType', DWORD),
#    ('ulPolicyPathLength', DWORD),
#    ('liPolicyLastWriteTime', LARGE_INTEGER),
#    ('ulMetadataSatelliteRosterIndex', DWORD),
#    ('ulManifestVersionMajor', DWORD),
#    ('ulManifestVersionMinor', DWORD),
#    ('ulPolicyVersionMajor', DWORD),
#    ('ulPolicyVersionMinor', DWORD),
#    ('ulAssemblyDirectoryNameLength', DWORD),
#    ('lpAssemblyEncodedAssemblyIdentity', PCWSTR),
#    ('lpAssemblyManifestPath', PCWSTR),
#    ('lpAssemblyPolicyPath', PCWSTR),
#    ('lpAssemblyDirectoryName', PCWSTR),
#    ('ulFileCount', DWORD),
#]
#PACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION = POINTER(_ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION)
#ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION = _ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION
#PCACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION = POINTER(_ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION)
#class _ACTIVATION_CONTEXT_DETAILED_INFORMATION(Structure):
#    pass
#_ACTIVATION_CONTEXT_DETAILED_INFORMATION._fields_ = [
#    ('dwFlags', DWORD),
#    ('ulFormatVersion', DWORD),
#    ('ulAssemblyCount', DWORD),
#    ('ulRootManifestPathType', DWORD),
#    ('ulRootManifestPathChars', DWORD),
#    ('ulRootConfigurationPathType', DWORD),
#    ('ulRootConfigurationPathChars', DWORD),
#    ('ulAppDirPathType', DWORD),
#    ('ulAppDirPathChars', DWORD),
#    ('lpRootManifestPath', PCWSTR),
#    ('lpRootConfigurationPath', PCWSTR),
#    ('lpAppDirPath', PCWSTR),
#]
#PACTIVATION_CONTEXT_DETAILED_INFORMATION = POINTER(_ACTIVATION_CONTEXT_DETAILED_INFORMATION)
#ACTIVATION_CONTEXT_DETAILED_INFORMATION = _ACTIVATION_CONTEXT_DETAILED_INFORMATION
#PCACTIVATION_CONTEXT_DETAILED_INFORMATION = POINTER(_ACTIVATION_CONTEXT_DETAILED_INFORMATION)
#class _EVENTLOGRECORD(Structure):
#    pass
#_EVENTLOGRECORD._fields_ = [
#    ('Length', DWORD),
#    ('Reserved', DWORD),
#    ('RecordNumber', DWORD),
#    ('TimeGenerated', DWORD),
#    ('TimeWritten', DWORD),
#    ('EventID', DWORD),
#    ('EventType', WORD),
#    ('NumStrings', WORD),
#    ('EventCategory', WORD),
#    ('ReservedFlags', WORD),
#    ('ClosingRecordNumber', DWORD),
#    ('StringOffset', DWORD),
#    ('UserSidLength', DWORD),
#    ('UserSidOffset', DWORD),
#    ('DataLength', DWORD),
#    ('DataOffset', DWORD),
#]
#EVENTLOGRECORD = _EVENTLOGRECORD
#PEVENTLOGRECORD = POINTER(_EVENTLOGRECORD)
#class _EVENTSFORLOGFILE(Structure):
#    pass
#_EVENTSFORLOGFILE._fields_ = [
#    ('ulSize', DWORD),
#    ('szLogicalLogFile', WCHAR * 256),
#    ('ulNumRecords', DWORD),
#    ('pEventLogRecords', EVENTLOGRECORD * 0),
#]
#PEVENTSFORLOGFILE = POINTER(_EVENTSFORLOGFILE)
#EVENTSFORLOGFILE = _EVENTSFORLOGFILE
#class _PACKEDEVENTINFO(Structure):
#    pass
#_PACKEDEVENTINFO._fields_ = [
#    ('ulSize', DWORD),
#    ('ulNumEventsForLogFile', DWORD),
#    ('ulOffsets', DWORD * 0),
#]
#PACKEDEVENTINFO = _PACKEDEVENTINFO
#PPACKEDEVENTINFO = POINTER(_PACKEDEVENTINFO)
#
## values for enumeration '_CM_SERVICE_NODE_TYPE'
#_CM_SERVICE_NODE_TYPE = c_int # enum
#SERVICE_NODE_TYPE = _CM_SERVICE_NODE_TYPE
#
## values for enumeration '_CM_SERVICE_LOAD_TYPE'
#_CM_SERVICE_LOAD_TYPE = c_int # enum
#SERVICE_LOAD_TYPE = _CM_SERVICE_LOAD_TYPE
#
## values for enumeration '_CM_ERROR_CONTROL_TYPE'
#_CM_ERROR_CONTROL_TYPE = c_int # enum
#SERVICE_ERROR_TYPE = _CM_ERROR_CONTROL_TYPE
#class _TAPE_ERASE(Structure):
#    pass
#_TAPE_ERASE._fields_ = [
#    ('Type', DWORD),
#    ('Immediate', BOOLEAN),
#]
#TAPE_ERASE = _TAPE_ERASE
#PTAPE_ERASE = POINTER(_TAPE_ERASE)
#class _TAPE_PREPARE(Structure):
#    pass
#_TAPE_PREPARE._fields_ = [
#    ('Operation', DWORD),
#    ('Immediate', BOOLEAN),
#]
#TAPE_PREPARE = _TAPE_PREPARE
#PTAPE_PREPARE = POINTER(_TAPE_PREPARE)
#class _TAPE_WRITE_MARKS(Structure):
#    pass
#_TAPE_WRITE_MARKS._fields_ = [
#    ('Type', DWORD),
#    ('Count', DWORD),
#    ('Immediate', BOOLEAN),
#]
#TAPE_WRITE_MARKS = _TAPE_WRITE_MARKS
#PTAPE_WRITE_MARKS = POINTER(_TAPE_WRITE_MARKS)
#class _TAPE_GET_POSITION(Structure):
#    pass
#_TAPE_GET_POSITION._fields_ = [
#    ('Type', DWORD),
#    ('Partition', DWORD),
#    ('Offset', LARGE_INTEGER),
#]
#TAPE_GET_POSITION = _TAPE_GET_POSITION
#PTAPE_GET_POSITION = POINTER(_TAPE_GET_POSITION)
#class _TAPE_SET_POSITION(Structure):
#    pass
#_TAPE_SET_POSITION._fields_ = [
#    ('Method', DWORD),
#    ('Partition', DWORD),
#    ('Offset', LARGE_INTEGER),
#    ('Immediate', BOOLEAN),
#]
#PTAPE_SET_POSITION = POINTER(_TAPE_SET_POSITION)
#TAPE_SET_POSITION = _TAPE_SET_POSITION
#class _TAPE_GET_DRIVE_PARAMETERS(Structure):
#    pass
#_TAPE_GET_DRIVE_PARAMETERS._fields_ = [
#    ('ECC', BOOLEAN),
#    ('Compression', BOOLEAN),
#    ('DataPadding', BOOLEAN),
#    ('ReportSetmarks', BOOLEAN),
#    ('DefaultBlockSize', DWORD),
#    ('MaximumBlockSize', DWORD),
#    ('MinimumBlockSize', DWORD),
#    ('MaximumPartitionCount', DWORD),
#    ('FeaturesLow', DWORD),
#    ('FeaturesHigh', DWORD),
#    ('EOTWarningZoneSize', DWORD),
#]
#PTAPE_GET_DRIVE_PARAMETERS = POINTER(_TAPE_GET_DRIVE_PARAMETERS)
#TAPE_GET_DRIVE_PARAMETERS = _TAPE_GET_DRIVE_PARAMETERS
#class _TAPE_SET_DRIVE_PARAMETERS(Structure):
#    pass
#_TAPE_SET_DRIVE_PARAMETERS._fields_ = [
#    ('ECC', BOOLEAN),
#    ('Compression', BOOLEAN),
#    ('DataPadding', BOOLEAN),
#    ('ReportSetmarks', BOOLEAN),
#    ('EOTWarningZoneSize', DWORD),
#]
#TAPE_SET_DRIVE_PARAMETERS = _TAPE_SET_DRIVE_PARAMETERS
#PTAPE_SET_DRIVE_PARAMETERS = POINTER(_TAPE_SET_DRIVE_PARAMETERS)
#class _TAPE_GET_MEDIA_PARAMETERS(Structure):
#    pass
#_TAPE_GET_MEDIA_PARAMETERS._fields_ = [
#    ('Capacity', LARGE_INTEGER),
#    ('Remaining', LARGE_INTEGER),
#    ('BlockSize', DWORD),
#    ('PartitionCount', DWORD),
#    ('WriteProtected', BOOLEAN),
#]
#PTAPE_GET_MEDIA_PARAMETERS = POINTER(_TAPE_GET_MEDIA_PARAMETERS)
#TAPE_GET_MEDIA_PARAMETERS = _TAPE_GET_MEDIA_PARAMETERS
#class _TAPE_SET_MEDIA_PARAMETERS(Structure):
#    pass
#_TAPE_SET_MEDIA_PARAMETERS._fields_ = [
#    ('BlockSize', DWORD),
#]
#PTAPE_SET_MEDIA_PARAMETERS = POINTER(_TAPE_SET_MEDIA_PARAMETERS)
#TAPE_SET_MEDIA_PARAMETERS = _TAPE_SET_MEDIA_PARAMETERS
#class _TAPE_CREATE_PARTITION(Structure):
#    pass
#_TAPE_CREATE_PARTITION._fields_ = [
#    ('Method', DWORD),
#    ('Count', DWORD),
#    ('Size', DWORD),
#]
#TAPE_CREATE_PARTITION = _TAPE_CREATE_PARTITION
#PTAPE_CREATE_PARTITION = POINTER(_TAPE_CREATE_PARTITION)
#class _TAPE_WMI_OPERATIONS(Structure):
#    pass
#_TAPE_WMI_OPERATIONS._fields_ = [
#    ('Method', DWORD),
#    ('DataBufferSize', DWORD),
#    ('DataBuffer', PVOID),
#]
#TAPE_WMI_OPERATIONS = _TAPE_WMI_OPERATIONS
#PTAPE_WMI_OPERATIONS = POINTER(_TAPE_WMI_OPERATIONS)
#
## values for enumeration '_TAPE_DRIVE_PROBLEM_TYPE'
#_TAPE_DRIVE_PROBLEM_TYPE = c_int # enum
#TAPE_DRIVE_PROBLEM_TYPE = _TAPE_DRIVE_PROBLEM_TYPE
#__all__ = ['PowerDeviceUnspecified', 'LPDEVMODEW', 'PLCID',
#           'tagENUMLOGFONTEXW', 'LPMENUTEMPLATEW', 'NPLOGBRUSH32',
#           'DLGPROC', 'tagIMEMENUITEMINFOW',
#           'IMAGE_RESOURCE_DIRECTORY', 'WINSTAENUMPROCA', 'st_vio',
#           'tagENUMLOGFONTEXA', 'PCURSORINFO', 'LPDEVMODEA',
#           'PPIXELFORMATDESCRIPTOR', 'WINSTAENUMPROCW',
#           'tagIMEMENUITEMINFOA', 'tagLOGBRUSH32', 'LPMENUTEMPLATEA',
#           'EMRSTROKEPATH', '_WSAServiceClassInfoA',
#           'PSYSTEM_POWER_CAPABILITIES', 'VerifySystemPolicyDc',
#           'PTIMEVAL', 'RGNDATAHEADER', 'tagHANDLETABLE',
#           'LPWSAOVERLAPPED_COMPLETION_ROUTINE', 'COM_REFRESH',
#           '_WSAServiceClassInfoW', '_IMAGE_TLS_DIRECTORY32',
#           'mysql_stmt_store_result', 'AclSizeInformation',
#           'HARDWAREHOOKSTRUCT', 'enum_mysql_stmt_state',
#           'IMAGE_FILE_HEADER', 'ADMINISTRATOR_POWER_POLICY',
#           'LPDRAWTEXTPARAMS', 'EMRSETBKMODE', 'SOUNDSENTRY',
#           'COR_VTABLE_CALL_MOST_DERIVED', 'tagICONMETRICSA',
#           'LOGICAL_PROCESSOR_RELATIONSHIP', 'PPOWER_ACTION_POLICY',
#           'mysql_stmt_row_seek', '_ACL_INFORMATION_CLASS',
#           'WinBuiltinBackupOperatorsSid', 'POBJECT_TYPE_LIST',
#           '_SLIST_HEADER', 'tagACCESSTIMEOUT', 'LONG64',
#           'ENUM_SERVICE_STATUSA', 'PIMAGE_OPTIONAL_HEADER32',
#           'MONITORENUMPROC', 'LPVIDEOPARAMETERS',
#           'WinInteractiveSid', 'PowerDeviceMaximum',
#           'ENUM_SERVICE_STATUSW', 'EXTLOGFONTA',
#           'AssemblyDetailedInformationInActivationContext', '_ABC',
#           'PEMRCREATECOLORSPACEW', 'SID', 'st_dynamic_array',
#           'HCOLORSPACE__', '_HEAP_INFORMATION_CLASS',
#           'enum_cursor_type', 'KILL_CONNECTION',
#           'N12_devicemodeW4DOLLAR_65E', 'EXTLOGFONTW',
#           'WinCreatorOwnerSid', 'PWSANAMESPACE_INFOA',
#           'SERVICE_DESCRIPTION', 'PDEBUGHOOKINFO',
#           'MYSQL_OPT_PROTOCOL', 'PEMRRESIZEPALETTE',
#           'mysql_stmt_insert_id', 'EMRPIXELFORMAT',
#           'GEOCLASS_REGION', 'CURSORSHAPE', 'OSVERSIONINFOW',
#           'CM_POWER_DATA', 'LPSECURITY_ATTRIBUTES', 'OSVERSIONINFOA',
#           'tagEMRMASKBLT', 'LPDRAWITEMSTRUCT',
#           'PWSASERVICECLASSINFO', 'LPMDICREATESTRUCT', 'PTBYTE',
#           'LPLOAD_DLL_DEBUG_INFO', 'in_addr',
#           '_FILE_SEGMENT_ELEMENT', 'MYSQL_TYPE_TINY',
#           '_IMAGE_RESOURCE_DIRECTORY', 'NMHDR',
#           '_CM_SERVICE_NODE_TYPE', 'ACL_INFORMATION_CLASS',
#           'LOGFONT', 'IMAGE_LOAD_CONFIG_DIRECTORY32',
#           'PEXCEPTION_POINTERS', 'mysql_shutdown',
#           '_WSANETWORKEVENTS', 'WinDigestAuthenticationSid',
#           '_DEBUG_EVENT', 'MYSQL_ROW', 'tagLOGCOLORSPACEW',
#           'tagEMRFILLRGN', 'PTITLEBARINFO', 'PCANDIDATELIST',
#           'LPEXIT_THREAD_DEBUG_INFO', 'PEMRSETBKCOLOR', 'PULONG64',
#           'PHANDLETABLE', 'ACTIVATION_CONTEXT_DETAILED_INFORMATION',
#           'PowerSystemShutdown', '_PSFEATURE_OUTPUT', 'PHANDLE',
#           'BITMAPCOREINFO', 'COM_FIELD_LIST',
#           'SC_STATUS_PROCESS_INFO', 'mysql_stmt_bind_param',
#           'mysql_get_ssl_cipher', 'REGSAM',
#           '_MESSAGE_RESOURCE_ENTRY', 'mysql_option',
#           'EMRSETVIEWPORTEXTEX', 'MYSQL_OPT_USE_REMOTE_CONNECTION',
#           'MODEMSETTINGS', 'CPINFO', 'EMRCLOSEFIGURE',
#           '_IMAGE_RESOURCE_DIR_STRING_U', 'TRIVERTEX',
#           'CURSOR_TYPE_NO_CURSOR', 'CM_Power_Data_s', 'USED_MEM',
#           'PEMRCREATEDIBPATTERNBRUSHPT', 'CPINFOEXA',
#           'LPHIGHCONTRASTA', 'SidTypeDomain', '_OSVERSIONINFOEXA',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_32E',
#           'SERVICE_STATUS_HANDLE__', 'FMTID', 'LPHIGHCONTRASTW',
#           'CPINFOEXW', 'PowerSystemSleeping3', 'tagDROPSTRUCT',
#           'EMRROUNDRECT', 'PowerSystemSleeping2',
#           'MYSQL_STMT_EXECUTE_DONE', 'MYSQL_TIMESTAMP_DATE',
#           'SystemExecutionState', '_TIME_ZONE_INFORMATION',
#           'CBT_CREATEWNDA', 'PSECURITY_IMPERSONATION_LEVEL',
#           'TokenDefaultDacl', 'WSASERVICECLASSINFO',
#           'TOKEN_GROUPS_AND_PRIVILEGES',
#           'WinAccountAdministratorSid', 'EMRTEXT',
#           'enum_mysql_timestamp_type', 'tagALTTABINFO',
#           'LPCPINFOEXA', 'HMETAFILE__', 'SYSNLS_FUNCTION',
#           'COM_DELAYED_INSERT', '_OSVERSIONINFOW',
#           'tagTTPOLYGONHEADER', 'SYSTEM_AUDIT_ACE',
#           'JOBOBJECT_ASSOCIATE_COMPLETION_PORT',
#           'ANON_OBJECT_HEADER', 'EMRSETWINDOWORGEX', 'st_mysql',
#           '_WSACOMPLETION', 'tagEMROFFSETCLIPRGN',
#           '_RTL_VERIFIER_THUNK_DESCRIPTOR', 'LPWSAPROTOCOL_INFOA',
#           '_IMAGE_SEPARATE_DEBUG_HEADER', 'off_t',
#           'IMAGE_CE_RUNTIME_FUNCTION_ENTRY', 'PEMRPOLYLINE',
#           'SYSTEM_BATTERY_STATE', 'MFENUMPROC',
#           'LPWSAPROTOCOL_INFOW', 'PLIST_ENTRY32', '_TOKEN_CONTROL',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_26E',
#           'ProcessorPowerPolicyCurrent', 'LPENUMLOGFONTW',
#           'SERIALKEYSA', 'HWINSTA__', 'IID',
#           'mysql_rpl_parse_enabled', 'tagEMRCREATEPALETTE',
#           'MESSAGE_RESOURCE_ENTRY', 'mysql_stmt_data_seek',
#           'SERIALKEYSW', 'TapeDriveWriteWarning', 'LPENUMLOGFONTA',
#           'IMAGE_SEPARATE_DEBUG_HEADER', 'tagEMREXTFLOODFILL',
#           '_IMAGE_IMPORT_DESCRIPTOR', 'PEMRPOLYLINETO16', 'CIEXYZ',
#           'mysql_server_init', '_OSVERSIONINFOEXW', 'PCHAR_INFO',
#           '_CREATE_PROCESS_DEBUG_INFO', 'EMRDELETEOBJECT',
#           'PEMRSELECTCLIPPATH', 'WinAccountDomainUsersSid',
#           'WELL_KNOWN_SID_TYPE', 'ExceptionContinueExecution',
#           'NUMBERFMTW', 'LPCRECTL', 'COM_DAEMON', 'PCWPRETSTRUCT',
#           'RTL_VERIFIER_THUNK_DESCRIPTOR', 'NPCANDIDATELIST',
#           'PGUITHREADINFO', 'st_udf_init', 'ICONMETRICS',
#           '__finddata64_t', 'NUMBERFMTA', 'LPPANOSE',
#           'IMPORT_OBJECT_NAME', 'WinBuiltinPrintOperatorsSid',
#           'NPIMECHARPOSITION', 'SECURITY_CONTEXT_TRACKING_MODE',
#           'COMP_NOTLESS', '_RGNDATAHEADER', 'PCOMPAREITEMSTRUCT',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_29E',
#           'PJOB_SET_ARRAY', 'COMIMAGE_FLAGS_IL_LIBRARY',
#           'st_mysql_data', 'FindExInfoMaxInfoLevel', 'LPAFPROTOCOLS',
#           '_TAPE_GET_POSITION', 'MYSQL_TIME', 'COM_STMT_EXECUTE',
#           'PEMROFFSETCLIPRGN', 'PNEWTEXTMETRICA',
#           'NONCLIENTMETRICSA', 'EMRSETICMPROFILEW',
#           'PWSANSCLASSINFOW', 'POWER_ACTION_POLICY',
#           'PNEWTEXTMETRICW', 'u_char', '_WSABUF', 'SC_ACTION_REBOOT',
#           'PWSANSCLASSINFOA', 'EMRSETICMPROFILEA',
#           'NONCLIENTMETRICSW', '_SYSTEM_ALARM_OBJECT_ACE',
#           'NEWTEXTMETRICEX', 'PSINJECTDATA', 'FOCUS_EVENT_RECORD',
#           'LPDISCDLGSTRUCTA', 'WinAccountGuestSid',
#           'tagMENUITEMINFOW', 'IMAGE_NT_HEADERS64',
#           'LPDISCDLGSTRUCTW', 'LPCOMMTIMEOUTS', 'LONG_PTR',
#           'EMRABORTPATH', 'enum_field_types', 'TCHAR',
#           'mysql_autocommit', 'WinRemoteLogonIdSid',
#           'PEMRSTROKEANDFILLPATH', 'PEMRSELECTCOLORSPACE',
#           'MDICREATESTRUCT', 'PHALF_PTR',
#           'VerifyProcessorPowerPolicyAc', 'NPEXTLOGPEN',
#           '_MESSAGE_RESOURCE_DATA', 'QOS', 'HANDLETABLE',
#           'WINDOWPLACEMENT', 'MYSQL_TYPE_TIME', 'HICON__',
#           'N7in_addr4DOLLAR_754DOLLAR_77E', '_SOCKET_ADDRESS_LIST',
#           'LPSC_HANDLE', 'EMRSELECTPALETTE', 'SevereError',
#           'PTAPE_SET_POSITION', 'PowerActionShutdown',
#           '_IMAGE_BOUND_FORWARDER_REF', 'LINEDDAPROC',
#           'tagNCCALCSIZE_PARAMS', '_SC_STATUS_TYPE',
#           'tagMENUITEMINFOA', 'ACCESS_DENIED_OBJECT_ACE',
#           'mysql_get_client_version', 'LPSERVICE_FAILURE_ACTIONS',
#           'STARTUPINFO', '_GUID', 'Win32ServiceShareProcess',
#           'PNONCLIENTMETRICSW', 'N10_LDT_ENTRY3DOLLAR_4E',
#           '_IMAGE_FUNCTION_ENTRY64', 'LPFONTSIGNATURE',
#           'MENUITEMTEMPLATEHEADER', 'LPSOCKADDR_IN', 'tagEMRFORMAT',
#           'PNONCLIENTMETRICSA', 'tagCURSORSHAPE',
#           'MYSQL_TIMESTAMP_DATETIME', 'OSVERSIONINFO', 'PLONG32',
#           'tagPOLYTEXTW', 'SOCKADDR_STORAGE', 'mysql_master_query',
#           'EMREXTCREATEPEN', 'tagFONTSIGNATURE', 'Vio',
#           'LPRASTERIZER_STATUS', 'tagPOLYTEXTA', '_AUDIT_EVENT_TYPE',
#           'LPDISCDLGSTRUCT', 'PCRITICAL_SECTION_DEBUG', 'SIZE_T',
#           '_IMAGE_RUNTIME_FUNCTION_ENTRY', 'PROC', 'DOCINFO',
#           'EMRPOLYLINE16', 'MYSQL_STATUS_READY', 'TokenAuditPolicy',
#           'PEMRALPHABLEND', 'PSSIZE_T', 'LANGUAGEGROUP_ENUMPROCW',
#           'EMRBEGINPATH', 'NPRECONVERTSTRING',
#           'PFLS_CALLBACK_FUNCTION', 'PIMAGE_SECTION_HEADER',
#           'LPPOINTFX', 'NEWTEXTMETRIC',
#           'PJOBOBJECT_BASIC_UI_RESTRICTIONS', 'PFE_EXPORT_FUNC',
#           'DOCINFOW', 'mysql_stmt_send_long_data', 'pvalueW',
#           'PEMRWIDENPATH', 'LPOUTLINETEXTMETRICA',
#           'EMRDELETECOLORSPACE', 'COMIMAGE_FLAGS_32BITREQUIRED',
#           'LPLOGPEN', 'PRGNDATAHEADER',
#           'AssemblyDetailedInformationInActivationContxt',
#           'PWNDCLASSEX', 'N14_WSACOMPLETION4DOLLAR_794DOLLAR_81E',
#           'NAMEENUMPROCW', 'OBJECTID', 'tagEMRCREATEMONOBRUSH',
#           'SID_AND_ATTRIBUTES', '_ACL', 'mysql_stat',
#           'N21_IMAGE_SECTION_HEADER4DOLLAR_23E',
#           'tagEMRSTRETCHDIBITS', '_GRADIENT_TRIANGLE', '_fsize_t',
#           'LPCREATESTRUCTW', '_ABCFLOAT', '_LUID_AND_ATTRIBUTES',
#           'SECURITY_DESCRIPTOR_CONTROL', 'LPLINGER', 'EMRGLSRECORD',
#           'TokenPrimaryGroup', 'EMRCOLORMATCHTOTARGET',
#           'PIMAGE_IMPORT_BY_NAME', 'Item_result', 'PVALCONTEXT',
#           'PQUERYHANDLER', '_EXCEPTION_RECORD64', 'LPENUMLOGFONTEXA',
#           'WSAECOMPARATOR', 'MENUBARINFO', 'POSVERSIONINFOA',
#           'PROTOENT', 'TIMERPROC', 'SID_AND_ATTRIBUTES_ARRAY',
#           '_CONSOLE_SCREEN_BUFFER_INFO', 'LPENUMLOGFONTEXW',
#           'tagEMRSETTEXTCOLOR', 'IMAGE_OPTIONAL_HEADER64',
#           'PEMRSETICMMODE', 'PRTL_VERIFIER_THUNK_DESCRIPTOR',
#           'tagSTYLESTRUCT', '_SECURITY_DESCRIPTOR_RELATIVE',
#           'PVALUEW', 'tagENHMETAHEADER',
#           'HeapCompatibilityInformation',
#           'PIMAGE_RESOURCE_DIRECTORY_STRING', 'st_mysql_field',
#           'PEVENTMSG', 'SCROLLBARINFO',
#           'PRTL_VERIFIER_DLL_DESCRIPTOR', 'PINT16',
#           'TIMEFMT_ENUMPROCW', 'PVALUEA', 'tagCBTACTIVATESTRUCT',
#           'PCUTSTR', 'JOBOBJECT_BASIC_ACCOUNTING_INFORMATION',
#           'mysql_set_server_option', 'HFONT__', 'POLYTEXT',
#           'QUERY_SERVICE_CONFIGA', 'PNEWTEXTMETRIC',
#           'NPNEWTEXTMETRIC', 'tagEMRPOLYPOLYLINE16',
#           'MAX_CLASS_NAME', 'BITMAPCOREHEADER',
#           'COR_ILMETHOD_SECT_SMALL_MAX_DATASIZE',
#           'QUERY_SERVICE_CONFIGW', 'PTAPE_GET_DRIVE_PARAMETERS',
#           'LPIMECHARPOSITION', 'TapeDriveReadWarning', 'PBYTE',
#           'MaxActivationContextInfoClass', '_COMMPROP',
#           '_SERVICE_DESCRIPTIONW', 'mysql_stmt_reset',
#           'LPWSAPROTOCOL_INFO', '_SID_AND_ATTRIBUTES', 'dev_t',
#           'LPPROGRESS_ROUTINE', 'PINPUT_RECORD', 'NT_TIB64',
#           'WinBuiltinPerfLoggingUsersSid', 'LPSOCKET_ADDRESS',
#           'LPGLYPHMETRICS', 'EMRRECTANGLE', 'HBITMAP__',
#           '_SERVICE_FAILURE_ACTIONSW', 'PNT_TIB64',
#           'EMRREALIZEPALETTE', 'TokenImpersonationLevel',
#           '_TOKEN_GROUPS_AND_PRIVILEGES', 'COM_STMT_RESET',
#           'IMAGE_VXD_HEADER', 'mysql_list_tables', 'DCB',
#           '_SECURITY_IMPERSONATION_LEVEL',
#           'WinAccountPolicyAdminsSid',
#           'ASSEMBLY_FILE_DETAILED_INFORMATION', 'LPDLGTEMPLATE',
#           'WNDENUMPROC', 'LPEXCEPTION_POINTERS',
#           'PTOKEN_AUDIT_POLICY_ELEMENT',
#           '_JOBOBJECT_BASIC_PROCESS_ID_LIST', '_cpinfo',
#           'PROPENUMPROCA', 'PEMRPAINTRGN', 'PSIZEL',
#           'PSECURITY_ATTRIBUTES', 'MEMORY_BASIC_INFORMATION64',
#           'BITMAPINFO', 'LPENUM_SERVICE_STATUS', 'PEMRSETLAYOUT',
#           'tagPIXELFORMATDESCRIPTOR', 'RTL_VERIFIER_DLL_DESCRIPTOR',
#           'NT_TIB32', 'mysql_slave_query', 'NPSTYLEBUFW',
#           'SOCKET_ADDRESS', 'EVENTMSG', 'LPEVENTMSG',
#           'RTL_VERIFIER_DLL_UNLOAD_CALLBACK', 'LPWNDCLASSA',
#           'EMRGDICOMMENT', 'HRGN__', 'tagEMRSETARCDIRECTION',
#           'LPWCH', 'LPKBDLLHOOKSTRUCT', 'LPWNDCLASSW', 'NPSTYLEBUFA',
#           'LPCLSID', 'LPCOMBOBOXINFO', 'tagMENUINFO',
#           'JOBOBJECT_SECURITY_LIMIT_INFORMATION', 'EXCEPTION_RECORD',
#           'PWNDCLASS', 'AFPROTOCOLS', 'PSYSTEM_POWER_LEVEL',
#           'ENUMLOGFONTA', 'CONSOLE_CURSOR_INFO',
#           'ACTIVATION_CONTEXT_QUERY_INDEX', 'MONITORINFO', 'LPCH',
#           'TOKEN_CONTROL', '_EVENTSFORLOGFILE', 'ENUMLOGFONTW',
#           '_WSAPROTOCOL_INFOW', 'MENUGETOBJECTINFO', 'NPWNDCLASSEXW',
#           '_WSAPROTOCOL_INFOA', 'OBJECT_TYPE_LIST',
#           'PJOBOBJECT_BASIC_ACCOUNTING_INFORMATION',
#           'N12_DEBUG_EVENT4DOLLAR_52E', 'IMAGE_IMPORT_DESCRIPTOR',
#           'BY_HANDLE_FILE_INFORMATION', 'NPWNDCLASSEXA',
#           'IMPORT_OBJECT_NAME_UNDECORATE', 'LPGRADIENT_TRIANGLE',
#           'IMAGE_IA64_RUNTIME_FUNCTION_ENTRY', 'os_off_t',
#           'PIMECHARPOSITION', 'MYSQL', '_dev_t', 'LPSERVICE_STATUS',
#           'SystemReserveHiberFile', 'LPREMOTE_NAME_INFO',
#           'PEMRPOLYPOLYGON', 'IMAGE_FUNCTION_ENTRY64',
#           'WinDialupSid', 'NETCONNECTINFOSTRUCT',
#           'mysql_get_proto_info', 'PJOBOBJECT_JOBSET_INFORMATION',
#           'PSZ', 'tagMULTIKEYHELPW', 'REPARSE_GUID_DATA_BUFFER',
#           'PEMRENDPATH', 'PSYSTEM_AUDIT_CALLBACK_ACE',
#           'STMT_ATTR_UPDATE_MAX_LENGTH', 'LPLOGPALETTE', 'EMRCHORD',
#           'LATENCY_TIME', 'N14_WSACOMPLETION4DOLLAR_794DOLLAR_80E',
#           'COM_PING', 'mysql_disable_rpl_parse', '__time64_t',
#           'LPSTICKYKEYS', 'tagENUMLOGFONTW', 'tagLOGBRUSH',
#           'OUTPUT_DEBUG_STRING_INFO', 'LPTEXTMETRIC',
#           'PLUID_AND_ATTRIBUTES_ARRAY', 'CLSID', 'PULONGLONG',
#           'tagENUMLOGFONTA', 'LPSCROLLINFO', '_FIXED', 'PHDEVNOTIFY',
#           '_IMAGE_LINENUMBER', 'PDRAWITEMSTRUCT',
#           'AclRevisionInformation', '_SERVICE_STATUS',
#           'tagEMRROUNDRECT', 'LPTHREAD_START_ROUTINE',
#           'LOGCOLORSPACEW', 'CURRENCYFMTW', 'MYSQL_FIELD_OFFSET',
#           'tagEMRSTRETCHBLT', 'mysql_enable_reads_from_master',
#           'tagEMRPOLYDRAW16', 'LOGCOLORSPACEA',
#           'PCONSOLE_CURSOR_INFO', 'LPQUERY_SERVICE_CONFIGW',
#           'PIMAGE_NT_HEADERS64', 'LPSERVICE_DESCRIPTIONW',
#           'IMAGE_EXPORT_DIRECTORY', 'PTOKEN_STATISTICS',
#           'JOBOBJECT_END_OF_JOB_TIME_INFORMATION', 'LPMENUITEMINFO',
#           'CRITICAL_SECTION', 'tagMOUSEMOVEPOINT', 'LPUTSTR',
#           'VS_FIXEDFILEINFO', 'JobObjectBasicProcessIdList',
#           'TOKEN_USER', '_SYSTEM_ALARM_ACE', 'CriticalError',
#           'PTOKEN_PRIMARY_GROUP',
#           'WinBuiltinIncomingForestTrustBuildersSid',
#           'SidTypeWellKnownGroup', 'IMAGE_RELOCATION',
#           'PGLYPHMETRICSFLOAT', 'EMRSETICMMODE', 'EMRSETTEXTCOLOR',
#           'IMAGE_AUX_SYMBOL_TYPE', '_PIMAGE_RUNTIME_FUNCTION_ENTRY',
#           'LPWSANSCLASSINFOW', '_REMOTE_NAME_INFOW',
#           'PMOUSE_EVENT_RECORD', 'LPWSAESETSERVICEOP', 'PSIZE_T',
#           'sockaddr_in', 'LPENUM_SERVICE_STATUSW',
#           'SYSTEM_ALARM_CALLBACK_OBJECT_ACE', 'LPCIEXYZ',
#           'LPCSCROLLINFO', 'LPWSANSCLASSINFOA', '_REMOTE_NAME_INFOA',
#           'LPSOCKADDR_STORAGE', 'GUID', 'LPHW_PROFILE_INFO',
#           'PRTL_RESOURCE_DEBUG', 'u_short', 'tagXFORM', 'HGLRC',
#           '_FLOATING_SAVE_AREA', 'tagCOLORCORRECTPALETTE',
#           'PADMINISTRATOR_POWER_POLICY', 'MEMORY_BASIC_INFORMATION',
#           'LPWSACOMPLETION', 'MYSQL_PROTOCOL_MEMORY', 'PPOLYTEXT',
#           '_MOUSE_EVENT_RECORD', '_IMAGE_DEBUG_MISC',
#           'PowerSystemWorking', 'KSPIN_LOCK', 'tagLOGCOLORSPACEA',
#           'SYSTEM_AUDIT_OBJECT_ACE', 'LANGUAGEGROUP_ENUMPROCA',
#           'WNDPROC', 'LPCOMMPROP', 'IMAGE_COR_MIH_EHRVA',
#           'LPDROPSTRUCT', 'LPCVOID', 'PEMRSETROP2', 'AutoLoad',
#           '_IMAGE_SYMBOL', '_IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY',
#           'PEMRINVERTRGN', 'LPWSANSCLASSINFO',
#           'RTL_VERIFIER_PROVIDER_DESCRIPTOR', 'IgnoreError',
#           'PLOGBRUSH32', 'PRTL_VERIFIER_PROVIDER_DESCRIPTOR',
#           'tagVS_FIXEDFILEINFO', '_STARTUPINFOA', 'ENUMLOGFONT',
#           'TAPE_SET_DRIVE_PARAMETERS', '_STARTUPINFOW',
#           'mysql_stmt_prepare', 'HTASK__', 'LPTRIVERTEX',
#           'tagHARDWAREHOOKSTRUCT', '_IMAGE_BOUND_IMPORT_DESCRIPTOR',
#           'WinAccountKrbtgtSid', 'TokenPrimary', 'tagEXTLOGFONTW',
#           '_DOCINFOA', 'LPLOGCOLORSPACEW', 'POSVERSIONINFOEX',
#           '_TAPE_PREPARE', 'LPLOGCOLORSPACEA', '_DOCINFOW',
#           'PINT_PTR', 'tagEXTLOGFONTA', 'LPWGLSWAP',
#           'tagEMRSETPIXELV', 'TOKEN_GROUPS', 'HFILE', 'HELPPOLY',
#           'LPOVERLAPPED', 'SystemPowerPolicyCurrent', 'SPHANDLE',
#           'PWNDCLASSA', 'RNRSERVICE_DEREGISTER', 'tagCOMBOBOXINFO',
#           'tagEMRSETDIBITSTODEVICE', 'PEMRPIE', 'COM_QUIT',
#           'tagEMRPOLYTEXTOUTA', 'IMAGE_THUNK_DATA64', 'PUSHORT',
#           'PWNDCLASSW', 'TokenUser', '_FLOAT128',
#           'tagEMREXTCREATEPEN', 'mysql_stmt_param_metadata',
#           'PSECURITY_CONTEXT_TRACKING_MODE', 'PCONSOLE_FONT_INFO',
#           'LPCGUID', 'NSP_NOTIFY_APC', '_KEY_EVENT_RECORD',
#           'tagTITLEBARINFO', 'PACCESS_ALLOWED_OBJECT_ACE',
#           'mysql_insert_id', 'tagEMRGLSBOUNDEDRECORD', '_TOKEN_USER',
#           'LPCMENUITEMINFOA', 'PHELPWININFO', 'PCH',
#           'WinBuiltinNetworkConfigurationOperatorsSid',
#           'CREATESTRUCTA', 'LPIMEMENUITEMINFO', 'LPCONDITIONPROC',
#           'SYSTEM_ALARM_OBJECT_ACE', 'PEMRPOLYLINE16',
#           'LPCMENUITEMINFOW', '_IMAGE_ROM_HEADERS', '_wfinddata_t',
#           'XFORM', 'MAT2', 'LOGPALETTE', 'PXFORM',
#           'MYSQL_TYPE_LONGLONG',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_31E',
#           'PIMAGE_NT_HEADERS32', 'PPOINT',
#           'tagEMRCREATEDIBPATTERNBRUSHPT', 'HMENU__', 'EMRFILLPATH',
#           'PACCESS_ALLOWED_CALLBACK_OBJECT_ACE',
#           'WinAuthenticatedUserSid', 'tagEMRSETCOLORADJUSTMENT',
#           'WNDCLASSEXA', 'MYSQL_RPL_MASTER', 'LPPOLYTEXTA',
#           'LPNETRESOURCEA', 'WNDCLASSEXW', '_WGLSWAP', 'sockproto',
#           'GEOCLASS', 'LPNETRESOURCEW', 'COMMTIMEOUTS',
#           'LPPOLYTEXTW', 'WSANETWORKEVENTS', 'METAFILEPICT',
#           'LPSOUNDSENTRY', 'EMRSELECTOBJECT', 'PKBDLLHOOKSTRUCT',
#           'LPPROCESS_HEAP_ENTRY', 'LPCPINFO',
#           'N9_NT_TIB644DOLLAR_10E', 'mysql_stmt_fetch', '_CHAR_INFO',
#           'EMRGRADIENTFILL', 'EVENTLOG_FULL_INFORMATION',
#           'REMOTE_NAME_INFOW', '_CM_SERVICE_LOAD_TYPE',
#           'NPOUTLINETEXTMETRICA', 'UHALF_PTR',
#           'NPOUTLINETEXTMETRICW', 'PFONTSIGNATURE', 'CREATESTRUCTW',
#           'REMOTE_NAME_INFOA', 'LPMENUTEMPLATE',
#           'tagBITMAPFILEHEADER', 'QUERY_SERVICE_LOCK_STATUSW',
#           'PIMAGE_OPTIONAL_HEADER64', 'NPDEVMODEA', 'SOCKADDR_IN',
#           'tagEMRSCALEVIEWPORTEXTEX', 'LOCALHANDLE',
#           'PWSANAMESPACE_INFOW',
#           'JobObjectAssociateCompletionPortInformation',
#           'LIST_ENTRY64', 'LPMOUSEMOVEPOINT', 'PPROCESS_INFORMATION',
#           'PTAPE_CREATE_PARTITION', 'AdapterType',
#           '_RASTERIZER_STATUS', 'LPNETINFOSTRUCT', 'tagEMR',
#           'PLOGFONT', 'JOBOBJECT_BASIC_PROCESS_ID_LIST', 'PSIZE',
#           'ENUMLOGFONTEXA', '_OBJECT_TYPE_LIST', 'PDISPLAY_DEVICE',
#           'SidTypeInvalid', 'PFNPROCESSPOLICIESW',
#           'SYSTEM_LOGICAL_PROCESSOR_INFORMATION', 'ENHMETAHEADER',
#           'PFNPROCESSPOLICIESA', 'LPCSADDR_INFO',
#           '_TOKEN_PRIVILEGES', '_LOGICAL_PROCESSOR_RELATIONSHIP',
#           'SHUTDOWN_WAIT_CRITICAL_BUFFERS', 'COMPAREITEMSTRUCT',
#           'tagNEWTEXTMETRICW', 'EMRELLIPSE', '_TOKEN_OWNER',
#           'PIMAGE_EXPORT_DIRECTORY', 'RIP_INFO', '_ICONINFO',
#           'EMRSETMAPMODE', 'tagLAYERPLANEDESCRIPTOR', '_numberfmtA',
#           'USHORT', 'mysql_stmt_row_tell',
#           '_QUERY_SERVICE_LOCK_STATUSA', 'MYSQL_TYPE_MEDIUM_BLOB',
#           'HW_PROFILE_INFOW', 'POSVERSIONINFOW', 'LRESULT',
#           'COR_DELETED_NAME_LENGTH', 'ENUM_SERVICE_STATUS',
#           'tagDELETEITEMSTRUCT', '_numberfmtW', 'NEARPROC',
#           'N12_devicemodeA4DOLLAR_584DOLLAR_59E', 'POFSTRUCT',
#           'LPUNIVERSAL_NAME_INFO', 'PDWORD64', 'HALF_PTR', 'my_bool',
#           'LPENUM_SERVICE_STATUS_PROCESSW', 'PRTL_OSVERSIONINFOW',
#           'tagBITMAPINFO', 'LPENUM_SERVICE_STATUS_PROCESSA',
#           '_QUOTA_LIMITS_EX', 'PHOSTENT', 'PPAINTSTRUCT',
#           'SERVICE_TABLE_ENTRYA', 'tagABORTPATH',
#           'SystemPowerLoggingEntry', 'MaxTokenInfoClass',
#           'PEMRPOLYPOLYLINE', 'TAPE_WMI_OPERATIONS',
#           'NCCALCSIZE_PARAMS', 'PAPCFUNC', 'HW_PROFILE_INFOA',
#           'N14_WSACOMPLETION4DOLLAR_794DOLLAR_83E', 'STYLESTRUCT',
#           'tagEMRPOLYLINE16', 'TokenSessionReference', 'LPLDT_ENTRY',
#           'tagUSEROBJECTFLAGS', 'IMEMENUITEMINFO', 'MY_CHARSET_INFO',
#           'LOGBRUSH', 'SERVICE_TABLE_ENTRYW', 'PVOID', 'MYSQL_STMT',
#           'NPIMEMENUITEMINFOW', 'PCOPYDATASTRUCT', 'LPNUMBERFMT',
#           'NPIMEMENUITEMINFOA', 'EMRPOLYPOLYGON16', 'LPOFSTRUCT',
#           'MYSQL_ROWS', 'LPGUITHREADINFO', 'LPHIGHCONTRAST',
#           'LPNEWTEXTMETRICA', 'PEMRCHORD',
#           'PJOBOBJECT_ASSOCIATE_COMPLETION_PORT', 'CPINFOEX',
#           'LPFIBER_START_ROUTINE', 'EMRENDPATH', 'COM_STATISTICS',
#           'HWINEVENTHOOK__', 'PDISPLAY_DEVICEA', 'LPDISPLAY_DEVICEW',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_27E',
#           'PREPARSE_GUID_DATA_BUFFER', 'PMOUSEMOVEPOINT',
#           '_IMAGE_BASE_RELOCATION', 'PowerActionSleep',
#           'LPDISPLAY_DEVICEA', 'PDISPLAY_DEVICEW',
#           'PSYSTEM_AUDIT_OBJECT_ACE', 'PMENUBARINFO',
#           'PCM_POWER_DATA', 'LPCREATESTRUCTA',
#           'COMIMAGE_FLAGS_ILONLY', 'COR_VERSION_MAJOR',
#           'MYSQL_SHARED_MEMORY_BASE_NAME', 'PIMAGE_OPTIONAL_HEADER',
#           'TapeDriveCleanDriveNow', 'LANGGROUPLOCALE_ENUMPROCW',
#           'PINT32', 'PLARGE_INTEGER', 'mysql_fetch_lengths',
#           'LPPIXELFORMATDESCRIPTOR', 'LPRGBQUAD', '_SYSTEMTIME',
#           'N13_IMAGE_SYMBOL4DOLLAR_244DOLLAR_25E',
#           'LPWSANAMESPACE_INFOW',
#           'WinBuiltinPreWindows2000CompatibleAccessSid',
#           'LPWSANAMESPACE_INFOA', '_SERVICE_TABLE_ENTRYW', 'PSTR',
#           'LPMSG', '_IMAGE_OS2_HEADER',
#           'MYSQL_REPORT_DATA_TRUNCATION', 'PANOSE', 'LPMSGBOXPARAMS',
#           'PTOKEN_GROUPS', 'NPABCFLOAT', 'MINMAXINFO',
#           'KBDLLHOOKSTRUCT', 'tagTTPOLYCURVE', 'TOKEN_AUDIT_POLICY',
#           'MYSQL_TYPE_GEOMETRY', 'PEMRPOLYBEZIER16', 'HOSTENT',
#           'mysql_row_tell', 'PTSTR',
#           'MYSQL_OPT_SSL_VERIFY_SERVER_CERT', 'EXCEPTION_RECORD64',
#           'LPHANDLE',
#           '_JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION',
#           'mysql_stmt_affected_rows', 'LPMSGBOXPARAMSA',
#           'ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION',
#           'PIMAGE_THUNK_DATA', 'TEXTMETRICA',
#           'SystemPowerStateHandler', 'tagEMRSETICMPROFILE',
#           'SERIALKEYS', 'LPCPINFOEXW', '_TOKEN_GROUPS',
#           'PEMRMODIFYWORLDTRANSFORM', 'TOKEN_STATISTICS',
#           'TEXTMETRICW', 'PWINDOWPLACEMENT', 'PULARGE_INTEGER',
#           'va_list', 'PEMRRECTANGLE', 'PBITMAPFILEHEADER',
#           'GEO_ISO3', 'GEO_ISO2', 'CIEXYZTRIPLE', 'PSOCKET_ADDRESS',
#           'protoent', 'PHELPWININFOA', 'PISECURITY_DESCRIPTOR',
#           'HWND__', 'MOUSEMOVEPOINT', 'mysql_kill',
#           'LPMONITORINFOEXA', 'MYSQL_OPT_LOCAL_INFILE',
#           'tagCLIENTCREATESTRUCT',
#           'N12_devicemodeW4DOLLAR_624DOLLAR_63E', 'PGRADIENT_RECT',
#           'PHELPWININFOW', 'PEMRSCALEWINDOWEXTEX',
#           'LPSERVICE_DESCRIPTION', 'LPMETARECORD', 'LPDCB', 'INT',
#           'val_context', 'BCHAR', 'PEMRSTRETCHBLT', 'NPEXTLOGFONT',
#           'MSGBOXPARAMSA', 'BLOB', 'NETRESOURCE', 'SHANDLE_PTR',
#           'PTOKEN_INFORMATION_CLASS', 'HHOOK__',
#           'N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_11E',
#           'PWSACOMPLETIONTYPE', 'POSVERSIONINFOEXW',
#           'PEMRSETTEXTALIGN', 'COM_STMT_PREPARE', 'st_mysql_options',
#           'ENUM_SERVICE_STATUS_PROCESS', 'PPROCESSOR_POWER_POLICY',
#           'LPFNDEVCAPS', 'enum_stmt_attr_type', 'EDITWORDBREAKPROCA',
#           'WIN32_FIND_DATA', 'TTPOLYCURVE', 'FindExSearchNameMatch',
#           'SECURITY_ATTRIBUTES', 'IMAGE_NT_HEADERS32', '_BLOB',
#           'SecurityIdentification', 'PVIDEOPARAMETERS',
#           'POWER_INFORMATION_LEVEL', '_PROCESSOR_POWER_POLICY_INFO',
#           'HW_PROFILE_INFO', 'SidTypeComputer', 'LPCONNECTDLGSTRUCT',
#           'JobObjectExtendedLimitInformation', '_PROCESS_HEAP_ENTRY',
#           'tagMDINEXTMENU', 'LPQUERY_SERVICE_LOCK_STATUS',
#           '_ImageArchitectureEntry',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_294DOLLAR_30E',
#           'RTL_OSVERSIONINFOW', 'PIMAGE_LOAD_CONFIG_DIRECTORY64',
#           'SYSTEM_POWER_CAPABILITIES', 'QUERY_SERVICE_CONFIG',
#           'COMSTAT', 'BITMAPV5HEADER', 'QOS_SD_MODE', 'VALENTA',
#           'IMAGE_ARCHIVE_MEMBER_HEADER', '_SID_NAME_USE',
#           '_VIDEOPARAMETERS', 'RGNDATA', 'LPFILETIME',
#           '_TAPE_CREATE_PARTITION', '_IMAGE_DEBUG_DIRECTORY',
#           'LCSGAMUTMATCH', 'mysql_rollback', 'VALENTW',
#           'UNIVERSAL_NAME_INFO', 'WinAccountControllersSid',
#           'ABORTPROC', 'N14_WSACOMPLETION4DOLLAR_794DOLLAR_82E',
#           'enum_mysql_set_option', 'LPSERVICE_TABLE_ENTRYW',
#           'COM_DROP_DB', 'N11_OVERLAPPED4DOLLAR_48E',
#           '_TOKEN_STATISTICS', 'tagEMRINVERTRGN', 'st_mysql_methods',
#           'N9_NT_TIB323DOLLAR_9E', '_TEB', 'WinAccountComputersSid',
#           'tagMOUSEKEYS', 'GLOBALHANDLE', 'SSIZE_T',
#           'TokenSandBoxInert', 'LPCMENUINFO', 'LPINT',
#           '_SECURITY_DESCRIPTOR', 'JOBOBJECTINFOCLASS',
#           '_OVERLAPPED', '_SECURITY_ATTRIBUTES',
#           'CONSOLE_SCREEN_BUFFER_INFO',
#           'VerifyProcessorPowerPolicyDc', 'HMONITOR__',
#           'IMAGE_TLS_DIRECTORY', 'mysql_thread_id', 'LOGCOLORSPACE',
#           'TOKEN_DEFAULT_DACL', 'EMRDRAWESCAPE', 'SENDASYNCPROC',
#           'NPRGNDATA', 'CALINFO_ENUMPROCA', 'MYSQL_RES',
#           'PEMRPOLYGON16', 'st_mysql_stmt', '_IMAGE_DATA_DIRECTORY',
#           'LPWSACOMPLETIONTYPE', 'IMAGE_AUX_SYMBOL_TYPE_TOKEN_DEF',
#           'LPRGNDATA', 'DATEFMT_ENUMPROCA', 'PMODEMSETTINGS',
#           'DISPLAY_DEVICEW', 'N17_KEY_EVENT_RECORD4DOLLAR_72E',
#           'NPEXTLOGFONTW', 'CALINFO_ENUMPROCW', 'HANDLE_PTR',
#           'size_t', '_REPARSE_GUID_DATA_BUFFER', 'DATEFMT_ENUMPROCW',
#           '_LUID', 'MYSQL_TYPE_TINY_BLOB', 'PLAYERPLANEDESCRIPTOR',
#           'SystemBatteryState', '_GRADIENT_RECT', 'GLYPHMETRICS',
#           'WSAVERSION', 'PDWORD_PTR', 'netent', 'LPDISPLAY_DEVICE',
#           'EMRSETLAYOUT', 'PEMRSETVIEWPORTEXTEX', '_FPO_DATA',
#           'IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_33E', 'RTL_CRITICAL_SECTION',
#           'EMRALPHABLEND', 'PEXTLOGFONT', 'LPCOMSTAT',
#           'LPBITMAPV5HEADER', 'ACL', 'PBITMAPINFO', 'DWORDLONG',
#           'NONCLIENTMETRICS', 'PIMAGE_BOUND_IMPORT_DESCRIPTOR',
#           'LPWIN32_STREAM_ID', 'IMAGE_TLS_DIRECTORY64',
#           'PMOUSEHOOKSTRUCT', 'sigset_t', 'tagGCP_RESULTSW',
#           'WSACOMPLETION', 'QUERY_SERVICE_LOCK_STATUSA',
#           'CURRENCYFMTA', 'tagLOGPEN', 'HRSRC__', 'ULONG32',
#           'tagGCP_RESULTSA', 'PTCHAR', 'SERVICETYPE',
#           '_ACCESS_ALLOWED_OBJECT_ACE', 'STICKYKEYS',
#           '_WSANSClassInfoW', 'COMMPROP', 'TAPE_DRIVE_PROBLEM_TYPE',
#           '_WSANSClassInfoA', 'EMRSETCOLORADJUSTMENT',
#           '_currencyfmtA', '_TAPE_SET_DRIVE_PARAMETERS',
#           'MENUITEMINFOW', '_QUERY_SERVICE_CONFIGA',
#           'MYSQL_RPL_ADMIN', 'MENUITEMINFOA',
#           'JOBOBJECT_BASIC_LIMIT_INFORMATION',
#           'EMBEDDED_QUERY_RESULT', 'mysql_get_parameters',
#           'NPDEVMODEW', 'CURSOR_TYPE_FOR_UPDATE',
#           '_QUERY_SERVICE_CONFIGW', 'ACCESSTIMEOUT', 'LPEXTLOGFONTW',
#           'MYSQL_OPT_USE_EMBEDDED_CONNECTION', 'PROPENUMPROCEXA',
#           'EMRPOLYGON', 'LT_DONT_CARE', 'PROPENUMPROCEXW',
#           'LPEXTLOGFONTA', 'MYSQL_TYPE_DECIMAL',
#           '_TOKEN_PRIMARY_GROUP', 'JobObjectJobSetInformation',
#           'mysql_stmt_num_rows', 'OVERLAPPED',
#           '_PROCESSOR_POWER_POLICY', 'mysql_status',
#           'PIMAGE_FUNCTION_ENTRY', 'AuditEventObjectAccess',
#           'LPCURRENCYFMTW', 'RGBTRIPLE', 'PTIMERAPCROUTINE',
#           'PALETTEENTRY', '_ImageArchitectureHeader',
#           'ExceptionCollidedUnwind', 'PEVENTMSGMSG',
#           'PISECURITY_DESCRIPTOR_RELATIVE', 'tagSTICKYKEYS',
#           'LPCURRENCYFMTA', 'HDESK__', 'LPUWSTR', 'OLDFONTENUMPROCA',
#           'MYSQL_PROTOCOL_DEFAULT',
#           'N19_IMAGE_THUNK_DATA324DOLLAR_37E', 'mysql_next_result',
#           'tagEMREXTSELECTCLIPRGN', 'MYSQL_OPT_RECONNECT',
#           '_EXCEPTION_DEBUG_INFO', 'OLDFONTENUMPROCW', 'NPPELARRAY',
#           'PEMRGLSRECORD', 'PowerSystemMaximum', 'IMAGE_DEBUG_MISC',
#           'LPSYSTEM_INFO', 'MYSQL_TYPE_TIMESTAMP', 'LPCWPSTRUCT',
#           'EMRPOLYPOLYLINE', 'TAPE_ERASE', 'PEMRBITBLT', 'NPLOGFONT',
#           'MYSQL_SET_CHARSET_DIR', 'DESKTOPENUMPROC',
#           'TRACKMOUSEEVENT', 'COPYDATASTRUCT',
#           'EMRINTERSECTCLIPRECT', 'PEMREXCLUDECLIPRECT', 'PNT_TIB',
#           'mysql_rpl_query_type', 'LPMSGBOXPARAMSW', 'QUERYHANDLER',
#           '_NT_TIB64', 'MYSQL_TYPE_NEWDECIMAL', 'LPDOCINFO',
#           'PSFEATURE_CUSTPAPER', 'CWPRETSTRUCT',
#           'WinCreatorGroupServerSid', 'LIST',
#           'PEMRCREATEBRUSHINDIRECT', '_ino_t',
#           '_IMAGE_FUNCTION_ENTRY', 'HCURSOR', 'IMPORT_OBJECT_DATA',
#           'mysql_set_local_infile_handler', 'PKEY_EVENT_RECORD',
#           'LPSOCKET_ADDRESS_LIST', 'PLIST_ENTRY', 'KERNINGPAIR',
#           'TAPE_SET_MEDIA_PARAMETERS', 'COM_DEBUG', 'LONG32',
#           'PEMRCOLORCORRECTPALETTE', 'COM_PROCESS_KILL',
#           'LPSERVICE_DESCRIPTIONA', 'LPGCP_RESULTS',
#           'SYSTEM_POWER_POLICY', 'PEMRFILLRGN', 'MONITORINFOEX',
#           'LPNLSVERSIONINFO', 'LPCANDIDATEFORM', 'mysql_info',
#           'LPENHMETARECORD', 'MYSQL_TYPE_LONG', 'INT8',
#           'PKSPIN_LOCK', 'EMRSETWINDOWEXTEX', 'ENUMLOGFONTEXW',
#           '_FINDEX_INFO_LEVELS', 'ACCESS_ALLOWED_CALLBACK_ACE',
#           'PIMEMENUITEMINFOW', 'TokenSessionId',
#           'LPHARDWAREHOOKSTRUCT', 'HEAP_INFORMATION_CLASS',
#           'N17_IMAGE_LINENUMBER4DOLLAR_35E', 'PIMEMENUITEMINFOA',
#           'VerifySystemPolicyAc', 'FIXED', 'CANDIDATELIST',
#           '_QOS_SHAPING_RATE', '_RGNDATA', 'LPHW_PROFILE_INFOW',
#           'tagEMRRESIZEPALETTE', 'REAL_RESULT', '_LIST_ENTRY',
#           '_DISPLAY_DEVICEW', 'WORKERCALLBACKFUNC',
#           '_IMAGE_OPTIONAL_HEADER64', 'LPHW_PROFILE_INFOA', 'LPRECT',
#           '_DISPLAY_DEVICEA', 'COLORADJUSTMENT',
#           '_PROCESS_INFORMATION', '_TAPE_WRITE_MARKS',
#           'MENUTEMPLATE', 'PWIN32_FIND_DATAA', 'LPREGISTERWORDW',
#           'COR_VTABLEGAP_NAME_LENGTH', 'LPWINDOWINFO',
#           'tagKBDLLHOOKSTRUCT', 'PWIN32_FIND_DATAW',
#           'LPREGISTERWORDA', 'PALTTABINFO', 'embedded_query_result',
#           'PCANDIDATEFORM', 'PACCESS_DENIED_CALLBACK_ACE',
#           'WinEnterpriseControllersSid', 'WinLocalServiceSid',
#           'EDITWORDBREAKPROCW', 'tagEMRTRANSPARENTBLT',
#           'PLUID_AND_ATTRIBUTES', 'LPTIME_ZONE_INFORMATION',
#           'NLSVERSIONINFO', 'LPTOGGLEKEYS',
#           'LPTOP_LEVEL_EXCEPTION_FILTER', 'MSGBOXPARAMSW',
#           'PIMAGE_RUNTIME_FUNCTION_ENTRY', 'intptr_t', 'PLONG_PTR',
#           'COR_VERSION_MAJOR_V2', 'PEMRSETMAPMODE', '_GLYPHMETRICS',
#           'ACCESS_MASK', 'PIMAGE_RESOURCE_DIRECTORY_ENTRY',
#           'PCOMPOSITIONFORM', '_OUTPUT_DEBUG_STRING_INFO', 'LPBLOB',
#           'EMRCOLORCORRECTPALETTE', '_QUERY_SERVICE_LOCK_STATUSW',
#           'WIN32_FILE_ATTRIBUTE_DATA', '_EXCEPTION_POINTERS',
#           'LPCURRENCYFMT', 'IMAGE_LOAD_CONFIG_DIRECTORY64',
#           'LPMINIMIZEDMETRICS', 'PEMRSETCOLORADJUSTMENT', 'PLOGPEN',
#           'FindExSearchLimitToDirectories', 'SERVICE_STATUS',
#           'mysql_error', 'MYSQL_OPTION_MULTI_STATEMENTS_ON',
#           'GEO_LATITUDE', 'SE_IMPERSONATION_STATE', '_cpinfoexA',
#           'N14_LARGE_INTEGER3DOLLAR_0E', 'PIMAGE_IMPORT_DESCRIPTOR',
#           'PSFEATURE_OUTPUT', 'PQUOTA_LIMITS',
#           'ProcessorStateHandler', 'SystemPowerStateNotifyHandler',
#           'PWSAVERSION', '_cpinfoexW', 'EMR', 'PSYSTEM_AUDIT_ACE',
#           'SystemPowerPolicyDc', 'GetFileExMaxInfoLevel',
#           'GRAYSTRINGPROC', 'character_set', 'PPSINJECTDATA',
#           '_SYSTEM_AUDIT_ACE', 'SidTypeGroup',
#           'mysql_real_escape_string', 'PEMRPIXELFORMAT',
#           '_SECURITY_QUALITY_OF_SERVICE', '_OUTLINETEXTMETRICW',
#           'PLOGBRUSH', 'mysql_stmt_fetch_column', 'mysql_use_result',
#           'EMRSELECTCOLORSPACE', '_OUTLINETEXTMETRICA',
#           'EMRRESTOREDC', 'PIMAGE_AUX_SYMBOL',
#           'SECURITY_IMPERSONATION_LEVEL', 'HELPINFO', 'TYPELIB',
#           'CURSOR_TYPE_READ_ONLY', 'PEMRTRANSPARENTBLT',
#           '_devicemodeW', 'LPWSANETWORKEVENTS', '_devicemodeA',
#           'LPWSAECOMPARATOR', 'SOCKET_ADDRESS_LIST',
#           'RelationProcessorCore', 'PEMREXTFLOODFILL',
#           'NPTEXTMETRICW', 'tagSCROLLBARINFO',
#           'PSYSTEM_ALARM_CALLBACK_ACE', 'PEMRCREATEMONOBRUSH',
#           'MYSQL_TYPE_NEWDATE', 'tagNMHDR', 'HDEVNOTIFY',
#           'NPTEXTMETRICA', 'GEO_FRIENDLYNAME', 'RASTERIZER_STATUS',
#           'N7in_addr4DOLLAR_754DOLLAR_76E', 'tagPELARRAY',
#           'KAFFINITY', 'TOKEN_OWNER', 'LPOUTLINETEXTMETRIC',
#           'WinBuiltinSystemOperatorsSid', 'COM_CONNECT_OUT',
#           'PMULTIKEYHELP', '_ACL_REVISION_INFORMATION',
#           'mysql_dump_debug_info', 'HELPWININFO',
#           'IMAGE_AUX_SYMBOL_TOKEN_DEF',
#           'PRTL_CRITICAL_SECTION_DEBUG', 'STMT_ATTR_PREFETCH_ROWS',
#           'PEMRSETPALETTEENTRIES', '_EXCEPTION_REGISTRATION_RECORD',
#           'FindExSearchMaxSearchOp',
#           'PACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION',
#           'DEBUG_EVENT', 'LPWSASERVICECLASSINFOA',
#           'PEMRSETWORLDTRANSFORM', 'UINT_PTR', 'tagEMRALPHABLEND',
#           'mysql_fetch_field', 'mysql_enable_rpl_parse', 'CALID',
#           'VALENT', '_NETCONNECTINFOSTRUCT', '_TAPE_ERASE',
#           'EMRFLATTENPATH', 'LPPROTOENT', 'HSTR__',
#           'N10_LDT_ENTRY3DOLLAR_43DOLLAR_5E', 'MYSQL_RPL_SLAVE',
#           'EMRSCALEWINDOWEXTEX', 'PUHALF_PTR',
#           'AuditEventDirectoryServiceAccess',
#           '_BY_HANDLE_FILE_INFORMATION', 'IMPORT_OBJECT_HEADER',
#           'tagSERIALKEYSW', 'TokenGroupsAndPrivileges', 'PCTSTR',
#           'LOCALE_ENUMPROCW', 'PEMRSETSTRETCHBLTMODE',
#           'PMENUGETOBJECTINFO', 'LPOUTLINETEXTMETRICW',
#           'tagCBT_CREATEWNDW', 'LOCALE_ENUMPROCA', 'tagSERIALKEYSA',
#           'time_t', 'mysql_field_seek', 'TokenGroups',
#           'PowerSystemUnspecified', 'SERVICE_DESCRIPTIONW',
#           'PPOINTFLOAT', 'NPEVENTMSG', 'EMROFFSETCLIPRGN',
#           'EMREXTESCAPE', 'JobObjectSecurityLimitInformation',
#           'mysql_store_result', 'RelationNumaNode', 'NPWNDCLASSA',
#           'PMSLLHOOKSTRUCT', 'mysql_embedded', 'tagWINDOWINFO',
#           'PBITMAPINFOHEADER', 'PPROTOENT', 'EMRSETPOLYFILLMODE',
#           'tagPAINTSTRUCT', '_CONTEXT', 'MYSQL_OPT_CONNECT_TIMEOUT',
#           'GEO_ENUMPROC', 'LPMETAHEADER', 'PEMRSTRETCHDIBITS',
#           'PEMRPOLYTEXTOUTW', 'TOKEN_SOURCE', 'LPMOUSEKEYS',
#           'PEMRCLOSEFIGURE', 'DLGTEMPLATE', 'tagEMREXTESCAPE',
#           'SYSTEM_ALARM_CALLBACK_ACE', 'MENUTEMPLATEA',
#           'PEMRPOLYTEXTOUTA', 'PIMAGE_ROM_OPTIONAL_HEADER',
#           '_JOBOBJECTINFOCLASS', 'EMRPOLYLINE', 'tagSOUNDSENTRYA',
#           'PIMAGE_RELOCATION', 'COMBOBOXINFO', 'PICONMETRICSW',
#           'PICONINFO', 'IMAGE_LOAD_CONFIG_DIRECTORY',
#           'WinBuiltinPowerUsersSid', 'PFLOWSPEC', 'CSADDR_INFO',
#           'mysql_stmt_bind_result', 'tagNONCLIENTMETRICSA',
#           'mysql_init', 'PICONMETRICSA', 'HIGHCONTRASTW',
#           'LPQOS_SHAPING_RATE', '_LOAD_DLL_DEBUG_INFO',
#           'tagEMREXTCREATEFONTINDIRECTW', 'PIXELFORMATDESCRIPTOR',
#           'tagEMRFILLPATH', 'provider_info', 'SecurityDelegation',
#           'st_mysql_time', 'MYSQL_METHODS', 'IMAGE_DEBUG_DIRECTORY',
#           'NPOUTLINETEXTMETRIC', '_SC_ENUM_TYPE',
#           'EMRCREATEBRUSHINDIRECT', 'EMREXTTEXTOUTW',
#           'IMAGE_COR20_HEADER', 'COM_PROCESS_INFO',
#           'FLOATING_SAVE_AREA', 'IN_ADDR', 'PSID_NAME_USE',
#           'LPCANDIDATELIST', '_TOKEN_INFORMATION_CLASS',
#           'IMAGE_NT_HEADERS', 'RTL_RESOURCE_DEBUG',
#           '_ACTIVATION_CONTEXT_QUERY_INDEX', '_nlsversioninfo',
#           'HDC__', 'PACCESS_DENIED_ACE', 'PBLENDFUNCTION',
#           'LPEXIT_PROCESS_DEBUG_INFO', 'mysql_get_host_info',
#           '_IMAGE_EXPORT_DIRECTORY', 'ICONINFO', 'IMAGE_SYMBOL',
#           'PEMRSETVIEWPORTORGEX', '_PRIVILEGE_SET', 'PRGNDATA',
#           'IMAGE_LINENUMBER', 'LPSTYLESTRUCT', 'LPMSLLHOOKSTRUCT',
#           'PCWSTR', 'PowerSystemHibernate', '_IMAGE_SECTION_HEADER',
#           'mysql_stmt_field_count', 'DESKTOPENUMPROCA',
#           '_ACCESS_DENIED_CALLBACK_ACE', 'tagEMRTEXT',
#           'PEXCEPTION_RECORD', 'tagEMRGDICOMMENT', 'WinWorldSid',
#           'N24_IMAGE_IMPORT_DESCRIPTOR4DOLLAR_38E', 'NPLOGFONTW',
#           'LPMEMORYSTATUS', 'mysql_ping', 'SC_ENUM_TYPE', 'SC_LOCK',
#           'PEMRPOLYLINETO', 'DESKTOPENUMPROCW',
#           'PIMAGE_ARCHITECTURE_ENTRY', 'rand_struct', 'NPLOGFONTA',
#           'DisableLoad', 'mysql_num_fields', 'tagCREATESTRUCTA',
#           'ABCFLOAT', 'EMRPOLYPOLYGON', 'PVALENT',
#           'PIMAGE_ROM_HEADERS', 'st_mysql_res',
#           '_EVENTLOG_FULL_INFORMATION', 'tagBITMAPCOREINFO', 'TBYTE',
#           'TOKEN_PRIMARY_GROUP', 'mysql_sqlstate', 'POINTFX',
#           'PEMRDRAWESCAPE', 'UCHAR', 'SidTypeUnknown', 'LPGUID',
#           'PRECONVERTSTRING', 'PTAPE_GET_MEDIA_PARAMETERS',
#           '_ACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION',
#           'TapeDriveReadError', 'NPWNDCLASSEX',
#           'PIMAGE_DEBUG_DIRECTORY', '_NON_PAGED_DEBUG_INFO',
#           'UNLOAD_DLL_DEBUG_INFO', 'LPNETRESOURCE',
#           'TAPE_GET_MEDIA_PARAMETERS', 'PRECT',
#           'tagEMRMODIFYWORLDTRANSFORM', 'LPCREATESTRUCT',
#           'NATIVE_TYPE_MAX_CB', '_WSAEcomparator',
#           'PHANDLER_ROUTINE', 'PAUDIT_EVENT_TYPE',
#           'PEMRPOLYPOLYGON16', 'PEVENTSFORLOGFILE',
#           'PACL_REVISION_INFORMATION', 'ProcessorPowerPolicyDc',
#           '_IMAGE_THUNK_DATA64', 'DEVMODEA', 'PEMRLINETO',
#           'PWIN32_FIND_DATA', 'NPPOLYTEXTA', 'LPWSAQUERYSETA',
#           'N12_devicemodeA4DOLLAR_58E', '_WSANAMESPACE_INFOA',
#           'MOUSE_EVENT_RECORD', 'LPBYTE',
#           '_IMAGE_COFF_SYMBOLS_HEADER', 'HENHMETAFILE__',
#           '_MEMORY_BASIC_INFORMATION', 'LPWSAQUERYSETW',
#           'NPPOLYTEXTW', 'PIMAGE_FILE_HEADER', 'WinLocalSid',
#           'LOCALESIGNATURE', 'PEMRSELECTOBJECT',
#           '_EXCEPTION_RECORD32', 'MYSQL_OPT_WRITE_TIMEOUT',
#           'SERVICE_FAILURE_ACTIONS',
#           'PJOBOBJECT_END_OF_JOB_TIME_INFORMATION',
#           'mysql_real_connect', 'LPOSVERSIONINFOEXW', 'PDEVMODEW',
#           'GET_FILEEX_INFO_LEVELS',
#           '_IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY', 'LPCTSTR',
#           'PTAPE_ERASE', 'IMAGE_OS2_HEADER', 'EMRFRAMERGN',
#           'PDEVMODEA', 'LPABC', 'PIMAGE_RESOURCE_DATA_ENTRY',
#           'LPOSVERSIONINFOEXA', 'PIMAGE_RESOURCE_DIR_STRING_U',
#           'N12_devicemodeA4DOLLAR_61E', 'LPCCH', 'uintptr_t',
#           'N14_LARGE_INTEGER3DOLLAR_1E', 'Win32ServiceOwnProcess',
#           'PNT_TIB32', 'JobObjectBasicAccountingInformation',
#           'FILE_NOTIFY_INFORMATION', 'EXCEPTION_RECORD32',
#           'MENUITEMINFO', 'TapeDriveUnsupportedMedia',
#           'LPENUM_SERVICE_STATUSA', 'LPENUMLOGFONT', 'WGLSWAP',
#           'PSYSTEM_BATTERY_STATE', '_SYSTEM_POWER_POLICY',
#           'PDIBSECTION', 'GOBJENUMPROC', 'LPENHMETAHEADER',
#           'LPWSANAMESPACE_INFO', 'MYSQL_STATUS_GET_RESULT',
#           'MSLLHOOKSTRUCT', 'PUINT16', 'LPSHELLHOOKINFO',
#           'N12_SYSTEM_INFO4DOLLAR_50E',
#           'N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_394DOLLAR_40E',
#           'FD_SET', 'LPQOS_OBJECT_HDR', 'mysql_select_db',
#           'ENUMLOGFONTEX', 'PUSEROBJECTFLAGS', 'EMRPOLYPOLYLINE16',
#           'CALTYPE', '_wfinddatai64_t', 'PMINMAXINFO',
#           'LPOSVERSIONINFOW', 'WSANSCLASSINFO', '_MODEMSETTINGS',
#           'PGENERIC_MAPPING', 'LPLAYERPLANEDESCRIPTOR',
#           '_TAPE_GET_MEDIA_PARAMETERS',
#           'N15_ULARGE_INTEGER3DOLLAR_2E', 'LPSTYLEBUF', 'WinNullSid',
#           'HOOKPROC', 'SOCKADDR', 'ULONGLONG', 'st_used_mem',
#           '_flowspec', 'FONTENUMPROCA', 'PELARRAY',
#           'EMRSCALEVIEWPORTEXTEX', 'WSACOMPLETIONTYPE',
#           'PCOLORADJUSTMENT', 'IMCENUMPROC', 'FONTENUMPROCW', 'PEMR',
#           '_ENUM_SERVICE_STATUSW', 'LPLOGFONTW',
#           'SYSTEM_AUDIT_CALLBACK_OBJECT_ACE',
#           'REGISTERWORDENUMPROCW', 'mysql_stmt_attr_get',
#           'IMPORT_OBJECT_NAME_NO_PREFIX', 'LPNUMBERFMTA',
#           'REGISTERWORDENUMPROCA', 'PEMRROUNDRECT', 'LPLOGFONTA',
#           '_ENUM_SERVICE_STATUSA', 'tagEMRPLGBLT',
#           'PIMAGE_RESOURCE_DIRECTORY', 'tagCOLORMATCHTOTARGET',
#           'MYSQL_TYPE_FLOAT', 'WAITORTIMERCALLBACKFUNC',
#           'MULTIKEYHELPA',
#           'N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_13E',
#           'LPFILTERKEYS', 'DWORD_PTR', 'tagMSLLHOOKSTRUCT',
#           'PMEMORY_BASIC_INFORMATION64', 'tagTPMPARAMS',
#           'MULTIKEYHELP', 'MYSQL_STMT_PREPARE_DONE',
#           'LPEXCEPTION_DEBUG_INFO', 'WinAccountDomainGuestsSid',
#           '_SID', 'SC_HANDLE__', '_CONNECTDLGSTRUCTA', 'SYSTEM_INFO',
#           'GRADIENT_TRIANGLE', 'LPCOLORADJUSTMENT', '_TOKEN_SOURCE',
#           'LPCURSORSHAPE', '_ADMINISTRATOR_POWER_POLICY',
#           '_CONNECTDLGSTRUCTW',
#           '_JOBOBJECT_BASIC_ACCOUNTING_INFORMATION', 'PICONMETRICS',
#           '_ACCESS_DENIED_ACE', 'NormalError', 'HIGHCONTRASTA',
#           'EMRSTRETCHDIBITS', 'IMAGE_FUNCTION_ENTRY',
#           'charset_info_st', '_WSAESETSERVICEOP',
#           'SystemPowerStateLogging', 'EMRSETDIBITSTODEVICE',
#           'PBY_HANDLE_FILE_INFORMATION', 'EMREXTCREATEFONTINDIRECTW',
#           '_ASSEMBLY_FILE_DETAILED_INFORMATION', 'PBITMAPCOREINFO',
#           'WinAccountCertAdminsSid', 'SERVICE_STATUS_PROCESS',
#           'WNDCLASS', 'LPCMENUITEMINFO', 'PIMAGE_LINENUMBER',
#           'GEO_LCID', 'PACL', 'BITMAPV4HEADER',
#           'PPROCESSOR_POWER_POLICY_INFO',
#           'PVECTORED_EXCEPTION_HANDLER', 'LPCIEXYZTRIPLE',
#           'STRING_RESULT', 'PFPO_DATA', 'GEO_RFC1766',
#           'RecognizerType', 'EMRPOLYBEZIERTO', 'LPFXPT2DOT30',
#           'IMAGE_COR_EATJ_THUNK_SIZE',
#           'COMIMAGE_FLAGS_STRONGNAMESIGNED', 'LPCURSORINFO',
#           'PTOKEN_GROUPS_AND_PRIVILEGES', 'PACE_HEADER',
#           'WSANAMESPACE_INFO', 'WSANAMESPACE_INFOW',
#           'N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_39E',
#           'TokenStatistics', '_JOB_SET_ARRAY', 'HELPWININFOW',
#           'WSANAMESPACE_INFOA', 'LPGCP_RESULTSW', 'CONNECTDLGSTRUCT',
#           'MDINEXTMENU', 'HELPWININFOA', 'PTOKEN_CONTROL',
#           'IMAGE_THUNK_DATA', 'EMRSETBKCOLOR', 'LPWNDCLASS',
#           'LPTEXTMETRICW', 'PEMRCREATECOLORSPACE', 'PSCROLLBARINFO',
#           'PIMAGE_SEPARATE_DEBUG_HEADER', 'LPTEXTMETRICA',
#           'PSID_AND_ATTRIBUTES_ARRAY', 'LPCRITICAL_SECTION_DEBUG',
#           'LPCHARSETINFO', 'SERVICE_TABLE_ENTRY', 'LIST_ENTRY',
#           'tagEMREXTTEXTOUTA', '_WIN32_FILE_ATTRIBUTE_DATA',
#           'PIMAGE_DEBUG_MISC', 'mysql_query', 'PEMRABORTPATH',
#           'PAFPROTOCOLS', 'ACTIVATION_CONTEXT_INFO_CLASS',
#           'PIMAGE_ARCHIVE_MEMBER_HEADER', 'LPSERIALKEYS', 'LPTSTR',
#           'PIMAGE_THUNK_DATA32', '_ACCESS_ALLOWED_CALLBACK_ACE',
#           'LPTIMEVAL', '_BLENDFUNCTION', 'MYSQL_TYPE_INT24',
#           'tagRECONVERTSTRING', 'PIMAGE_VXD_HEADER', 'NPCHARSETINFO',
#           'SYSTEM_POWER_LEVEL', 'PSOCKADDR_STORAGE', 'PABCFLOAT',
#           'WinProxySid', 'enum_server_command', 'NPCOMPOSITIONFORM',
#           'WinBuiltinRemoteDesktopUsersSid', 'SECURITY_INFORMATION',
#           '_SE_IMPERSONATION_STATE', '_HEAPINFO', 'LPACCEL',
#           'LPCBTACTIVATESTRUCT', 'COM_INIT_DB', 'mysql_num_rows',
#           'UDF_INIT', '_IMAGE_IMPORT_BY_NAME', 'NPCANDIDATEFORM',
#           'MENUINFO', 'WINDOWINFO', 'PWSACOMPLETION',
#           'PSYSTEM_ALARM_ACE', 'PMETARECORD', 'LPNEWTEXTMETRICW',
#           'PowerDeviceD0', 'PowerDeviceD1', 'PowerDeviceD2',
#           'PowerDeviceD3', 'LANGGROUPLOCALE_ENUMPROCA',
#           'EMRPOLYBEZIER', 'PMDINEXTMENU', 'tagBITMAP',
#           'tagBITMAPINFOHEADER', 'PCWPSTRUCT', 'LPFXPT16DOT16',
#           'OUTLINETEXTMETRIC',
#           'PSYSTEM_LOGICAL_PROCESSOR_INFORMATION', 'PEMREOF',
#           'tagMSGBOXPARAMSA', 'LPBITMAPCOREINFO',
#           '_JOBOBJECT_END_OF_JOB_TIME_INFORMATION',
#           '_TAPE_DRIVE_PROBLEM_TYPE', 'REGISTERWORDA',
#           'IMAGE_IMPORT_BY_NAME', 'LPMEMORYSTATUSEX',
#           'LPIMEMENUITEMINFOA', 'PROCESSOR_POWER_POLICY',
#           'FILTERKEYS', 'REGISTERWORDW', '_IMAGE_NT_HEADERS',
#           'PSOCKADDR_IN', 'LUID_AND_ATTRIBUTES_ARRAY',
#           'LPIMEMENUITEMINFOW', 'PIN_ADDR', 'MAX_PACKAGE_NAME',
#           'LPWINDOWPLACEMENT', 'PEMRMASKBLT', 'PREGISTERWORDW',
#           'TOKEN_PRIVILEGES', 'mysql_options', 'PATTERN',
#           'PACCESS_DENIED_OBJECT_ACE', 'PIMAGE_BASE_RELOCATION',
#           'st_typelib', 'mysql_disable_reads_from_master',
#           'tagEMREOF', 'PREGISTERWORDA', 'GEO_OFFICIALNAME',
#           'PCOORD', 'WinNTLMAuthenticationSid', 'PCOMBOBOXINFO',
#           'PEMRMOVETOEX', '_SC_ACTION_TYPE', 'INPUT_RECORD',
#           'LPMODEMSETTINGS', 'LPSYSTEMTIME', 'NPEXTLOGFONTA',
#           'QOS_SHAPING_RATE', 'PTOKEN_DEFAULT_DACL',
#           'PJOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION',
#           'SERVICE_DESCRIPTIONA', 'ANIMATIONINFO',
#           '_SERVICE_TABLE_ENTRYA', 'PSECURITY_DESCRIPTOR',
#           'GCP_RESULTSA', '_TAPE_WMI_OPERATIONS',
#           'FileInformationInAssemblyOfAssemblyInActivationContxt',
#           'mysql_real_query', 'MYSQL_TYPE_STRING', 'PIMAGE_SYMBOL',
#           'GCP_RESULTSW', 'PRIVILEGE_SET', 'EXIT_THREAD_DEBUG_INFO',
#           'PSID_AND_ATTRIBUTES', 'GEOCLASS_NATION', 'HPEN__',
#           'RNRSERVICE_DELETE', 'NWPSTR',
#           '_SYSTEM_LOGICAL_PROCESSOR_INFORMATION', 'ino_t',
#           '_WSAQuerySetA', 'NPMSG', '_PACKEDEVENTINFO',
#           '_WINDOW_BUFFER_SIZE_RECORD',
#           'N13_IMAGE_SYMBOL4DOLLAR_24E', '_WSAQuerySetW',
#           'PEMREXTCREATEFONTINDIRECTW', 'FARPROC',
#           'EMRSETMAPPERFLAGS', 'PTAPE_PREPARE', '_SOCKET_ADDRESS',
#           'PUTSTR', 'PSTYLEBUFW', 'LPBITMAPV4HEADER',
#           'LPKERNINGPAIR', 'PBITMAPV5HEADER', 'COMPOSITIONFORM',
#           'DWORD64', 'LPCREATE_THREAD_DEBUG_INFO', 'PSTYLEBUFA',
#           '_JOBOBJECT_ASSOCIATE_COMPLETION_PORT', 'ULONG_PTR',
#           'mysql_rpl_probe', 'SYSTEM_ALARM_ACE', 'mysql_rpl_type',
#           'GEOID', 'PSINGLE_LIST_ENTRY', 'PEMRPOLYBEZIER', 'UINT16',
#           'PABC', 'ExceptionNestedException',
#           '_EXCEPTION_DISPOSITION', 'MaxJobObjectInfoClass',
#           'mysql_stmt_error', 'PWINDOWINFO', 'PEMRINTERSECTCLIPRECT',
#           'GRADIENT_RECT', 'tagICONMETRICSW',
#           'N14_WSACOMPLETION4DOLLAR_79E', 'LPPOINT', 'PLONG',
#           'LPGLYPHMETRICSFLOAT', 'PEMRCREATEPALETTE',
#           'DATEFMT_ENUMPROCEXW', 'LPSERVICE_MAIN_FUNCTIONW',
#           'PTAPE_WRITE_MARKS', 'IMEMENUITEMINFOA', 'LPVOID',
#           'PIMAGE_TLS_DIRECTORY', 'N15_ULARGE_INTEGER3DOLLAR_3E',
#           'LPSERVICE_MAIN_FUNCTIONA', 'MYSQL_TYPE_NULL',
#           '_JOBOBJECT_JOBSET_INFORMATION',
#           'CREATE_THREAD_DEBUG_INFO', 'EMRSETICMPROFILE',
#           'POWER_ACTION', 'PSID', 'IMEMENUITEMINFOW',
#           'PJOBOBJECT_BASIC_PROCESS_ID_LIST',
#           'IMPORT_OBJECT_NAME_TYPE', 'PPROVIDER',
#           'WinLocalSystemSid', 'PRTL_OSVERSIONINFOEXW', 'PKAFFINITY',
#           'LPPAINTSTRUCT', 'SC_STATUS_TYPE',
#           'tagEMRSETWORLDTRANSFORM', 'PROPENUMPROCEX',
#           'EMRSETMETARGN', 'METAHEADER', 'list_walk_action',
#           'ACL_SIZE_INFORMATION',
#           'N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_41E',
#           'PFNGETPROFILEPATHW', 'GENERIC_MAPPING', 'PEMREXTTEXTOUTW',
#           'mysql_eof', 'LPTPMPARAMS', 'PFNGETPROFILEPATHA',
#           'TokenOwner', 'LOAD_DLL_DEBUG_INFO', 'PEMREXTTEXTOUTA',
#           'IMAGE_ROM_HEADERS', 'LPSTYLEBUFW', 'PEXTLOGFONTW',
#           'mysql_enum_shutdown_level', 'mysql_refresh',
#           'IMAGE_RESOURCE_DATA_ENTRY', '_WIN32_STREAM_ID',
#           'HINSTANCE__', 'PEXTLOGFONTA', 'PPELARRAY',
#           'MYSQL_TYPE_VAR_STRING', 'mysql_thread_end', 'LPEXTLOGPEN',
#           'LPANIMATIONINFO', 'COMIMAGE_FLAGS_TRACKDEBUGDATA',
#           'EMREXTSELECTCLIPRGN', 'servent',
#           'WinAccountSchemaAdminsSid', 'PEMRSETDIBITSTODEVICE',
#           'TOGGLEKEYS', 'tagMSGBOXPARAMSW',
#           '_ACTIVATION_CONTEXT_INFO_CLASS', 'NAMEENUMPROCA',
#           'EVENTLOGRECORD', 'WINDOW_BUFFER_SIZE_RECORD', 'LONGLONG',
#           'N12_SYSTEM_INFO4DOLLAR_504DOLLAR_51E',
#           'TapeDriveMediaLifeExpired', 'DEBUGHOOKINFO', 'LPWORD',
#           'MYSQL_TIMESTAMP_NONE', 'TIMEVAL', 'mysql_change_user',
#           'PFLOATING_SAVE_AREA', 'tagEMRPIXELFORMAT',
#           'IMPORT_OBJECT_TYPE', 'MYSQL_TIMESTAMP_ERROR',
#           'mysql_get_server_info', 'ACCESS_DENIED_ACE',
#           'PSYSTEM_ALARM_CALLBACK_OBJECT_ACE', 'WSANSCLASSINFOW',
#           'PIMAGE_DATA_DIRECTORY',
#           'PJOBOBJECT_BASIC_LIMIT_INFORMATION', '_OBJECTID',
#           'tagGUITHREADINFO', 'PWCH', 'WinBuiltinUsersSid',
#           'WinAccountDomainAdminsSid', 'WSANSCLASSINFOA',
#           'WSAQUERYSET', 'NSP_NOTIFY_HWND', 'PDWORD32', 'tagPOINTFX',
#           'ProcessorStateHandler2', '_ENUM_SERVICE_STATUS_PROCESSA',
#           'RTL_CRITICAL_SECTION_DEBUG', 'FLASHWINFO', 'PDWORDLONG',
#           '_GLYPHMETRICSFLOAT', 'tagEMRNAMEDESCAPE',
#           '_ENUM_SERVICE_STATUS_PROCESSW', 'EXCEPTION_DISPOSITION',
#           'COM_BINLOG_DUMP', 'PEMRGDICOMMENT', 'PTRIVERTEX',
#           'mysql_stmt_execute', '_SERVICE_FAILURE_ACTIONSA',
#           'PINT64', 'mysql_debug', 'PCSADDR_INFO', '_SYSTEM_INFO',
#           'LPQUERY_SERVICE_CONFIG', 'EMRANGLEARC', 'CREATESTRUCT',
#           'GEO_LONGITUDE', 'SECURITY_QUALITY_OF_SERVICE', 'LOGPEN',
#           'MINIMIZEDMETRICS', 'PVALENTW', 'UNIVERSAL_NAME_INFOW',
#           'LUID', 'LPMENUBARINFO', 'TokenSource', 'LPLONG',
#           'tagRGBTRIPLE', 'LPBOOL', 'MENUTEMPLATEW',
#           'EMRTRANSPARENTBLT', 'tagEMREXCLUDECLIPRECT',
#           'NEWTEXTMETRICW', 'INT32', 'LPMONITORINFO',
#           'tagNEWTEXTMETRICEXA', 'ENUMRESNAMEPROCA', 'SYSGEOCLASS',
#           'CODEPAGE_ENUMPROCW', 'PMSGBOXPARAMSW', 'timeval',
#           'tagNEWTEXTMETRICEXW', 'ENUMRESNAMEPROCW',
#           'tagMETAFILEPICT', 'PMEMORY_BASIC_INFORMATION32',
#           'NEWTEXTMETRICA', '_QUOTA_LIMITS', 'PMSGBOXPARAMSA',
#           'tagPALETTEENTRY', 'CODEPAGE_ENUMPROCA', 'LPLOGBRUSH',
#           'BATTERY_REPORTING_SCALE', '_WIN32_FIND_DATAW',
#           'LPFLOWSPEC', 'N7_NT_TIB3DOLLAR_8E',
#           'PACTIVATION_CONTEXT_DETAILED_INFORMATION',
#           'FINDEX_SEARCH_OPS', '_WIN32_FIND_DATAA',
#           'LPNONCLIENTMETRICS', 'EMRPAINTRGN', 'PDEVMODE',
#           'MYSQL_TYPE_BIT', 'NPCWPRETSTRUCT',
#           'SYSTEM_AUDIT_CALLBACK_ACE', 'tagMOUSEHOOKSTRUCT',
#           'CURRENCYFMT', 'list_add', 'PWSTR', 'PCRITICAL_SECTION',
#           'PLONGLONG', 'ACCESS_ALLOWED_ACE', 'NPABC',
#           'SYSTEM_POWER_STATUS', 'LPBITMAPINFOHEADER',
#           '_TAPE_GET_DRIVE_PARAMETERS', 'EMRCREATEDIBPATTERNBRUSHPT',
#           'NPLOGPALETTE', 'PTOKEN_USER', 'PCCH', 'LPSTARTUPINFOW',
#           'tagDRAWITEMSTRUCT', 'JOB_SET_ARRAY', 'PUINT32',
#           'EMRSETPIXELV', '_MEMORYSTATUSEX', 'LPSTARTUPINFOA',
#           '_IMAGE_RESOURCE_DIRECTORY_STRING',
#           'PIMAGE_TLS_DIRECTORY32', 'PLINGER', 'mysql_stmt_errno',
#           'MENUITEMTEMPLATE', 'tagEMRSELECTCLIPPATH',
#           'mysql_thread_init', 'N17_IMAGE_RELOCATION4DOLLAR_34E',
#           'LPMETAFILEPICT', 'PIMAGE_CE_RUNTIME_FUNCTION_ENTRY',
#           '_CONSOLE_CURSOR_INFO', 'PIMAGE_COFF_SYMBOLS_HEADER',
#           '_EXIT_THREAD_DEBUG_INFO', 'KEY_EVENT_RECORD',
#           'LPGCP_RESULTSA', 'COM_QUERY', 'tagCOPYDATASTRUCT',
#           'tagNONCLIENTMETRICSW', 'CLIENTCREATESTRUCT',
#           'PIMAGE_COR20_HEADER', 'MYSQL_READ_DEFAULT_FILE',
#           'EMRSELECTCLIPPATH', 'MYSQL_OPT_READ_TIMEOUT',
#           'tagCURSORINFO', 'MYSQL_BIND', 'WinThisOrganizationSid',
#           '_WSAPROTOCOLCHAIN',
#           'JobObjectBasicAndIoAccountingInformation',
#           '_IMAGE_RESOURCE_DIRECTORY_ENTRY', 'VIDEOPARAMETERS',
#           'mysql_commit', 'MEMORYSTATUS', 'MYSQL_STMT_FETCH_DONE',
#           'IMAGE_COR_MIH_METHODRVA', 'CHARSETINFO', 'EMRMOVETOEX',
#           'WinNetworkServiceSid',
#           'ActivationContextDetailedInformation',
#           'SystemPowerInformation', '_exception', 'PEMRSETBKMODE',
#           'SHORT', 'GROUP', 'WinAccountEnterpriseAdminsSid',
#           'tagEMRELLIPSE', '_TAPE_SET_POSITION', 'LPMODEMDEVCAPS',
#           '_SYSTEM_POWER_STATUS', 'PACCESS_ALLOWED_ACE',
#           'PMEASUREITEMSTRUCT', 'SystemPowerCapabilities',
#           'tagCWPSTRUCT', 'LPCWCH', 'mysql_server_end',
#           '_SINGLE_LIST_ENTRY', 'PTEXTMETRIC', 'LPIID',
#           'COM_SET_OPTION', 'PWCHAR', 'tagMEASUREITEMSTRUCT',
#           'PDLGITEMTEMPLATEW', 'PWSANAMESPACE_INFO',
#           'EMRCREATECOLORSPACE', 'PEXCEPTION_RECORD64', 'PLUID',
#           'LPHANDLER_FUNCTION_EX', 'mysql_stmt_init', 'FCHAR',
#           'WinServiceSid', 'WinBatchSid', '_TOKEN_AUDIT_POLICY',
#           '_MEMORY_BASIC_INFORMATION32', 'PEMRSAVEDC', '_POINTFLOAT',
#           'LPSTARTUPINFO', 'METARECORD',
#           '_IMAGE_RESOURCE_DATA_ENTRY', 'DISCDLGSTRUCT', 'HKL__',
#           '_FINDEX_SEARCH_OPS', 'PEMRPOLYDRAW16', '_NETRESOURCEA',
#           'LPHELPWININFO', 'NT_TIB', 'PPOWER_ACTION',
#           'PIMAGE_FUNCTION_ENTRY64',
#           'PIMAGE_IA64_RUNTIME_FUNCTION_ENTRY', 'PSYSTEMTIME',
#           'NPPOINT', 'LDT_ENTRY', 'LPUINT', 'QUOTA_LIMITS',
#           '_IMAGE_TLS_DIRECTORY64', '_NETRESOURCEW',
#           'EMREXTTEXTOUTA', 'tagIMECHARPOSITION',
#           'PMENUITEMTEMPLATEHEADER', 'PFE_IMPORT_FUNC', 'PVOID64',
#           'PPROCESS_HEAP_ENTRY', 'LPCONNECTDLGSTRUCTW', 'PVALENTA',
#           'LPDLGTEMPLATEW', 'PMSG', 'IMAGE_BASE_RELOCATION',
#           'LPSIZE', '_COMMTIMEOUTS', 'PEMRPOLYBEZIERTO16',
#           'N12_devicemodeW4DOLLAR_62E', 'WINSTAENUMPROC',
#           'tagCHARSETINFO', 'WSAQUERYSETA', 'LPXFORM',
#           '_ACTIVATION_CONTEXT_DETAILED_INFORMATION', 'PRLIST_ENTRY',
#           'PPALETTEENTRY', 'tagCWPRETSTRUCT', '_DRAWPATRECT',
#           'PTOKEN_PRIVILEGES', 'JobObjectBasicUIRestrictions',
#           'LPMDINEXTMENU', 'WSAQUERYSETW', 'DriverType', 'LPPATTERN',
#           'PULONG32', 'PBITMAPCOREHEADER', 'EMRINVERTRGN',
#           'LPCWPRETSTRUCT', 'UINT8', 'WNDCLASSW',
#           'N10_CHAR_INFO4DOLLAR_74E', 'SID_NAME_USE',
#           'PEMRPOLYBEZIERTO', 'PEMRFLATTENPATH',
#           'WinOtherOrganizationSid', '_UNIVERSAL_NAME_INFOW',
#           'LPBITMAPFILEHEADER', 'PEMRPOLYGON',
#           'PIMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY', 'LPCOMMCONFIG',
#           'u_long', 'DATEFMT_ENUMPROCEXA', 'st_udf_args',
#           'N37_SYSTEM_LOGICAL_PROCESSOR_INFORMATION4DOLLAR_114DOLLAR_12E',
#           '_OFSTRUCT', 'LPSOCKADDR',
#           'JOBOBJECT_BASIC_UI_RESTRICTIONS', 'COM_STMT_CLOSE',
#           'PowerSystemSleeping1',
#           'N19_IMAGE_THUNK_DATA644DOLLAR_36E', 'COMP_EQUAL',
#           'LT_LOWEST_LATENCY', '_SYSTEM_AUDIT_CALLBACK_ACE',
#           'EMRCREATEPALETTE', 'tagEXTLOGPEN', 'LPNMHDR',
#           'PACCESS_TOKEN', 'QUERY_SERVICE_LOCK_STATUS', 'ROW_RESULT',
#           'SC_ACTION_RESTART', 'EMRSETMITERLIMIT',
#           'STMT_ATTR_CURSOR_TYPE', 'PUINT_PTR', 'SERVICE_ERROR_TYPE',
#           'ULONG64', 'tagEMRARC', 'LPDLGTEMPLATEA',
#           'UNIVERSAL_NAME_INFOA', 'my_ulonglong', 'MSGBOXPARAMS',
#           'ICMENUMPROCW', 'PJOBOBJECT_EXTENDED_LIMIT_INFORMATION',
#           'N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_55E',
#           'SHUTDOWN_WAIT_CONNECTIONS', 'tagEMRCREATECOLORSPACEW',
#           'EMRMASKBLT', 'COORD', 'PTOKEN_AUDIT_POLICY',
#           'ICMENUMPROCA', 'TIMEFMT_ENUMPROCA',
#           'N17_IMAGE_AUX_SYMBOL4DOLLAR_264DOLLAR_274DOLLAR_28E',
#           '_SYSTEM_AUDIT_OBJECT_ACE', 'PTAPE_GET_POSITION',
#           'WinTerminalServerSid', 'FLOWSPEC', 'FileSystemType',
#           'NSP_NOTIFY_IMMEDIATELY', 'LPNCCALCSIZE_PARAMS',
#           '_MEMORYSTATUS', 'SecurityAnonymous', 'OFSTRUCT', 'PINT',
#           'LPDELETEITEMSTRUCT', '_IMAGE_FILE_HEADER', 'RGBQUAD',
#           'BITMAPINFOHEADER', 'tagTRACKMOUSEEVENT',
#           'WinBuiltinDomainSid', 'WIN32_STREAM_ID',
#           'IMAGE_COR_MIH_BASICBLOCK', 'PTOP_LEVEL_EXCEPTION_FILTER',
#           'GUITHREADINFO', 'BootLoad', 'PLIST_ENTRY64',
#           'JOBOBJECT_JOBSET_INFORMATION', 'EMREXCLUDECLIPRECT',
#           'fd_set', 'LPTTPOLYCURVE', 'PEMRSETARCDIRECTION',
#           'tagEMRANGLEARC', 'REGISTERWORD', 'MYSQL_MANAGER',
#           'NLS_FUNCTION', 'LPMAT2', 'tagCANDIDATELIST',
#           'st_mysql_rows', 'EMRSETROP2', 'tagMULTIKEYHELPA',
#           'mysql_close', 'tagEMRFRAMERGN', 'TapeDriveHardwareError',
#           'LPWSASERVICECLASSINFO', '_INPUT_RECORD', 'PFLOAT128',
#           'tagEMRLINETO', 'ProcessorPowerPolicyAc',
#           'LPMENUITEMINFOW', 'KILL_QUERY',
#           'IMAGE_BOUND_FORWARDER_REF', 'PHKEY',
#           'PIMAGE_BOUND_FORWARDER_REF', 'PWSAESETSERVICEOP',
#           'SERVICE_NODE_TYPE', 'N10_LDT_ENTRY3DOLLAR_43DOLLAR_6E',
#           'MYSQL_TYPE_SHORT', 'SidTypeAlias', 'USEROBJECTFLAGS',
#           'tagEMRCREATEPEN', 'NPREGISTERWORDA', 'tagEMRBITBLT',
#           '_PSINJECTDATA', 'LPOSVERSIONINFOA', 'MYSQL_TYPE_ENUM',
#           'LPBY_HANDLE_FILE_INFORMATION', 'tagWNDCLASSA',
#           '_IMAGE_DOS_HEADER', 'LPSOUNDSENTRYA', 'PINT8',
#           'DISPLAY_DEVICE', 'WinSChannelAuthenticationSid',
#           '_complex', 'PowerActionHibernate', 'CCHAR', 'LPHELPINFO',
#           'PowerActionShutdownOff', 'myodbc_remove_escape',
#           'tagNEWTEXTMETRICA', 'PWGLSWAP', 'LPSOUNDSENTRYW',
#           'PEMRPOLYPOLYLINE16', 'EXIT_PROCESS_DEBUG_INFO',
#           'TapeDriveReadWriteError', 'EMRSETTEXTALIGN',
#           'JOBOBJECT_EXTENDED_LIMIT_INFORMATION',
#           'CURSOR_TYPE_SCROLLABLE', 'LPWSASERVICECLASSINFOW',
#           'IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY', 'MDICREATESTRUCTA',
#           'UINT32', 'EMRPOLYTEXTOUTA', 'LPBITMAP',
#           'TokenRestrictedSids', 'SERVENT', '_finddatai64_t',
#           'LPCUWSTR', 'PSID_IDENTIFIER_AUTHORITY', 'tagRGBQUAD',
#           'LPMONITORINFOEXW', 'SCROLLINFO', 'EMRWIDENPATH',
#           'tagWNDCLASSW', 'FXPT16DOT16', 'PTOKEN_TYPE',
#           'DISCDLGSTRUCTW', 'LUID_AND_ATTRIBUTES', 'SOCKET',
#           'LPWIN32_FIND_DATA', '_IO_COUNTERS', 'MYSQL_TYPE_VARCHAR',
#           'tagLOGPALETTE', 'DISCDLGSTRUCTA', 'PULONG',
#           'COM_CREATE_DB', 'mysql_protocol_type', 'LPCONTEXT',
#           'PTAPE_SET_DRIVE_PARAMETERS', 'LPWSADATA', 'PEMRFRAMERGN',
#           'SYSTEMTIME', 'HIMC__', 'NPREGISTERWORD', 'PCSTR',
#           'tagEMRRESTOREDC', 'IMAGE_SECTION_HEADER',
#           'PEMRSETICMPROFILEA', 'wint_t', '_MODEMDEVCAPS',
#           'mysql_list_processes',
#           'PCASSEMBLY_FILE_DETAILED_INFORMATION',
#           'PEMRSETICMPROFILEW', 'MYSQL_SET_CLIENT_IP',
#           'PACCESS_ALLOWED_CALLBACK_ACE', 'LPWSAOVERLAPPED',
#           'LPBITMAPINFO', 'PROCESS_HEAP_ENTRY',
#           'MEMORY_BASIC_INFORMATION32',
#           '_SYSTEM_ALARM_CALLBACK_OBJECT_ACE', 'LPLOGCOLORSPACE',
#           'tagTOGGLEKEYS', 'PSLIST_HEADER',
#           'TOKEN_AUDIT_POLICY_ELEMENT', 'DECIMAL_RESULT',
#           'WSAPROTOCOL_INFO', 'mysql_list_dbs',
#           'IMAGE_DATA_DIRECTORY', 'IMAGE_RESOURCE_DIRECTORY_ENTRY',
#           'LPBITMAPCOREHEADER', 'HWINEVENTHOOK',
#           'IMPORT_OBJECT_CONST', 'LPSERIALKEYSA', 'EMRARCTO',
#           'PACCESS_MASK', 'u_int', 'COM_CHANGE_USER', 'PTOKEN_OWNER',
#           'PPSFEATURE_OUTPUT', 'LPSERIALKEYSW', 'tagEMRSELECTOBJECT',
#           'LPREMOTE_NAME_INFOW', 'MYSQL_STATUS_USE_RESULT',
#           'PSYSTEM_POWER_STATE', 'EXCEPTION_POINTERS', '_COMSTAT',
#           'LPREMOTE_NAME_INFOA', 'tagEVENTMSG', 'CBT_CREATEWNDW',
#           'EMRSAVEDC', 'LPSIZEL', 'RECONVERTSTRING', '_ACE_HEADER',
#           'tagBITMAPCOREHEADER',
#           'N19_PROCESS_HEAP_ENTRY4DOLLAR_534DOLLAR_54E',
#           'LPSCROLLBARINFO', '_JOBOBJECT_SECURITY_LIMIT_INFORMATION',
#           'tagICEXYZTRIPLE', 'EMRFILLRGN', 'PRTL_CRITICAL_SECTION',
#           'EMRSETBRUSHORGEX', 'FindExSearchLimitToDevices',
#           'DEVICE_POWER_STATE', 'LPWIN32_FILE_ATTRIBUTE_DATA',
#           'EMRSETSTRETCHBLTMODE', 'PMODEMDEVCAPS', 'HGLRC__',
#           'PEMRCOLORMATCHTOTARGET', 'ProcessorInformation',
#           'tagPOINTS', 'PMENUITEMTEMPLATE', 'WSAESETSERVICEOP',
#           'POINTS', 'LPMINMAXINFO', 'NPWNDCLASSW',
#           'LAYERPLANEDESCRIPTOR', 'PLONG64', 'tagANIMATIONINFO',
#           'LPDIBSECTION', 'SINGLE_LIST_ENTRY', 'PEMRPOLYDRAW',
#           'MYSQL_SECURE_AUTH', '_JOBOBJECT_BASIC_UI_RESTRICTIONS',
#           'PIMAGE_NT_HEADERS', 'POINTER_64_INT', 'INT_RESULT',
#           'N19_PROCESS_HEAP_ENTRY4DOLLAR_53E', '_WSANAMESPACE_INFOW',
#           'PEMREXTSELECTCLIPRGN', 'PEMRSETMITERLIMIT',
#           'NPEVENTMSGMSG', '_SERVICE_DESCRIPTIONA', '_finddata_t',
#           'mysql_send_query', 'EMRNAMEDESCAPE', 'tagSOUNDSENTRYW',
#           'NPRECT', '_FOCUS_EVENT_RECORD', 'BLENDFUNCTION',
#           'TITLEBARINFO', 'PLDT_ENTRY', 'PBITMAPV4HEADER',
#           'tagEMRPOLYPOLYLINE', 'tagENHMETARECORD',
#           'PJOBOBJECT_SECURITY_LIMIT_INFORMATION', 'PPVALUEA',
#           'DRAWITEMSTRUCT', 'RTL_VERIFIER_DLL_LOAD_CALLBACK',
#           'TAPE_PREPARE', 'LPCRITICAL_SECTION',
#           'ExceptionContinueSearch',
#           'PCACTIVATION_CONTEXT_DETAILED_INFORMATION', 'PPVALUEW',
#           'LPSERVICE_TABLE_ENTRY', 'LastSleepTime',
#           'JobObjectEndOfJobTimeInformation',
#           'MESSAGE_RESOURCE_BLOCK', 'PEMRSETMETARGN',
#           'tagCREATESTRUCTW', 'PMENU_EVENT_RECORD', 'LCSCSTYPE',
#           'TEXTMETRIC', 'WSADATA', 'PIMAGE_TLS_DIRECTORY64', 'PCWCH',
#           'st_net', 'LPRIP_INFO', 'PFILETIME', 'PEVENTLOGRECORD',
#           'LPHANDLETABLE', 'EXTLOGPEN',
#           '_IMAGE_CE_RUNTIME_FUNCTION_ENTRY',
#           'PIMAGE_LOAD_CONFIG_DIRECTORY', '_RIP_INFO', 'HUMPD',
#           'SHELLHOOKINFO', 'HKEY__', 'SC_ACTION_RUN_COMMAND',
#           'EMRPOLYGON16', 'NPLOGBRUSH', 'PowerActionWarmEject',
#           'SECURITY_DESCRIPTOR', 'EXTLOGFONT', 'tagMDICREATESTRUCTA',
#           'SystemPowerPolicyAc', 'tagMDICREATESTRUCTW', 'PEMRARC',
#           'tagMONITORINFO', '_IMAGE_OPTIONAL_HEADER',
#           'CONNECTDLGSTRUCTA', 'mysql_stmt_free_result',
#           'LPCDLGTEMPLATE', 'MYSQL_TYPE_SET',
#           'mysql_get_character_set_info', 'tagWINDOWPOS',
#           'LPDLGITEMTEMPLATEA', 'CONNECTDLGSTRUCTW',
#           'tagMINIMIZEDMETRICS', 'LPDLGITEMTEMPLATEW', '_NT_TIB32',
#           '_SC_ACTION', 'tagTEXTMETRICW', 'NPPOLYTEXT',
#           'PMESSAGE_RESOURCE_ENTRY', 'tagDIBSECTION',
#           'N25_REPARSE_GUID_DATA_BUFFER4DOLLAR_14E',
#           'tagTEXTMETRICA', '_RTL_VERIFIER_DLL_DESCRIPTOR',
#           'COM_TABLE_DUMP', 'MYSQL_TYPE_DATE',
#           'EMRSETWORLDTRANSFORM', 'PIMAGE_TLS_CALLBACK',
#           'PCONSOLE_SCREEN_BUFFER_INFO', 'TAPE_CREATE_PARTITION',
#           'LPHELPWININFOW', '_RTL_VERIFIER_PROVIDER_DESCRIPTOR',
#           'SC_ACTION_NONE', 'PFILE_NOTIFY_INFORMATION',
#           'EMRPOLYDRAW16', 'PSYSTEM_POWER_POLICY', 'LPPOINTS',
#           'LPHELPWININFOA', 'JobObjectBasicLimitInformation',
#           'EMRSTROKEANDFILLPATH', 'IMECHARPOSITION', 'LOGFONTW',
#           'NPPATTERN', 'PROCESSOR_POWER_POLICY_INFO',
#           'ACCESS_DENIED_CALLBACK_ACE', 'pvalueA',
#           '_GET_FILEEX_INFO_LEVELS', 'LOGFONTA',
#           'N11_OVERLAPPED4DOLLAR_484DOLLAR_49E', 'HIMC',
#           'MYSQL_TYPE_BLOB', 'NPREGISTERWORDW', 'PEMREXTCREATEPEN',
#           'IMAGE_BOUND_IMPORT_DESCRIPTOR', '_SERVICE_STATUS_PROCESS',
#           'TPMPARAMS', 'TapeDriveWriteError', '_MAT2',
#           'POSVERSIONINFOEXA', '_CREATE_THREAD_DEBUG_INFO',
#           '_IMAGE_ROM_OPTIONAL_HEADER', 'LPICONMETRICSW', 'LPTCH',
#           'APC_CALLBACK_FUNCTION', 'MYSQL_ROW_OFFSET',
#           'N13_INPUT_RECORD4DOLLAR_73E', 'LPICONMETRICSA',
#           'PEMRSETMAPPERFLAGS', '_NT_TIB', 'FINDEX_INFO_LEVELS',
#           'EMRBITBLT', 'IMAGE_TLS_DIRECTORY32',
#           'LPNETCONNECTINFOSTRUCT', 'PPRIVILEGE_SET',
#           'LPDEBUG_EVENT', 'tagCANDIDATEFORM',
#           'LPCREATE_PROCESS_DEBUG_INFO', 'LPMOUSEHOOKSTRUCT',
#           'PCUWSTR', 'FXPT2DOT30', 'EMRPOLYBEZIERTO16',
#           'PNONCLIENTMETRICS', '_ACCESS_DENIED_OBJECT_ACE',
#           '_ACL_SIZE_INFORMATION', '_ACCESS_ALLOWED_ACE',
#           'PMINIMIZEDMETRICS', 'EMRCREATEMONOBRUSH',
#           'PBATTERY_REPORTING_SCALE', 'LPTTPOLYGONHEADER',
#           'PSECURITY_QUALITY_OF_SERVICE', 'NETINFOSTRUCT',
#           'IMAGE_OPTIONAL_HEADER', 'GLYPHMETRICSFLOAT',
#           'PEMRREALIZEPALETTE', 'mysql_read_query_result',
#           'AUDIT_EVENT_TYPE', 'LPOSVERSIONINFOEX', 'LPHOSTENT',
#           'LPDOCINFOA', 'SidTypeUser', 'PIMAGE_OS2_HEADER',
#           'rf_SetTimer', 'ACCESS_ALLOWED_CALLBACK_OBJECT_ACE',
#           '_LDT_ENTRY', 'tagHELPINFO', 'LPDOCINFOW',
#           'mysql_fetch_row', 'PEMRANGLEARC', 'PFLASHWINFO',
#           '_TAPE_SET_MEDIA_PARAMETERS', 'PBOOLEAN', 'TokenType',
#           'tagHIGHCONTRASTW', 'tagFILTERKEYS', 'CBT_CREATEWND',
#           'tagMETAHEADER', '_CSADDR_INFO', 'MYSQL_TYPE_LONG_BLOB',
#           '_RTL_CRITICAL_SECTION', 'SERVICE_LOAD_TYPE',
#           'tagHIGHCONTRASTA', 'longlong', 'ABC', '_QOS_SD_MODE',
#           'tagREGISTERWORDA', 'POUTLINETEXTMETRIC',
#           'MYSQL_INIT_COMMAND', 'ENUMRESTYPEPROCA', 'PSOCKADDR',
#           'tagMENUBARINFO', 'PSYSTEM_AUDIT_CALLBACK_OBJECT_ACE',
#           'LPIN_ADDR', 'st_mem_root', 'EMRLINETO',
#           'ENUMRESTYPEPROCW', 'tagREGISTERWORDW', 'tagSCROLLINFO',
#           '_IMAGE_NT_HEADERS64', 'wctype_t',
#           '_JOBOBJECT_BASIC_LIMIT_INFORMATION', 'IMPORT_OBJECT_CODE',
#           'LPOSVERSIONINFO',
#           'FileInformationInAssemblyOfAssemblyInActivationContext',
#           'PTAPE_WMI_OPERATIONS', 'RTL_OSVERSIONINFOEXW',
#           'mysql_free_result', 'LPPOLYTEXT', 'sockaddr_storage',
#           'POUTLINETEXTMETRICA', 'PROPENUMPROCW', 'tagWNDCLASSEXA',
#           'PFOCUS_EVENT_RECORD', 'POUTLINETEXTMETRICW',
#           'QUOTA_LIMITS_EX', 'LPSERVICE_FAILURE_ACTIONSW',
#           'EMRSETPALETTEENTRIES', 'LPWINDOWPOS', 'GEOTYPE',
#           'LPCRECT', 'IMAGE_RUNTIME_FUNCTION_ENTRY', 'LPWSAQUERYSET',
#           '_heapinfo', 'STYLEBUFA', 'DELETEITEMSTRUCT',
#           'WinBuiltinPerfMonitoringUsersSid', 'EXCEPTION_DEBUG_INFO',
#           'LPMENUINFO', 'MYSQL_TYPE_DOUBLE', 'mysql_fetch_fields',
#           'STYLEBUFW', 'EMRSTRETCHBLT', 'PPSFEATURE_CUSTPAPER',
#           'NPPAINTSTRUCT', 'PPATTERN', 'MYSQL_PROTOCOL_SOCKET',
#           'COR_VTABLE_32BIT', 'IMAGE_AUX_SYMBOL', 'PEMRELLIPSE',
#           'ENHMETARECORD', 'EMRPOLYBEZIER16',
#           'N12_devicemodeA4DOLLAR_584DOLLAR_60E',
#           'PTAPE_SET_MEDIA_PARAMETERS', 'NPDEBUGHOOKINFO',
#           '_OSVERSIONINFOA', 'PTEXTMETRICW', 'PEMRDELETECOLORSPACE',
#           'SHUTDOWN_WAIT_UPDATES', 'EMRMODIFYWORLDTRANSFORM',
#           'WinAccountRasAndIasServersSid', 'tagCOMPAREITEMSTRUCT',
#           'ACL_REVISION_INFORMATION', 'mysql_hex_string',
#           'PTEXTMETRICA', 'EMRCREATECOLORSPACEW', 'ALTTABINFO',
#           'value_entW', '_currencyfmtW', 'tagEMRSETPALETTEENTRIES',
#           'PENHMETAHEADER', 'N12_devicemodeW4DOLLAR_624DOLLAR_64E',
#           '_TRIVERTEX', 'WSAPROTOCOLCHAIN', 'NETRESOURCEW',
#           'PACL_SIZE_INFORMATION', 'GetFileExInfoStandard',
#           'FONTENUMPROC', 'tagEMRGRADIENTFILL', 'mysql_row_seek',
#           'LPRECONVERTSTRING', 'tagDRAWTEXTPARAMS', 'CONTEXT',
#           'PIO_COUNTERS', 'PTOKEN_SOURCE', 'COM_TIME',
#           'WSAPROTOCOL_INFOA', 'mysql_stmt_param_count', 'ulonglong',
#           'CRITICAL_SECTION_DEBUG', 'HIGHCONTRAST',
#           'PIMAGE_DOS_HEADER', 'PEMRSETPOLYFILLMODE',
#           'PEMRSETPIXELV', 'EMRGLSBOUNDEDRECORD',
#           'PEMRSETWINDOWORGEX', 'WSAPROTOCOL_INFOW', 'COM_CONNECT',
#           'PFD_SET', 'MYSQL_OPTION_MULTI_STATEMENTS_OFF', 'DEVMODEW',
#           'PEMRDELETEOBJECT', '_off_t', 'PEMRRESTOREDC',
#           'ACCESS_ALLOWED_OBJECT_ACE', 'INT_PTR',
#           'IMAGE_ROM_OPTIONAL_HEADER', 'INT16', 'FSHORT',
#           'LPLOGFONT', 'NETRESOURCEA', 'tagMENUGETOBJECTINFO',
#           'MULTIKEYHELPW', 'PMULTIKEYHELPA',
#           'ENUM_SERVICE_STATUS_PROCESSW', 'TapeDriveSnappedTape',
#           'PCHARSETINFO', 'TOKEN_INFORMATION_CLASS',
#           'PEMRGRADIENTFILL', '_SYSTEM_AUDIT_CALLBACK_OBJECT_ACE',
#           'EXECUTION_STATE', 'IMAGE_THUNK_DATA32',
#           'ACCESS_DENIED_CALLBACK_OBJECT_ACE', 'PMULTIKEYHELPW',
#           'ENUM_SERVICE_STATUS_PROCESSA', 'uint',
#           'WinCreatorGroupSid', 'STYLEBUF', 'PTIME_ZONE_INFORMATION',
#           'LPWIN32_FIND_DATAW', 'TIME_ZONE_INFORMATION',
#           'NPCWPSTRUCT', 'tagHELPWININFOA',
#           'LPEVENTLOG_FULL_INFORMATION', 'SecurityImpersonation',
#           'CHAR', 'PROPENUMPROC', 'WinCreatorOwnerServerSid',
#           'LPWIN32_FIND_DATAA', 'RNRSERVICE_REGISTER',
#           'MSGBOXCALLBACK', 'ICONMETRICSA', 'mysql_field_count',
#           'tagHELPWININFOW', 'SID_IDENTIFIER_AUTHORITY', 'DOCINFOA',
#           'tagLOGFONTA', 'PUINT64', 'LPEVENTMSGMSG', 'LPLOGBRUSH32',
#           'NPLOGPEN', 'tagLOGFONTW', 'PEMRTEXT', '_DISCDLGSTRUCTA',
#           'PEXCEPTION_RECORD32', 'LPNONCLIENTMETRICSA',
#           'PSECURITY_INFORMATION', 'LPNONCLIENTMETRICSW',
#           'GEO_TIMEZONES', '_DISCDLGSTRUCTW', 'OSVERSIONINFOEX',
#           'ICONMETRICSW', 'DIBSECTION', 'COMPARE_STRING',
#           '_NETINFOSTRUCT', 'LPQOS_SD_MODE', 'PEMRSETICMPROFILE',
#           'LPWNDCLASSEX', 'HIMCC', 'EDITWORDBREAKPROC',
#           'ReplacesCorHdrNumericDefines',
#           'SHUTDOWN_WAIT_ALL_BUFFERS', 'PRECTL', 'NPSTR',
#           'LPSERVENT', 'DRAWPATRECT', 'FindExInfoStandard',
#           'PowerActionNone', 'IMAGE_DOS_HEADER', 'LOGBRUSH32',
#           'LPMEASUREITEMSTRUCT', '_FILE_NOTIFY_INFORMATION',
#           'LPCOMPAREITEMSTRUCT', 'EMREXTFLOODFILL', 'tagACCEL',
#           '_WSAVersion', 'LPEXCEPTION_RECORD', 'EMRPOLYDRAW',
#           'PIMAGE_ARCHITECTURE_HEADER', 'HPALETTE__', 'LPCOLORREF',
#           'LPCOMPOSITIONFORM', 'PASSEMBLY_FILE_DETAILED_INFORMATION',
#           'IMAGE_ARCHITECTURE_ENTRY', 'WinBuiltinReplicatorSid',
#           'MONITORINFOEXW', 'WNDCLASSA', 'ENHMFENUMPROC',
#           'PLOGPALETTE', 'LPTRACKMOUSEEVENT', 'PEMRARCTO',
#           'MONITORINFOEXA', 'MENU_EVENT_RECORD', 'LPCDLGTEMPLATEW',
#           'MDICREATESTRUCTW', 'PEMRSETBRUSHORGEX',
#           '_IMAGE_AUX_SYMBOL', '_DEVICE_POWER_STATE',
#           'PIMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY', 'PAINTSTRUCT',
#           'EMRPLGBLT', 'LPCDLGTEMPLATEA', 'PWSAECOMPARATOR',
#           'PFILE_SEGMENT_ELEMENT', 'LIST_ENTRY32',
#           'LPENUM_SERVICE_STATUS_PROCESS', '_AFPROTOCOLS',
#           '_WSACOMPLETIONTYPE', 'LPDLGITEMTEMPLATE',
#           'EMRPOLYLINETO16', 'FLOAT', 'LPMENUITEMINFOA',
#           'TOKEN_TYPE', 'LPACCESSTIMEOUT', 'PWORD',
#           'PMEMORY_BASIC_INFORMATION', 'PEMRBEGINPATH',
#           'LPUNLOAD_DLL_DEBUG_INFO', 'PMESSAGE_RESOURCE_DATA',
#           'LPEXTLOGFONT', 'LPENUMLOGFONTEX', 'mysql_list_fields',
#           'MEM_ROOT', 'GEO_OFFICIALLANGUAGES', 'WinNtAuthoritySid',
#           'PEMRNAMEDESCAPE', 'tagLOCALESIGNATURE',
#           'NEWTEXTMETRICEXW', 'PEMRGLSBOUNDEDRECORD',
#           'PCACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION',
#           '_COMMCONFIG', 'tagWNDCLASSEXW', 'PEMRPLGBLT', 'CHAR_INFO',
#           '_UNLOAD_DLL_DEBUG_INFO', 'WSAData', 'DISPLAY_DEVICEA',
#           'CREATE_PROCESS_DEBUG_INFO', 'HBRUSH__', 'PEMRCREATEPEN',
#           'MOUSEKEYS', 'PUCHAR',
#           'N20IMPORT_OBJECT_HEADER4DOLLAR_46E',
#           'LPSERVICE_FAILURE_ACTIONSA', 'PIMAGE_THUNK_DATA64',
#           'LPDEBUGHOOKINFO', '_PSFEATURE_CUSTPAPER', 'PSTYLEBUF',
#           'EMRRESIZEPALETTE', 'PIMEMENUITEMINFO',
#           'mysql_warning_count', 'PEMRSETTEXTCOLOR',
#           'CONSOLE_FONT_INFO', 'REMOTE_NAME_INFO', 'PPOINTS',
#           'SystemLoad', 'COM_STMT_FETCH', 'PMETAHEADER',
#           'PSYSTEM_ALARM_OBJECT_ACE', 'MODEMDEVCAPS',
#           'MYSQL_OPT_NAMED_PIPE', 'COM_SHUTDOWN', 'tagMETARECORD',
#           'COR_VERSION_MINOR', 'DRAWTEXTPARAMS', 'PPOINTL',
#           'NEWTEXTMETRICEXA', 'MYSQL_OPT_COMPRESS', 'LPCUTSTR',
#           'LPMULTIKEYHELPW', 'PFIBER_START_ROUTINE',
#           'WSASERVICECLASSINFOW', 'mysql_affected_rows',
#           'WSASERVICECLASSINFOA', 'mysql_thread_safe',
#           'PEMRSETCOLORSPACE', 'LPMULTIKEYHELPA', 'NPDEVMODE',
#           '_TOKEN_AUDIT_POLICY_ELEMENT', 'PISID', 'PUINT',
#           'PROCESS_INFORMATION', 'HIMCC__', 'WNDCLASSEX',
#           'BITMAPFILEHEADER', 'PHARDWAREHOOKSTRUCT',
#           'LPCLIENTCREATESTRUCT', 'TAPE_GET_DRIVE_PARAMETERS',
#           'COMMCONFIG', 'COM_REGISTER_SLAVE',
#           'PSE_IMPERSONATION_STATE', 'LPHANDLER_FUNCTION',
#           'IMAGE_OPTIONAL_HEADER32', 'LPREGISTERWORD',
#           'SHUTDOWN_DEFAULT', 'ushort', 'PEMRSCALEVIEWPORTEXTEX',
#           'PQUOTA_LIMITS_EX', 'tagEMRSETCOLORSPACE',
#           'tagEMRPOLYDRAW', 'OUTLINETEXTMETRICW',
#           'TapeDriveScsiConnectionError', 'PWSAQUERYSET',
#           'tagPANOSE', 'OUTLINETEXTMETRICA', 'PDROPSTRUCT',
#           'SHUTDOWN_WAIT_TRANSACTIONS', 'mysql_set_character_set',
#           'WinBuiltinAdministratorsSid', 'PUWSTR', 'EMRARC',
#           'POINTFLOAT', 'TokenPrivileges', 'LPWSAVERSION',
#           'tagCIEXYZ', 'IMAGE_RESOURCE_DIR_STRING_U', 'MYSQL_DATA',
#           'EMRFORMAT', 'tagCOLORADJUSTMENT', 'mysql_more_results',
#           'PBITMAP', 'MYSQL_TIMESTAMP_TIME', 'LPCPINFOEX',
#           'PIMAGE_LOAD_CONFIG_DIRECTORY32', 'PACKEDEVENTINFO',
#           '_TOKEN_TYPE', 'TAPE_WRITE_MARKS', '_GENERIC_MAPPING',
#           'PPVALUE', 'DRAWSTATEPROC', 'NPWNDCLASS', 'LPICONMETRICS',
#           'USN', 'MEASUREITEMSTRUCT', '_EVENTLOGRECORD', 'DWORD32',
#           'tagHW_PROFILE_INFOW', 'tagMINMAXINFO',
#           'PEMRSELECTPALETTE', 'hostent', 'PFNRECONCILEPROFILEW',
#           'MYSQL_TYPE_DATETIME', 'tagHW_PROFILE_INFOA',
#           '_QualityOfService', 'PFNRECONCILEPROFILEA',
#           'IMPORT_OBJECT_ORDINAL', 'PGRADIENT_TRIANGLE', 'UINT64',
#           'POLYTEXTA', 'PSECURITY_DESCRIPTOR_CONTROL',
#           'LPMDICREATESTRUCTA', 'EMREOF', 'EMRSETCOLORSPACE',
#           'MYSQL_SET_CHARSET_NAME', 'LPDWORD', 'POLYTEXTW',
#           'PDELETEITEMSTRUCT', 'MYSQL_OPT_GUESS_CONNECTION',
#           'WinRestrictedCodeSid', 'LPMULTIKEYHELP',
#           'LPMDICREATESTRUCTW', 'mysql_set_local_infile_default',
#           'PTCH', 'MESSAGE_RESOURCE_DATA',
#           'N31_IMAGE_RESOURCE_DIRECTORY_ENTRY4DOLLAR_414DOLLAR_42E',
#           'LPFNDEVMODE', 'SidTypeDeletedAccount', 'ACE_HEADER',
#           'LPFMTID', 'MYSQL_READ_DEFAULT_GROUP',
#           'mysql_fetch_field_direct', 'tagKERNINGPAIR', 'LPPELARRAY',
#           'WinBuiltinGuestsSid', 'MEMORYSTATUSEX', 'PDRAWPATRECT',
#           'MYSQL_OPT_USE_RESULT', 'PWINDOW_BUFFER_SIZE_RECORD',
#           'MYSQL_TYPE_YEAR', 'mysql_errno', 'PEMREXTESCAPE',
#           'MYSQL_PROTOCOL_PIPE', 'tagEMRGLSRECORD',
#           'EMRSETARCDIRECTION', 'NPNEWTEXTMETRICW', 'list_delete',
#           'st_mysql_manager', 'mysql_character_set_name', 'NET',
#           'PLOCALESIGNATURE', 'NPNEWTEXTMETRICA', 'COLOR16',
#           '_IMAGE_THUNK_DATA32',
#           'PACCESS_DENIED_CALLBACK_OBJECT_ACE', 'SYSTEM_POWER_STATE',
#           'SECURITY_DESCRIPTOR_RELATIVE', 'WINDOWPOS',
#           'PENHMETARECORD', 'PUINT8', '_MEMORY_BASIC_INFORMATION64',
#           'FONTSIGNATURE', 'ACCEL',
#           'PCACTIVATION_CONTEXT_QUERY_INDEX', 'SC_ENUM_PROCESS_INFO',
#           'CWPSTRUCT', 'FLOAT128',
#           '_ACCESS_DENIED_CALLBACK_OBJECT_ACE', 'CURSORINFO',
#           'st_list', 'PDLGITEMTEMPLATEA', 'PDWORD',
#           '_RTL_CRITICAL_SECTION_DEBUG', 'LPWSABUF', 'IO_COUNTERS',
#           'EVENTSFORLOGFILE', 'FLONG', 'tagEMRSETMITERLIMIT',
#           'CBTACTIVATESTRUCT', 'LPCONNECTDLGSTRUCTA', '_DCB',
#           'PWSANSCLASSINFO', 'LPCBT_CREATEWND', '__wfinddata64_t',
#           'LPOUTPUT_DEBUG_STRING_INFO', 'UILANGUAGE_ENUMPROCW',
#           '_SYSTEM_ALARM_CALLBACK_ACE', '_UNIVERSAL_NAME_INFOA',
#           'PWSAQUERYSETW', 'IMAGE_ARCHITECTURE_HEADER',
#           'PPACKEDEVENTINFO', 'NUMBERFMT', 'PWSAQUERYSETA',
#           '_CONSOLE_FONT_INFO', 'MYSQL_FIELD',
#           '_IMAGE_ARCHIVE_MEMBER_HEADER', 'NPTEXTMETRIC',
#           'REG_PROVIDER', 'DROPSTRUCT', 'MYSQL_STMT_INIT_DONE',
#           'TAPE_SET_POSITION', 'NON_PAGED_DEBUG_INFO',
#           'tagSTYLEBUFW', 'WinLogonIdsSid',
#           'SERVICE_FAILURE_ACTIONSA', 'PEXTLOGPEN', 'SOUNDSENTRYW',
#           'LPABCFLOAT', 'SERVICE_FAILURE_ACTIONSW', 'WSABUF',
#           'tagSTYLEBUFA', 'EMRPOLYTEXTOUTW',
#           'COM_STMT_SEND_LONG_DATA', 'PCONTEXT',
#           'mysql_get_client_info', 'LPWNDCLASSEXA', 'PREGISTERWORD',
#           '_EXIT_PROCESS_DEBUG_INFO', 'SLIST_HEADER',
#           'LPWNDCLASSEXW', '_MESSAGE_RESOURCE_BLOCK', 'LPDEVMODE',
#           'FILE_SEGMENT_ELEMENT', 'COR_VTABLE_64BIT',
#           'mysql_ssl_set', 'PCHAR', 'value_entA',
#           'st_mysql_parameters', 'BITMAP',
#           'N13_SLIST_HEADER4DOLLAR_47E', 'TTPOLYGONHEADER',
#           'PPOLYTEXTW', 'LPPROCESS_INFORMATION',
#           'tagEMRCREATEBRUSHINDIRECT', 'tagEMRSETVIEWPORTORGEX',
#           'CANDIDATEFORM', 'PNON_PAGED_DEBUG_INFO', 'LPHKL',
#           'N23_IMAGE_FUNCTION_ENTRY644DOLLAR_45E',
#           'PACTIVATION_CONTEXT_QUERY_INDEX', 'PPOLYTEXTA',
#           'PTHREAD_START_ROUTINE', 'SOUNDSENTRYA',
#           'tagDEBUGHOOKINFO', 'PBOOL', 'PWNDCLASSEXW', 'SYSGEOTYPE',
#           'POSVERSIONINFO', 'tagCBT_CREATEWNDA', 'WinAnonymousSid',
#           'PWNDCLASSEXA', 'PEMRSTROKEPATH', 'INT64',
#           'TapeDriveTimetoClean', 'PDLGITEMTEMPLATE',
#           'LPMONITORINFOEX', 'UILANGUAGE_ENUMPROCA',
#           'TAPE_GET_POSITION', '_IMAGE_RELOCATION', 'linger',
#           'PDEVICE_POWER_STATE', 'LINGER', 'PEMRFILLPATH',
#           'LastWakeTime', '_TOKEN_DEFAULT_DACL', 'PMSGBOXPARAMS',
#           'LPWSAPROTOCOLCHAIN', 'PSMALL_RECT', 'tagWINDOWPLACEMENT',
#           'GEO_NATION', 'TapeDriveProblemNone', 'NSP_NOTIFY_EVENT',
#           'WinNetworkSid', 'PIMAGE_AUX_SYMBOL_TOKEN_DEF',
#           'tagEMRCREATECOLORSPACE', 'SC_ACTION_TYPE',
#           'mysql_get_server_version',
#           'WinBuiltinAccountOperatorsSid', 'COM_END',
#           'LPNEWTEXTMETRIC', 'DLGITEMTEMPLATE',
#           'LPOVERLAPPED_COMPLETION_ROUTINE', 'mysql_stmt_attr_set',
#           'EMRCREATEPEN', 'PWSASERVICECLASSINFOA', 'COM_SLEEP',
#           'PMESSAGE_RESOURCE_BLOCK', 'PULONG_PTR',
#           'NPIMEMENUITEMINFO', 'LPRECTL',
#           'JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION',
#           'LPSYSTEM_POWER_STATUS', 'PSHORT',
#           'TapeDriveReadWriteWarning', 'mysql_data_seek',
#           'LPSC_ACTION', 'PWSASERVICECLASSINFOW',
#           'TokenImpersonation', 'STARTUPINFOA', 'PWINDOWPOS',
#           'LPPALETTEENTRY', 'PEMRSETWINDOWEXTEX', 'STARTUPINFOW',
#           'FPO_DATA', 'COR_VTABLE_FROM_UNMANAGED',
#           'IMAGE_COFF_SYMBOLS_HEADER', 'LPUNIVERSAL_NAME_INFOA',
#           '_IMAGE_VXD_HEADER', 'CALINFO_ENUMPROCEXA',
#           'MOUSEHOOKSTRUCT', '_SID_IDENTIFIER_AUTHORITY', 'LPQOS',
#           'mysql_escape_string', 'CALINFO_ENUMPROCEXW', 'NPSTYLEBUF',
#           'tagEMRSETMAPPERFLAGS', 'WINEVENTPROC',
#           'LPUNIVERSAL_NAME_INFOW', 'AdministratorPowerPolicy',
#           'HACCEL__', 'ActivationContextBasicInformation',
#           '_CM_ERROR_CONTROL_TYPE', 'LPCBT_CREATEWNDW', 'sockaddr',
#           'OSVERSIONINFOEXW', 'LPQUERY_SERVICE_CONFIGA',
#           'tagEMRSETVIEWPORTEXTEX', 'HUMPD__',
#           'LPSERVICE_TABLE_ENTRYA',
#           '_ACCESS_ALLOWED_CALLBACK_OBJECT_ACE', 'DemandLoad',
#           'LPQUERY_SERVICE_LOCK_STATUSW', 'OSVERSIONINFOEXA',
#           'LPFD_SET', 'LPCBT_CREATEWNDA',
#           'LPQUERY_SERVICE_LOCK_STATUSA', 'N7in_addr4DOLLAR_75E',
#           '_SYSTEM_POWER_STATE', 'PowerActionShutdownReset',
#           'tagCOMPOSITIONFORM', 'PEMRFORMAT', 'MYSQL_PARAMETERS',
#           'tagEMRSELECTPALETTE', 'EMRPIE', 'QOS_OBJECT_HDR',
#           'EMRPOLYLINETO', 'PowerActionReserved',
#           '_MENU_EVENT_RECORD', 'MYSQL_PROTOCOL_TCP', 'PSERVENT',
#           'LPLOCALESIGNATURE', 'u_int64', '_EXCEPTION_RECORD',
#           'st_mysql_bind', 'mysql_field_tell', 'PVALUE',
#           'LPGRADIENT_RECT', 'LPSERVICE_STATUS_PROCESS',
#           '_JOBOBJECT_EXTENDED_LIMIT_INFORMATION',
#           'mysql_stmt_close', 'DEVMODE',
#           'IMAGE_RESOURCE_DIRECTORY_STRING', 'GCP_RESULTS',
#           'mysql_stmt_result_metadata', 'mysql_stmt_sqlstate',
#           'EMRSETVIEWPORTORGEX', 'UDF_ARGS', 'tagEMRPOLYLINE',
#           'LPTITLEBARINFO', 'LPSTYLEBUFA', 'SC_ACTION',
#           'LPNUMBERFMTW', 'tagMONITORINFOEXW', 'WinSelfSid',
#           'ENUMRESLANGPROCW', 'PLOGFONTA', 'NSP_NOTIFY_PORT',
#           'NPBITMAP', 'tagMONITORINFOEXA', 'PFLOAT',
#           'ENUMRESLANGPROCA', 'PLOGFONTW', 'LPALTTABINFO']
#
