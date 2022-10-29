 
import requests 
from translator.basetranslator import basetrans
from utils.config import globalconfig,syncconfig
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
                "sqlite文件": "" ,
                
            } 
        }
    def inittranslator(self):
        configfile=globalconfig['fanyi'][self.typename]['argsfile']
        self.path=''
        if os.path.exists(configfile) ==False:
            return ''
        
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        syncconfig(js,self.defaultsetting())
        if js['args']['sqlite文件']=="":
            return ''
        else:
            self.path = js['args']['sqlite文件']  
            try:
                try:
                    if os.path.exists(self.path):
                        self.sql=sqlite3.connect(self.path,check_same_thread=False)
                except:
                    return '无效文件'
            except:
                return ''
    def translate(self,content): 
        configfile=globalconfig['fanyi'][self.typename]['argsfile'] 
        if os.path.exists(configfile) ==False:
            return ''
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        syncconfig(js,self.defaultsetting())
       #sqls=[]
         
        if js['args']['sqlite文件']!="":
             
            if self.path!= js['args']['sqlite文件']  :
                self.path = js['args']['sqlite文件']  
                try:
                    if os.path.exists(self.path):
                        self.sql=sqlite3.connect(self.path,check_same_thread=False)
                except:
                    return '无效文件'
        
        # for sql in sqls:
        try:
            ret=self.sql.execute(f'SELECT machineTrans FROM artificialtrans WHERE source = "{content}"').fetchone()
        except:
            return ''
        if ret:
            ret=json.loads(ret[0])
            
            return ret 
        else:
            return {}
             
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')