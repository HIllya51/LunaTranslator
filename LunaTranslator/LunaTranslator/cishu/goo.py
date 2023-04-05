from utils.config import globalconfig
import requests
from urllib.parse import quote
import re
from utils.utils import getproxy
from traceback import print_exc
class goo:
     
    def search(self,word):
        url=f'https://dictionary.goo.ne.jp/srch/all/{quote(word)}/m1u/'
        x=(requests.get(url,proxies=getproxy()).text)
        xx=re.findall('<section>([\\s\\S]*?)</section>',x) 
         
        xx=''.join(xx)
        xx=re.sub('<h1>([\\s\\S]*?)</h1>','',xx)
        xx=re.sub('<a([\\s\\S]*?)>','',xx)
         
        xx=re.sub('</a>','',xx)
        
        return xx