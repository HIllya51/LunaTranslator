 
import requests 
from translator.basetranslator import basetrans
from utils.config import globalconfig
import os
import json
import sqlite3

class TS(basetrans): 
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
            
        if js['args']['sqlite文件']=="":
            return '未指定sqlite文件'
        else:
            if self.path!= js['args']['sqlite文件']  :
                self.path = js['args']['sqlite文件']  
            try:
                self.sql=(sqlite3.connect( self.path ,check_same_thread = False))
            except:
                return '无效的sqlite文件' 
        ret=self.sql.execute(f'SELECT * FROM artificialtrans WHERE source = "{content}"').fetchone()
        if ret is  None: 
            return '无预翻译'
        else:  
            _id,source,mt,ut=ret

            if ut!='':
                return ut
            elif mt!='':
                return mt 
            else:
                return '无预翻译'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')