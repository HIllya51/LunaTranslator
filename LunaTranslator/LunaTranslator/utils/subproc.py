import subprocess,os,time,win32event,win32api,win32con
from traceback import print_exc
import multiprocessing,threading
from utils.getpidlist import pid_running
allsubprocess=[] 
allsubprocess2={}
def subproc(cmd,keep=False,name=None, cwd=None,stdin=None,  stdout=None, encoding=None,  errors='ignore'): 
    st=subprocess.STARTUPINFO()
    st.dwFlags=subprocess.STARTF_USESHOWWINDOW
    st.wShowWindow=subprocess.SW_HIDE
    try: 
        if encoding:
            ss=subprocess.Popen(cmd,cwd=cwd,stdin=stdin, stdout=stdout,  startupinfo=st,encoding=encoding,errors=errors)
        else:
            ss=subprocess.Popen(cmd,cwd=cwd,stdin=stdin, stdout=stdout,  startupinfo=st )
    except:
        print_exc()
        ss=None
    if keep:
            allsubprocess.append(ss) 
    if name:
        if name in allsubprocess2:
            try:
                allsubprocess2[name].kill()
            except:
                pass
        allsubprocess2[name]=ss
    return ss
def __wrap(pid,target,args): 
            threading.Thread(target=target,args=args).start()  
            win32event.WaitForSingleObject(win32api.OpenProcess(win32con.SYNCHRONIZE,0, pid),win32event.INFINITE) 
            os._exit(0)
def mutiproc(target,args): 
    try:
        pid=os.getpid()
        

        ss=multiprocessing.Process(target=__wrap,args=(pid,target,args),daemon=True)
        #ss=multiprocessing.Process(target=target,args=args,daemon=True)
        #allsubprocess.append(ss)
        ss.start()
        return ss
    except:
        print_exc()
        return None
def endsubprocs():
    for sub in allsubprocess:
        try:
            sub.kill()
        except:
            pass
    for _ in allsubprocess2:
        try:
            allsubprocess2[_].kill()
        except:
            pass