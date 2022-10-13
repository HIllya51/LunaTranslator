    
from utils.config import globalconfig  
import subprocess
class tts():
    
    def __init__(self,showlist ,_): 
                
        st=subprocess.STARTUPINFO()
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.SW_HIDE

        p=subprocess.Popen('./files/tts/tts_l.exe',stdout=subprocess.PIPE,startupinfo=st)
        
        count=str(p.stdout.readline(),encoding='utf8')
        count=count.replace('\r','').replace('\n','')
        count=int(count)
        self.voicelist=[]
        for i in range(count):

             
            res=str(p.stdout.readline(),encoding='utf8').replace('\r','').replace('\n','')
            self.voicelist.append(res.split('\\')[-1]) 
        showlist.emit(self.voicelist)
        if globalconfig['reader']['windowstts']['voice']=='' and len(self.voicelist)>0:
            globalconfig['reader']['windowstts']['voice']=self.voicelist[0]
        self.speaking=None
    def read(self,content): 
        if len(self.voicelist)==0:
            return 
        if globalconfig['reader']['windowstts']['voice'] not in self.voicelist:
            return
        i=self.voicelist.index(globalconfig['reader']['windowstts']['voice'])
         
        if self.speaking:
            self.speaking.kill()
                
        st=subprocess.STARTUPINFO()
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.SW_HIDE

        self.speaking=subprocess.Popen(f'./files/tts/tts_s.exe {i} {globalconfig["ttscommon"]["rate"]} {globalconfig["ttscommon"]["volume"]} "{content}"',stdout=subprocess.PIPE,startupinfo=st )
        
      