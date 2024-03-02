  
from translator.basetranslator import basetrans
from myutils.config import globalconfig,savehook_new_data
import os
import json 
import winsharedutils
import gobject
class TS(basetrans): 
    def checkfilechanged(self,p1,p):
        if self.paths!=(p1,p):
            self.json={}
            if p:
                for pp in p.split('|'):
                    if os.path.exists(pp):
                        with open(pp,'r',encoding='utf8') as f:
                            self.json.update(json.load(f))
            if p1:
                if os.path.exists(p1):
                    with open(p1,'r',encoding='utf8') as f:
                        self.json.update(json.load(f))
            self.paths=(p1,p)
    def unsafegetcurrentgameconfig(self):
        try:
            _path=gobject.baseobject.textsource.pname
            _path=savehook_new_data[_path]['gamejsonfile']
            return _path
        except:
            return None
    def inittranslator(self):
        self.paths=(None,None)
        self.checkfilechanged(self.unsafegetcurrentgameconfig(), self.config['json文件'] )
    def translate(self,content):  
        self.checkfilechanged(self.unsafegetcurrentgameconfig(),self.config['json文件'] ) 
        if globalconfig['premtsimiuse']:
            mindis=9999999
            
            for jc in self.json:
                dis=winsharedutils.distance(content,jc) 
                if dis<mindis:
                    mindis=dis
                    if mindis<globalconfig['premtsimi']: 
                        if type(self.json[jc])==str:
                            savet=self.json[jc]
                        elif self.json[jc]['userTrans'] and self.json[jc]['userTrans']!='':
                            savet=self.json[jc]['userTrans']
                        
                        elif self.json[jc]['machineTrans'] and self.json[jc]['machineTrans']!='':
                            savet= self.json[jc]['machineTrans']
            return savet
        else:
            if type(self.json[content])==str:
                return self.json[content]
            elif self.json[content]['userTrans'] and self.json[content]['userTrans']!='':
                return self.json[content]['userTrans']
            
            elif self.json[content]['machineTrans'] and self.json[content]['machineTrans']!='':
                return self.json[content]['machineTrans']
                 