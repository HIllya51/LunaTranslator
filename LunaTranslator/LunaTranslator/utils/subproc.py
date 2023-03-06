import subprocess
from traceback import print_exc
import sys
sys.path.append('../')
import threading,win32utils,win32con
from ctypes import sizeof
allsubprocess=[] 
allsubprocess2={}
class Pipe:
    def __init__(self,pipe) -> None:
        self.pipe=pipe
        self.buf=b''
    def read_(self):
        print("beforeread")
        print(self.pipe)
        x=win32utils.ReadFile(self.pipe,63335,None)[1]
        print("read",x)
        self.buf+=x
    def read(self):
        print(self.pipe)
        import win32file
        x=win32file.ReadFile(self.pipe,63335,None)[1]
        print(1,x)
        return x
class Process:
    def __init__(self,process,hstdin,hstdout) -> None:
        self.pid=process.dwProcessId
        self.hProcess=process.hProcess
        self.stdout=(hstdout)
        self.stdin=(hstdin)
    def kill(self):
        win32utils.TerminateProcess(self.hProcess, 0)
def Popen(cmd,cwd=None,SW_HIDE=0):
    STARTF_USESHOWWINDOW=1
    saAttr =win32utils.SECURITY_ATTRIBUTESStruct()
            
    saAttr.nLength = sizeof(win32utils.SECURITY_ATTRIBUTESStruct); 
    saAttr.bInheritHandle = True; 
    saAttr.lpSecurityDescriptor = None; 

    hPipeOutputRead ,hPipeOutputWrite =win32utils.CreatePipe(saAttr,0)
    hPipeInputRead ,hPipeInputWrite = win32utils.CreatePipe(saAttr,0)
    
    si=win32utils.STARTUPINFOW()
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW
    si.wShowWindow = SW_HIDE;
    si.hStdInput = hPipeInputRead;
    si.hStdOutput = hPipeOutputWrite;
    si.hStdError = hPipeOutputWrite;
    
    process=win32utils.CreateProcess(None,cmd,None , None , True ,0 , None ,cwd,si)
    hpipestdout=Pipe(hPipeOutputRead)
    #threading.Thread(target=hpipestdout.read_,daemon=True).start()
    # win32utils. CloseHandle(hPipeOutputWrite);
    # win32utils. CloseHandle(hPipeInputRead)
    

    return Process(process,Pipe(hPipeInputWrite),hpipestdout)

def subproc2(cmd,keep=False,name=None, cwd=None): 
    try: 
        ss=Popen(cmd,cwd=cwd)
    except:
        print_exc()
        return
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
        