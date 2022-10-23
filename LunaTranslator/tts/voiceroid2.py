    
from utils.config import globalconfig  
import subprocess
import time
import os
import threading
import  multiprocessing
from PyQt5.QtCore import QProcess
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
         
        
        #def _():
        if True:     
                    
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
            dllpath=os.path.join(os.getcwd(),'files/voiceroid2/aitalked.dll')
            exepath=os.path.join(os.getcwd(),'files/voiceroid2/voice2.exe')
            print(f'"{exepath}" "{globalconfig["reader"]["voiceroid2"]["path"]}" "{dllpath}" {globalconfig["reader"]["voiceroid2"]["voice"]} 1 {(globalconfig["ttscommon"]["rate"]+10.0)/(20.0)*1+0.5} "{savepath}" {shift}')
            # self.speaking=subprocess.run(f'"{exepath}" "{globalconfig["reader"]["voiceroid2"]["path"]}" "{dllpath}" {globalconfig["reader"]["voiceroid2"]["voice"]} 1 {(globalconfig["ttscommon"]["rate"]+10.0)/(20.0)*1+0.5} "{savepath}" {shift}',shell=True,  startupinfo=st,cwd= globalconfig["reader"]["voiceroid2"]["path"])
            # self.speaking=None
            # self.mp3playsignal.emit(savepath,globalconfig["ttscommon"]["volume"])
            if os.path.exists('./tmp')==False:
                os.mkdir('./tmp')
            with open('./tmp/voiceroid2.bat','w',encoding='utf8') as ff:
                
                ff.write('taskkill /im voice2.exe /F\n' f'"{exepath}" "{globalconfig["reader"]["voiceroid2"]["path"]}" "{dllpath}" {globalconfig["reader"]["voiceroid2"]["voice"]} 1 {(globalconfig["ttscommon"]["rate"]+10.0)/(20.0)*1+0.5} "{savepath}" {shift}'+'\n+exit')
            
            subprocess.run("taskkill /im voice2.exe /F",startupinfo=st)
            import win32api 
            win32api.WinExec(f'"{exepath}" "{globalconfig["reader"]["voiceroid2"]["path"]}" "{dllpath}" {globalconfig["reader"]["voiceroid2"]["voice"]} 1 {(globalconfig["ttscommon"]["rate"]+10.0)/(20.0)*1+0.5} "{savepath}" {shift}',0)
             
            #subprocess.Popen('tmp\\voiceroid2.bat' ,shell=True,startupinfo=st )
        #threading.Thread(target=_).start()
         