import threading
import textsource.hook.define as define
  
import ctypes,time
from ctypes import Structure,c_int,c_char,sizeof,cast,POINTER
from myutils.wrapper import threader
import sys
import os  
import win32utils
import mmap
import subprocess 
from myutils.hwnd import is64bit
import ctypes
import textsource.hook.hookcode as hookcode
from myutils.hwnd import getpidexe
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
    def Push(self,buff):
        self.lasttime=time.time()
        self.lock.acquire()
        self.buffer+=self.parsebuff(buff)
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
    def callbacks(self,OnConnect,OnDisconnect,OnCreate,OnDestroy,Output,Console):
        self.OnDisconnect=threader(OnDisconnect)
        self.OnConnect=threader(OnConnect)
        self.OnCreate=threader(OnCreate)
        self.OnDestroy=threader(OnDestroy)
        self.Output=threader(Output)
        self.Console=threader(Console)
    def passf(self,*parm):
        pass
    def clear(self):
        self.OnDisconnect=self.passf
        self.OnConnect=self.passf
        self.OnCreate=self.passf
        self.OnDestroy=self.passf
        self.Output=self.passf
        self.Console=self.passf
    def toint(self,byte4):
        return c_int.from_buffer_copy(byte4).value
    def __init__(self) -> None:
        self.ProcessRecord={}
        self.clear()
        self.started=False
        self.textthreadslock=threading.Lock()
        self.textthreads={}
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
    def start(self):
        if self.started:
            return
        self.started=True
        self._start()
    def _start(self):
        def _():
            
            hookPipe = win32utils.CreateNamedPipe(define.HOOK_PIPE_NAME,
                                                win32con.PIPE_ACCESS_INBOUND,
                                                win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_READMODE_MESSAGE | win32con.PIPE_WAIT,
                                                win32con.PIPE_UNLIMITED_INSTANCES,
                                                0,
                                                0,
                                                0,
                                                win32utils.pointer(win32utils.get_SECURITY_ATTRIBUTES()))
            hostPipe = win32utils.CreateNamedPipe(define.HOST_PIPE_NAME,
                                                    win32con.PIPE_ACCESS_OUTBOUND,
                                                    win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_READMODE_MESSAGE | win32con.PIPE_WAIT,
                                                    win32con.PIPE_UNLIMITED_INSTANCES,
                                                    0,
                                                    0,
                                                    0,
                                                    win32utils.pointer(win32utils.get_SECURITY_ATTRIBUTES()))
            
            pipeAvailableEvent = win32utils.CreateEvent(False, False, define.PIPE_AVAILABLE_EVENT)
            win32utils.SetEvent(pipeAvailableEvent)
            win32utils.ConnectNamedPipe(hookPipe, None)
            win32utils.CloseHandle(pipeAvailableEvent)
            self._start() 
            processId = self.toint(win32utils.ReadFile(hookPipe, 4,None) )
            
            _is64bit=is64bit(processId)
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
            t=self.textthreads.pop(_)
            self.OnDestroy(_)
        self.textthreadslock.release()
    def OnMessage(self,data,processId,_is64bit):
        cmd=self.toint(data[:4]) 
        if(cmd==define. HOST_NOTIFICATION_TEXT):
            self.Console(define.ConsoleOutputNotif.from_buffer_copy(data).message.decode('ascii'))
        elif(cmd==define.HOST_NOTIFICATION_FOUND_HOOK):
            #print("HOST_NOTIFICATION_FOUND_HOOK")
            if _is64bit:
                _HookFoundNotif=define.HookFoundNotif64
            else:
                _HookFoundNotif=define.HookFoundNotif32
            _HookFoundNotif=_HookFoundNotif.from_buffer_copy(data)
            text=_HookFoundNotif.text.text
            if len(text)>12:
                self.ProcessRecord[processId].OnHookFound(hookcode.Generate(_HookFoundNotif.hp,processId),text)
            _HookFoundNotif.hp.type&=~hookcode.USING_UNICODE
            try:
                text=win32utils.MultiByteToWideChar(_HookFoundNotif.text.text,sizeof(define.hookfoundtext),_HookFoundNotif.hp.codepage)
                if text is not None and len(text)>12:
                    self.ProcessRecord[processId].OnHookFound(hookcode.Generate(_HookFoundNotif.hp,processId),text)
            except:pass
            try:
                _HookFoundNotif.hp.codepage=65001
                text=win32utils.MultiByteToWideChar(_HookFoundNotif.text.text,sizeof(define.hookfoundtext),_HookFoundNotif.hp.codepage)
                if text is not None and len(text)>12:
                    self.ProcessRecord[processId].OnHookFound(hookcode.Generate(_HookFoundNotif.hp,processId),text)
            except:pass
        elif(cmd==define.HOST_NOTIFICATION_FOUND_HOOK_2):
            if _is64bit:
                _HookFoundNotif=define.HookFoundNotif_2_64
            else:
                _HookFoundNotif=define.HookFoundNotif_2_32
            _HookFoundNotif=_HookFoundNotif.from_buffer_copy(data)
            text=_HookFoundNotif.text.text
            #print(_HookFoundNotif.hcode,hookcode.Generate(_HookFoundNotif.hp,processId))
            hp=hookcode.Parse(_HookFoundNotif.hcode,_HookFoundNotif.hp)
            if len(text)>12:
                self.ProcessRecord[processId].OnHookFound(hookcode.Generate(hp,processId),text)
            hp.type&=~hookcode.USING_UNICODE
            try:
                text=win32utils.MultiByteToWideChar(_HookFoundNotif.text.text,sizeof(define.hookfoundtext),hp.codepage)
                if text is not None and len(text)>12:
                    self.ProcessRecord[processId].OnHookFound(hookcode.Generate(hp,processId),text)
            except:pass
            try:
                hp.codepage=65001
                text=win32utils.MultiByteToWideChar(_HookFoundNotif.text.text,sizeof(define.hookfoundtext),hp.codepage)
                if text is not None and len(text)>12:
                    self.ProcessRecord[processId].OnHookFound(hookcode.Generate(hp,processId),text)
            except:pass
        elif(cmd==define.HOST_NOTIFICATION_RMVHOOK):
            self.removethreads(processId,define.HookRemovedNotif.from_buffer_copy(data).address)
        else:
            tp=define.ThreadParam.from_buffer_copy(data)
            
            if tp not in self.textthreads:
                self.textthreadslock.acquire()
                self.textthreads[tp]=TextThread(tp,self.ProcessRecord[tp.processId].GetHook(tp.addr),self)
                self.textthreadslock.release()
                self.OnCreate(self.textthreads[tp])
            self.textthreads[tp].Push(data[sizeof(tp):])
    #
    def Attach(self,pid,arch):
         
        injecter=os.path.abspath('./files/plugins/shareddllproxy{}.exe'.format(arch))
        dll=os.path.abspath('./files/plugins/LunaHook/LunaHook{}.dll'.format(arch))
        print(injecter,os.path.exists(injecter))
        print(dll,os.path.exists(dll))
        subprocess.Popen('"{}" dllinject {} "{}"'.format(injecter,pid,dll))

    def InsertHookCode(self,pid,hookcode):
        if pid in self.ProcessRecord:
            return self.ProcessRecord[pid].InsertHookCode(hookcode)
    def FindHooks(self,pid,sp,onfound):
        if pid in self.ProcessRecord:
            self.ProcessRecord[pid].FindHooks(sp,onfound)
    def Detach(self,pid):
        if pid in self.ProcessRecord:
            self.ProcessRecord[pid].Detach()
    def RemoveHook(self,pid,addr):
        if pid in self.ProcessRecord:
            self.ProcessRecord[pid].RemoveHook(addr)
    
if __name__=='__main__':
    rpc=RPC(print,print,print,print,print)
    rpc.start()
    while True:
            x=input()
            if(x=='detach'): 
                rpc.Call('Detach',int(input()))
            elif x=='attach':
                rpc.Call('Attach',int(input()))
            elif x=='insert':
                rpc.Call("InsertHookCode",int(input()),input())