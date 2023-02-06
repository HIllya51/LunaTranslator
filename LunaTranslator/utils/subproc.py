import subprocess,os,time,win32event,win32api,win32con
from traceback import print_exc
import multiprocessing,threading
from utils.getpidlist import pid_running
allsubprocess=[] 
def subproc(cmd,cwd=None,stdin=None,encoding=None, stdout=None,keep=False,run=False): 
    st=subprocess.STARTUPINFO()
    st.dwFlags=subprocess.STARTF_USESHOWWINDOW
    st.wShowWindow=subprocess.SW_HIDE
    try:
        if run:
            xx=subprocess.run
        else:
            xx=subprocess.Popen
        ss=xx(cmd,cwd=cwd,stdin=stdin, stdout=stdout,  startupinfo=st)
         
    except:
        print_exc()
        ss=None
    if keep:
            allsubprocess.append(ss) 
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
    