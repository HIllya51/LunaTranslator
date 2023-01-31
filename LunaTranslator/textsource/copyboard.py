 
import time 
from PyQt5.QtWidgets import  QApplication 
from textsource.textsourcebase import basetext
class copyboard(basetext):
    def __init__(self,textgetmethod) -> None:
        self.last_paste_str = '' 
        
        self.ending=False
        self.typename='copy'
    
        self.md5='0' 
        self.prefix='0_copy'
        super(copyboard,self).__init__(textgetmethod)
    
    def gettextthread(self ):
                 
            time.sleep(0.1)
            paste_str = QApplication.clipboard().text()
            if self.last_paste_str != paste_str:
                self.last_paste_str =paste_str
                return (paste_str)
    def runonce(self):
        paste_str =QApplication.clipboard().text()
        self.textgetmethod(paste_str,False)