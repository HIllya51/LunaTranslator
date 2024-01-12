import threading
from queue import Queue  
import re ,os
import time ,gobject
from collections import OrderedDict
import ctypes,functools
import windows
import textsource.hook.define as define
from myutils.config import globalconfig ,savehook_new_data ,_TR,static_data 
from textsource.textsourcebase import basetext 
from myutils.utils import checkchaos   
from textsource.hook.host import RPC

class texthook(basetext  ): 
    def __init__(self,pids,hwnd,pname  ,autostarthookcode=None,needinserthookcode=None) :
        print(pids,hwnd,pname  ,autostarthookcode,needinserthookcode)
        self.RPC=RPC()
        if autostarthookcode is None:
            autostarthookcode=[]
        if needinserthookcode is None:
            needinserthookcode=[]
        
        self.newline=Queue()  
        self.newline_delaywait=Queue()
        self.is64bit=windows.Is64bit(pids[0])
        self.lock=threading.Lock()
        self.hookdatacollecter=OrderedDict() 
        self.hooktypecollecter=OrderedDict() 
        self.currentname=None
        self.numcharactorcounter={}
        self.reverse={}
        self.forward=[]
        self.selectinghook=None
        self.selectedhook=[]
        self.selectedhookidx=[]
        self.allow_set_text_name=globalconfig['allow_set_text_name']
        
        self.pids=pids
        self.pname=pname
        self.hwnd=hwnd
        self.runonce_line=''
        self.autostarthookcode=[tuple(__) for __ in autostarthookcode]
        self.isremoveuseless=savehook_new_data[self.pname]["removeuseless"] and len(self.autostarthookcode)
        self.needinserthookcode=needinserthookcode
        self.removedaddress=[] 
        self.HookCode=None 
        self.sharedcell=None
        self.RPC.callbacks(
            lambda pid:time.sleep(savehook_new_data[self.pname]['inserthooktimeout']/1000) or [self.RPC.InsertHookCode(pid,hookcode) for hookcode in needinserthookcode]+[self.createembedsharedmem(pid),self.showgamename()],
            lambda pid: print(pid,"disconenct"),
            self.onnewhook,
            self.onremovehook,
            self.handle_output,
            gobject.baseobject.hookselectdialog.sysmessagesignal.emit,
            self.getembedtext,
            self.newhookinsert
        )  
        self.setsettings()

        gobject.baseobject.hookselectdialog.changeprocessclearsignal.emit()
        if len(autostarthookcode)==0 and len(savehook_new_data[self.pname]['embedablehook'])==0:
            gobject.baseobject.hookselectdialog.realshowhide.emit(True)
        
          
        threading.Thread(target=self.delaycollectallselectedoutput).start()
        _pids=[]
        for pid in self.pids:
            if self.testalready(pid)==False:
                self.RPC.start(pid)
                _pids.append(pid)
         
        if len(_pids):
            self.RPC.Attach(_pids,'64' if self.is64bit else '32')
        super(texthook,self).__init__(*self.checkmd5prefix(pname))
    def testalready(self,pid):
        _mutext=windows.AutoHandle(windows.CreateMutex(False,define.ITH_HOOKMAN_MUTEX_+str(pid)))
        err=windows.GetLastError()
        exists= err==windows.ERROR_ALREADY_EXISTS
        return exists

    def newhookinsert(self,addr,hcode):
        for _hc,_addr,_ctx1,_ctx2 in savehook_new_data[self.pname]['embedablehook']:
            if hcode==_hc:
                self.useembed(addr,_ctx1,_ctx2,True) 
    def getembedtext(self,text,tt):  
        if globalconfig['autorun']==False:
            self.embedcallback(text,0,text)
            return 
        if self.checkisusingembed(tt.tp.addr,tt.tp.ctx,tt.tp.ctx2):
            self.newline.put((text,False, functools.partial(self.embedcallback,text),True))
        
    def embedcallback(self,text,_unused,trans): 
        self.sharedcell.contents.text=trans 
        
        self.notify(self.EMBEDPID,text)
    def createembedsharedmem(self,pid):
         
        self.EMBEDPID=pid
        fmap1=windows.OpenFileMapping(windows.FILE_MAP_READ|0x2,False,'EMBED_SHARED_MEM'+str(pid))
        address1=windows.MapViewOfFile(fmap1, windows.FILE_MAP_READ|0x2,  4096)
         
        self.sharedcell=ctypes.cast(address1,ctypes.POINTER(define.EmbedSharedMem)) 
        self.flashembedsettings()
    def flashembedsettings(self):
        if self.sharedcell is None:return
        self.sharedcell.contents.waittime=int(1000* globalconfig['embedded']['timeout_translate'])
        self.sharedcell.contents.fontCharSet=2#static_data["charsetmap"][globalconfig['embedded']['changecharset_charset']]
        self.sharedcell.contents.fontCharSetEnabled=False#globalconfig['embedded']['changecharset']
        self.sharedcell.contents.fontFamily=globalconfig['embedded']['changefont_font'] if globalconfig['embedded']['changefont'] else ''
        self.sharedcell.contents.spaceadjustpolicy=globalconfig['embedded']['insertspace_policy']
        self.sharedcell.contents.keeprawtext=globalconfig['embedded']['keeprawtext']
    def notify(self,pid,text):
        _b=text.encode('utf-16-le')
        def hs(text):
            _b=text.encode('utf-16-le')
            u64=ctypes.c_uint64(5381)
            for i in range(len(_b)): 
                u64=ctypes.c_uint64((u64.value<<5)+u64.value+_b[i])
            return (u64.value)
        hash_=hs(text)
        eventName = define.LUNA_NOTIFY % (pid, hash_) 
        ev = windows.AutoHandle(windows.CreateEvent( False, False, eventName)  )
        windows.SetEvent(ev) 
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
        
        self.hookdatacollecter[key]=[] 
        self.hooktypecollecter[key]=0
        gobject.baseobject.hookselectdialog.addnewhooksignal.emit(key  ,select,[textthread]) 
        self.lock.release()
        return True
    def setsettings(self):
        self.RPC.setting.timeout=globalconfig['textthreaddelay']
        self.RPC.setting.flushbuffersize=globalconfig['flushbuffersize']
        self.RPC.setting.defaultcodepag=self.codepage() 
    def codepage(self):
        try:
            cpi=savehook_new_data[self.pname]["codepage_index"]
            cp= static_data["codepage_real"][cpi]
        except:
            cp=932
        return cp
     
    def defaultsp(self):
        usestruct=define.SearchParam()
        if not self.is64bit:
            usestruct.pattern=bytes([0x55,0x8b,0xec])
            usestruct.length=3
            usestruct.offset=0
            usestruct.maxAddress=0xFFFFFFFF
        else:
            usestruct.pattern=bytes([0xCC,0xCC,0x48,0x89])
            usestruct.length=4
            usestruct.offset=2
            usestruct.maxAddress=0xFFFFFFFFFFFFFFFF
        usestruct.address_method=0
        usestruct.padding=0
        usestruct.minAddress=0
        usestruct.search_method=0
        usestruct.searchTime=30000
        usestruct.maxRecords=100000
        usestruct.codepage=self.codepage()
        usestruct.boundaryModule=os.path.basename(self.pname)
        return usestruct

    def findhook(self,usestruct):
        self.savefound={}
        self.foundnum=0
        def __waitforok():
            #time.sleep(usestruct.searchTime/1000)
            _last=0
            for i in range(100):
                #print(self.foundnum)
                if _last!=self.foundnum or _last==0:
                    _last=self.foundnum
                    time.sleep(1)
                else:
                    break
            print('??',_last,self.foundnum)
            gobject.baseobject.hookselectdialog.getfoundhooksignal.emit(self.savefound.copy())
        def _(hc,text):
            # try:print(hc,text)
            # except:print(hc)
            if hc not in self.savefound:
                self.savefound[hc]=[]
            self.savefound[hc].append(text)
            if self.foundnum==0:
                threading.Thread(target=__waitforok).start()
            self.foundnum+=1
            #print(self.foundnum)
        for pid in self.pids:  
            self.RPC.FindHooks(pid,usestruct,_)
        
        
    def inserthook(self,hookcode):  
        for pid in self.pids:
            print(hookcode)
            self.RPC.InsertHookCode(pid,hookcode)
        
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
            if self.hooktypecollecter[key]==1:
                self.currentname=output
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
    def checkisusingembed(self,address,ctx1,ctx2):
        if self.sharedcell is None:return
        for i in range(10):
            if(self.sharedcell.contents.using[i]):
                if (self.sharedcell.contents.addr[i],self.sharedcell.contents.ctx1[i],self.sharedcell.contents.ctx2[i])==(address,ctx1,ctx2):
                    return True
        
        return False
    def useembed(self,address,ctx1,ctx2,use):
        if self.sharedcell is None:return
        for i in range(10):
            if(self.sharedcell.contents.using[i]):
                if (self.sharedcell.contents.addr[i],self.sharedcell.contents.ctx1[i],self.sharedcell.contents.ctx2[i])==(address,ctx1,ctx2):
                    if use==False:
                        self.sharedcell.contents.addr[i]=0
                        self.sharedcell.contents.ctx1[i]=0
                        self.sharedcell.contents.ctx2[i]=0
                        self.sharedcell.contents.using[i]=0
        if use:
            for i in range(10):
                if(self.sharedcell.contents.using[i]==0): 
                        self.sharedcell.contents.using[i]=1
                        self.sharedcell.contents.addr[i]=address
                        self.sharedcell.contents.ctx1[i]=ctx1
                        self.sharedcell.contents.ctx2[i]=ctx2
                        break
        
    def gettextthread(self ):
            text=self.newline.get()
            while self.newline.empty()==False:
                text=self.newline.get()  
            return text
    def gettextonce(self):
         
        return self.runonce_line
    def end(self):    
        for pid in self.pids:
            self.RPC.Detach(pid)
        self.RPC.end()
        time.sleep(0.1)
        super().end()
     