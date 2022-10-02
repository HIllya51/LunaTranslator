  
from threading import Thread
import win32pipe, win32file 
from multiprocessing import Queue 
from PyQt5.QtCore import QProcess ,QByteArray
import re  
import time
from textsource.textsourcebase import basetext 
class textractor(basetext):
     
    hookdatacollecter={}
    hookdatasort=[]
    reverse={}
    forward=[]
    selectinghook=None
    selectedhook=None
    def __init__(self,textgetmethod,hookselectdialog,pid,pname,arch)  : 
        self.newline=Queue() 
        self.typename='textractor'
        self.ending=False 
        self.hookselectdialog=hookselectdialog
        self.p = QProcess()    
        self.p.readyReadStandardOutput.connect(self.handle_stdout)  
        self.p.finished.connect(self.cleanup)
        self.p.start(f"./files/Textractor/x{arch}/TextractorCLI.exe")
        self.pid=pid
        self.pname=pname
        self.arch=arch
        self.notarch='86' if arch=='64' else '64'
        
        
        self.textfilter=''
        self.autostart=False
        self.HookCode=None 
        self.userinserthookcode=[]
        self.runonce_line=''
         
        self.attach(self.pid)
        super( ).__init__(textgetmethod) 
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n')
    def cleanup(self):
        print('end')
    def inserthook(self,hookcode):
        print(f'{hookcode} -P{self.pid}\r\n')
        #self.p.write( QByteArray((f'{hookcode} -P{self.pid}\r\n').encode(encoding='utf-16-le'))) 
        
    def exit(self):
         
        self.p.write( QByteArray((f'11\r\n').encode(encoding='utf-16-le'))) 
    def attach(self,pid): 
        print(f'attach -P{pid}\r\n')
        self.p.write( QByteArray((f'attach -P{pid}\r\n').encode(encoding='utf-16-le'))) 
    def detach(self,pid):
        self.p.write( QByteArray((f'detach -P{pid}\r\n').encode(encoding='utf-16-le'))) 
    def handle_stdout(self): 
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf16",errors='ignore') 
        #print(stdout)
        reres=self.re.findall(stdout) #re.findall('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n',stdout)
        for ares in reres:
            thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode,output =ares
            if output[-2:]=='\r\n':
                output=output[:-2]
            if output[-1]=='\n':
                output=output[:-1]
            if output[-1]=='\r':
                output=output[:-1]
            key =(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)
 
            
            if key==self.selectedhook:
                self.newline.put(output) 
                self.runonce_line=output
             
            if key not in self.hookdatacollecter:
                if self.autostart:
                    if self.autostarthookcode==HookCode:

                        self.selectedhook=self.selectinghook=key
                        self.autostart=False
                self.hookdatacollecter[key]=[]
                self.hookdatasort.append(key)
                self.hookselectdialog.addnewhooksignal.emit(key  ) 
            
            #print(self.selectedhook)
            self.hookdatacollecter[key].append(output)
            if key==self.selectinghook:
                self.hookselectdialog.getnewsentencesignal.emit(output)
    def gettextthread(self ):

            paste_str=self.newline.get()
            self.textgetmethod(paste_str)
    def runonce(self):
         
        self.textgetmethod(self.runonce_line,False)
    def end(self):
         
        self.detach(self.pid)
        self.exit()   
        self.ending=True
     