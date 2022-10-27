from utils.config import globalconfig
import sqlite3
import Levenshtein
import numpy as np
import os
class linggesi():
    def __init__(self):
        self.sql=None
        try:
            self.sql=sqlite3.connect(os.path.join(globalconfig['linggesi']['path'] ,'ja-zh.db'),check_same_thread=False)
        except:
            pass
    def search(self,word):
        
            try:
                x=self.sql.execute(f"select word,content from entry where word like '%{word}%'")
                exp=x.fetchall()
                dis=9999
                save=[]
                dis=[]
                for w,xx in exp:
                
                    d=Levenshtein.distance(w,word)
                    dis.append(d)
                     
                srt=np.argsort(dis)[:10] 
                save=[exp[i][0]+'<br>'+exp[i][1] for i in srt]
                return '<hr>'.join(save)
            except:
                return None