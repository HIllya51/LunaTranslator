  
from translator.basetranslator import basetrans
from myutils.config import  globalconfig,savehook_new_data
import gobject,os
import xml.etree.ElementTree as ET  
import winsharedutils
class TS(basetrans): 
    def unsafegetcurrentgameconfig(self):
        try:
            _path=gobject.baseobject.textsource.pname
            _path=savehook_new_data[_path]['gamexmlfile']
            return _path
        except:
            return None
    def checkfilechanged(self,p1,p):
        if self.paths!=(p1,p):
            self.json={}
            if p:
                for pp in p.split('|'):
                    if os.path.exists(pp):
                        self.json.update(self.loadxml(pp))
            if p1:
                if os.path.exists(p1):
                    self.json.update(self.loadxml(p1))
            self.paths=(p1,p)
    def loadxml(self,p):
        xml=ET.parse(p) 
        jsxml={}
        for _ in xml.find('comments').findall('comment'): 
            _text=_.find('text').text
            _context=_.find('context').text
            jsxml[_text]=_context
        return jsxml
     
    def inittranslator(self):
        self.paths=(None,None)
        self.checkstates( ) 
    
    def checkstates(self ):
        try:
            self.checkfilechanged(self.unsafegetcurrentgameconfig(),self.config['xml文件'] )
        except:
            pass 

    def translate(self,content):  
        self.checkstates( )
        
        if globalconfig['premtsimiuse']:
            mindis=9999999
        
        
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
        
            if self.config[content]['userTrans'] and self.config[content]['userTrans']!='':
                return self.config[content]['userTrans']
            
            elif self.config[content]['machineTrans'] and self.config[content]['machineTrans']!='':
                return self.config[content]['machineTrans'] 