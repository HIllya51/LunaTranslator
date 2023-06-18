import threading
from queue import Queue  
import re ,os
import time ,gobject
from collections import OrderedDict
import win32utils
import textsource.hook.define as define
from myutils.config import globalconfig ,savehook_new_data ,_TR,static_data 
from textsource.textsourcebase import basetext 
from myutils.utils import checkchaos   
from textsource.hook.host import RPC

class texthook(basetext  ): 
    def __init__(self,textgetmethod,pids,hwnd,pname  ,autostarthookcode=None,needinserthookcode=None) :
        print(pids,hwnd,pname  ,autostarthookcode,needinserthookcode)
        self.RPC=RPC()
        if autostarthookcode is None:
            autostarthookcode=[]
        if needinserthookcode is None:
            needinserthookcode=[]
        gobject.baseobject.hookselectdialog.changeprocessclearsignal.emit()
        if len(autostarthookcode)==0:
            gobject.baseobject.hookselectdialog.realshowhide.emit(True)
        self.newline=Queue()  
        self.newline_delaywait=Queue()
        self.is64bit=win32utils.Is64bit(pids[0])
        self.lock=threading.Lock()
        self.hookdatacollecter=OrderedDict() 
        self.numcharactorcounter={}
        self.reverse={}
        self.forward=[]
        self.selectinghook=None
        self.selectedhook=[]
        self.selectedhookidx=[]
         
        
        self.pids=pids
        self.pname=pname
        self.hwnd=hwnd
        self.runonce_line=''
        self.autostarthookcode=[tuple(__) for __ in autostarthookcode]
        self.isremoveuseless=savehook_new_data[self.pname]["removeuseless"] and len(self.autostarthookcode)
        self.needinserthookcode=needinserthookcode
        self.removedaddress=[] 
        self.HookCode=None 
        
        self.RPC.callbacks(
            lambda pid:time.sleep(savehook_new_data[self.pname]['inserthooktimeout']/1000) or [self.RPC.InsertHookCode(pid,hookcode) for hookcode in needinserthookcode],
            lambda pid: print(pid,"disconenct"),
            self.onnewhook,
            self.onremovehook,
            self.handle_output,
            gobject.baseobject.hookselectdialog.sysmessagesignal.emit
        ) 
        self.setcodepage()
        self.setdelay()
        threading.Thread(target=self.delaycollectallselectedoutput).start()
        for pid in self.pids:
            self.RPC.start(pid)
            self.RPC.Attach(pid,'64' if self.is64bit else '32')
        super(texthook,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
     
    def onremovehook(self,tp): 
        toremove=[]
        self.lock.acquire()
        for key in self.hookdatacollecter:
            if key[1]==tp.addr: 
                toremove.append(key)
        for key in toremove:
                gobject.baseobject.hookselectdialog.removehooksignal.emit(key)
                self.hookdatacollecter.pop(key) 
        self.lock.release()
    def parsetextthread(self,textthread):
        key=(
            textthread.tp.processId,
            textthread.tp.addr,
            textthread.tp.ctx,
            textthread.tp.ctx2,
            textthread.hp.name.decode('ascii'),
            textthread.hpcode
            )
        return key
    def match_compatibility(self,key,autostarthookcode):
        base= (key[2]&0xffff,key[3]&0xffff,key[5])==(autostarthookcode[2]&0xffff,autostarthookcode[3]&0xffff,autostarthookcode[5])
        name=((key[-1][:8]=='UserHook' and autostarthookcode[-1][:8]=='UserHook' )or(key[-1]==autostarthookcode[-1]))
        return base and name
    def onnewhook(self,textthread):
        key=self.parsetextthread(textthread)
        if self.isremoveuseless:
            if key[1] not in [_[1] for _ in self.autostarthookcode]:
                self.RPC.RemoveHook(key[0],key[1])
                return False
        
        self.lock.acquire()
        select=False
        for _i,autostarthookcode in enumerate(self.autostarthookcode): 
            if self.match_compatibility(key,autostarthookcode): 
                self.selectedhook+=[key]
                self.selectinghook=key
                select=True
                break
        gobject.baseobject.hookselectdialog.addnewhooksignal.emit(key  ,select) 
        self.hookdatacollecter[key]=[] 
        
        self.lock.release()
        return True
    def setdelay(self):
        self.RPC.setting.timeout=globalconfig['textthreaddelay']
    def codepage(self):
        try:
            cpi=savehook_new_data[self.pname]["codepage_index"]
            cp= static_data["codepage_real"][cpi]
        except:
            cp=932
        return cp
    
    def setcodepage(self):
        self.RPC.setting.defaultcodepag=self.codepage() 
    def defaultsp(self):
        if not self.is64bit:
            usestruct=define.SearchParam32()
            usestruct.pattern=bytes([0x55,0x8b,0xec])
            usestruct.length=3
            usestruct.offset=0
            usestruct.searchTime=30000
            usestruct.maxRecords=100000
            usestruct.codepage=self.codepage()
            usestruct.padding=0
            usestruct.minAddress=0
            usestruct.maxAddress=0xFFFFFFFF
            usestruct.boundaryModule=os.path.basename(self.pname)
        else:
            usestruct=define.SearchParam64()
            usestruct.pattern=bytes([0xCC,0xCC,0x48,0x89])
            usestruct.length=4
            usestruct.offset=2
            usestruct.searchTime=30000
            usestruct.maxRecords=100000
            usestruct.codepage=self.codepage()
            usestruct.padding=0
            usestruct.minAddress=0
            usestruct.maxAddress=0xFFFFFFFFFFFFFFFF
            usestruct.boundaryModule=os.path.basename(self.pname)

        return usestruct

    def findhook(self,usestruct):
        self.savefound={}
        self.foundnum=0
        def _(hc,text):
            if hc not in self.savefound:
                self.savefound[hc]=[]
            self.savefound[hc].append(text)
            self.foundnum+=1
            #print(self.foundnum)
        for pid in self.pids:  
            self.RPC.FindHooks(pid,usestruct,_)
        def __waitforok():
            time.sleep(usestruct.searchTime/1000)
            _last=0
            for i in range(10):
                if _last!=self.foundnum or _last==0:
                    _last=self.foundnum
                    time.sleep(1)
                else:
                    break
            print('??',_last,self.foundnum)
            gobject.baseobject.hookselectdialog.getfoundhooksignal.emit(self.savefound)
        threading.Thread(target=__waitforok).start()
    def inserthook(self,hookcode):  
        for pid in self.pids:
            print(hookcode)
            ret=self.RPC.InsertHookCode(pid,hookcode)
        #print(hookcode,x.stdout[0])
            if not ret:
                gobject.baseobject.hookselectdialog.getnewsentencesignal.emit(_TR('！特殊码格式错误！'))
            else:
                gobject.baseobject.hookselectdialog.getnewsentencesignal.emit(_TR('插入特殊码')+hookcode+_TR('成功'))
          
    def removehook(self,pid,address):
        for pid in self.pids:
            self.RPC.RemoveHook(pid,address)
    def delaycollectallselectedoutput(self):
        collector=[]
        while True:
            _=self.newline_delaywait.get()
            collector.append(_)
            time.sleep(globalconfig['textthreaddelay']/1000)
            while self.newline_delaywait.empty()==False:
                collector.append(self.newline_delaywait.get())
            self.newline.put(collector)
            self.runonce_line=collector 
            collector=[]
    def handle_output(self,textthread,output):   
            #print(output)       
            key=self.parsetextthread(textthread)
            
            if globalconfig['filter_chaos_code'] and checkchaos(output): 
                return
            
            
            if key not in self.hookdatacollecter:
                if self.onnewhook(textthread)==False:
                    return
            self.lock.acquire()

            if len(self.selectedhook)==1:
                if (key in self.selectedhook): 
                    self.newline.put(output)
                    self.runonce_line=output 
            else:
                if (key in self.selectedhook): 
                    self.newline_delaywait.put(output)
            if key==self.selectinghook:
                gobject.baseobject.hookselectdialog.getnewsentencesignal.emit(output)
            
            if key not in self.numcharactorcounter:
                self.numcharactorcounter[key]=0
            while self.numcharactorcounter[key]>1000000:
                _=self.hookdatacollecter[key].pop(0)
                self.numcharactorcounter[key]-=len(_)
            self.hookdatacollecter[key].append(output) 
            self.numcharactorcounter[key]+=len(output)
            gobject.baseobject.hookselectdialog.update_item_new_line.emit(key,output)
            
            self.lock.release()  
    
    def gettextthread(self ):
            paste_str=self.newline.get()
            while self.newline.empty()==False:
                paste_str=self.newline.get()  
            return paste_str
    def runonce(self):
         
        self.textgetmethod(self.runonce_line,False)
    def end(self):    
        for pid in self.pids:
            self.RPC.Detach(pid)
        self.RPC.end()
        time.sleep(0.1)
        super().end()
     