  
from threading import Thread
import win32pipe, win32file 
from multiprocessing import Queue 
from PyQt5.QtCore import QProcess ,QByteArray ,QTimer
import re  
import time
from textsource.textsourcebase import basetext 
class textractor(basetext  ): 
    def __init__(self,object,textgetmethod,hookselectdialog,pid,pname,arch,autostart=False,autostarthookcode=None) :
        self.newline=Queue() 
        self.reset(object,textgetmethod,hookselectdialog,pid,pname,arch,autostart,autostarthookcode)
        self.textgetmethod=textgetmethod
        self.t=Thread(target=self.gettextthread_)
        self.t.setDaemon(True)
        self.t.start()
         
    def reset(self,object,textgetmethod,hookselectdialog,pid,pname,arch,autostart=False,autostarthookcode=None)  : 
        
        self.hookdatacollecter={}
        self.hookdatasort=[]
        self.reverse={}
        self.forward=[]
        self.selectinghook=None
        self.selectedhook=[]
        
        self.typename='textractor'
        self.ending=False 
        self.hookselectdialog=hookselectdialog
        # self.p = QProcess()    
        # self.p.readyReadStandardOutput.connect(self.handle_stdout)  
        # self.p.start(f"./files/Textractor/x{arch}/TextractorCLI.exe")
        self.object=object
        #self.object.translation_ui.killprocesssignal.emit()
        self.object.translation_ui.startprocessignal.emit(f"./files/Textractor/x{arch}/TextractorCLI.exe",[self.handle_stdout])
        #self.p.start(r"C:\tmp\textractor_src\Textractor-cmd\builds\RelWithDebInfo_x64\TextractorCLI.exe")
        self.pid=pid
        self.pname=pname
        self.arch=arch
        self.notarch='86' if arch=='64' else '64'
        self.attach(self.pid)
        self.textfilter=''
        self.autostart=autostart
        self.autostarthookcode=autostarthookcode
        
        if self.autostart:
            t=QTimer()
            def __(self,h,t):
                self.inserthook(h)
                t.stop()
            t.timeout.connect(lambda: __(self,autostarthookcode[-1],t))
            t.start(1000)
        self.HookCode=None 
        self.userinserthookcode=[]
        self.runonce_line=''
        
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n')
     
    
    def inserthook(self,hookcode):
        # self.timer=QTimer()
        # self.timer.timeout.connect(self.insert)
        # self.timer.start(1000)
        # self.p.write( QByteArray((f'{hookcode} -P{self.pid}\r\r').encode(encoding='utf-16-le'))) 
        # print(111111111111111111111111111111111111111111)
        # print(self.p)
        self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'{hookcode} -P{self.pid}\r\n').encode(encoding='utf-16-le')))
        #麻了 就是不知道为什么写入不进去。。。
    def exit(self):
        self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'11\r\n').encode(encoding='utf-16-le'))) 
    def attach(self,pid):  
        self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'attach -P{pid}\r\n').encode(encoding='utf-16-le')))
        #self.p.write( QByteArray((f'attach -P{pid}\r\n').encode(encoding='utf-16-le'))) 
    def detach(self,pid):
        self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'detach -P{pid}\r\n').encode(encoding='utf-16-le'))) 
    # def handle_stdout(self): 
    #     data = self.p.readAllStandardOutput()
    def handle_stdout(self,p): 
        data =  p.readAllStandardOutput()
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
 
            
            #if key==self.selectedhook:
            if key in self.selectedhook:
                #print(11)
                #print(key==self.selectedhook,key,self.selectedhook)
                self.newline.put(output) 
                self.runonce_line=output
                
            if key not in self.hookdatacollecter:
                #print(self.autostarthookcode,HookCode)
                if self.autostart:
                    if key in self.selectedhook:
                        continue
                    #print(self.autostarthookcode,HookCode)
                    #if self.autostarthookcode==HookCode and self.guessreal(output):
                    for autostarthookcode in self.autostarthookcode:

                        if (thread_tp_ctx,thread_tp_ctx2,HookCode)==(autostarthookcode[-4],autostarthookcode[-3],autostarthookcode[-1]):
                            self.selectedhook+=[key]
                            self.selectinghook=key
                            if len(self.selectedhook)==len(self.autostarthookcode):
                                self.autostart=False
                self.hookdatacollecter[key]=[]
                self.hookdatasort.append(key)
                self.hookselectdialog.addnewhooksignal.emit(key  ) 
            
            #print(self.selectedhook)
            self.hookdatacollecter[key].append(output)
            if key==self.selectinghook:
                self.hookselectdialog.getnewsentencesignal.emit(output)
            self.hookselectdialog.update_item_new_line.emit(key,output)
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
        self.object.translation_ui.killprocesssignal.emit()
        #self.ending=True
     