 
import requests 
from translator.basetranslator import basetrans
from utils.config import translatorsetting ,globalconfig
import os
import json
import sqlite3
import Levenshtein
class TS(basetrans): 
   
    def inittranslator(self):
        js=translatorsetting[self.typename]
        if js['args']['json文件']=="":
            return ''
        else:
            self.path = js['args']['json文件']  
            try:
                with open(self.path,'r',encoding='utf8') as f:
                    self.json=json.load(f)
                #self.sql=(sqlite3.connect( self.path ,check_same_thread = False))
            except:
                return ''
    def translate(self,content): 
        js=translatorsetting[self.typename]
       #sqls=[]
        jsons=[]
        if js['args']['json文件']!="":
             
            if self.path!= js['args']['json文件']  :
                self.path = js['args']['json文件']  
                try:
                    with open(self.path,'r',encoding='utf8') as f:
                        self.json=json.load(f)
                except:
                    return '无效文件'
        try:
            #sqls+=[self.sql]
            jsons+=[self.json]
        except:
            pass
       
       
        if globalconfig['premtsimiuse']:
            mindis=9999999
            savet='无预翻译'
            for js in jsons:
                for jc in js:
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
            for js in jsons:
                
                if content   in js: 
                #if ret is  None:  
                    #_id,source,mt,ut=ret 
                    
                    if js[content]['userTrans'] and js[content]['userTrans']!='':
                        return js[content]['userTrans']
                    
                    elif js[content]['machineTrans'] and js[content]['machineTrans']!='':
                        return js[content]['machineTrans']
            return '无预翻译'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')