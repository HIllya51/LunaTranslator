import subprocess
from threading import Thread
import win32pipe, win32file 
from  queue  import Queue
import re  
import pywintypes
from textsource.textsourcebase import basetext
class textractor(basetext):
    handle = win32pipe.CreateNamedPipe(
                                "\\\\.\\Pipe\\textractorcommand",
                                win32pipe.PIPE_ACCESS_DUPLEX,
                                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                                1, 65536, 65536,
                                0,
                                None)
    handle2 = win32pipe.CreateNamedPipe(
                                "\\\\.\\Pipe\\textractoroutput",
                                win32pipe.PIPE_ACCESS_DUPLEX,
                                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                                1, 65536, 65536,
                                0,
                                None)
    hookdatacollecter=[]
        
    reverse={}
    selectinghook=None
    selectedhook=None
    
    def tryconnect(self):
        while True:
            if self.ending:
                break
            
            data = win32file.ReadFile(self.handle2, 65535, None)
            
            paste_str=str(data[1],encoding='utf-16' )  
            self.handle_stdout(paste_str) 
    def __init__(self,textgetmethod,hookselectdialog,pid,pname,arch)  : 
        self.newline=Queue() 
        self.ending=False 
        self.hookselectdialog=hookselectdialog
        self.p=subprocess.Popen(f"./Textractor/x{arch}/TextractorCLI.exe")
        print(1)
        win32pipe.ConnectNamedPipe(self.handle, None) 
        win32pipe.ConnectNamedPipe(self.handle2, None) 
        self.tryconnectt=Thread(target=self.tryconnect) 
        self.tryconnectt.start()
        self.pid=pid
        self.pname=pname
        self.arch=arch
        self.notarch='86' if arch=='64' else '64'
        self.attach(self.pid)
        
        self.HookCode=None 
         
        super( ).__init__(textgetmethod) 
 
         
    def exit(self):
        win32file.WriteFile(self.handle, bytes(f'111',encoding='utf8') ) 
         
    def attach(self,pid): 
        
        win32file.WriteFile(self.handle, bytes(f'attach -P{pid}',encoding='utf8') ) 
    
    def detach(self,pid):
        
        win32file.WriteFile(self.handle, bytes(f'detach -P{pid}',encoding='utf8') )
    
    def handle_stdout(self,stdout):
           
        print(stdout)
        reres=re.findall('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n',stdout)
        for ares in reres:
            thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode,output =ares
            
            if (thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode) not in self.reverse:
                self.hookdatacollecter.append([])
                self.hookselectdialog.addnewhooksignal.emit((thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode))
                self.reverse[(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)]=len(list(self.reverse.keys()))
            
            index=self.reverse[(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)]
            #print(self.selectinghook,index)
            if self.selectinghook and index==self.selectinghook:
                self.hookselectdialog.getnewsentencesignal.emit(output)
            if self.selectedhook and index==self.selectedhook:
                self.newline.put(output) 
            self.hookdatacollecter[index].append(output)
            
            
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
        self.detach(self.pid)
        self.exit()  
        
        self.p.kill()
        self.p.terminate()  
         
        #win32pipe.DisconnectNamedPipe(self.handle)  
        
        self.ending=True