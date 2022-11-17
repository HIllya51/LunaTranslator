import subprocess
import multiprocessing
st=subprocess.STARTUPINFO()
st.dwFlags=subprocess.STARTF_USESHOWWINDOW
st.wShowWindow=subprocess.SW_HIDE
allsubprocess=[]
def subproc(cmd,cwd=None,stdin=None,encoding=None, stdout=None,keep=False): 
    ss=subprocess.Popen(cmd,cwd=cwd,stdin=stdin, stdout=stdout,  startupinfo=st)
    if keep:
        allsubprocess.append(ss) 
    return ss
 
def mutiproc(target,args): 
    ss=multiprocessing.Process(target=target,args=args)
    allsubprocess.append(ss)
    return ss
def endsubprocs():
    for sub in allsubprocess:
        try:
            sub.kill()
        except:
            pass