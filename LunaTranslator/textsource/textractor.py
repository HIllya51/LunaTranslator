  
from threading import Thread
import win32pipe, win32file 
from multiprocessing import Queue 
from PyQt5.QtCore import QProcess ,QByteArray
import re  
import time
from textsource.textsourcebase import basetext 
class textractor(basetext ):
    def __init__(self,textgetmethod,hookselectdialog,pid,pname,arch,autostart=False,autostarthookcode=None) :
        self.newline=Queue() 
        self.reset(textgetmethod,hookselectdialog,pid,pname,arch,autostart,autostarthookcode)
        self.textgetmethod=textgetmethod
        self.t=Thread(target=self.gettextthread_)
        self.t.setDaemon(True)
        self.t.start()
        
    def reset(self,textgetmethod,hookselectdialog,pid,pname,arch,autostart=False,autostarthookcode=None)  : 
        
        self.hookdatacollecter={}
        self.hookdatasort=[]
        self.reverse={}
        self.forward=[]
        self.selectinghook=None
        self.selectedhook=None
        
        self.typename='textractor'
        self.ending=False 
        self.hookselectdialog=hookselectdialog
        self.p = QProcess()    
        self.p.readyReadStandardOutput.connect(self.handle_stdout)  
        self.p.start(f"./files/Textractor/x{arch}/TextractorCLI.exe")
        self.pid=pid
        self.pname=pname
        self.arch=arch
        self.notarch='86' if arch=='64' else '64'
        self.attach(self.pid)
        self.textfilter=''
        self.autostart=autostart
        self.autostarthookcode=autostarthookcode
        # if self.autostart:
        #     self.inserthook(autostarthookcode)
        self.HookCode=None 
        self.userinserthookcode=[]
        self.runonce_line=''
        
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n')
     

    def inserthook(self,hookcode):
        self.p.write( QByteArray((f'{hookcode} -P{self.pid}\r\r').encode(encoding='utf-16-le'))) 
        
    def exit(self):
        self.p.write( QByteArray((f'11\r\n').encode(encoding='utf-16-le'))) 
    def attach(self,pid): 
         
        self.p.write( QByteArray((f'attach -P{pid}\r\n').encode(encoding='utf-16-le'))) 
    def detach(self,pid):
        self.p.write( QByteArray((f'detach -P{pid}\r\n').encode(encoding='utf-16-le'))) 
    def handle_stdout(self): 
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf16",errors='ignore') 
         
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
                #print(11)
                #print(key==self.selectedhook,key,self.selectedhook)
                self.newline.put(output) 
                self.runonce_line=output
                
            if key not in self.hookdatacollecter:
                #print(self.autostarthookcode,HookCode)
                if self.autostart:
                    #print(self.autostarthookcode,HookCode)
                    if self.autostarthookcode==HookCode and self.guessreal(output):

                        self.selectedhook=self.selectinghook=key
                        self.autostart=False
                self.hookdatacollecter[key]=[]
                self.hookdatasort.append(key)
                self.hookselectdialog.addnewhooksignal.emit(key  ) 
            
            #print(self.selectedhook)
            self.hookdatacollecter[key].append(output)
            if key==self.selectinghook:
                self.hookselectdialog.getnewsentencesignal.emit(output)
    def guessreal(self,line):
        if len(line)<100 and (re.match('「(.*)」',line) or\
            re.match('(.*)。',line)):
            return True
        return False
    def gettextthread(self ):
            #print(333333)
            paste_str=self.newline.get()
            self.textgetmethod(paste_str)
    def runonce(self):
         
        self.textgetmethod(self.runonce_line,False)
    def end(self):
        
        self.detach(self.pid)
        self.exit()   
        self.p.kill()
        #self.ending=True
     