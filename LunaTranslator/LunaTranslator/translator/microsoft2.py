 
from traceback import print_exc
import requests
from urllib.parse import quote
import re
import json  

from myutils.config import globalconfig
from translator.basetranslator import basetrans
import time

class TS(basetrans): 
    def langmap(self):
        return {'zh':'zh-Hans','cht':'zh-Hant'}
    def translate(self,content): 
         
        return self.session.get('http://api.microsofttranslator.com/V2/Ajax.svc/Translate?appId=F84955C82256C25518548EE0C161B0BF87681F2F&from='+self.srclang+'&to='+self.tgtlang+'&text='+content).content.decode('utf_8_sig')[1:-1]

    