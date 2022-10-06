import win32api,win32con,win32security
INJECT_TIMEOUT=3000
import skwinapi
def injectdll(dllpath, pid=0, handle=None, timeout=INJECT_TIMEOUT):
    """Either pid or the process handle should be specified
    @param  dllpath  unicode ABSOLUTE path to dll
    @param  pid  LONG
    @param  handle  HANDLE
    @param  timeout  int  msecs
    @return  bool
    """
    #if not dllpath or not os.path.exists(dllpath):
    #  print("error: dll does not exist")
    #  return False
    print("enter: pid = %s" % pid)
    try: dllpath = dllpath.decode('utf8')
    except UnicodeDecodeError:
      print("exit: error: failed to decode dll path to utf8")
      return False
    LOADLIBRARYW = getModuleFunctionAddress('LoadLibraryW', 'kernel32.dll')
    if not LOADLIBRARYW:
      print("exit error: cannot find LoadLibraryW from kernel32")
      return False
    data = dllpath
    dataSize = len(dllpath) * 2 + 2 # L'\0'
    ok = injectfunc1(LOADLIBRARYW, data, dataSize, pid=pid, handle=handle, timeout=timeout)
    print("exit: ret = ok")
    return ok

def getModuleFunctionAddress(func, module=None):
    """
    @param  func  str
    @param  module  str
    @return  int  address
    """
    return win32api.GetProcAddress(
        win32api.GetModuleHandle(module),
        func)

SE_DEBUG_PRIVILEGE = 'SeDebugPrivilege'
PROCESS_INJECT_ACCESS = (
    win32con.PROCESS_CREATE_THREAD |
    win32con.PROCESS_QUERY_INFORMATION |
    win32con.PROCESS_VM_OPERATION |
    win32con.PROCESS_VM_WRITE |
    win32con.PROCESS_VM_READ)
def injectfunc1(addr, arg, argsize, pid=0, handle=None, timeout=INJECT_TIMEOUT):
    """Inject function with 1 argument
    Either pid or the process handle should be specified
    @param  addr  LONG  function memory address
    @param  arg  LPVOID
    @param  argsize  int
    @param  pid  LONG
    @param  handle  HANDLE
    @param  timeout  int  msecs
    @return  bool
    """
    print("enter: pid = "+str( pid))
    isLocalHandle = False # bool
    if not handle and pid:
      isLocalHandle = True
      try:
        handle = win32api.OpenProcess(PROCESS_INJECT_ACCESS, 0, pid)
        if not handle:
          with SkProcessElevator(SE_DEBUG_PRIVILEGE) as priv:
            if priv.isElevated():
              handle = win32api.OpenProcess(PROCESS_INJECT_ACCESS, 0, pid)
      except Exception as e:
        print("windows error:", e)
    if not handle:
      print("exit: error: failed to get process handle")
      return False

    ret = False
    hProcess = handle
    try:
      data = arg
      dataSize = argsize

      # Reserved & commit
      # http://msdn.microsoft.com/en-us/library/windows/desktop/aa366803%28v=vs.85%29.aspx
      # http://msdn.microsoft.com/en-us/library/ms810627.aspx
      remoteData = skwinapi.VirtualAllocEx(
          hProcess, # process
          None,  # __in_opt address
          dataSize,  # data size
          win32con.MEM_RESERVE|win32con.MEM_COMMIT,
          win32con.PAGE_READWRITE)
      if remoteData:
        if skwinapi.WriteProcessMemory(hProcess, remoteData, data, dataSize, None):
          hThread = skwinapi.CreateRemoteThread(
              hProcess,
              None, 0,
              skwinapi.LPTHREAD_START_ROUTINE(addr),
              remoteData,
              0, None)
          if hThread:
            skwinapi.WaitForSingleObject(hThread, timeout)
            win32api.CloseHandle(hThread)
            ret = True
        skwinapi.VirtualFreeEx(hProcess, remoteData, dataSize, win32con.MEM_RELEASE)
    except Exception as e:
      print("windows error:", e)
    if isLocalHandle: # only close the handle if I create it
      try: win32api.CloseHandle(hProcess)
      except Exception as e: print("windows error:", e)
    print("exit: ret = ok")
    return ret

class _SkProcessElevator: pass
class SkProcessElevator:
    def __init__(self, priv):
      """
      @param  priv  unicode or [unicode] or None
      """
      d = self.__d = _SkProcessElevator()

      if type(priv) in (str, bytes):
        priv = [priv]

      d.token = None    # process token
      try:
        d.privileges = [(  # current or previous privileges
          win32security.LookupPrivilegeValue('', p),
          win32con.SE_PRIVILEGE_ENABLED,
        ) for p in priv] if priv else [] # [] not None
      except Exception as  e: # pywintypes.error
        print(e)
        d.privileges = None

    def __enter__(self):
      d = self.__d
      if not d.privileges:
        print("failed to elevate privilege. This is might be a Windows XP machine")
        return

      # See: http://msdn.microsoft.com/ja-jp/library/windows/desktop/ms724944%28v=vs.85%29.aspx
      # See: http://nullege.com/codes/search/win32security.AdjustTokenPrivileges
      # See: http://www.oschina.net/code/explore/chromium.r67069/third_party/python_24/Lib/site-packages/win32/Demos/security/setkernelobjectsecurity.py

      #pid = win32api.GetCurrentProcessId()
      #ph = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)

      ph =  win32api.GetCurrentProcess()
      #d.token = win32security.OpenProcessToken(ph, win32con.TOKEN_ALL_ACCESS)
      d.token = win32security.OpenProcessToken(ph,
          win32con.TOKEN_ADJUST_PRIVILEGES|win32con.TOKEN_QUERY)
      d.privileges = win32security.AdjustTokenPrivileges(d.token, 0, d.privileges)

      if win32api.GetLastError():
        print("failed to elevate process privilege")
      else:
        print("process privileges elevated")
      return self

    def __exit__(self, *err):
      d = self.__d
      if d.token:
        if d.privileges is not None:
          win32security.AdjustTokenPrivileges(d.token, 0, d.privileges)
        try: win32api.CloseHandle(d.token)
        except Exception as e: print("windows error:", e)
        d.token = None

    def isElevated(self):
      """
      @return  bool  if contain token
      """
      return bool(self.__d.token)
