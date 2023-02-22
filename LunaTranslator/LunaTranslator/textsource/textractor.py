import threading
from queue import Queue  
import re  
import time
from traceback import print_exc
from collections import OrderedDict
import os 
from utils import somedef
from utils.config import globalconfig ,_TR 
from utils.u16lesubprocess import u16lesubprocess
from utils.getpidlist import getarch
from textsource.textsourcebase import basetext 
from utils.chaos import checkchaos  
class textractor(basetext  ): 
    def __init__(self,textgetmethod,hookselectdialog,pid,hwnd,pname  ,autostarthookcode=None) :
        if autostarthookcode is None:
            autostarthookcode=[]
        hookselectdialog.changeprocessclearsignal.emit()
        if len(autostarthookcode)==0:
            hookselectdialog.realshowhide.emit(True)
        self.newline=Queue()  
        self.arch=getarch(pid) 
        self.lock=threading.Lock()
         
        self.hookdatacollecter=OrderedDict() 
        self.reverse={}
        self.forward=[]
        self.selectinghook=None
        self.selectedhook=[]
        self.selectedhookidx=[]
        self.batchselectinghook=None
        self.strictmatchedhook=[]
        self.strictmatchidx=[] 
        self.is_strict_matched_hook=False 
        self.hookselectdialog=hookselectdialog
        
        self.pid=pid
        self.pname=pname
        self.hwnd=hwnd
        self.userinserthookcode=[]
        self.runonce_line=''
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] ([\\s\\S]*)')
         
        #
        self.textfilter=''
        self.matched_hook_num=0 
        self.autostarthookcode=[tuple(__) for __ in autostarthookcode]
        self.autostarting=len(self.autostarthookcode)>0
        self.removedaddress=[] 
        self.HookCode=None 
         
        #self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)\] (.*)\n')
        
        #embedtranslater(self.pid,self.textgetmethod,self.append ) 
        super(textractor,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
        self.textractor_init()
    def textractor_init(self):  
        if self.arch is None:
            return 
        self.u16lesubprocess=u16lesubprocess(f"./files/Textractor/x{self.arch}/TextractorCLI.exe")
        self.u16lesubprocess.readyread=self.handle_stdout
        self.attach(self.pid)
        
        self.setcodepage()
         
        self.setdelay()
        if self.autostarting: 
            threading.Thread(target=self.autostartinsert,daemon=True).start() 
     
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
        self.u16lesubprocess.writer(f'+{delay} -P{self.pid}\n') 
    def setcodepage(self):
        #cp=globalconfig["codepage"]
        
        cpi=globalconfig["codepage_index"]
        cp= somedef.codepage_real[cpi]
        self.u16lesubprocess.writer(f'={cp} -P{self.pid}\n') 
    def findhook(self ): 
        self.u16lesubprocess.writer((f'find -P{self.pid}\n')) 
    def inserthook(self,hookcode): 
        print(f'{hookcode} -P{self.pid}')
        self.u16lesubprocess.writer((f'{hookcode} -P{self.pid}\n')) 
    def attach(self,pid):  
        self.u16lesubprocess.writer(f'attach -P{pid}\n') 
        print(f'attach -P{pid} ')
    def detach(self,pid):
        self.u16lesubprocess.writer(f'detach -P{pid}\n') 
        print(f'detach -P{pid} ')
    def strictmatch(self,thread_tp_ctx,thread_tp_ctx2,HookCode,autostarthookcode):
        return (int(thread_tp_ctx,16)&0xffff,thread_tp_ctx2,HookCode)==(int(autostarthookcode[-4],16)&0xffff,autostarthookcode[-3],autostarthookcode[-1])

    def handle_stdout(self,stdout):#p): 
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
        newline={} 
        
        self.lock.acquire() 
        for ares in reres:
            
            thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode,output =ares
            if HookCode=='HB0@0' or thread_handle=='0' or thread_tp_processId=='0'  :
                continue 
            if globalconfig['filter_chaos_code'] and checkchaos(output): 
                continue
             
            
            key =(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)
 
                
            if key not in self.hookdatacollecter:
                #print(self.autostarthookcode,HookCode)
                 
                if self.autostarting  : 
                    
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
                                
                                self.u16lesubprocess.writer(f'-{address} -P{self.pid}\n')
         
         
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
            paste_str=self.newline.get()  
    def gettextthread(self ):
            #print(333333)
            paste_str=self.newline.get()
            return paste_str
    def runonce(self):
         
        self.textgetmethod(self.runonce_line,False)
    def end(self):

        try:
            self.detach(self.pid)
            self.u16lesubprocess.kill()
        except:
            print_exc()  
         
         
        self.ending=True
     