from utils.config import globalconfig
import sqlite3
import winsharedutils 
import os
from traceback import print_exc
class linggesi():
    def __init__(self):
        self.sql=None
        try:
            if os.path.exists(os.path.join(globalconfig['cishu']['linggesi']['path'] ,'ja-zh.db'))==False or \
                os.path.exists(os.path.join(globalconfig['cishu']['linggesi']['path'] ,'ja-zh-gbk.db'))==False:
                return 
            self.sql=sqlite3.connect(os.path.join(globalconfig['cishu']['linggesi']['path'] ,'ja-zh.db'),check_same_thread=False)
            self.sql2=sqlite3.connect(os.path.join(globalconfig['cishu']['linggesi']['path'] ,'ja-zh-gbk.db'),check_same_thread=False)
        except:
            pass
    def end(self):
        self.sql.close()
        self.sql2.close()
    def search(self,word):
         
                mp={}
                for sql in [self.sql,self.sql2]:
                    x=sql.execute(f"select word,content from entry where word like '%{word}%'")
                    exp=x.fetchall()
                     
                    
                    for w,xx in exp:
                        
                        d=winsharedutils.distance(w,word) 
                        mp[w]=[xx,d]
                         

                        
                        
                x=sorted(list(mp.keys()),key=lambda x: mp[x][1])[:10]
                save=[w+'<br>'+mp[w][0] for w in x]
                return '<hr>'.join(save)
             