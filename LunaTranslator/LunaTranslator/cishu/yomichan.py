import os
import requests
from urllib.parse import quote
import re,json
from myutils.proxy import getproxy
from cishu.cishubase import cishubase


class yomichan(cishubase):
    def init(self):
        self.sql = None

        path = self.config["path"]
        self.datas=[]
        for f in os.listdir(path):
            if f.startswith('term_bank_') and f.endswith('.json'):
                with open(os.path.join(path,f),'r',encoding='utf8') as ff:
                    self.datas+=json.loads(ff.read())
        
    def search(self, word):
        best=[]
        normal=[]
        bad=[]
        for item in self.datas:
            if item[0]==word:
                best.append(item)
            elif item[0].startswith(word) or item[0].endswith(word):
                normal.append(item)
            elif word in item[0]:
                bad.append(item)
        
        if len(bad)+len(best)+len(normal)==0:return
        html=''
        for item in best+normal+bad:
            word=item[0]
            hira=item[1]
            explain=item[5][0].replace("\n","<br>")
            html+=f'<tr><td><font color="#FF0000" size=5>{word}</font>{hira}</td></tr><tr><td>{explain}</td></tr>'
        html=f'<table><tbody>{html}</tbody></table>'
        #print(html)
        return html