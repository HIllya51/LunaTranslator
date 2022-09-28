 
import json
import re
import time
import hashlib
import requests
from urllib import request
from urllib.parse import quote 
from translator.basetranslator import basetrans
import random
import functools
import urllib
 

class TS(basetrans):
    def inittranslator(self): 
         
        self.typename='selfbuild' 
    def realfy(self,content): 
        try:
            ss=requests.get('http://127.0.0.1:14366',json= {'content':content}).json()
        except requests.exceptions.ReadTimeout:
            ss=''
        return ss
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')