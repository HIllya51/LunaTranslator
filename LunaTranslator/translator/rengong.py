 
import requests 
from translator.basetranslator import basetrans
from utils.config import globalconfig
import os
import json
import sqlite3

class TS(basetrans): 
    def __init__(self,rootobject) :
        super(TS,self).__init__()
        self.rootbobject=rootobject
    @classmethod
    def defaultsetting(self):
        return {
            "args": {
                "sqlite文件": "" 
            } 
        }
    def inittranslator(self):
        configfile=globalconfig['fanyi'][self.typename]['argsfile']
        
        if os.path.exists(configfile) ==False:
            return ''
        
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
            
        if js['args']['sqlite文件']=="":
            return ''
        else:
            self.path = js['args']['sqlite文件']  
            try:
                self.sql=(sqlite3.connect( self.path ,check_same_thread = False))
            except:
                return ''
    def translate(self,content): 
        configfile=globalconfig['fanyi'][self.typename]['argsfile'] 
        if os.path.exists(configfile) ==False:
            return ''
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        sqls=[]
        if js['args']['sqlite文件']!="":
             
            if self.path!= js['args']['sqlite文件']  :
                self.path = js['args']['sqlite文件']  
                try:
                    self.sql=sqlite3.connect( self.path ,check_same_thread = False)
                    
                except:
                    return '无效的sqlite文件' 
        try:
            sqls+=[self.sql]
        except:
            pass
        if 'sqlwrite' in dir(self.rootbobject.textsource):
            sqls+=[self.rootbobject.textsource.sqlwrite]
         
        for sql in sqls:
            ret=sql.execute(f'SELECT * FROM artificialtrans WHERE source = "{content}"').fetchone()
            
            if ret is  None: 
                continue
            else:  
                _id,source,mt,ut=ret 
               
                if ut!='':
                    return ut
                elif mt!='':
                    return mt 
        return '无预翻译'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')