
from threading import Thread

import win32pipe, win32file

from multiprocessing import Queue

from textsource.textsourcebase import basetext
class namepipe(basetext):
    handle = win32pipe.CreateNamedPipe(
                                r'\\.\Pipe\newsentence',
                                win32pipe.PIPE_ACCESS_DUPLEX,
                                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                                1, 65536, 65536,
                                0,
                                None)
    def __init__(self,textgetmethod)  : 
        self.typename='textractor_pipe'
        self.newline=Queue() 
        self.ending=False 
        
        win32pipe.ConnectNamedPipe(self.handle, None)
        self.tryconnectt=Thread(target=self.tryconnect) 
        self.tryconnectt.start()
        super( ).__init__(textgetmethod) 
        
    def tryconnect(self):
        while True:
            if self.ending:
                break
            
            data = win32file.ReadFile(self.handle, 65535, None)
                
            paste_str=str(data[1],encoding='utf-8' )[:-1] 
            self.newline.put(paste_str) 
    def gettextthread(self ):
         
            paste_str=self.newline.get()
            self.textgetmethod(paste_str)
    def runonce(self):
        if self.newline.empty():
            return
        while self.newline.empty()==False:
            paste_str=self.newline.get()
        self.textgetmethod(paste_str)
    def end(self):
         
        
        self.ending=True
        win32pipe.DisconnectNamedPipe(self.handle) 