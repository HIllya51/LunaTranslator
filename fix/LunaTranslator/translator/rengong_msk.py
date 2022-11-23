 
import requests 
from translator.basetranslator import basetrans
from utils.config import translatorsetting ,globalconfig
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
        js=translatorsetting[self.typename]
        self.checkstates(js)
    
    def checkstates(self,js):
        try:
            self.checkfilechanged(js['args']['txt文件'] ) 
        except:
            pass
    def translate(self,content): 
        js=translatorsetting[self.typename]
        self.checkstates(js)
        
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for js in [self.json ]:
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
            for js in [self.json ]:
                if js[content]['userTrans'] and js[content]['userTrans']!='':
                    return js[content]['userTrans']
                
                elif js[content]['machineTrans'] and js[content]['machineTrans']!='':
                    return js[content]['machineTrans']
                
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')