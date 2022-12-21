from utils.config import globalconfig
import requests
from urllib.parse import quote
import re
from traceback import print_exc
class goo:
     
    def search(self,word):
        url=f'https://dictionary.goo.ne.jp/srch/all/{quote(word)}/m1u/'
        x=(requests.get(url).text)
        xx=re.findall('<section>([\\s\\S]*?)</section>',x) 
         
        return ''.join(xx)