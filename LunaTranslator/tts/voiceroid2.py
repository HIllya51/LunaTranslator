    
from utils.config import globalconfig  
import subprocess
import time
import os
import threading
class tts():
    
    def __init__(self,showlist ,mp3playsignal): 
        
       
        
        self.voicelist=[]
        if os.path.exists(globalconfig['reader']['voiceroid2']['path'])==False:
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
         
        
        def _():
            if self.speaking:
                self.speaking.kill()
                    
            st=subprocess.STARTUPINFO()
            st.dwFlags=subprocess.STARTF_USESHOWWINDOW
            st.wShowWindow=subprocess.SW_HIDE

            shift=''
            for _ in content.encode('shift-jis'):
                shift+=' '+str(int(_))
            fname=str(time.time())
            if os.path.exists('./ttscache/')==False:
                os.mkdir('./ttscache/')
            
            savepath=os.path.join(os.getcwd(),'ttscache',fname+'.wav')

            self.speaking=subprocess.run(f'./files/voiceroid2/voice2.exe "{globalconfig["reader"]["voiceroid2"]["path"]}" ./files/voiceroid2/aitalked.dll {globalconfig["reader"]["voiceroid2"]["voice"]} 1 {(globalconfig["ttscommon"]["rate"]+10.0)/(20.0)*1+0.5} "{savepath}" {shift}', startupinfo=st )
            self.speaking=None
            self.mp3playsignal.emit(savepath,globalconfig["ttscommon"]["volume"])
        threading.Thread(target=_).start()