
from utils.subproc import subproc_w
from utils.config import globalconfig  
import threading
class tts():
    
    def __init__(self,showlist ,_): 
                 
        p=subproc_w('./files/tts/tts_l.exe',needstdio=True)
        
        count=str(p.stdout.readline(),encoding='utf8')
        count=count.replace('\r','').replace('\n','')
        count=int(count)
        self.voicelist=[]
        for i in range(count):

             
            res=str(p.stdout.readline(),encoding='utf8').replace('\r','').replace('\n','')
            self.voicelist.append(res.split('\\')[-1]) 
        showlist.emit(self.voicelist)
        if  len(self.voicelist)>0 and globalconfig['reader']['windowstts']['voice'] not in self.voicelist:  
            globalconfig['reader']['windowstts']['voice']=self.voicelist[0]
            
    def read(self,content):
        threading.Thread(target=self.read_t,args=(content,)).start()
    def read_t(self,content): 
        if len(content)==0:
            return
        if len(self.voicelist)==0:
            return 
        if globalconfig['reader']['windowstts']['voice'] not in self.voicelist:
            return
        i=self.voicelist.index(globalconfig['reader']['windowstts']['voice'])
          

        subproc_w(f'./files/tts/tts_s.exe {i} {globalconfig["ttscommon"]["rate"]} {globalconfig["ttscommon"]["volume"]} "{content}"',name="windowstts" )
        
      