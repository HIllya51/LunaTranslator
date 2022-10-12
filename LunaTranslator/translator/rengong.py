 
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
                "json文件": "" ,
                
            } 
        }
    def inittranslator(self):
        configfile=globalconfig['fanyi'][self.typename]['argsfile']
        
        if os.path.exists(configfile) ==False:
            return ''
        
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        syncconfig(js,self.defaultsetting())
        if js['args']['json文件']=="":
            return ''
        else:
            self.path = js['args']['json文件']  
            try:
                with open(self.path,'r',encoding='utf8') as f:
                    self.json=json.load(f)
                #self.sql=(sqlite3.connect( self.path ,check_same_thread = False))
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
        jsons=[]
        if js['args']['json文件']!="":
             
            if self.path!= js['args']['json文件']  :
                self.path = js['args']['json文件']  
                try:
                    with open(self.path,'r',encoding='utf8') as f:
                        self.json=json.load(f)
                except:
                    return '无效文件'
        try:
            #sqls+=[self.sql]
            jsons+=[self.json]
        except:
            pass
        # if 'sqlwrite' in dir(self.rootbobject.textsource):
        #     sqls+=[self.rootbobject.textsource.sqlwrite]
        if 'json' in dir(self.rootbobject.textsource):
            jsons+=[(self.rootbobject.textsource.json)]
        # for sql in sqls:
        #     ret=sql.execute(f'SELECT * FROM artificialtrans WHERE source = "{content}"').fetchone()
        for js in jsons:
            if content not in js: 
            #if ret is  None: 
                continue
            else:  
                #_id,source,mt,ut=ret 
                if js[content]['userTrans']!='':
                    js[content]['userTrans']
                
                elif js[content]['machineTrans']!='':
                    return js[content]['machineTrans']
        return '无预翻译'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')