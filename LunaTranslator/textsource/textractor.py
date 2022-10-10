  
from threading import Thread
import win32pipe, win32file 
from multiprocessing import Queue 
from PyQt5.QtCore import QProcess ,QByteArray ,QTimer
import re  
import time
import subprocess
from utils.config import globalconfig 
from textsource.textsourcebase import basetext 
class textractor(basetext  ): 
    def __init__(self,object,textgetmethod,hookselectdialog,pid,pname,arch,autostart=False,autostarthookcode=[]) :
        self.newline=Queue() 
        self.reset(object,textgetmethod,hookselectdialog,pid,pname,arch,autostart,autostarthookcode)
        self.textgetmethod=textgetmethod
        self.t=Thread(target=self.gettextthread_)
        self.t.setDaemon(True)
        self.t.start()
         
    def reset(self,object,textgetmethod,hookselectdialog,pid,pname,arch,autostart=False,autostarthookcode=[])  : 
        
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
        self.autostarthookcode=[tuple(__) for __ in autostarthookcode]
        
        if self.autostart:
            self.autostarttimeout=QTimer()
            self.autostarttimeout.timeout.connect(self.autostartinsert)
            self.autostarttimeout.start(1000)
        self.HookCode=None 
        self.userinserthookcode=[]
        self.runonce_line=''
         
        #self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n')
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] ([\\s\\S]*)')
    def autostartinsert(self):
        for _h in self.autostarthookcode:
                    x=subprocess.run(f'./files/hookcodecheck.exe {_h[-1]}',stdout=subprocess.PIPE)
                    if(x.stdout[0]==ord('0')):
                        continue
                    self.inserthook(_h[-1])
        self.autostarttimeout.stop()
    def inserthook(self,hookcode):
        # self.timer=QTimer()
        # self.timer.timeout.connect(self.insert)
        # self.timer.start(1000)
        # self.p.write( QByteArray((f'{hookcode} -P{self.pid}\r\r').encode(encoding='utf-16-le'))) 
        # print(111111111111111111111111111111111111111111)
        # print(self.p)
        print(f'{hookcode} -P{self.pid}\r\n')
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
        reres=[]
      
        while True:
            ss=self.re.search(stdout)
            if ss is None:
                break
            if len(reres)>0:
                reres[-1][-1]=reres[-1][-1][:ss.start()]
            ares=ss.groups()
            reres.append(list(ares))
            stdout=ares[-1]
        #reres=self.re.findall(stdout) #re.findall('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n',stdout)
         
        for ares in reres:
            
            thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode,output =ares
            output=output[:-1]
            if output[-2:]=='\r\n':
                output=output[:-2]
            if output[-1]=='\n':
                output=output[:-1]
            if output[-1]=='\r':
                output=output[:-1]
            key =(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)
 
            
            #if key==self.selectedhook:
            
                
            if key not in self.hookdatacollecter:
                #print(self.autostarthookcode,HookCode)
                if self.autostart:
                    if key in self.selectedhook:
                        continue
                    #print(self.autostarthookcode,HookCode)
                    #if self.autostarthookcode==HookCode and self.guessreal(output):
                    for autostarthookcode in self.autostarthookcode:
                         
                        #print((thread_tp_ctx,thread_tp_ctx2,HookCode)==(autostarthookcode[-4],autostarthookcode[-3],autostarthookcode[-1]),(thread_tp_ctx,thread_tp_ctx2,HookCode),(autostarthookcode[-4],autostarthookcode[-3],autostarthookcode[-1]))
                       # print(thread_tp_ctx,thread_tp_ctx2,autostarthookcode)
                        if (int(thread_tp_ctx,16)&0xffff,thread_tp_ctx2,HookCode)==(int(autostarthookcode[-4],16)&0xffff,autostarthookcode[-3],autostarthookcode[-1]):
                        #if (HookCode)==(autostarthookcode[-1]):
                            self.selectedhook+=[key]
                            self.selectinghook=key
                            if len(self.selectedhook)==len(self.autostarthookcode):
                                self.autostart=False
                self.hookdatacollecter[key]=[]
                self.hookdatasort.append(key)
                self.hookselectdialog.addnewhooksignal.emit(key  ) 
            
            #print(self.selectedhook)
            self.hookdatacollecter[key].append(output)
             
            if (key in self.selectedhook):
                #print(11)
                #print(key==self.selectedhook,key,self.selectedhook)
                self.newline.put(output) 
                self.runonce_line=output
            # else:
                 
            #     if globalconfig['extractalltext']:
            #         #print(self.autostarthookcode+self.selectedhook)
            #         for h in set(self.autostarthookcode+self.selectedhook):
            #             if key[-1]==h[-1]:
            #                 self.newline.put(output)
            #                 self.runonce_line=output
                            #print(output)
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
     