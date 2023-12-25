from traceback import print_exc
from translator.basetranslator import basetrans
from myutils.config import globalconfig
import os
import json
import sqlite3
import winsharedutils
class TS(basetrans):  
    def checkfilechanged(self,p):
        if self.path!=p:
            if os.path.exists(p):
                    self.sql=sqlite3.connect(p,check_same_thread=False)
                    self.path=p
    def end(self):
        self.sql.close()
    def inittranslator(self):
        self.path=''
        self.checkfilechanged(self.config['sqlite文件'])
    def translate(self,content): 
        self.checkfilechanged(self.config['sqlite文件'])
        if globalconfig['premtsimiuse']:
            mindis=9999999
            savet="{}"
            ret=self.sql.execute('SELECT * FROM artificialtrans  ').fetchall()
            
            for line in ret:
                text=line[1]
                trans=line[2]
                dis=winsharedutils.distance(content,text)  
                if dis<mindis:
                    mindis=dis
                    if mindis<globalconfig['premtsimi']:
                        savet=trans
            try:
                ret=json.loads(savet) 
            except:
                #旧版兼容
                ret= {'premt':ret[0]}

        else:

            ret=self.sql.execute('SELECT machineTrans FROM artificialtrans WHERE source = ?',(content,)).fetchone()
            try:
                ret=json.loads(ret[0]) 
            except:
                ret= {'premt':ret[0]}
        if self.config['仅使用激活的翻译']:
            realret={}
            for key in ret:
                if key in globalconfig['fanyi'] and globalconfig['fanyi'][key]['use']:
                    realret[key]=ret[key]
            ret=realret
        return ret  
     