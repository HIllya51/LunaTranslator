from utils.config import globalconfig
import sqlite3,os
import Levenshtein,re
from utils.argsort import argsort
import xml.etree.ElementTree as ET  
from traceback import print_exc
class jmdict():
    def __init__(self):
        return
        self.sql=None
        try:
            path=(globalconfig['jmdict']['path'] )
            if os.path.exists(path):
                self.xml= ET.parse(globalconfig['jmdict']['path']) 
        except:
            print_exc()
    
    def search(self,word):
         
            try:
                 
                dis=9999
                dis=[]
                savew=[]
                for w in self.save: 
                    if word in w or w in word:
                        d=Levenshtein.distance(w,word)
                        dis.append(d)
                        savew.append(w)
                saveres=[]
                srt=argsort(dis) 
                for ii in srt: 
                    saveres.append(savew[ii]+'<br>'+re.sub('/EntL.*/','', self.save[savew[ii]][1:]))
                    if len(saveres)>=10:
                        break
                return '<hr>'.join(saveres)
            except: 
                print_exc()
                return None
         