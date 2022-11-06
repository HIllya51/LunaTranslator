    
from utils.config import globalconfig   
import time
import os 
from traceback import print_exc
import subprocess
import requests,json,threading
voicevoxprocess=None
from utils.subproc import subproc
class tts():
     
    def __init__(self,showlist ,mp3playsignal): 
        global voicevoxprocess
        if voicevoxprocess:
            voicevoxprocess.kill()
            voicevoxprocess=None
          
        self.voicelist=[]
        showlist.emit(self.voicelist)
        if os.path.exists(globalconfig['reader']['voicevox']['path'])==False or \
            os.path.exists(os.path.join(globalconfig['reader']['voicevox']['path'],'run.exe'))==False   :
            return
        voicevoxprocess=subproc(os.path.join(globalconfig['reader']['voicevox']['path'],'run.exe'),cwd=globalconfig['reader']['voicevox']['path'] ,keep=True)
        
        while True:
            try:
                  

                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive', 
                    'Pragma': 'no-cache',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52',
                    'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }

                response = requests.get('http://127.0.0.1:50021/speakers',  headers=headers,proxies={'http':None,'https':None}).json()
                
            except:

                time.sleep(1)
            break
        self.voicelist=[_['name'] for _ in response]
        showlist.emit(self.voicelist)
        if  len(self.voicelist)>0 and globalconfig['reader']['voicevox']['voice'] not in self.voicelist:
            globalconfig['reader']['voicevox']['voice']=self.voicelist[0]
        if  len(self.voicelist)>0 and globalconfig['reader']['voicevox']['voice'] not in self.voicelist:
            globalconfig['reader']['voicevox']['voice']=self.voicelist[0]
        self.speaking=None
        self.mp3playsignal=mp3playsignal
    def read(self,content):
        threading.Thread(target=self.read_t,args=(content,)).start()
         
    def read_t(self,content):
        if len(content)==0:
            return
        if len(self.voicelist)==0:
            return 
        if globalconfig['reader']['voicevox']['voice'] not in self.voicelist:
            return
        i=self.voicelist.index(globalconfig['reader']['voicevox']['voice'])
         
        
        #def _():
        if True:     
                     
                        
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            params = {
                'speaker': i,
                'text':content
            }
 
            response = requests.post('http://localhost:50021/audio_query', params=params, headers=headers,  proxies={'http':None,'https':None})
            print(response.json())
            fname=str(time.time())
            if os.path.exists('./ttscache/')==False:
                os.mkdir('./ttscache/') 
            headers = {
                'Content-Type': 'application/json',
            } 
            params = {
                'speaker': i,
            }  
            response = requests.post('http://localhost:50021/synthesis', params=params, headers=headers, data=json.dumps(response.json()) )
            with open('./ttscache/'+fname+'.wav','wb') as ff:
                ff.write(response.content)
            self.mp3playsignal.emit('./ttscache/'+fname+'.wav',globalconfig["ttscommon"]["volume"])
            #subprocess.Popen('tmp\\voiceroid2.bat' ,shell=True,startupinfo=st )
        #threading.Thread(target=_).start()
         