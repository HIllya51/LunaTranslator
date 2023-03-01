from utils.config import globalconfig
import sqlite3,os
import Levenshtein
from utils.utils import argsort
class xiaoxueguan():
    def __init__(self):
        self.sql=None
        try:
            path=(globalconfig['cishu']['xiaoxueguan']['path'] )
            if os.path.exists(path):
                self.sql=sqlite3.connect( path,check_same_thread=False) 
        except:
            pass
    def end(self):
        self.sql.close()
    def search(self,word): 
            
                x=self.sql.execute(f"select word,explanation from xiaoxueguanrizhong where word like '%{word}%'")
                exp=x.fetchall()
                dis=9999
                save=[]
                dis=[]
                for w,xx in exp:
                
                    d=Levenshtein.distance(w,word)
                    dis.append(d)
                     
                srt=argsort(dis)[:10]
                save=['<span h>'+exp[i][1].replace('\\n','') for i in srt]
                return '<hr>'.join(save)
             