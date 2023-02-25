import subprocess,time
import threading
from traceback import print_exc

class u16lesubprocess():
    def __init__(self,command) -> None:
        self.cache=[]
        self.cachelock=threading.Lock()
        st=subprocess.STARTUPINFO()
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.SW_HIDE
        self.process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE, startupinfo=st,encoding='utf-16-le',errors='ignore')
        
        self.isstart=True
        self.readyread=None
        threading.Thread(target=self.cacheread).start()
        threading.Thread(target=self.readokmonitor).start()
    def cacheread(self):
        while self.process:
            _=self.process.stdout.readline() 
            self.cachelock.acquire()
            self.cache.append(_)
            self.cachelock.release()
    def readokmonitor(self):
        while self.process:
            self.cachelock.acquire()
            l1=len(self.cache) 
            self.cachelock.release()
            time.sleep(0.001)
            self.cachelock.acquire()
            l2=len(self.cache)
            
            if l1==l2 and l1:  
                if self.readyread is None:
                    continue
                try:
                    self.readyread(''.join(self.cache)) 
                except:
                    print_exc()
                    
                self.cache.clear()
            self.cachelock.release()
    def writer(self,xx):
        self.process.stdin.write(xx )
        self.process.stdin.flush()
    def kill(self):
        if self.process:
            self.process.kill() 
        self.process=None 