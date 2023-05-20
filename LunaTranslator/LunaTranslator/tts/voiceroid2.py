    
from utils.config import globalconfig   
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
        
        self.checkpath()
    def getvoicelist(self):
        voicelist=[]
        if os.path.exists(self.config['path'])==False:
            return []
        l=os.listdir(os.path.join(self.config['path'],'Voice'))
         
        for _ in l:
            if '_' in _ :
                _l=_.split('_') 
                if len(_l)>=2:
                    if _l[-1]=='44':
                        voicelist.append(_)
        return voicelist
    def voiceshowmap(self,voice):
        name=voice.split('_')[0]
        jpname={
            'yukari':'結月ゆかり',
            'akari':'紲星あかり',
            'kiritan':'東北きりたん',
            'itako':'東北イタコ',
            'zunko':'東北ずん子',
            'yuzuru':'伊織弓鶴',
            'tsuina':'ついなちゃん',
            'akane':'琴葉茜',
            'aoi':'琴葉葵',
            'kou':'水奈瀬コウ',
            'sora':'桜乃そら',
            'tamiyasu':'民安ともえ',
            'ai':'月読アイ',
            'shouta':'月読ショウタ',
            'seika':'京町セイカ',
            'una':'音街ウナ',
            'yoshidakun':'鷹の爪吉田',
            'galaco':'ギャラ子'
        }
        vv=jpname[name]
        if 'west' in voice:
            vv+='（関西弁）'
        return vv
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
            ##dllpath=r'C:\Users\wcy\Downloads\zunko\aitalked.dll'
            exepath=os.path.join(os.getcwd(),'files/plugins/shareddllproxy32.exe')
            self.savepath=savepath


            t=time.time()
            t= str(t) 
            pipename='\\\\.\\Pipe\\voiceroid2_'+t
            waitsignal='voiceroid2waitload_'+t
            def linear_map(x): 
                if x >= 0 :
                    x= 0.1 * x + 1.0
                else:
                    x= 0.05 * x+ 1.0
                return x
            self.engine=subproc_w(f'"{exepath}" voiceroid2 "{self.config["path"]}" "{dllpath}" {self.config["voice"]} 44100 {linear_map(globalconfig["ttscommon"]["rate"])} "{savepath}"  {pipename} {waitsignal}',name='voicevoid2')
            
            win32utils.WaitForSingleObject(win32utils.CreateEvent(False, False, waitsignal),win32utils.INFINITE); 
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
        
             