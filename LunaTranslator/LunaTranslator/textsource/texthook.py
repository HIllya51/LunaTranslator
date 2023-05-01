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
import ctypes
import ctypes,win32con
class rpcstruc(ctypes.Structure):
    _fields_=[
        ('cmd',ctypes.c_wchar*1000),
        ('param1',ctypes.c_wchar*1000),
        ('param2',ctypes.c_wchar*1000)
    ]
class texthook(basetext  ): 
    def __init__(self,textgetmethod,hookselectdialog,pids,hwnd,pname  ,autostarthookcode=None,needinserthookcode=None) :
        print(pids,hwnd,pname  ,autostarthookcode,needinserthookcode)
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
         
        self.readthread()
        self.attach()
        
        self.setcodepage()
         
        self.setdelay()
        
        for _h in self.needinserthookcode:  
            self.inserthook(_h )
    def readthread(self):
        def _():
            while True:
                xx=win32utils.ReadFile(self.rpcoutputPipe, 4, None) 
                if(xx==b''):break
                slen=ctypes.c_int.from_buffer_copy(xx).value 
                xx=win32utils.ReadFile(self.rpcoutputPipe, slen, None)
                 
                if(xx==b''):break 
                xx=xx.decode('utf-16-le',errors='ignore') 
                self.rpccalldispatch(xx)
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
    def findhook(self):
        for pid in self.pids: 
            self.rpccall("find",pid)
        
    def inserthook(self,hookcode): 
        hookcode=hookcode.replace('\r','').replace('\n','').replace('\t','')
        x=Parsecode(hookcode)
        #print(hookcode,x.stdout[0])
        if(x is None):
            self.hookselectdialog.getnewsentencesignal.emit(_TR('！特殊码格式错误！'))
        else:
            self.hookselectdialog.getnewsentencesignal.emit(_TR('插入特殊码')+hookcode+_TR('成功'))
        for pid in self.pids:
            self.rpccall("inserthook",pid,hookcode)
        return True
    def attach(self):  
        for pid in self.pids:
            self.rpccall('attach',pid)
    def detach(self):
        for pid in self.pids:
            self.rpccall('detach',pid)
    def strictmatch(self,thread_tp_ctx,thread_tp_ctx2,HookCode,autostarthookcode):
        return (int(thread_tp_ctx,16)&0xffff,thread_tp_ctx2,HookCode)==(int(autostarthookcode[-4],16)&0xffff,autostarthookcode[-3],autostarthookcode[-1])
    def rpccalldispatch(self,line):
        #print(line)
        cmd=line[0]
        data=line[1:]
         
        {
            'T':self.handle_output,
            'R':self.removehookcall,
            'F':self.hookfound
        }[cmd](data)
    def hookfound(self,line):
        fname=line
        hooks={}
        with open(fname,'rb') as ff:
            while True:
                b=ff.read(4)
                if(len(b))<4:break
                length=ctypes.c_int.from_buffer_copy(b).value
                b=ff.read(length)
                if(len(b))<length:break
                line=b.decode('utf-16-le',errors='ignore')
                _=line.split('=>')
                hookcode=_[0]
                res='=>'.join(_[1:])
                
                if hookcode not in hooks:
                    hooks[hookcode]=[]
                hooks[hookcode].append(res)
        self.hookselectdialog.getfoundhooksignal.emit(hooks)
    def removehookcall(self,line): 
        
        self.removehookre=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*?):(.*?)\]')
        removehookre=self.removehookre.match(line)
        
        key=removehookre.groups()
        #print(key) 
        if key in self.hookdatacollecter:
            self.hookselectdialog.removehooksignal.emit(key)
            self.hookdatacollecter.pop(key) 
    def removehook(self,pid,address):
        self.rpccall('removehook',pid,address)
    def handle_output(self,line): 
        self.textre=re.compile('\[([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*?):(.*?)\]([\\s\\S]*)')
        thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode,output =self.textre.match(line).groups() 
        
        
        if HookCode=='HB0@0':
            if thread_name=='Console':
                self.hookselectdialog.sysmessagesignal.emit(output)
            return  
        if globalconfig['filter_chaos_code'] and checkchaos(output): 
            return
        self.lock.acquire()
        key =(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode)


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
        
            self.hookselectdialog.addnewhooksignal.emit(key  ,select) 
        #print(key,self.selectedhook,output)
        
        if (key in self.selectedhook): 
            self.newline.put(output)
            self.runonce_line=output
         
            
        if key==self.selectinghook:
            self.hookselectdialog.getnewsentencesignal.emit(output)
        
    
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
     