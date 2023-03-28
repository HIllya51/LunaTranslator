
import time,threading
from traceback import print_exc
import subprocess
allsubprocess2={}
 
def subproc_w(cmd,cwd=None ,needstdio=False,encoding=None ,name=None):
     
    _pipe=subprocess.PIPE if needstdio else None
    errors='ignore' if encoding else None
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    creationflags=subprocess.SW_HIDE
    
    if name and  name in allsubprocess2:
        try:
            allsubprocess2[name].kill()
        except:
            print_exc()
    
    ss=subprocess.Popen(cmd,cwd=cwd,stdin=_pipe,stdout=_pipe,stderr=_pipe,encoding=encoding,creationflags=creationflags,startupinfo=startupinfo,errors=errors)
     
    if name:
        allsubprocess2[name]=ss
    return ss

# import win32utils,win32con,msvcrt,io
# def subproc_w(cmd,cwd=None,wait=False,needstdio=False,encoding=None ,name=None):
         
#     class Handle(int):
#             closed = False 
#             def Detach(self):
#                 if not self.closed:
#                     self.closed = True 
#                     return int(self)
#                 raise ValueError("already closed") 
#             def __del__(self):
#                 if not self.closed:
#                     self.closed = True
#                     win32utils.CloseHandle(self)
#     class __:        
#         def createstdiopipes(self ):
#             hStdInputr, hStdInputw =[Handle(win32utils.DuplicateHandle(Handle(_))) for _ in win32utils.CreatePipe(None, 0) ]
#             hStdOutputr, hStdOutputw = [Handle(win32utils.DuplicateHandle(Handle(_))) for _ in win32utils.CreatePipe(None, 0) ]
#             hStdErrorr, hStdErrorw =  [Handle(win32utils.DuplicateHandle(Handle(_))) for _ in  win32utils.CreatePipe(None, 0) ]
#             return hStdInputr,hStdInputw,hStdOutputr,hStdOutputw,hStdErrorr,hStdErrorw
             
#         def __init__(self,cmd,cwd=None,wait=False,needstdio=False,encoding=None) -> None:
#             info=win32utils.STARTUPINFO()  
#             bufsize=-1
#             errors='ignore'
#             info.dwFlags = win32con.STARTF_USESTDHANDLES | win32con.STARTF_USESHOWWINDOW;
#             info.wShowWindow=win32con.SW_HIDE 
#             if needstdio:
#                 hStdInputr,hStdInputw,hStdOutputr,hStdOutputw,hStdErrorr,hStdErrorw=self.createstdiopipes()
                
#                 hStdInputw = msvcrt.open_osfhandle(hStdInputw.Detach() , 0) 
#                 hStdOutputr = msvcrt.open_osfhandle(hStdOutputr.Detach() , 0)
#                 hStdErrorr = msvcrt.open_osfhandle(hStdErrorr.Detach() , 0)
        
#                 self.stdin = io.open(hStdInputw, 'wb', bufsize)
#                 self.stdout = io.open(hStdOutputr, 'rb', bufsize)
#                 self.stderr = io.open(hStdErrorr, 'rb', bufsize)
#                 if encoding:
#                     self.stdin = io.TextIOWrapper(self.stdin,  encoding=encoding, errors=errors)  
#                     self.stdout = io.TextIOWrapper(self.stdout, encoding=encoding, errors=errors)  
#                     self.stderr = io.TextIOWrapper(self.stderr, encoding=encoding, errors=errors)
                
#                 info.hStdInput = hStdInputr
#                 info.hStdOutput = hStdOutputw 
#                 info.hStdError = hStdErrorw

#             self.handle=win32utils.CreateProcess(None, cmd,  None, None,  True,  win32utils.CREATE_NO_WINDOW, None,  cwd,  info) 
#             if wait:
#                 win32utils.WaitForSingleObject(self.handle.hProcess,win32utils.INFINITE) 
#         def kill(self):
#             win32utils.TerminateProcess(self.handle.hProcess,0)
            
#     if name and  name in allsubprocess2:
#         try:
#             allsubprocess2[name].kill()
#         except:
#             print_exc()
#     ss=__(cmd,cwd,wait,needstdio,encoding) 
#     if name:
#         allsubprocess2[name]=ss
#     return ss
def endsubprocs():
    for _ in allsubprocess2:
        try:
            allsubprocess2[_].kill()
        except:
            pass


class u16lesubprocess():
    def __init__(self,commands) -> None:
        self.caches=[]
        self.cachelocks=[]
        self.processes=[]
        self.writelog=None
        self.isstart=True
        self.readyread=None
        for i in range(len(commands)):
            self.processes.append(subproc_w(commands[i],needstdio=True,encoding='utf-16-le'))
            self.caches.append([])
            self.cachelocks.append(threading.Lock() )
            threading.Thread(target=self.cacheread,args=(i,)).start()
            threading.Thread(target=self.readokmonitor,args=(i,)).start()
    def cacheread(self,i):
        while self.isstart:
            _=self.processes[i].stdout.readline()
            if(len(_)==0):break
            self.cachelocks[i].acquire()
            self.caches[i].append(_[:-1])
            self.cachelocks[i].release()
    def readokmonitor(self,i):
        while self.isstart:
            self.cachelocks[i].acquire()
            l1=len(self.caches[i]) 
            self.cachelocks[i].release()
            time.sleep(0.001)
            self.cachelocks[i].acquire()
            l2=len(self.caches[i])
            
            if l1==l2 and l1 and self.readyread:
                try:
                    #self.readyread(''.join(self.caches[i])) 
                    self.readyread( (self.caches[i])) 
                except:
                    print_exc()
                    
                self.caches[i].clear()
            self.cachelocks[i].release()
    def writer(self,xx,idx=None):
        for i in range(len(self.processes)):
            if idx and idx!=i:continue
            try:
                if self.writelog:
                    self.writelog("Operation: "+xx)
                self.processes[i].stdin.write(xx +'\n')
                self.processes[i].stdin.flush()
            except:
                pass
    def kill(self):
        self.isstart=False 
        for p in self.processes:
            try:
                p.kill()
            except:
                pass
        