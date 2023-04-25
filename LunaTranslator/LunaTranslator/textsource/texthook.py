import threading
from queue import Queue  
import re  
import time,win32utils
from traceback import print_exc
from collections import OrderedDict
from utils.hookcode import Parsecode
from utils import somedef
from utils.config import globalconfig ,savehook_new_data ,_TR
from utils.subproc import subproc_w
from textsource.textsourcebase import basetext 
from utils.utils import checkchaos  
from utils.hwnd import pid_running
import ctypes,win32con
class rpcstruc(ctypes.Structure):
    _fields_=[
        ('cmd',ctypes.c_wchar*1000),
        ('param1',ctypes.c_wchar*1000),
        ('param2',ctypes.c_wchar*1000)
    ]
class texthook(basetext  ): 
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
        self.arch=win32utils.GetBinaryType(pname)
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
        self.rpccalllock=threading.Lock()
        self.autostarthookcode=[tuple(__) for __ in autostarthookcode]
        self.autostarting=(len(self.autostarthookcode)>0) or (len(needinserthookcode)>0)
        
        self.needinserthookcode=needinserthookcode
        self.removedaddress=[] 
        self.HookCode=None 
        
        #embedtranslater(self.pid,self.textgetmethod,self.append ) 
        super(texthook,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
        self.texthook_init()
    def texthook_init(self):  
        if self.arch is None:
            return 
        arch={0:'86',6:'64'}[self.arch]
        self.process=subproc_w(f"./files/plugins/TextHookEngine/x{arch}/LunaHost.exe",name='host')

        rpcoutputPipe="\\\\.\\pipe\\LUNA_RPC_OUTPUT"
        rpccallPipe="\\\\.\\pipe\\LUNA_RPC_CALL"
        waitsignal="LUNA_RPC_PIPE_AVAILABLE"
        
        secu=win32utils.get_SECURITY_ATTRIBUTES()
        win32utils.WaitForSingleObject(win32utils.CreateEvent(win32utils.pointer(secu),False, False, waitsignal),win32utils.INFINITE); 
        self.rpcoutputPipe = win32utils.CreateFile( rpcoutputPipe, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
        self.rpccallPipe = win32utils.CreateFile( rpccallPipe, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
        self.re=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*?):(.*?)\] ([\\s\\S]*)')
        
        self.readthread()
        self.attach()
        
        self.setcodepage()
         
        self.setdelay()
        if self.autostarting: 
            threading.Thread(target=self.autostartinsert,daemon=True).start() 
    def readthread(self):
        def _():
            while True:
                xx=win32utils.ReadFile(self.rpcoutputPipe, 4, None) 
                if(xx==b''):break
                slen=ctypes.c_int.from_buffer_copy(xx).value 
                xx=win32utils.ReadFile(self.rpcoutputPipe, slen, None)
                 
                if(xx==b''):break 
                xx=xx.decode('utf-16-le',errors='ignore') 
                self.handle_output(xx)
        threading.Thread(target=_).start()
    def rpccall(self,cmd,param1=None,param2=None):
        
        _=[cmd]
        if param1: _+=[str(param1)]
        if param2: _+=[str(param2)]  
        self.hookselectdialog.sysmessagesignal.emit(("Operation: "+' '.join(_)))

        param1=str(param1)
        param2=str(param2)
        rpcparam=rpcstruc()
        rpcparam.cmd=cmd
        rpcparam.param1=param1
        rpcparam.param2=param2
        self.rpccalllock.acquire()
        win32utils.WriteFile(self.rpccallPipe,bytes(rpcparam))
        self.rpccalllock.release()
    def autostartinsert(self):   
        time.sleep(1)
        if len(self.pids)>1:return
        for _h in self.needinserthookcode: 
            if self.ending:break
            self.inserthook(_h,self.pids[0])
            
    def setdelay(self):
        delay=globalconfig['textthreaddelay']
        self.rpccall("delay",delay)
    
    def setcodepage(self):
        try:
            cpi=savehook_new_data[self.pname]["codepage_index"]
            cp= somedef.codepage_real[cpi]
        except:
            cp=932
        self.rpccall("codepage",cp)
    def findhook(self,pid):
        self.rpccall("find",pid)
    def inserthook(self,hookcode,pid): 
        hookcode=hookcode.replace('\r','').replace('\n','').replace('\t','')
        x=Parsecode(hookcode)
        #print(hookcode,x.stdout[0])
        if(x is None):
            self.hookselectdialog.getnewsentencesignal.emit(_TR('！特殊码格式错误！'))
        self.rpccall("inserthook",pid,hookcode)
        return True
    def attach(self):  
        for pid in self.pids:
            if pid_running(pid):
                self.rpccall('attach',pid)
    def detach(self):
        for pid in self.pids:
            if pid_running(pid):
                self.rpccall('detach',pid)
    def strictmatch(self,thread_tp_ctx,thread_tp_ctx2,HookCode,autostarthookcode):
        return (int(thread_tp_ctx,16)&0xffff,thread_tp_ctx2,HookCode)==(int(autostarthookcode[-4],16)&0xffff,autostarthookcode[-3],autostarthookcode[-1])

    def handle_output(self,line): 
        thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode,output =self.re.match(line).groups() 
        try:
            remove_useless_hook=(not self.dontremove) and savehook_new_data[self.pname]['remove_useless_hook']
        except:
            remove_useless_hook=False
        
        if HookCode=='HB0@0':
            if thread_name=='Console':
                self.hookselectdialog.sysmessagesignal.emit(output)
            return  
        if globalconfig['filter_chaos_code'] and checkchaos(output): 
            return
        self.lock.acquire()
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
        
            hasnewhook=True
        #print(key,self.selectedhook,output)
        
        if (key in self.selectedhook): 
            self.newline.put(output)
            self.runonce_line=output
        else:
            if remove_useless_hook:
                hookcodes=[_[-1] for _ in self.selectedhook]+[_[-1] for _ in self.autostarthookcode]
                if len(hookcodes)>0:
                    address=key[2]
                    if key[-1] not in hookcodes:
                        if address not in self.removedaddress: 
                            self.removedaddress.append(address)
                            address=int(address,16)
                            for pid in self.pids:
                                if pid_running(pid):
                                    self.rpccall('removehook',pid,address)
        
        
        if hasnewhook :
            if remove_useless_hook and select:
                self.hookselectdialog.addnewhooksignal.emit(key  ,select) 
            elif remove_useless_hook==False:
                self.hookselectdialog.addnewhooksignal.emit(key  ,select) 

                
        if key==self.selectinghook:
            self.hookselectdialog.getnewsentencesignal.emit(output)
        if (remove_useless_hook and key in (self.selectedhook)) or remove_useless_hook==False:

            self.hookdatacollecter[key].append(output) 
            self.hookselectdialog.update_item_new_line.emit(key,output)
        
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
            self.process.kill()
        except:
            print_exc()  
         
         
        super().end()
     