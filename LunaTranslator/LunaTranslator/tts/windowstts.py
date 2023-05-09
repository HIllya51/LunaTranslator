 
import threading,time
import winsharedutils

from tts.basettsclass import TTSbase 
class TTS(TTSbase):
    def getvoicelist(self):
        return winsharedutils.SAPI_List()
    def speak(self,content,rate,voice,voice_idx):
        print("?")
        fname=str(time.time()) 
         
        winsharedutils.SAPI_Speak(content,voice_idx,rate,100,'./cache/tts/'+fname+'.wav')
        return './cache/tts/'+fname+'.wav'
     