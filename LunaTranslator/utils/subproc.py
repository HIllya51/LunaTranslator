import subprocess,os,time
from traceback import print_exc
import multiprocessing,threading
from utils.getpidlist import pid_running
allsubprocess=[] 
def subproc(cmd,cwd=None,stdin=None,encoding=None, stdout=None,keep=False): 
    st=subprocess.STARTUPINFO()
    st.dwFlags=subprocess.STARTF_USESHOWWINDOW
    st.wShowWindow=subprocess.SW_HIDE
    try:
        ss=subprocess.Popen(cmd,cwd=cwd,stdin=stdin, stdout=stdout,  startupinfo=st)
         
    except:
        print_exc()
        ss=None
    if keep:
            allsubprocess.append(ss) 
    return ss
def __wrap(pid,target,args):
            def __processrunningcheck(pid ):
                while True:
                    if pid_running(pid)==False:
                        os._exit(0) 
                    time.sleep(0.1)
            threading.Thread(target=__processrunningcheck,args=(pid,)).start()
            target(*args)
def mutiproc(target,args): 
    try:
        pid=os.getpid()
        

        ss=multiprocessing.Process(target=__wrap,args=(pid,target,args),daemon=True)
        #ss=multiprocessing.Process(target=target,args=args,daemon=True)
        #allsubprocess.append(ss)
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
    