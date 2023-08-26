import threading
import textsource.hook.define as define
  
import ctypes,time
from ctypes import Structure,c_int,c_char,sizeof,cast,POINTER
from myutils.wrapper import threader
import sys
import os  ,subprocess
import win32utils
from myutils.config import globalconfig 
import win32utils
from myutils.hwnd import testprivilege

import ctypes
import textsource.hook.hookcode as hookcode
import win32con
class ProcessRecord():
    def __init__(self,pipe,processId,_is64bit) -> None:
        self.pipe=pipe
        self.processId=processId
        self._is64bit=_is64bit
        if _is64bit:
            buff=define.MAX_HOOK*define.TextHook64
        else:
            buff=define.MAX_HOOK*define.TextHook32
        HOOK_SECTION_SIZE=sizeof(buff)
        self.buff=buff 
        self.OnHookFound=0
        fmap1=win32utils.OpenFileMapping(win32utils.FILE_MAP_READ,False,define.SHAREDMEMDPREFIX+str(processId))
        address1=win32utils.MapViewOfFile(fmap1, win32utils.FILE_MAP_READ,   HOOK_SECTION_SIZE)
        
        fmap2=win32utils.OpenFileMapping(win32utils.FILE_MAP_READ,False,define.HOOKCODEGET+str(processId))
        address2=win32utils.MapViewOfFile(fmap2, win32utils.FILE_MAP_READ,   sizeof(define.MAX_HOOK*define.Hookcodeshared))

        self.sharedtexthook=cast(address1,POINTER(buff)) 
        self.sharedhookcode=cast(address2,POINTER(define.MAX_HOOK*define.Hookcodeshared)) 
 
    def GetHook(self,addr):  
        for i,_hook in enumerate(self.sharedtexthook.contents): 
            if(_hook.address==addr):
                code=self.sharedhookcode.contents[i].code
                return _hook,code
        return None,None
    def Send(self,struct):
        win32utils.WriteFile(self.pipe,bytes(struct))
    #calls
    def Detach(self):
        self.Send(define.DetachCmd()) 
    def RemoveHook(self,address): 
        self.Send((define.RemoveHookCmd(address)))
    def InsertHookCode(self,string):
        if len(string) and string[0]=='E':
            self.Send(define.InsertHookCodeNaive(string))
        else:
            if self._is64bit:
                hp_t=define.HookParam64
                cmd_t=define.InsertHookCmd64
            else:
                hp_t=define.HookParam32
                cmd_t=define.InsertHookCmd32
            hp=hookcode.Parse(string,hp_t())
            print(hp)
            if hp:
                self.Send(cmd_t(hp))
                return True
            else:
                return False
            
    def FindHooks(self,sp,OnHookFound):
        self.OnHookFound=OnHookFound
        if self._is64bit:
            self.Send(define.FindHookCmd64(sp))
        else:
            self.Send(define.FindHookCmd32(sp))
        self.OnHookFound=OnHookFound
    def RemoveHook(self,addr):
        self.Send(define.RemoveHookCmd(addr));
class TextThread():
    def __init__(self,tp,_,host) -> None:
        (texthook,hcode)=_
        hp=texthook.hp
        self.tp=tp
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
        if not( globalconfig['direct_filterrepeat']and (len(buffer)>=3) and (buffer in self.saverepeat)):
            self.lasttime=time.time()
            self.buffer+=buffer
        if len(self.buffer):
            self.saverepeat=self.buffer
        self.lock.release()
    def Pop(self):
        self.lock.acquire()
        _=self.buffer
        self.buffer=''
        self.lock.release()
        return _
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
                if(win32utils.IsDBCSLeadByteEx(cp,buff[0])):
                    self.leadbyte=buff
                    return ''
        
        
        if (hp.type &hookcode.HEX_DUMP) :
            _ret=buff.hex()
        elif hp.type& hookcode.USING_UNICODE:
            _ret=buff.decode('utf-16',errors='ignore')
        else:
            if hp.codepage==0:
                cp=self.host.setting.defaultcodepag
            else:
                cp=hp.codepage
            _ret=win32utils.MultiByteToWideChar(buff,len(buff),cp)
            if _ret is None:
                _ret=''	
        if hp.type&hookcode.FULL_STRING:
            _ret+='\n'
        return _ret
