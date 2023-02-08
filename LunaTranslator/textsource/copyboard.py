 
import time  
from textsource.textsourcebase import basetext
import pyperclip,ctypes,win32process,os
class copyboard(basetext):
    def __init__(self,textgetmethod) -> None:
        self.last_paste_str = '' 
          
        super(copyboard,self).__init__(textgetmethod,'0','0_copy')
    
    def gettextthread(self ):
                 
            time.sleep(0.1)
            paste_str = pyperclip.paste()
            
            if self.last_paste_str != paste_str:
                self.last_paste_str =paste_str 
                if win32process.GetWindowThreadProcessId(ctypes.windll.user32.GetClipboardOwner())[1]==os.getpid():
                    return  
                return (paste_str)
    def runonce(self): 
        self.textgetmethod(pyperclip.paste(),False)