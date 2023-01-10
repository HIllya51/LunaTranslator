import subprocess,time
import threading
from PyQt5.QtCore import QProcess,QByteArray
 
class u16lesubprocess():
    def __init__(self,command) -> None:
        self.cache=[]
        
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
            self.cache.append(_)
            
    def readokmonitor(self):
        while self.process:
            
            l1=len(self.cache) 
            time.sleep(0.001)
            l2=len(self.cache)
            if l1==l2 and l1:  
                if self.readyread is None:
                    continue
                self.readyread(''.join(self.cache)) 
                    
                self.cache.clear()
        
    def writer(self,xx):
        self.process.stdin.write(xx )
        self.process.stdin.flush()
    def kill(self):
        if self.process:
            self.process.kill() 
        self.process=None 