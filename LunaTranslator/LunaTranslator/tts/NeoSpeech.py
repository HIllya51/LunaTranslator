    
from myutils.config import globalconfig   
import time
import os 
import windows
from traceback import print_exc
from tts.basettsclass import TTSbase 
import ctypes
from myutils.subproc import subproc_w,autoproc
class TTS(TTSbase): 
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
            
        self.engine=autoproc(subproc_w('"{}" neospeech  {} {}  "{}"'.format(exepath,pipename,waitsignal,savepath),name='neospeech'))
        
        windows.WaitForSingleObject(windows.AutoHandle(windows.CreateEvent(False, False, waitsignal)),windows.INFINITE); 
        windows.WaitNamedPipe(pipename,windows.NMPWAIT_WAIT_FOREVER)
        self.hPipe = windows.AutoHandle(windows.CreateFile( pipename, windows.GENERIC_READ | windows.GENERIC_WRITE, 0,
                None, windows.OPEN_EXISTING, windows.FILE_ATTRIBUTE_NORMAL, None))
    def getvoicelist(self):
        
        return ['VW Misaki']
           
         
    def speak(self,content,rate,voice,voice_idx):    
            windows.WriteFile(self.hPipe,bytes(ctypes.c_uint(rate)))
            windows.WriteFile(self.hPipe,content.encode('utf-16-le'))
            fname=windows.ReadFile(self.hPipe,1024,None).decode('utf-16-le')
            if os.path.exists(fname):
                return(fname)
        
             