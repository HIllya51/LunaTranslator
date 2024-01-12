import threading
import textsource.hook.define as define
  
import ctypes,time
from ctypes import Structure,c_int,c_char,sizeof,cast,POINTER
from myutils.wrapper import threader
import sys
import os  ,subprocess 
from myutils.config import globalconfig 
import windows
from myutils.hwnd import testprivilege

import ctypes
import textsource.hook.hookcode as hookcode
class ProcessRecord():
    def __init__(self,pipe,processId) -> None:
        self.pipe=pipe
        self.processId=processId
        buff=define.MAX_HOOK*define.TextHook
        HOOK_SECTION_SIZE=sizeof(buff)
        self.OnHookFound=0
        fmap1=windows.OpenFileMapping(windows.FILE_MAP_READ,False,define.SHAREDMEMDPREFIX+str(processId))
        address1=windows.MapViewOfFile(fmap1, windows.FILE_MAP_READ,   HOOK_SECTION_SIZE)
        
        fmap2=windows.OpenFileMapping(windows.FILE_MAP_READ,False,define.HOOKCODEGET+str(processId))
        address2=windows.MapViewOfFile(fmap2, windows.FILE_MAP_READ,   sizeof(define.MAX_HOOK*define.Hookcodeshared))

        self.sharedtexthook=cast(address1,POINTER(buff)) 
        self.sharedhookcode=cast(address2,POINTER(define.MAX_HOOK*define.Hookcodeshared)) 
 
    def GetHook(self,addr):  
        for i,_hook in enumerate(self.sharedtexthook.contents): 
            if(_hook.address==addr):
                code=self.sharedhookcode.contents[i].code
                return _hook,code
        return None,None
    def Send(self,struct):
        windows.WriteFile(self.pipe,bytes(struct))
    #calls
    def Detach(self):
        self.Send(define.DetachCmd()) 
    def RemoveHook(self,address): 
        self.Send((define.RemoveHookCmd(address)))
    def InsertHookCode(self,string):
        if len(string) and string[0]=='E':
            self.Send(define.InsertHookCodeNaive(string))
        else: 
            hp=hookcode.Parse(string)
            print(hp)
            if hp:
                self.Send(define.InsertHookCmd(hp))
                return True
            else:
                return False
            
    def FindHooks(self,sp,OnHookFound):
        self.OnHookFound=OnHookFound
        self.Send(define.FindHookCmd(sp))
        self.OnHookFound=OnHookFound
    def RemoveHook(self,addr):
        self.Send(define.RemoveHookCmd(addr));
class TextThread():
    def __init__(self,rpc,tp,_,host) -> None:
        (texthook,hcode)=_
        hp=texthook.hp
        self.tp=tp
        self.rpc=rpc
        self.hp=hp
        self.hpcode=hcode#hookcode.Generate(hp,tp.processId)
        self.host=host
        self.buffer=''
        self.lasttime=0
        self.lock=threading.Lock()
        self.leadbyte=0 
        self.saverepeat=''
    def Push(self,buff):
        
        self.lock.acquire()
        buffer=self.parsebuff(buff)
        if self.rpc.setting.timeout==0 and self.hp.type&hookcode.FULL_STRING:
            self.rpc.Output(self,buffer)
        elif not( globalconfig['direct_filterrepeat']and (len(buffer)>=3) and (buffer in self.saverepeat)):
            self.buffer+=buffer
        self.lasttime=time.time()
        if len(self.buffer):
            self.saverepeat=self.buffer
        
        if len(self.buffer)>=self.host.setting.flushbuffersize:
            _=self.buffer
            self.buffer=''
            self.rpc.Output(self,_)

        self.lock.release()
 
    def parsebuff(self,buff):
        hp=self.hp
        if hp.codepage==0:
            cp=self.host.setting.defaultcodepag
        else:
            cp=hp.codepage
        if len(buff)==1:
            if self.leadbyte:
                buff=self.leadbyte+buff
                self.leadbyte=0
            else:
                if(windows.IsDBCSLeadByteEx(cp,buff[0])):
                    self.leadbyte=buff
                    return ''
        
        
        if (hp.type &hookcode.HEX_DUMP) :
            _ret=buff.hex()
        elif hp.type& hookcode.USING_UNICODE:
            try:
                _ret=buff.decode('utf-16',errors='ignore')
            except:
                return ''
        else:
            if hp.codepage==0:
                cp=self.host.setting.defaultcodepag
            else:
                cp=hp.codepage
            _ret=windows.MultiByteToWideChar(buff,len(buff),cp)
            if _ret is None:
                _ret=''	
        if hp.type&hookcode.FULL_STRING:
            _ret+='\n'
        return _ret
