  
from translator.basetranslator import basetrans
from utils.config import  globalconfig
import os 
import xml.etree.ElementTree as ET  
import winsharedutils
class TS(basetrans): 
    def checkfilechanged(self,p):
        if self.path!=p:
            self.path=p
            self.json=self.loadxml(p)
    def loadxml(self,p):
        xml=ET.parse(p) 
        jsxml={}
        for _ in xml.find('comments').findall('comment'): 
            _text=_.find('text').text
            _context=_.find('context').text
            jsxml[_text]=_context
        return jsxml
     
    def inittranslator(self):
        self.path=''
        self.md5=''
        self.path2='' 
        self.checkstates( ) 
    
    def checkstates(self ):
        self.jsons=[]
        try:
            self.checkfilechanged(self.config['xml文件'] )
            self.jsons.append(self.json)
        except:
            pass 

    def translate(self,content):  
        self.checkstates( )
        
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for js in self.jsons:
                for jc in self.json:
                    dis=winsharedutils.distance(content,jc) 
                    if dis<mindis:
                        mindis=dis
                        if mindis<globalconfig['premtsimi']: 
                            if self.config[jc]['userTrans'] and self.config[jc]['userTrans']!='':
                                savet=self.config[jc]['userTrans']
                            
                            elif self.config[jc]['machineTrans'] and self.config[jc]['machineTrans']!='':
                                savet= self.config[jc]['machineTrans']
            return savet
        else:
            for js in self.jsons:
                if self.config[content]['userTrans'] and self.config[content]['userTrans']!='':
                    return self.config[content]['userTrans']
                
                elif self.config[content]['machineTrans'] and self.config[content]['machineTrans']!='':
                    return self.config[content]['machineTrans'] 