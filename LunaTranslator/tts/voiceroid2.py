    
from utils.config import globalconfig   
import time
import os ,threading
from traceback import print_exc
class tts():
    
    def __init__(self,showlist ,mp3playsignal,tm): 
        
       
        self.tm=tm
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
    def read(self,content):  
        if len(content)==0:
            return
        if len(self.voicelist)==0:
            return 
        if globalconfig['reader']['voiceroid2']['voice'] not in self.voicelist:
            return
        i=self.voicelist.index(globalconfig['reader']['voiceroid2']['voice'])
         
        
        #def _():
        if True:     
                     
            shift=''
            try:
                for _ in content.encode('shift-jis'):
                    shift+=' '+str(int(_))
            except:
                return

            fname=str(time.time()) 
            savepath=os.path.join(os.getcwd(),'ttscache',fname+'.wav')
            dllpath=os.path.join(os.getcwd(),'files/voiceroid2/aitalked.dll')
            exepath=os.path.join(os.getcwd(),'files/voiceroid2/voice2.exe')
            
            import win32pipe, win32file,win32con
            try:
                win32pipe.WaitNamedPipe("\\\\.\\Pipe\\newsentence"+self.tm,win32con.NMPWAIT_WAIT_FOREVER)
                hPipe = win32file.CreateFile( "\\\\.\\Pipe\\newsentence"+self.tm, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                        None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
                win32file.WriteFile(hPipe,f'"{exepath}" "{globalconfig["reader"]["voiceroid2"]["path"]}" "{dllpath}" {globalconfig["reader"]["voiceroid2"]["voice"]} 1 {(globalconfig["ttscommon"]["rate"]+10.0)/(20.0)*1+0.5} "{savepath}" {shift}'.encode('utf8'))
            except:
                print_exc()
            #subprocess.Popen('tmp\\voiceroid2.bat' ,shell=True,startupinfo=st )
        #threading.Thread(target=_).start()
            def waitfile(): 
                while True: 
                    if os.path.exists(savepath):
                        self.mp3playsignal.emit(savepath,globalconfig["ttscommon"]["volume"])
                        break
                    time.sleep(0.05)
            threading.Thread(target=waitfile).start()
            