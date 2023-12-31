
from traceback import print_exc 
 
import requests  ,os

from myutils.config import globalconfig  
from translator.basetranslator import basetrans  
import json

from myutils.subproc import subproc_w,autoproc
class TS(basetrans):   
    def inittranslator(self):
        path=self.config['路径']
        if path=="":
            return False
        if os.path.exists(path)==False:
            return False
        yakupath=os.path.join(path,'YakuYaku/server.py')
        yakupathd=os.path.join(path,'YakuYaku')
        pypath=os.path.join(path,'python-3.11.5-embed-amd64/python.exe')
        if os.path.exists(pypath)==False:
             return False
        self.engine=autoproc(subproc_w('"{}" "{}"'.format(pypath,yakupath),cwd=yakupathd,name='yakuyaku'))
    def translate(self,query):  
           
            res=requests.get('http://127.0.0.1:1998/',params={'text':query,'t2s':'t2s' if self.tgtlang=='zh' else ''}).text
            
            return res 