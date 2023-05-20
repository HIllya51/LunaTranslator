    
from utils.config import globalconfig   
import time
import os ,threading,win32utils,win32con
from traceback import print_exc
from tts.basettsclass import TTSbase 
import ctypes
from utils.subproc import subproc_w
class TTS(TTSbase):
    def end(self):
        try:
            self.engine.kill()
        except:
            pass
    def init(self): 
     
        self.rate=globalconfig["ttscommon"]["rate"]
        self.voice=self.config["voice"]
        fname=str(time.time()) 
        savepath=os.path.join(os.getcwd(),'cache/tts',fname) 
        exepath=os.path.join(os.getcwd(),'files/plugins/shareddllproxy32.exe')
        self.savepath=savepath


        t=time.time()
        t= str(t) 
        pipename='\\\\.\\Pipe\\voiceroid2_'+t
        waitsignal='voiceroid2waitload_'+t
            
        self.engine=subproc_w(f'"{exepath}" neospeech  {pipename} {waitsignal}  "{savepath}"',name='neospeech')
        
        win32utils.WaitForSingleObject(win32utils.CreateEvent(False, False, waitsignal),win32utils.INFINITE); 
        win32utils.WaitNamedPipe(pipename,win32con.NMPWAIT_WAIT_FOREVER)
        self.hPipe = win32utils.CreateFile( pipename, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
    def getvoicelist(self):
        
        return ['VW Misaki']
           
         
    def speak(self,content,rate,voice,voice_idx):    
            win32utils.WriteFile(self.hPipe,bytes(ctypes.c_uint(rate)))
            win32utils.WriteFile(self.hPipe,content.encode('utf-16-le'))
            fname=win32utils.ReadFile(self.hPipe,1024,None).decode('utf-16-le')
            if os.path.exists(fname):
                return(fname)
        
             