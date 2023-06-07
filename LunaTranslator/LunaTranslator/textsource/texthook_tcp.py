 
import time  
from textsource.textsourcebase import basetext
from utils.config import globalconfig
import winsharedutils,ctypes,win32utils,os
import socket,threading
import ctypes
from queue import Queue
from traceback import print_exc
def sendbinarys(conn):
    base=r'.\files\plugins'
    targets=[
        r'\LunaHook\LunaHook32.dll'
    ]
    
    for target in targets:
        with open(base+target,'rb') as ff:
            b=ff.read() 
            conn.sendall(bytes(ctypes.c_uint(len(b)))+b)

class texthook_tcp(basetext):
    def end(self):
        try:
            self.socket.close() 
        except:
            print_exc()
    def __init__(self,textgetmethod) -> None: 
        
        self.newline=Queue()  
        self.runonce_line=''
        
        super(texthook_tcp,self).__init__(textgetmethod,'0','0_texthook_tcp')

        threading.Thread(target= self._run).start()
    def _run(self):
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('',globalconfig['tcp_port']))
        self.socket.listen(10)
        while not self.ending:
            conn, addr =self.socket.accept()
            
            sendbinarys(conn)
            # 关闭连接
            while True:
                try:
                    data = conn.recv(4)
                    l=ctypes.c_int.from_buffer_copy(data) 
                    get=conn.recv(l.value).decode('utf-16-le',errors='ignore')
                    self.runonce_line=get
                    self.newline.put(get)
                except:
                    print_exc()
                    break
    def gettextthread(self ):
                 
            return self.newline.get()
    def runonce(self): 
        self.textgetmethod(self.runonce_line,False)