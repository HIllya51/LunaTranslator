 
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
        xml=ET.parse(p) 
        jsxml={}
        for _ in xml.find('comments').findall('comment'): 
            _text=_.find('text').text
            _context=_.find('context').text
            jsxml[_text]=_context
        return jsxml
    
    def checkmd5changedordirchanged(self,p):
        if self.path2!=p or self.md5 !=self.object.textsource.md5:
            self.path2=p
            self.md5=self.object.textsource.md5
            self.json2=self.loadxml(os.path.join(self.path2,self.md5+'.xml'))

    def inittranslator(self):
        self.path=''
        self.md5=''
        self.path2=''
        js=translatorsetting[self.typename]
        self.checkstates(js)
    
    def checkstates(self,js):
        try:
            self.checkfilechanged(js['args']['xml文件'] )
        except:
            pass
        try:

            self.checkmd5changedordirchanged(self,js['args']['xml目录'] )
        except:
            pass
    def translate(self,content): 
        js=translatorsetting[self.typename]
        self.checkstates(js)
        
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for js in [self.json,self.json2]:
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
            for js in [self.json,self.json2]:
                if js[content]['userTrans'] and js[content]['userTrans']!='':
                    return js[content]['userTrans']
                
                elif js[content]['machineTrans'] and js[content]['machineTrans']!='':
                    return js[content]['machineTrans']
                
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')