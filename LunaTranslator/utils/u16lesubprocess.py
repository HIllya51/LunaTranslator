import subprocess,time
import threading
from PyQt5.QtCore import QProcess,QByteArray
 
class u16lesubprocess():
    def __init__(self,command) -> None:
        self.cache=bytearray()
        
        st=subprocess.STARTUPINFO()
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.SW_HIDE
        self.process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE, startupinfo=st)
        threading.Thread(target=self.cacheread).start()
        threading.Thread(target=self.readokmonitor).start()
        self.isstart=True
        self.readyread=None
    def cacheread(self):
        while self.process:
            _=self.process.stdout.readline()
            if self.isstart:
                self.cache+=bytearray(_ )
            else:
                self.cache+=bytearray(_[1:] ) 
            
            self.cache+=bytearray([0])
            self.isstart=False
    def readokmonitor(self):
        while self.process:
            
            l1=len(self.cache) 
            time.sleep(0.001)
            l2=len(self.cache)
            if l1==l2 and l1:
                if self.readyread:
                    
                    #print(self.cache)
                    self.readyread((self.cache).decode('utf-16-le',errors='ignore')) 
                    
                self.cache.clear()
        
    def writer(self,xx):
        self.process.stdin.write(xx.encode('utf-16-le'))
        self.process.stdin.flush()
    def kill(self):
        self.process.kill()
        self.process=None 