class RPCSettings:
    def __init__(self) -> None:
        self.timeout=100
        self.defaultcodepag=932
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
            win32utils.CancelIo(_)
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
                if len(textthread.buffer)>0 and (timenow-textthread.lasttime>self.setting.timeout/1000 or len(textthread.buffer)>3000):
                    buff=textthread.Pop()
                    self.Output(textthread,buff)
                    textthread.lasttime=timenow
            self.textthreadslock.release()
    def start(self,pid):
    
        hookPipe = win32utils.CreateNamedPipe(define.HOOK_PIPE_NAME+str(pid),
                                            win32con.PIPE_ACCESS_INBOUND,
                                            win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_READMODE_MESSAGE | win32con.PIPE_WAIT,
                                            win32con.PIPE_UNLIMITED_INSTANCES,
                                            0,
                                            0,
                                            0,
                                            win32utils.pointer(win32utils.get_SECURITY_ATTRIBUTES()))
        hostPipe = win32utils.CreateNamedPipe(define.HOST_PIPE_NAME+str(pid),
                                                win32con.PIPE_ACCESS_OUTBOUND,
                                                win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_READMODE_MESSAGE | win32con.PIPE_WAIT,
                                                win32con.PIPE_UNLIMITED_INSTANCES,
                                                0,
                                                0,
                                                0,
                                                win32utils.pointer(win32utils.get_SECURITY_ATTRIBUTES()))
        
        pipeAvailableEvent = win32utils.CreateEvent(False, False, define.PIPE_AVAILABLE_EVENT+str(pid))
        win32utils.SetEvent(pipeAvailableEvent)
        self.hookPipes.append(hookPipe)
        def _():
            win32utils.ConnectNamedPipe(hookPipe, None)
            win32utils.CloseHandle(pipeAvailableEvent)
            processId = self.toint(win32utils.ReadFile(hookPipe, 4,None) )
            
            _is64bit=win32utils.Is64bit(processId)
            self.ProcessRecord[processId]=ProcessRecord(hostPipe,processId,_is64bit)
            self.OnConnect(processId) 
            
            while True:  
                data=win32utils.ReadFile(hookPipe,50000,None) 
                if len(data)==0 :break
                if len(data)==50000:continue
                self.OnMessage(data,processId,_is64bit)
            self.ProcessRecord.pop(processId)
            win32utils.CloseHandle(hookPipe)
            win32utils.CloseHandle(hostPipe)
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
    def OnMessage(self,data,processId,_is64bit):
        cmd=self.toint(data[:4]) 
        if(cmd==define. HOST_NOTIFICATION_TEXT):
            self.Console(define.ConsoleOutputNotif.from_buffer_copy(data).message.decode('utf8'))
        
        elif(cmd==define.HOST_NOTIFICATION_FOUND_HOOK):
            if _is64bit:
                _HookFoundNotif=define.HookFoundNotif64
            else:
                _HookFoundNotif=define.HookFoundNotif32
            _HookFoundNotif=_HookFoundNotif.from_buffer_copy(data)
            text=_HookFoundNotif.text.text
            #print(_HookFoundNotif.hcode,hookcode.Generate(_HookFoundNotif.hp,processId))
            hp=hookcode.Parse(_HookFoundNotif.hcode,_HookFoundNotif.hp)
            if len(text)>12:
                self.ProcessRecord[processId].OnHookFound(hookcode.Generate(hp,processId),text)
            hp.type&=~hookcode.USING_UNICODE
            codepages=[hp.codepage] 
            if hp.codepage!=65001:
                codepages+=[65001] 
                
            for codepage in codepages:
                try:
                    hp.codepage=codepage
                    text=win32utils.MultiByteToWideChar(_HookFoundNotif.text.text,sizeof(define.hookfoundtext),hp.codepage)
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
                self.textthreads[tp]=TextThread(tp,self.ProcessRecord[tp.processId].GetHook(tp.addr),self)
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
            win32utils.ShellExecute(0,'runas',injecter,'dllinject {} "{}"'.format(pid,dll),None,win32con.SW_HIDE)
        else:
            ret=subprocess.run('"{}" dllinject {} "{}"'.format(injecter,pid,dll)).returncode
            if(ret==0):
                win32utils.ShellExecute(0,'runas',injecter,'dllinject {} "{}"'.format(pid,dll),None,win32con.SW_HIDE)
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
    