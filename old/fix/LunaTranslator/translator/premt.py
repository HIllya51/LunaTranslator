from traceback import print_exc
import requests 
from translator.basetranslator import basetrans
from utils.config import globalconfig,translatorsetting
import os
import json
import sqlite3
import Levenshtein
class TS(basetrans): 
    def __init__(self,rootobject) :
        super(TS,self).__init__()
        self.rootbobject=rootobject 
    def inittranslator(self):
        js=translatorsetting[self.typename]
        if js['args']['sqlite文件']=="":
            return '未指定文件'
        else:
            self.path = js['args']['sqlite文件']   
            try:
                if os.path.exists(self.path):
                    self.sql=sqlite3.connect(self.path,check_same_thread=False)
            except:
                return '无效文件' 
    def translate(self,content): 
        js=translatorsetting[self.typename]
        if js['args']['sqlite文件']!="":
             
            if self.path!= js['args']['sqlite文件']  :
                self.path = js['args']['sqlite文件']  
                try:
                    if os.path.exists(self.path):
                        self.sql=sqlite3.connect(self.path,check_same_thread=False)
                except:
                    return '无效文件'
        else:
            return '未指定文件'
        if globalconfig['premtsimiuse']:
            mindis=9999999
            savet="{}"
            ret=self.sql.execute(f'SELECT source,machineTrans FROM artificialtrans  ').fetchall()
            for jc,mt in ret:
                dis=Levenshtein.distance(content,jc)  
                if dis<mindis:
                    mindis=dis
                    if mindis<globalconfig['premtsimi']:
                        savet=mt
            return json.loads(savet)
        else:

            try:
                ret=self.sql.execute(f'SELECT machineTrans FROM artificialtrans WHERE source = "{content}"').fetchone()
            
                ret=json.loads(ret[0]) 
                return ret 
            except:
                print_exc()
                return {}
             
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')