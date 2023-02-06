import threading
from queue import Queue  
import re  
import time
import hashlib,subprocess
from collections import OrderedDict
import os 
from utils.config import globalconfig 
from utils.u16lesubprocess import u16lesubprocess
from utils.getpidlist import getarch
from textsource.textsourcebase import basetext 
from utils.chaos import checkchaos 
from traceback import print_exc
from textsource.embedded import embedtranslater
class textractor(basetext  ): 
    def __init__(self,object,textgetmethod,hookselectdialog,pid,hwnd,pname ,autostarthookcode=[]) :
        self.newline=Queue()  
        self.arch=getarch(pid) 
        self.lock=threading.Lock()
        with open(pname,'rb') as ff:
            bs=ff.read() 
        self.md5=hashlib.md5(bs).hexdigest()
        self.prefix=self.md5+'_'+os.path.basename(pname).replace('.'+os.path.basename(pname).split('.')[-1],'') 
        
        
        self.hookdatacollecter=OrderedDict() 
        self.reverse={}
        self.forward=[]
        self.selectinghook=None
        self.selectedhook=[]
        self.selectedhookidx=[]
        self.strictmatchedhook=[]
        self.strictmatchidx=[]
        self.textgetmethod=textgetmethod
        self.typename='textractor'
        self.ending=False 
        self.is_strict_matched_hook=False 
        self.hookselectdialog=hookselectdialog
        # self.p = QProcess()    
        # self.p.readyReadStandardOutput.connect(self.handle_stdout)  
        # self.p.start(f"./files/Textractor/x{arch}/TextractorCLI.exe")
        self.object=object
        #self.object.translation_ui.killprocesssignal.emit()
        
        #self.object.translation_ui.startprocessignal.emit(f"./files/Textractor/x{self.arch}/TextractorCLI.exe",[self.handle_stdout])
        self.u16lesubprocess=u16lesubprocess(f"./files/Textractor/x{self.arch}/TextractorCLI.exe")
        self.u16lesubprocess.readyread=self.handle_stdout
        #self.p.start(r"C:\tmp\textractor_src\Textractor-cmd\builds\RelWithDebInfo_x64\TextractorCLI.exe")
        self.pid=pid
        self.pname=pname
        self.hwnd=hwnd
        self.userinserthookcode=[]
        self.runonce_line=''
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] ([\\s\\S]*)')
        self.notarch='86' if self.arch=='64' else '64'
        self.setcodepage()
        self.setdelay()
        self.attach(self.pid)
        self.textfilter=''
        self.matched_hook_num=0 
        self.autostarthookcode=[tuple(__) for __ in autostarthookcode]
        self.autostarting=len(self.autostarthookcode)>0
        self.removedaddress=[]
        if self.autostarting: 
            threading.Thread(target=self.autostartinsert,daemon=True).start() 
        self.HookCode=None 
         
        #self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n')
        
        if globalconfig['embedded']['use']:
            self.startembedengine()
        super(textractor,self).__init__(textgetmethod)
    def startembedengine(self,_=None):
        try:  
                self.embeddedengine=embedtranslater(self.pid,self.textgetmethod)
        except:
            print_exc()
    def autostartinsert(self):
        time.sleep(3)
        dumpling=[]
        if self.ending:
            return 
        self.lock.acquire() 
        for _h in self.autostarthookcode:
            ready=False

            for _hh in self.hookdatacollecter: 
                if _h[-1]==_hh[-1]:
                    ready=True 
                    break
            if ready==False:
                    if _h[-1] in dumpling:
                        continue
                    else:
                        dumpling.append(_h[-1]) 
                    self.inserthook(_h[-1])
        self.lock.release()
        #self.autostarttimeout.stop()
    def setdelay(self):
        delay=globalconfig['textthreaddelay']
        #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'+{delay} -P{self.pid}\r\n').encode(encoding='utf-16-le')))
        self.u16lesubprocess.writer(f'+{delay} -P{self.pid}\r\n')
    def setcodepage(self):
        #cp=globalconfig["codepage"]
        
        cpi=globalconfig["codepage_index"]
        cp= globalconfig["codepage_real"][cpi]
        #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'={cp} -P{self.pid}\r\n').encode(encoding='utf-16-le')))
        self.u16lesubprocess.writer(f'={cp} -P{self.pid}\r\n')
    def findhook(self ):
        #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'find -P{self.pid}\r\n').encode(encoding='utf-16-le')))
        self.u16lesubprocess.writer((f'find -P{self.pid}\r\n'))
    def inserthook(self,hookcode):
        # self.timer=QTimer()
        # self.timer.timeout.connect(self.insert)
        # self.timer.start(1000)
        # self.p.write( QByteArray((f'{hookcode} -P{self.pid}\r\r').encode(encoding='utf-16-le'))) 
        # print(111111111111111111111111111111111111111111)
        # print(self.p)
        print(f'{hookcode} -P{self.pid}')
        #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'{hookcode} -P{self.pid}\r\n').encode(encoding='utf-16-le')))
        self.u16lesubprocess.writer((f'{hookcode} -P{self.pid}\r\n'))
    def exit(self):
        #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'11\r\n').encode(encoding='utf-16-le'))) 
        self.u16lesubprocess.writer(f'11\r\n')
    def attach(self,pid):  
        #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'attach -P{pid}\r\n').encode(encoding='utf-16-le')))
        self.u16lesubprocess.writer(f'attach -P{pid}\r\n')
        print(f'attach -P{pid} ')
    def detach(self,pid):
        #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'detach -P{pid}\r\n').encode(encoding='utf-16-le'))) 
        self.u16lesubprocess.writer(f'detach -P{pid}\r\n')
        print(f'detach -P{pid} ')
    def strictmatch(self,thread_tp_ctx,thread_tp_ctx2,HookCode,autostarthookcode):
        return (int(thread_tp_ctx,16)&0xffff,thread_tp_ctx2,HookCode)==(int(autostarthookcode[-4],16)&0xffff,autostarthookcode[-3],autostarthookcode[-1])

    def handle_stdout(self,stdout):#p): 
        #data =  p.readAllStandardOutput()
        #stdout = bytes(data).decode("utf16",errors='ignore') 
        #print(stdout)
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
        newline={} 
        
        self.lock.acquire() 
        for ares in reres:
            
            thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode,output =ares
            if HookCode=='HB0@0' or thread_handle=='0' or thread_tp_processId=='0'  :
                continue 
            if globalconfig['filter_chaos_code'] and checkchaos(output): 
                continue
             
            
            key =(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)
 
            
            #if key==self.selectedhook:
            
                
            if key not in self.hookdatacollecter:
                #print(self.autostarthookcode,HookCode)
                 
                if self.autostarting: 
                    
                    for _i,autostarthookcode in enumerate(self.autostarthookcode):  
                        if _i in self.strictmatchidx:
                            continue
                        if self.strictmatch(thread_tp_ctx,thread_tp_ctx2,HookCode,autostarthookcode ): 
                            self.selectedhook+=[key]
                            self.strictmatchedhook+=[key]
                            self.strictmatchidx.append(_i)
                            self.selectedhookidx.append(_i)
                            self.selectinghook=key
                            self.matched_hook_num+=1 
                            __=self.strictmatchedhook.copy()
                            self.strictmatchedhook.sort(key=lambda x:self.strictmatchidx[__.index(x)])
                            self.strictmatchidx.sort()
                            __=self.selectedhook.copy()
                            self.selectedhook.sort(key=lambda x:self.selectedhookidx[__.index(x)])
                            self.selectedhookidx.sort()
                        elif HookCode==autostarthookcode[-1] and len(self.selectedhook)!=len(self.autostarthookcode): 
                            
                            self.selectedhook+=[key]
                            self.selectedhookidx.append(_i)
                            self.selectinghook=key   
                            __=self.selectedhook.copy()
                            self.selectedhook.sort(key=lambda x:self.selectedhookidx[__.index(x)])
                            self.selectedhookidx.sort()
                    if len(self.autostarthookcode)==self.matched_hook_num:
                        self.autostarting=False
                        self.selectedhook=self.strictmatchedhook 
                self.hookdatacollecter[key]=[] 
                self.hookselectdialog.addnewhooksignal.emit(key  ) 
            
            #print(key,self.selectedhook,output)
            self.hookdatacollecter[key].append(output) 

            
            if (key in self.selectedhook): 
                #刷新速度太快的时候，一个thread会同时出好几个文本
                if key not in newline:
                    newline[key]=[output]
                else:
                    newline[key].append(output) 
            else:
                if globalconfig['remove_useless_hook']:
                    hookcodes=[_[-1] for _ in self.selectedhook]+[_[-1] for _ in self.autostarthookcode]
                    if len(hookcodes)>0:
                        address=key[2]
                        if key[-1] not in hookcodes:
                            if address not in self.removedaddress: 
                                self.removedaddress.append(address)
                                address=int(address,16) 
                                print(key)
                                #self.object.translation_ui.writeprocesssignal.emit( QByteArray((f'-{address} -P{self.pid}\r\n').encode(encoding='utf-16-le'))) 
                                self.u16lesubprocess.writer(f'-{address} -P{self.pid}\r\n')
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
         
        if len(newline):  
        
            newline_copy=['\n'.join(newline[k])  for k in newline]   
            linekey=list(newline.keys())
            newline=newline_copy.copy()
            try:
                newline.sort(key=lambda x: self.selectedhook.index(linekey[newline_copy.index(x)])  )
            except:
                pass
            #real='\n'.join(newline)
            #self.newline.put(real) 
            #self.runonce_line=real
            self.newline.put(newline) 
            self.runonce_line=newline
        self.lock.release() 
    def ignoretext(self):
        while self.newline.empty()==False:
            self.newline.get() 
    def gettextthread(self ):
            #print(333333)
            paste_str=self.newline.get()
            return paste_str
    def runonce(self):
         
        self.textgetmethod(self.runonce_line,False)
    def end(self,direct=False):
        if direct==False:
            try:
                self.detach(self.pid)
            except:
                pass
            #self.exit()   
            time.sleep(0.1)
        try:
            self.embeddedengine.end()
        except:
            print_exc()
        self.u16lesubprocess.kill()
        #self.object.translation_ui.killprocesssignal.emit()
        self.ending=True
     