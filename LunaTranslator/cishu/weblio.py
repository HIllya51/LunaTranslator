from utils.config import globalconfig
import requests
from urllib.parse import quote
import re
from traceback import print_exc
class weblio:
     
    def search(self,word):
        url='https://www.weblio.jp/content/'+ quote(word)
        x=(requests.get(url).text)
        xx=re.findall('<div class=kijiWrp>([\\s\\S]*?)<br class=clr>',x)[0]
         
        return xx