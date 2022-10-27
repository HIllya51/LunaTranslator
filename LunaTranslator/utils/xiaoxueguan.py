from utils.config import globalconfig
import sqlite3
import Levenshtein
class xiaoxueguan():
    def __init__(self):
        self.sql=None
        try:
            self.sql=sqlite3.connect(globalconfig['xiaoxueguan']['path'],check_same_thread=False)
        except:
            pass
    def search(self,word):
        if self.sql:
            try:
                x=self.sql.execute(f"select word,explanation from xiaoxueguanrizhong where word like '%{word}%'")
                exp=x.fetchall()
                dis=9999
                save=None
                
                for w,xx in exp:
                
                    d=Levenshtein.distance(w,word)
                    if d<dis:
                        dis=d
                        save=xx
            
                return save.replace('\\n','')
            except:
                return None
        else:
            return None