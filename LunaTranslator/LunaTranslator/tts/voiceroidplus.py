    
from utils.config import globalconfig   ,_TR
import time
import os ,threading,win32utils,win32con
from traceback import print_exc
from tts.basettsclass import TTSbase 

from utils.subproc import subproc_w
class TTS(TTSbase):
    def end(self):
        try:
            self.engine.kill()
        except:
            pass
    def init(self): 
        self.path=''
        self.voice=''
        self.rate=''
        
        self.voicelist=self.getvoicelist()
        if  globalconfig['reader'][self.typename]['voice'] not in self.voicelist:  
            globalconfig['reader'][self.typename]['voice']=self.voicelist[0]
        
        #self.checkpath()
    def getvoicelist(self):
        voicelist=[]
        if os.path.exists(self.config['path'])==False:
            return []
        l=os.listdir(os.path.join(self.config['path'],'Voice'))
        for _ in l:
            if _!='index.dat':
                voicelist.append(_)
                
        if voicelist[0] not in ['kiritan_22','zunko_22','akane_22','aoi_22']:           
            voicelist=[_TR("错误")+" "+_TR("不支持的版本")] 
        return voicelist
          
    def checkpath(self):
        if self.config["path"]=="":
            return False
        if os.path.exists(self.config["path"])==False:
            return False
        if   self.config["path"]!=self.path or self.config["voice"]!=self.voice or globalconfig["ttscommon"]["rate"]!=self.rate:
            self.path=self.config["path"]
            self.rate=globalconfig["ttscommon"]["rate"]
            self.voice=self.config["voice"]
            fname=str(time.time()) 
            savepath=os.path.join(os.getcwd(),'cache/tts',fname+'.wav')
            dllpath=os.path.join(self.path,'aitalked.dll') 
            
            exepath=os.path.join(os.getcwd(),'files/plugins/shareddllproxy32.exe')
            self.savepath=savepath


            t=time.time()
            t= str(t) 
            pipename='\\\\.\\Pipe\\voiceroid2_'+t
            waitsignal='voiceroid2waitload_'+t
            #速率不可调
            self.engine=subproc_w(f'"{exepath}" voiceroid2 "{self.config["path"]}" "{dllpath}" {self.config["voice"]} 22050 0 "{savepath}"  {pipename} {waitsignal}',name='voicevoid2') 
            
            secu=win32utils.get_SECURITY_ATTRIBUTES()
            win32utils.WaitForSingleObject(win32utils.CreateEvent(win32utils.pointer(secu),False, False, waitsignal),win32utils.INFINITE); 
            win32utils.WaitNamedPipe(pipename,win32con.NMPWAIT_WAIT_FOREVER)
            self.hPipe = win32utils.CreateFile( pipename, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                    None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
    def speak(self,content,rate,voice,voice_idx):  
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
            
            fname=win32utils.ReadFile(self.hPipe,1024,None).decode('utf8')
            if os.path.exists(fname):
                return(fname)
        