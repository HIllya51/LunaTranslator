    
from utils.config import globalconfig 
import time 
 
import threading
from win32com.client import Dispatch
import ctypes 
class tts():
    
    def __init__(self,showlist ): 
         
        ctypes.windll.ole32.CoInitialize()
        self.Windows_Speak = Dispatch('SAPI.Spvoice')
        self.voicelist=[]
        try:
            for i in range(99999): 
                    self.voicelist.append(self.Windows_Speak.GetVoices().Item(i).GetDescription()) #just to see what voice is used
                    
        except:
            pass 
        ctypes.windll.ole32.CoUninitialize()
        showlist.emit(self.voicelist)
    def read(self,content,rate=1):
        print('reading',content)
        i=self.voicelist.index(globalconfig['windowstts']['voice'])
        if i==-1:
            return 
        self.Windows_Speak.Voice = self.Windows_Speak.GetVoices().Item(i)
        self.Windows_Speak.Rate=float(globalconfig['windowstts']['rate'])
        self.Windows_Speak.Volume=float(globalconfig['windowstts']['volume'])
        
        print(dir(self.Windows_Speak))
        threading.Thread(target=self.Windows_Speak.Speak,args=(content,)).start() 
      