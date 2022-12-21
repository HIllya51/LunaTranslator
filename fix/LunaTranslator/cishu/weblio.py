from utils.config import globalconfig
import requests
from urllib.parse import quote
import re,time
from traceback import print_exc
class weblio:
     
    def search(self,word):
        url='https://www.weblio.jp/content/'+ quote(word)
        x=(requests.get(url).text)
        _all=[]
        _xx=re.findall('<div class=kijiWrp>([\\s\\S]*?)<br class=clr>',x)
        for xx in _xx:
            
            xx=re.sub('<a(.*?)>','',xx)
            
            xx=re.sub('</a>','',xx)
            
            xx=re.sub('class="(.*?)"','',xx) 
            _all.append(xx) 
        return '<br>'.join(_all)