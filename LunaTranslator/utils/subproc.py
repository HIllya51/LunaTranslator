import subprocess
st=subprocess.STARTUPINFO()
st.dwFlags=subprocess.STARTF_USESHOWWINDOW
st.wShowWindow=subprocess.SW_HIDE
allsubprocess=[]
def subproc(cmd,cwd=None,stdin=None, stdout=None): 
    ss=subprocess.Popen(cmd,cwd=cwd,stdin=stdin, stdout=stdout,  startupinfo=st)
    allsubprocess.append(ss) 
    return ss

def endsubprocs():
    for sub in allsubprocess:
        try:
            sub.kill()
        except:
            pass