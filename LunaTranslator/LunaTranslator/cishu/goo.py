from myutils.config import globalconfig
import requests
from urllib.parse import quote
import re
from myutils.proxy import getproxy
from traceback import print_exc
class goo:
     
    def search(self,word):
        url='https://dictionary.goo.ne.jp/srch/all/{}/m1u/'.format(quote(word))
        x=(requests.get(url,proxies=getproxy()).text)
        xx=re.findall('<section>([\\s\\S]*?)</section>',x) 
         
        xx=''.join(xx)
        xx=re.sub('<h1>([\\s\\S]*?)</h1>','',xx)
        xx=re.sub('<a([\\s\\S]*?)>','',xx)
         
        xx=re.sub('</a>','',xx)
        
        return xx