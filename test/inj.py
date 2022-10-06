import os
import inject
dlls=["/../Python/msvcr100.dll",
   "/../Python/msvcp100.dll",
   "/../Qt/PySide/QtCore4.dll",
    "/../Qt/PySide/QtNetwork4.dll",
   "/bin/vnragent.dll"]
def inject_vnragent(**kwargs):
    """
    @param* pid  ulong
    @param* handle  HANDLE
    @return  bool
    """
    print("enter")
    ret = True
    for dllpath in dlls:
      #dllpath = os.path.abspath(dllpath)
      dllpath = os.path.abspath(dllpath)
      assert os.path.exists(dllpath), "needed dll does not exist: %s" % dllpath
      ret = inject.injectdll(dllpath, **kwargs) and ret
    print("leave: ret = %s" % ret)
    return ret

def attachProcess(self, pid): # -> bool
      
      ok = inject_vnragent(pid=pid)
       
      if ok:
        injectedPid = pid
        injectTimer.start()
      return ok