import subprocess
from traceback import print_exc
allsubprocess=[] 
allsubprocess2={}

def subproc(cmd,keep=False,name=None, cwd=None,stdin=None,  stdout=None): 
    st=subprocess.STARTUPINFO()
    st.dwFlags=subprocess.STARTF_USESHOWWINDOW
    st.wShowWindow=subprocess.SW_HIDE
    try: 
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
# def __wrap(pid,target,args): 
#             threading.Thread(target=target,args=args).start()  
#             win32utils.WaitForSingleObject(win32utils.OpenProcess(win32con.SYNCHRONIZE,0, pid),win32utils.INFINITE) 
#             os._exit(0)
# def mutiproc(target,args): 
#     try:
#         import multiprocessing
#         pid=os.getpid()
        

#         ss=multiprocessing.Process(target=__wrap,args=(pid,target,args),daemon=True)
#         #ss=multiprocessing.Process(target=target,args=args,daemon=True)
#         #allsubprocess.append(ss)
#         ss.start()
#         return ss
#     except:
#         print_exc()
#         return None
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
        