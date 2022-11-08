
import os
import time 
import pyperclip
import json,sqlite3,threading
from traceback import print_exc
from textsource.textsourcebase import basetext
class copyboard(basetext):
    def __init__(self,textgetmethod) -> None:
        self.last_paste_str = '' 
        
        self.ending=False
        self.typename='copy'
    
        self.md5='0'
        self.sqlfname='./transkiroku/0_copy.sqlite'
        self.sqlfname_all='./transkiroku/0_copy.premt_synthesize.sqlite'
        self.jsonfname='./transkiroku/0_copy.json'
            
        super(copyboard,self).__init__(textgetmethod)
    
    def gettextthread(self ):
                 
            time.sleep(0.1)
            paste_str = pyperclip.paste()
            if self.last_paste_str != paste_str:
                self.last_paste_str =paste_str
                return (paste_str)
    def runonce(self):
        paste_str = pyperclip.paste() 
        self.textgetmethod(paste_str,False)