class RPCSettings:
    def __init__(self) -> None:
        self.timeout=100
        self.defaultcodepag=932
        self.flushbuffersize=3000
class RPC(): 
    def callbacks(self,OnConnect,OnDisconnect,OnCreate,OnDestroy,Output,Console,EmbedCall,HookInsert):
        self.OnDisconnect=threader(OnDisconnect)
        self.OnConnect=threader(OnConnect)
        self.OnCreate=(OnCreate)    #有并发问题，会插入Embed的text两次
        self.OnDestroy=threader(OnDestroy)
        self.Output=threader(Output)
        self.Console=threader(Console)
        self.EmbedCall=threader(EmbedCall)
        self.HookInsert=threader(HookInsert)
    def toint(self,byte4):
        return c_int.from_buffer_copy(byte4).value
    def end(self):
        for _ in self.hookPipes:
            windows.CancelIo(_)
    def __init__(self) -> None:
        self.ProcessRecord={}
        self.textthreadslock=threading.Lock()
        self.textthreads={}
        self.hookPipes=[]
        self.setting=RPCSettings()
        threading.Thread(target=self.outputthread).start()
    def outputthread(self):
        while True:
            time.sleep(0.001)
            timenow=time.time() 
            self.textthreadslock.acquire()
            for _,textthread in self.textthreads.items():
                textthread.lock.acquire()
                if len(textthread.buffer)>0 and (timenow-textthread.lasttime>self.setting.timeout/1000):
                    buff=textthread.buffer
                    textthread.buffer=''
                    self.Output(textthread,buff)
                    textthread.lasttime=timenow
                textthread.lock.release()
            self.textthreadslock.release()
    def start(self,pid):
    
        hookPipe = windows.CreateNamedPipe(define.HOOK_PIPE_NAME+str(pid),
                                            windows.PIPE_ACCESS_INBOUND,
                                            windows.PIPE_TYPE_MESSAGE | windows.PIPE_READMODE_MESSAGE | windows.PIPE_WAIT,
                                            windows.PIPE_UNLIMITED_INSTANCES,
                                            0,
                                            0,
                                            0)
        hostPipe = windows.CreateNamedPipe(define.HOST_PIPE_NAME+str(pid),
                                                windows.PIPE_ACCESS_OUTBOUND,
                                                windows.PIPE_TYPE_MESSAGE | windows.PIPE_READMODE_MESSAGE | windows.PIPE_WAIT,
                                                windows.PIPE_UNLIMITED_INSTANCES,
                                                0,
                                                0,
                                                0 )
        
        pipeAvailableEvent = windows.CreateEvent(False, False, define.PIPE_AVAILABLE_EVENT+str(pid))
        windows.SetEvent(pipeAvailableEvent)
        self.hookPipes.append(hookPipe)
        def _():
            windows.ConnectNamedPipe(hookPipe, None)
            windows.CloseHandle(pipeAvailableEvent)
            processId = self.toint(windows.ReadFile(hookPipe, 4,None) )
            
            self.ProcessRecord[processId]=ProcessRecord(hostPipe,processId)
            self.OnConnect(processId) 
            
            while True:  
                data=windows.ReadFile(hookPipe,50000,None) 
                if len(data)==0 :break
                if len(data)==50000:continue
                self.OnMessage(data,processId)
            self.ProcessRecord.pop(processId)
            windows.CloseHandle(hookPipe)
            windows.CloseHandle(hostPipe)
            self.removethreads(processId)
            self.OnDisconnect((processId))
        threading.Thread(target=_,daemon=True).start()
    def removethreads(self,pid,addr=None):
        self.textthreadslock.acquire()
        toremove=[]
        for textthread in self.textthreads:
            if textthread.processId==pid:
                if addr:
                    if textthread.addr==addr:
                        toremove.append(textthread)
                else:
                    toremove.append(textthread)
        for _ in toremove:
            self.textthreads.pop(_)
            self.OnDestroy(_)
        self.textthreadslock.release()
    def OnMessage(self,data,processId):
        cmd=self.toint(data[:4]) 
        if(cmd==define. HOST_NOTIFICATION_TEXT):
            try:
                message=define.ConsoleOutputNotif.from_buffer_copy(data).message.decode('utf8')
            except:
                message="ErrorDecodeMessage"
            self.Console(message)
        
        elif(cmd==define.HOST_NOTIFICATION_FOUND_HOOK):
            _HookFoundNotif=define.HookFoundNotif
            _HookFoundNotif=_HookFoundNotif.from_buffer_copy(data)
            text=_HookFoundNotif.text.text
            #print(_HookFoundNotif.hcode,hookcode.Generate(_HookFoundNotif.hp,processId))
            hp=hookcode.Parse(_HookFoundNotif.hcode)
            if len(text)>12:
                self.ProcessRecord[processId].OnHookFound(hookcode.Generate(hp,processId),text)
            hp.type&=~hookcode.USING_UNICODE
            codepages=[hp.codepage] 
            if hp.codepage!=65001:
                codepages+=[65001] 
                
            for codepage in codepages:
                try:
                    hp.codepage=codepage
                    text=windows.MultiByteToWideChar(_HookFoundNotif.text.text,sizeof(define.hookfoundtext),hp.codepage)
                    if text is not None and len(text)>12:
                        self.ProcessRecord[processId].OnHookFound(hookcode.Generate(hp,processId),text)
                except:pass
            
        elif(cmd==define.HOST_NOTIFICATION_RMVHOOK):
            self.removethreads(processId,define.HookRemovedNotif.from_buffer_copy(data).address)
        elif(cmd==define.HOST_NOTIFICATION_INSERTHOOK):
                    
            addr=define.HookInsertingNotif.from_buffer_copy(data).addr
            _,hcode=self.ProcessRecord[processId].GetHook(addr)
            self.HookInsert(addr,hcode)
        else:
            tp=define.ThreadParam.from_buffer_copy(data)
            
            if tp not in self.textthreads:
                self.textthreadslock.acquire()
                self.textthreads[tp]=TextThread(self,tp,self.ProcessRecord[tp.processId].GetHook(tp.addr),self)
                self.OnCreate(self.textthreads[tp])
                self.textthreadslock.release()
            if self.textthreads[tp].hpcode[0]=='E':
                #self.Output(self.textthreads[tp],self.textthreads[tp].parsebuff(data[sizeof(tp):]))
                self.EmbedCall(self.textthreads[tp].parsebuff(data[sizeof(tp):]),self.textthreads[tp])
            self.textthreads[tp].Push(data[sizeof(tp):])
    #
    def Attach(self,pids,arch):
        
        injecter=os.path.abspath('./files/plugins/shareddllproxy{}.exe'.format(arch))
        dll=os.path.abspath('./files/plugins/LunaHook/LunaHook{}.dll'.format(arch))
        print(injecter,os.path.exists(injecter))
        print(dll,os.path.exists(dll))
        #subprocess.Popen('"{}" dllinject {} "{}"'.format(injecter,pid,dll))
        pid=' '.join([str(_) for _ in pids])
        if any(map(testprivilege,pids))==False: 
            windows.ShellExecute(0,'runas',injecter,'dllinject {} "{}"'.format(pid,dll),None,windows.SW_HIDE)
        else:
            ret=subprocess.run('"{}" dllinject {} "{}"'.format(injecter,pid,dll)).returncode
            if(ret==0):
                windows.ShellExecute(0,'runas',injecter,'dllinject {} "{}"'.format(pid,dll),None,windows.SW_HIDE)
    @threader
    def InsertHookCode(self,pid,hookcode):
        if pid in self.ProcessRecord:
            self.ProcessRecord[pid].InsertHookCode(hookcode)
    @threader
    def FindHooks(self,pid,sp,onfound):
        if pid in self.ProcessRecord:
            self.ProcessRecord[pid].FindHooks(sp,onfound)
    @threader
    def Detach(self,pid):
        if pid in self.ProcessRecord:
            self.ProcessRecord[pid].Detach()
    @threader
    def RemoveHook(self,pid,addr):
        if pid in self.ProcessRecord:
            self.ProcessRecord[pid].RemoveHook(addr)
    