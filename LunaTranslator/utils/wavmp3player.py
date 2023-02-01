import os

class wavmp3player( ):
    def __init__(self):
        self.i=0
    def mp3playfunction(self,path,volume):
        if os.path.exists(path)==False:
            return 
        self._playsoundWin(path,volume)
    def _playsoundWin(self,sound,volume ): 
        from ctypes import  windll 
        from sys    import getfilesystemencoding
        
        try:
            windll.winmm.mciSendStringA((f"stop lunatranslator_mci_{self.i}").encode(getfilesystemencoding()), 0, 0, 0);
            windll.winmm.mciSendStringA((f"close lunatranslator_mci_{self.i}").encode(getfilesystemencoding()), 0, 0, 0);
            self.i+=1 

            windll.winmm.mciSendStringA(f'open "{sound}" alias lunatranslator_mci_{self.i}'.encode(getfilesystemencoding()), 0, 0, 0);  
            windll.winmm.mciSendStringA(f'setaudio lunatranslator_mci_{self.i} volume to {volume*10}'.encode(getfilesystemencoding()), 0, 0, 0); 
            windll.winmm.mciSendStringA((f'play lunatranslator_mci_{self.i}').encode(getfilesystemencoding()),0,0,0)
            
        except:
            pass