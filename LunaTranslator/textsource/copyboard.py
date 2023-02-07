 
import time  
from textsource.textsourcebase import basetext
import pyperclip,ctypes,win32process,os
class copyboard(basetext):
    def __init__(self,textgetmethod,_) -> None:
        self.last_paste_str = '' 
        
        self.ending=False
        self.typename='copy'
    
        self.md5='0' 
        self.prefix='0_copy'
        super(copyboard,self).__init__(textgetmethod)
    
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