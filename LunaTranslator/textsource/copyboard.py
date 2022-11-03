
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
        try:
             
            self.md5='0'
            self.sqlfname='./transkiroku/0_0.sqlite'
            self.sqlfname_all='./transkiroku/0_0.premt_synthesize.sqlite'
            self.jsonfname='./transkiroku/0_0.json'
            def loadjson(self):
                if os.path.exists(self.jsonfname):
                    with open(self.jsonfname,'r',encoding='utf8') as ff:
                        self.json=json.load(ff)
                else:
                    self.json={}
            threading.Thread(target=loadjson,args=(self,)).start()
            self.sqlwrite=sqlite3.connect(self.sqlfname,check_same_thread = False)
            self.sqlwrite2=sqlite3.connect(self.sqlfname_all,check_same_thread = False)
            try:
                self.sqlwrite.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT,userTrans TEXT);')
            except:
                pass
            try:
                self.sqlwrite2.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT);')
            except:
                pass
        except:
            print_exc()
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