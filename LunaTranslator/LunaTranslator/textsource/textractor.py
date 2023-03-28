import threading
from queue import Queue  
import re  
import time
from traceback import print_exc
from collections import OrderedDict
import os 
from utils import somedef
from utils.config import globalconfig ,savehook_new_data 
from utils.subproc import u16lesubprocess
from utils.hwnd import getarch
from textsource.textsourcebase import basetext 
from utils.utils import checkchaos  
class textractor(basetext  ): 
    def __init__(self,textgetmethod,hookselectdialog,pids,hwnd,pname  ,autostarthookcode=None,needinserthookcode=None,dontremove=False) :
        print(pids,hwnd,pname  ,autostarthookcode,needinserthookcode,dontremove)
        if autostarthookcode is None:
            autostarthookcode=[]
        if needinserthookcode is None:
            needinserthookcode=[]
        hookselectdialog.changeprocessclearsignal.emit()
        if len(autostarthookcode)==0:
            hookselectdialog.realshowhide.emit(True)
        self.newline=Queue()  
        self.arch=getarch(pids[0]) 
        self.lock=threading.Lock()
        self.dontremove=dontremove
        self.hookdatacollecter=OrderedDict() 
        self.reverse={}
        self.forward=[]
        self.selectinghook=None
        self.selectedhook=[]
        self.selectedhookidx=[]
         
        self.hookselectdialog=hookselectdialog
        
        self.pids=pids
        self.pname=pname
        self.hwnd=hwnd
        self.runonce_line=''
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*?):(.*?)\]')
         
         
        self.autostarthookcode=[tuple(__) for __ in autostarthookcode]
        self.autostarting=(len(self.autostarthookcode)>0) or (len(needinserthookcode)>0)
        
        self.needinserthookcode=needinserthookcode
        self.removedaddress=[] 
        self.HookCode=None 
        
        self.namehook=[]
        self.currentname=None
        #embedtranslater(self.pid,self.textgetmethod,self.append ) 
        super(textractor,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
        self.textractor_init()
    def textractor_init(self):  
        if self.arch is None:
            return 
        TextractorCLI=[]
        base=f"./files/plugins/Textractor/x{self.arch}/TextractorCLI.exe"
        extra=f"./files/plugins/Textractor/x{self.arch}/TextractorCLI_extra.exe"
        if globalconfig['textractor_engine_base_use']:TextractorCLI.append(base)
        if globalconfig['textractor_engine_extra_use']:TextractorCLI.append(extra)
        self.u16lesubprocess=u16lesubprocess(TextractorCLI)
        self.u16lesubprocess.readyread=self.handle_stdout
        self.u16lesubprocess.writelog=self.hookselectdialog.sysmessagesignal.emit
        self.attach()
        
        self.setcodepage()
         
        self.setdelay()
        if self.autostarting: 
            threading.Thread(target=self.autostartinsert,daemon=True).start() 
     
    def autostartinsert(self):   
        time.sleep(1)
        if len(self.pids)>1:return
        for _h in self.needinserthookcode: 
            if self.ending:break
            self.inserthook(_h,self.pids[0])
            
    def setdelay(self):
        delay=globalconfig['textthreaddelay']
        self.pidswrite(f'+{delay}')
    def pidswrite(self,prefix,idx=None):
        for pid in self.pids:
            self.u16lesubprocess.writer(f'{prefix} -P{pid}',idx) 
    def setcodepage(self):
        try:
            cpi=savehook_new_data[self.pname]["codepage_index"]
            cp= somedef.codepage_real[cpi]
        except:
            cp=932
        self.pidswrite(f'={cp}')
    def findhook(self,pid):
        self.u16lesubprocess.writer(f'find -P{pid}',0) 
    def inserthook(self,hookcode,pid): 
        hookcode=hookcode.replace('\r','').replace('\n','').replace('\t','')
        self.u16lesubprocess.writer(f'{hookcode} -P{pid}',0) 
    def attach(self):  
        self.pidswrite('attach')
    def detach(self):
        self.pidswrite('detach')
    def strictmatch(self,thread_tp_ctx,thread_tp_ctx2,HookCode,autostarthookcode):
        return (int(thread_tp_ctx,16)&0xffff,thread_tp_ctx2,HookCode)==(int(autostarthookcode[-4],16)&0xffff,autostarthookcode[-3],autostarthookcode[-1])

    def handle_stdout(self,lines): 
        allres=[]
        
        for line in lines:
            match=self.re.match(line)
            if match: 
                allres.append([match.groups(),[line[match.span()[1]+1:]]])
            elif len(allres): 
                allres[-1][1].append(line)
         
        newline={} 
        
        self.lock.acquire() 
        self.currentname=None
        try:
            remove_useless_hook=(not self.dontremove) and savehook_new_data[self.pname]['remove_useless_hook']
            namehook=savehook_new_data[self.pname]['namehook']
        except:
            namehook=[]
            remove_useless_hook=False
        for ares in allres:
            
            (thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode),output =ares
            output='\n'.join(output)
            
            if HookCode=='HB0@0' or thread_handle=='0' or thread_tp_processId=='0'  :
                if thread_name=='Console':
                    #print((thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode),output)
                    self.hookselectdialog.sysmessagesignal.emit(output)
                continue 
            if globalconfig['filter_chaos_code'] and checkchaos(output): 
                continue
             
            
            key =(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)
 
            hasnewhook=False
            if key not in self.hookdatacollecter:
                #print(self.autostarthookcode,HookCode)
                select=False
                if self.autostarting  :
                    for _i,autostarthookcode in enumerate(self.autostarthookcode): 
                        if self.strictmatch(thread_tp_ctx,thread_tp_ctx2,HookCode,autostarthookcode ): 
                            self.selectedhook+=[key]
                            self.selectinghook=key
                            self.selectedhookidx.append(_i)
                            __=self.selectedhook.copy()
                            self.selectedhook.sort(key=lambda x:self.selectedhookidx[__.index(x)])
                            self.selectedhookidx.sort()
                            select=True
                            break
                    if len(self.autostarthookcode)==len(self.selectedhook):
                        self.autostarting=False
                self.hookdatacollecter[key]=[] 
                isname= list(key[-4:]) in namehook
                
                hasnewhook=True
                if isname:self.namehook.append(key)
            
            #print(key,self.selectedhook,output)
            
            if (key) in self.namehook:
                self.currentname=output
            
            
            if (key in self.selectedhook): 
                #刷新速度太快的时候，一个thread会同时出好几个文本
                if key not in newline:
                    newline[key]=[output]
                else:
                    newline[key].append(output) 
            else:
                if remove_useless_hook:
                    hookcodes=[_[-1] for _ in self.selectedhook]+[_[-1] for _ in self.autostarthookcode]
                    if len(hookcodes)>0:
                        address=key[2]
                        if key[-1] not in hookcodes:
                            if address not in self.removedaddress: 
                                self.removedaddress.append(address)
                                address=int(address,16)
                                self.pidswrite(f'-{address}')
         
            
            if hasnewhook :
                if remove_useless_hook and select:
                    self.hookselectdialog.addnewhooksignal.emit(key  ,select,isname) 
                elif remove_useless_hook==False:
                    self.hookselectdialog.addnewhooksignal.emit(key  ,select,isname) 

                    
            if key==self.selectinghook:
                self.hookselectdialog.getnewsentencesignal.emit(output)
            if (remove_useless_hook and key in (self.selectedhook+self.namehook)) or remove_useless_hook==False:

                self.hookdatacollecter[key].append(output) 
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
    def end(self):

        try:
            self.detach()
            time.sleep(0.1)
            self.u16lesubprocess.kill()
        except:
            print_exc()  
         
         
        super().end()
     