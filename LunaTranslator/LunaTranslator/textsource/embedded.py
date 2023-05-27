  
from utils.config import globalconfig ,_TR   ,static_data
from textsource.textsourcebase import basetext   
import functools,queue,time,win32utils
import threading,json 
import platform
import os
from utils.hwnd import is64bit
from utils.subproc import subproc_w
from textsource.embed.sharedmemwin import winsharedmem
from textsource.embed.socketpack3 import packstrlist,packdata,unpackuint32,unpackstrlist
class embedded(basetext  ):  
    def inject_vnragent(self,pid): 
        dllpath=os.path.abspath('./files/plugins/LunaEmbedEngine32.dll')
        
        subproc_w(f'.\\files\\plugins\\shareddllproxy32.exe dllinject {pid} "{dllpath}" ') 
        
    def start(self):
        def _():  
            try:
                hostpipe = win32utils.CreateNamedPipe(
                    "\\\\.\\pipe\\LUNA_EMBEDDED_HOST",
                    win32utils.PIPE_ACCESS_DUPLEX,
                    win32utils.PIPE_TYPE_BYTE | win32utils.PIPE_READMODE_BYTE,
                    win32utils.PIPE_UNLIMITED_INSTANCES, 65536, 65536,
                    0,
                    None
                )
                hookpipe = win32utils.CreateNamedPipe(
                    "\\\\.\\pipe\\LUNA_EMBEDDED_HOOK",
                    win32utils.PIPE_ACCESS_DUPLEX,
                    win32utils.PIPE_TYPE_BYTE | win32utils.PIPE_READMODE_BYTE,
                    win32utils.PIPE_UNLIMITED_INSTANCES, 65536, 65536,
                    0,
                    None
                ) 
                print('Waiting for client connection...')
                self.hostpipe=hostpipe
                self.hookpipe=hookpipe
                event=win32utils.CreateEvent(False, False, "LUNA_EMBEDDED_WAIT")
                win32utils.SetEvent(event); 
                win32utils.ConnectNamedPipe(hostpipe, None) 
                win32utils.ConnectNamedPipe(hookpipe, None) 
                print('Client connected.') 
                while True:
                    
                    headSize = 4 
                    data = win32utils.ReadFile(hostpipe, headSize,None) 
                    if data==b'':break
                    size = unpackuint32(data)
                    data = win32utils.ReadFile(hostpipe, size,None) 
                    if data==b'':break
                    print(data) 
                    self._onDataReceived(data, hostpipe)
            finally:
                win32utils.DisconnectNamedPipe(hostpipe)
                win32utils.CloseHandle(hostpipe) 
                self._onDisconnected()
        threading.Thread(target=_).start()
    def _onDisconnected(self):  
        self.winmem.detachProcess(self.injectedPid) 
    def _onEngineReceived(self, name): # str
        self.engineName = name 

        if name : 
            self.winmem.attachProcess(self.injectedPid)
            self.getenginename(name)
            #print("%s: %s" % ( ("Detect game engine"), name))
        else: 
            self.unrecognizedengine()
            if self.injectedPid : 
                self.winmem.detachProcess(self.injectedPid)
                self.injectedPid=0
    def _onDataReceived(self, data, socket):
        print("dataReceived",data)
        args = unpackstrlist(data) 
        if not args:
            print("unpack data failed")
            return
        self._onCall(socket, *args)
    def _onCall(self, socket, cmd, *params): # on serverMessageReceived
        
        if cmd == 'agent.ping':
            if params:
                pid = int(params[0])
                if pid:
                    self._onAgentPing(socket, pid) 
        elif cmd == 'agent.engine.name':
            if params:
                self._onEngineReceived(params[0])
        elif cmd == 'agent.engine.text':
            if len(params) == 5: 
                self._onEngineText(*params)
    def _onAgentPing(self, socket, pid): 
        self.agentPid = pid  
        self.injectTimer=True
        
        self.sendSettings()
    
    def setAgentSettings(self, data): 
        try: 
            data = json.dumps(data) #, ensure_ascii=False) # the json parser in vnragent don't enforce ascii
            self.callAgent('settings', data)
        except TypeError as e:
            from traceback import print_exc 
            print_exc() 
    
    def callAgent(self, *args): 
            data = packstrlist(args)
            #print("senddata",bytes(data))
                    
            if isinstance(data, str):
                data = data.encode('utf8', errors='ignore')
            
            data = packdata(data) 
            
            print("before",data)
            
            win32utils.WriteFile(self.hookpipe,(data) )
            print('writeok')  
    def sendSettings(self): 
        
        
        data={"embeddedScenarioTranscodingEnabled": False, "embeddedFontCharSetEnabled": globalconfig['embedded']['changecharset'], "embeddedTranslationWaitTime":int(1000* globalconfig['embedded']['timeout_translate']), "embeddedOtherTranscodingEnabled": False, "embeddedSpacePolicyEncoding": "shift-jis", "windowTranslationEnabled": True, "windowTextVisible": True, "embeddedNameTranscodingEnabled": False, "gameEncoding": "shift-jis", "embeddedOtherTranslationEnabled": False, "embeddedSpaceSmartInserted": globalconfig['embedded']['insertspace_policy']==2, "embeddedFontCharSet": static_data["charsetmap"][globalconfig['embedded']['changecharset_charset']], "embeddedScenarioWidth": 0, "embeddedScenarioTextVisible": globalconfig['embedded']['keeprawtext'], "windowTranscodingEnabled": False, "nameSignature": 0, "embeddedScenarioTranslationEnabled": True, "embeddedScenarioVisible": True, "embeddedFontScale": 0, "embeddedAllTextsExtracted": False, "embeddedOtherVisible": True, "embeddedFontFamily": globalconfig['embedded']['changefont_font'] if globalconfig['embedded']['changefont'] else '', "embeddedTextEnabled": True, "scenarioSignature": 0, "embeddedOtherTextVisible": False, "embeddedNameTextVisible": False, "embeddedSpaceAlwaysInserted": globalconfig['embedded']['insertspace_policy']==1, "embeddedNameTranslationEnabled": True, "debug": True, "embeddedNameVisible": True, "embeddedFontWeight": 0}
        
        self.setAgentSettings(data)
    
    def sendSetting(self, k, v):
        data = {k:v} 
        self.setAgentSettings(data)
    def disableAgent(self): self.callAgent('disable')
    def _onEngineText(self, text, hash, sig, role, trans):
        """
        @param    text    unicode
        @param    hash    qint64
        @param    role    int
        @param    trans    bool     need translation
        """ 
        if self.winmem.isAttached()==False:
            self.winmem.attachProcess(self.injectedPid)
        try: 
            role = int(role)
            sig = int(sig) 
            if trans=='1':
                #print(text) 
                self.sendEmbeddedTranslation(text, hash,     role ) 
        except ValueError:
            print("failed to convert text hash or role to integer")
    def sendEmbeddedTranslation(self, text, hash, role ): 
         
        import functools
        self.translate(text,functools.partial(self.sendEmbeddedTranslation_,hash,role))
    def sendEmbeddedTranslation_(self,    hash, role, language,trans):
        hash = int(hash)
         
        m = self.winmem
         
        if m.isAttached(): # and m.lock(): 
            # Due to the logic, locking is not needed
            index = 0
            m.setDataStatus(index, m.STATUS_BUSY)
            m.setDataHash(index, hash)
            m.setDataRole(index, role)
            m.setDataLanguage(index, language)
            
            m.setDataText(index, trans) 
            m.setDataStatus(index, m.STATUS_READY)    
            m.notify(hash, role)
    def attachProcess(self, pid): # -> bool  
      
      self.inject_vnragent(pid=pid)
    
      self.injectedPid = pid  
      self.injectTimer=False
      def _():
        time.sleep(5000)
        if self.injectTimer : 
            self.timeout()
      threading.Thread(target=_).start() 
    def __init__(self,textgetmethod,hookselectdialog,pids,hwnd,pname,parent) : 
         
        self.textgetmethod, self.pids,self.hwnd,self.pname =textgetmethod,pids,hwnd,pname
        self.parent=parent 
        
        hookselectdialog.changeprocessclearsignal.emit()
        self.hookselectdialog=hookselectdialog
        self.newline=queue.Queue()
        self.agentreceiveddata='' 
        self.winmem = winsharedmem( )
        #b=win32utils.GetBinaryType(pname)
        b=is64bit(pids[0])
        if b:
            self.embeddedfailed(_TR("暂不支持64程序"))
        else:
            self.attachProcess(pids[0])    
            self.start()
        super(embedded,self).__init__(textgetmethod,*self.checkmd5prefix(pname))
    def timeout(self): 
        self.embeddedfailed(_TR("连接超时"))
     
    def unrecognizedengine(self): 
        self.embeddedfailed(_TR("无法识别的引擎"))
    def getenginename(self,name): 
        self.textgetmethod("<msg>"+_TR("识别到引擎")+name) 
    def translate(self,text ,embedcallback):
        self.agentreceiveddata=text
        self.hookselectdialog.getnewsentencesignal.emit(text)
        if globalconfig['autorun']:
            self.newline.put((self.agentreceiveddata,False, embedcallback))
        else:
            embedcallback('zhs',text) 
    def gettextthread(self ): 
            paste_str=self.newline.get()
            return paste_str
    def embeddedfailed(self,result): 
        self.textgetmethod("<msg>"+result+'  '+ _TR("内嵌失败，请使用普通HOOK"))     
    def runonce(self): 
        self.textgetmethod(self.agentreceiveddata,False)
    def end(self):  
        self.winmem.quit() 
        self.disableAgent()
        super().end()