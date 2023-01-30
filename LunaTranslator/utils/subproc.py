import subprocess,os
from traceback import print_exc
import multiprocessing

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
 
def mutiproc(target,args): 
    try:
        ss=multiprocessing.Process(target=target,args=args,daemon=True)
        allsubprocess.append(ss)
        return ss
    except:
        return None
def endsubprocs():
    for sub in allsubprocess:
        try:
            sub.kill()
        except:
            pass
    