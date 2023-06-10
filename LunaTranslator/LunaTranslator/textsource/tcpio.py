 
import time  
from textsource.textsourcebase import basetext
from myutils.config import globalconfig,_TR
import winsharedutils,ctypes,win32utils,os
import socket,threading
import ctypes
from queue import Queue
from traceback import print_exc

class tcpio(basetext):
    def __init__(self,textgetmethod) -> None: 
        
        self.newline=Queue()  
        self.runonce_line=''
        
        super(tcpio,self).__init__(textgetmethod,'0','0_tcpio')

        threading.Thread(target= self._run).start()
    # def _run(self):
    #     self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.socket.bind(('',globalconfig['tcp_port']))
    #     self.socket.listen(10)
        
    #     while not self.ending:
    #         conn, addr =self.socket.accept()
             
    #         # 关闭连接
    #         while True:
    #             try:
    #                 data = conn.recv(4)
    #                 l=ctypes.c_int.from_buffer_copy(data) 
    #                 get=conn.recv(l.value).decode('utf-16-le',errors='ignore')
    #                 self.runonce_line=get
    #                 self.newline.put(get)
    #             except:
    #                 print_exc()
    #                 break
    def _run(self):
         
        while not self.ending: 
            sock=socket.socket()
            try:
                sock.connect((globalconfig['tcp_ip_as_client'],globalconfig['tcp_port_as_client']))
            except ConnectionRefusedError:
                self.newline.put('<msg_1>'+_TR('连接失败'))
                continue
           
            while True:
                try:
                    data = sock.recv(4)
                    l=ctypes.c_int.from_buffer_copy(data) 
                    get=sock.recv(l.value).decode('utf8',errors='ignore')
                    self.runonce_line=get
                    self.newline.put(get)
                except:
                    print_exc()
                    break
    def gettextthread(self ):
                 
            return self.newline.get()
    def runonce(self): 
        self.textgetmethod(self.runonce_line,False)