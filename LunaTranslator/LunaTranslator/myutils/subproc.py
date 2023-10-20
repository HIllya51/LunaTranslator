
import time,threading
from traceback import print_exc
import subprocess
allsubprocess2={}
 
def subproc_w(cmd,cwd=None ,needstdio=False ,name=None,encoding='utf8',run=False):
     
    _pipe=subprocess.PIPE if needstdio else None
    
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow=subprocess.SW_HIDE
    if name and  name in allsubprocess2:
        try:
            allsubprocess2[name].kill()
        except:
            print_exc()
    try:
        if run:
            _f=subprocess.run
        else:
            _f=subprocess.Popen

        if needstdio:
            ss=_f(cmd,cwd=cwd,stdin=_pipe,stdout=_pipe,stderr=_pipe,startupinfo=startupinfo,encoding=encoding)
        else:
            ss=_f(cmd,cwd=cwd,stdin=_pipe,stdout=_pipe,stderr=_pipe,startupinfo=startupinfo)
        
        if name:
            allsubprocess2[name]=ss
    
        return ss
    except:
        print_exc()
        return None
def endsubprocs():
    for _ in allsubprocess2:
        try:
            allsubprocess2[_].kill()
        except:
            pass

 