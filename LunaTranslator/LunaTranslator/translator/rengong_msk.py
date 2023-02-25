 
import requests 
from translator.basetranslator import basetrans
from utils.config import  globalconfig
import os 
import xml.etree.ElementTree as ET  
import Levenshtein
class TS(basetrans): 
    def checkfilechanged(self,p):
        if self.path!=p:
            self.path=p
            self.json=self.loadxml(p)
    def loadxml(self,p):
        with open(p,'r',encoding='utf8') as ff:
            txt=ff.read()
        txtjson={}
        ls=txt.split('\n')

        save=[[],[]]
        use=0
        for i in range(len(ls)):
            if ls[i]=='<j>' or i==len(ls)-1:
                try:
                    txtjson['\n'.join(save[0])]='\n'.join(save[1])
                except:
                    pass

                use=0
            elif ls[i]=='<c>' :
                use=1
            else:
                save[use].append(ls[i])
    def inittranslator(self):
        self.path=''  
        self.checkstates()
    
    def checkstates(self):
        try:
            self.checkfilechanged(self.config['txt文件'] ) 
        except:
            pass
    def translate(self,content):  
        self.checkstates()
        
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for js in [self.json ]:
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
            for js in [self.json ]:
                if self.config[content]['userTrans'] and self.config[content]['userTrans']!='':
                    return self.config[content]['userTrans']
                
                elif self.config[content]['machineTrans'] and self.config[content]['machineTrans']!='':
                    return self.config[content]['machineTrans']
                