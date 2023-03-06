    
from utils.config import globalconfig   
import time
import os ,threading,win32utils,win32con
from traceback import print_exc
from utils.subproc import subproc
class tts():
    def end(self):
        try:
            self.engine.kill()
        except:
            pass
    def __init__(self,showlist ,mp3playsignal ): 
         
        self.voicelist=[]
        if os.path.exists(globalconfig['reader']['voiceroid2']['path'])==False:
            showlist.emit(self.voicelist)
            return
        l=os.listdir(os.path.join(globalconfig['reader']['voiceroid2']['path'],'Voice'))
        for _ in l:
            if _!='index.dat':
                self.voicelist.append(_)
         
        showlist.emit(self.voicelist)
        if  len(self.voicelist)>0 and globalconfig['reader']['voiceroid2']['voice'] not in self.voicelist:
            globalconfig['reader']['voiceroid2']['voice']=self.voicelist[0]
        self.speaking=None
        self.mp3playsignal=mp3playsignal
        self.path=None
        self.checkpath()
    def checkpath(self):
        if globalconfig["reader"]["voiceroid2"]["path"]=="":
            return False
        if os.path.exists(globalconfig["reader"]["voiceroid2"]["path"])==False:
            return False
        if   globalconfig["reader"]["voiceroid2"]["path"]!=self.path or globalconfig["reader"]["voiceroid2"]["voice"]!=self.voice or globalconfig["ttscommon"]["rate"]!=self.rate:
            self.path=globalconfig["reader"]["voiceroid2"]["path"]
            self.rate=globalconfig["ttscommon"]["rate"]
            self.voice=globalconfig["reader"]["voiceroid2"]["voice"]
            fname=str(time.time()) 
            savepath=os.path.join(os.getcwd(),'cache/tts',fname+'.wav')
            dllpath=os.path.join(os.getcwd(),'files/voiceroid2/aitalked.dll')
            exepath=os.path.join(os.getcwd(),'files/voiceroid2/voice2.exe')
            self.savepath=savepath

            try:
                self.engine.kill()
            except:
                pass
            t=time.time()
            t= str(t) 
            pipename='\\\\.\\Pipe\\voiceroid2_'+t
            waitsignal='voiceroid2waitload_'+t
            #self.engine=subproc(f'./files/x64_x86_dll/jbj7.exe "{self.dllpath}"'+dictpath,stdin=subprocess.PIPE,name='jbj', stdout=subprocess.PIPE ,encoding='utf-16-le')
            self.engine=subproc(f'"{exepath}" "{globalconfig["reader"]["voiceroid2"]["path"]}" "{dllpath}" {globalconfig["reader"]["voiceroid2"]["voice"]} 1 {(globalconfig["ttscommon"]["rate"]+10.0)/(20.0)*1+0.5} "{savepath}"  {pipename} {waitsignal}',name='voicevoid2')
            #!!!!!!!!!!!!!!stdout=subprocess.PIPE 之后，隔一段时间之后，exe侧writefile就写不进去了！！！！！不知道为什么！！！
           
            secu=win32utils.get_SECURITY_ATTRIBUTES()
            win32utils.WaitForSingleObject(win32utils.CreateEvent(win32utils.pointer(secu),False, False, waitsignal),win32utils.INFINITE); 
            win32utils.WaitNamedPipe(pipename,win32con.NMPWAIT_WAIT_FOREVER)
            self.hPipe = win32utils.CreateFile( pipename, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                    None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
    def read(self,content):
        threading.Thread(target=self.read_t,args=(content,)).start()
    def read_t(self,content):  
        if len(content)==0:
            return
        if len(self.voicelist)==0:
            return 
        if globalconfig['reader']['voiceroid2']['voice'] not in self.voicelist:
            return
        i=self.voicelist.index(globalconfig['reader']['voiceroid2']['voice'])
         
        self.checkpath()
        #def _():
        if True:     
                     
            try:
                content.encode('shift-jis')
            except:
                return
            code1=content.encode('shift-jis') 
            #print(code1)
            win32utils.WriteFile(self.hPipe,code1)
            _=win32utils.ReadFile(self.hPipe,1024,None)
            #print(_)
            fname=_[1].decode('utf8')
            print('++++',fname,'+++++')
            print(os.path.exists(fname))
            if os.path.exists(fname):
                self.mp3playsignal.emit(fname,globalconfig["ttscommon"]["volume"])
             