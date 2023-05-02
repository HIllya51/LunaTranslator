import threading
import textsource.hook.define as define
  
import ctypes,time
from ctypes import Structure,c_int,c_char,sizeof,cast,POINTER

import sys
import os  
sys.path.append(r'C:\Users\wcy\Documents\GitHub\LunaTranslator\LunaTranslator\LunaTranslator')
import win32utils
import mmap
import subprocess 
import textsource.hook.hookcode as hookcode
from utils.hwnd import getpidexe
import win32con
class ProcessRecord():
    def __init__(self,pipe,processId,bit) -> None:
        self.pipe=pipe
        self.processId=processId
        self.bit=bit
        if self.bit==0:
            buff=define.MAX_HOOK*define.TextHook32
        else:
            buff=define.MAX_HOOK*define.TextHook64
        HOOK_SECTION_SIZE=sizeof(buff)
        self.buff=buff 
        self.OnHookFound=0
        self.mmap=mmap.mmap(0,HOOK_SECTION_SIZE,define.SHAREDMEMDPREFIX+str(processId),mmap.ACCESS_READ) 
    def GetHook(self,addr):  
        for _hook in self.buff.from_buffer_copy(self.mmap): 
            if(_hook.address==addr):
                return _hook
        return None
    def Send(self,struct):
        win32utils.WriteFile(self.pipe,bytes(struct))
    #calls
    def Detach(self):
        self.Send(define.DetachCmd()) 
    def RemoveHook(self,address): 
        self.Send((define.RemoveHookCmd(address)))
    def InsertHookCode(self,string):
        if self.bit==0:
            hp_t=define.HookParam32
            cmd_t=define.InsertHookCmd32
        else:
            hp_t=define.HookParam64
            cmd_t=define.InsertHookCmd64
        hp=hookcode.Parse(string,hp_t())
        print(hp)
        if hp:
            self.Send(cmd_t(hp))
            return True
        else:
            return False
    def FindHooks(self,sp,OnHookFound):
        self.OnHookFound=OnHookFound
        if self.bit==0:
            self.Send(define.FindHookCmd32(sp))
        else:
            self.Send(define.FindHookCmd64(sp))
        self.OnHookFound=OnHookFound
    def RemoveHook(self,addr):
        self.Send(define.RemoveHookCmd(addr));
class TextThread():
    def __init__(self,tp,hp,host) -> None:
        self.tp=tp
        self.hp=hp
        self.hpcode=hookcode.Generate(hp,tp.processId)
        self.host=host
        self.buffer=''
        self.lasttime=0
        self.lock=threading.Lock()
        self.running=True
        threading.Thread(target=self.flush).start()
    def stop(self):
        self.running=False
    def flush(self):
        while self.running:
            time.sleep(0.001)
            timenow=time.time() 
            if len(self.buffer)>0 and (timenow-self.lasttime>self.host.setting.timeout/1000 or len(self.buffer)>3000):
                buff=self.Pop()
                self.host.Output(self,buff)
                self.lasttime=timenow
            
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
        self.OnDisconnect=OnDisconnect
        self.OnConnect=OnConnect
        self.OnCreate=OnCreate
        self.OnDestroy=OnDestroy
        self.Output=Output
        self.Console=Console
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

        self.textthreadslock=threading.Lock()
        self.textthreads={}
        self.setting=RPCSettings()
       
    def start(self):
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
            
            pipeAvailableEvent = win32utils.CreateEvent(win32utils.pointer(win32utils.get_SECURITY_ATTRIBUTES()), False, False, define.PIPE_AVAILABLE_EVENT)
            win32utils.SetEvent(pipeAvailableEvent)
            win32utils.ConnectNamedPipe(hookPipe, None)
            processId = self.toint(win32utils.ReadFile(hookPipe, 4,None) )
            self.OnConnect(processId) 
            bit=win32utils.GetBinaryType(getpidexe(processId))
            self.ProcessRecord[processId]=ProcessRecord(hostPipe,processId,bit)
            self.start() 
            while True:  
                data=win32utils.ReadFile(hookPipe,50000,None) 
                if len(data)==0 :break
                self.OnMessage(data,processId,bit)
            self.ProcessRecord.pop(processId)
            self.OnDisconnect((processId))
        threading.Thread(target=_,daemon=True).start()
    
    def OnMessage(self,data,processId,bit):
        cmd=self.toint(data[:4]) 
        if(cmd==define. HOST_NOTIFICATION_TEXT):
            self.Console(define.ConsoleOutputNotif.from_buffer_copy(data).message.decode('ascii'))
        elif(cmd==define.HOST_NOTIFICATION_FOUND_HOOK):
            #print("HOST_NOTIFICATION_FOUND_HOOK")
            if bit==0:
                _HookFoundNotif=define.HookFoundNotif32
            else:
                _HookFoundNotif=define.HookFoundNotif64
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
        elif(cmd==define.HOST_NOTIFICATION_RMVHOOK):
            self.textthreadslock.acquire()
            toremove=[]
            for textthread in self.textthreads:
                if textthread.processId==processId and  textthread.addr==define.HookRemovedNotif.from_buffer_copy(data).address:
                    toremove.append(textthread)
            for _ in toremove:
                t=self.textthreads.pop(_)
                t.stop()
                self.OnDestroy(_)
            self.textthreadslock.release()
            #todo
        else:
            tp=define.ThreadParam.from_buffer_copy(data)
            
            if tp not in self.textthreads:
                self.textthreadslock.acquire()
                self.textthreads[tp]=TextThread(tp,self.ProcessRecord[tp.processId].GetHook(tp.addr).hp,self)
                self.textthreadslock.release()
                self.OnCreate(self.textthreads[tp])
            self.textthreads[tp].Push(data[sizeof(tp):])
    #
    def Attach(self,pid,arch):
         
        injecter=os.path.abspath(f'./files/plugins/LunaInjector/dllinject{arch}.exe')
        dll=os.path.abspath(f'./files/plugins/LunaHook/LunaHook{arch}.dll')
        print(injecter,os.path.exists(injecter))
        print(dll,os.path.exists(dll))
        subprocess.Popen(f'"{injecter}" {pid} "{dll}"')

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