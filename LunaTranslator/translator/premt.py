from traceback import print_exc
import requests 
from translator.basetranslator import basetrans
from utils.config import globalconfig,translatorsetting
import os
import json
import sqlite3
import Levenshtein
class TS(basetrans):  
    def checkfilechanged(self,p):
        if self.path!=p:
            if os.path.exists(self.path):
                    self.sql=sqlite3.connect(self.path,check_same_thread=False)
            
    def inittranslator(self):
        self.path=''
        js=translatorsetting[self.typename]
        self.checkfilechanged(js['args']['sqlite文件'])
    def translate(self,content): 
        js=translatorsetting[self.typename]
        self.checkfilechanged(js['args']['sqlite文件'])
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