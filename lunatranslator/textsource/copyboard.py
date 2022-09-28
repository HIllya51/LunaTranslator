
from threading import Thread
import time 
import pyperclip
from textsource.textsourcebase import basetext
class copyboard(basetext):
    def __init__(self,textgetmethod) -> None:
        self.last_paste_str = '' 
        
        self.ending=False
        self.typename='copy'
        super(copyboard,self).__init__(textgetmethod)
    
    def gettextthread(self ):
                 
            time.sleep(0.1)
            paste_str = pyperclip.paste()
            if self.last_paste_str != paste_str:
                self.last_paste_str =paste_str
                self.textgetmethod(paste_str)
    def runonce(self):
        paste_str = pyperclip.paste() 
        self.textgetmethod(paste_str)