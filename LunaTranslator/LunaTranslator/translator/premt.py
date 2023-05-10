from traceback import print_exc
from translator.basetranslator import basetrans
from utils.config import globalconfig
import os
import json
import sqlite3
from utils.utils import quote_identifier
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
            ret=self.sql.execute(f'SELECT source,machineTrans FROM artificialtrans  ').fetchall()
            for jc,mt in ret:
                dis=winsharedutils.distance(content,jc)  
                if dis<mindis:
                    mindis=dis
                    if mindis<globalconfig['premtsimi']:
                        savet=mt
            try:
                ret=json.loads(savet) 
            except:
                #旧版兼容
                ret= {'premt':ret[0]}

        else:

            ret=self.sql.execute(f'SELECT machineTrans FROM artificialtrans WHERE source = {quote_identifier(content)}').fetchone()
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
     