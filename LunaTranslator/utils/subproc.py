import subprocess
import multiprocessing
st=subprocess.STARTUPINFO()
st.dwFlags=subprocess.STARTF_USESHOWWINDOW
st.wShowWindow=subprocess.SW_HIDE
allsubprocess=[]
allsubprocessmap={}
def subproc(cmd,cwd=None,stdin=None,encoding=None, stdout=None,keep=False,key=None): 
    try:
        ss=subprocess.Popen(cmd,cwd=cwd,stdin=stdin, stdout=stdout,  startupinfo=st)
    except:
        ss=None
    if keep:
        if key:
            try:
                allsubprocessmap[key].kill()
            except:
                pass
            allsubprocessmap[key]=ss
        else:
            allsubprocess.append(ss) 
    return ss
 
def mutiproc(target,args): 
    try:
        ss=multiprocessing.Process(target=target,args=args)
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
    for sub in allsubprocessmap:
        try:
            allsubprocessmap[sub].kill()
        except:
            pass