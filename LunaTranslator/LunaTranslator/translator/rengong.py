  
from translator.basetranslator import basetrans
from utils.config import globalconfig
import os
import json 
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
        self.checkfilechanged(self.config['args']['json文件'] )
    def translate(self,content):  
        self.checkfilechanged(self.config['args']['json文件'] )
       
        js=self.json
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for jc in self.json:
                dis=Levenshtein.distance(content,jc) 
                if dis<mindis:
                    mindis=dis
                    if mindis<globalconfig['premtsimi']: 
                        if self.config[jc]['userTrans'] and self.config[jc]['userTrans']!='':
                            savet=self.config[jc]['userTrans']
                        
                        elif self.config[jc]['machineTrans'] and self.config[jc]['machineTrans']!='':
                            savet= self.config[jc]['machineTrans']
            return savet
        else:
        
            if self.config[content]['userTrans'] and self.config[content]['userTrans']!='':
                return self.config[content]['userTrans']
            
            elif self.config[content]['machineTrans'] and self.config[content]['machineTrans']!='':
                return self.config[content]['machineTrans']
                 