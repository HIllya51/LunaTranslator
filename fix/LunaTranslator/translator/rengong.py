 
import requests 
from translator.basetranslator import basetrans
from utils.config import translatorsetting ,globalconfig
import os
import json
import sqlite3
import Levenshtein
class TS(basetrans): 
    def checkfilechanged(self,p):
        if self.path!=p:
            if os.path.exists(p):
                with open(p,'r',encoding='utf8') as f:
                    self.json=json.load(f)
                self.path=p
    def inittranslator(self):
        self.path=''
        js=translatorsetting[self.typename]
        self.checkfilechanged(js['args']['json文件'] )
    def translate(self,content): 
        js=translatorsetting[self.typename]
        self.checkfilechanged(js['args']['json文件'] )
       
        js=self.json
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for jc in self.json:
                dis=Levenshtein.distance(content,jc) 
                if dis<mindis:
                    mindis=dis
                    if mindis<globalconfig['premtsimi']: 
                        if js[jc]['userTrans'] and js[jc]['userTrans']!='':
                            savet=js[jc]['userTrans']
                        
                        elif js[jc]['machineTrans'] and js[jc]['machineTrans']!='':
                            savet= js[jc]['machineTrans']
            return savet
        else:
        
            if js[content]['userTrans'] and js[content]['userTrans']!='':
                return js[content]['userTrans']
            
            elif js[content]['machineTrans'] and js[content]['machineTrans']!='':
                return js[content]['machineTrans']
                
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')