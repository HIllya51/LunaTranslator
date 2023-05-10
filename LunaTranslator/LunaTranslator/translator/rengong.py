  
from translator.basetranslator import basetrans
from utils.config import globalconfig
import os
import json 
import winsharedutils
class TS(basetrans): 
    def checkfilechanged(self,p):
        if self.path!=p:
            if os.path.exists(p):
                with open(p,'r',encoding='utf8') as f:
                    self.json=json.load(f)
                self.path=p
    def inittranslator(self):
        self.path='' 
        self.checkfilechanged(self.config['json文件'] )
    def translate(self,content):  
        self.checkfilechanged(self.config['json文件'] ) 
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for jc in self.json:
                dis=winsharedutils.distance(content,jc) 
                if dis<mindis:
                    mindis=dis
                    if mindis<globalconfig['premtsimi']: 
                        if self.json[jc]['userTrans'] and self.json[jc]['userTrans']!='':
                            savet=self.json[jc]['userTrans']
                        
                        elif self.json[jc]['machineTrans'] and self.json[jc]['machineTrans']!='':
                            savet= self.json[jc]['machineTrans']
            return savet
        else:
        
            if self.json[content]['userTrans'] and self.json[content]['userTrans']!='':
                return self.json[content]['userTrans']
            
            elif self.json[content]['machineTrans'] and self.json[content]['machineTrans']!='':
                return self.json[content]['machineTrans']
                 