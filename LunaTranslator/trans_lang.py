import sys,time
sys.path.append('./')
from translator.baiduapi import TS

class TS1(TS):
    @property
    def srclang(self):
        return 'zh'
    @property
    def tgtlang(self):
        return 'ru'
if __name__=='__main__':
    TS1.settypename('baiduapi')
    a=TS1()
    import os,json
    
    f='Русский язык.json'
    with open('./files/lang/'+f,'r',encoding='utf8')  as ff:
        js=ff.read()
        js=json.loads(js)
    for k in js:
        if js[k]=='':
            js[k]=a.translate(k)
            print(k,js[k]) 
            with open('./files/lang/'+f,'w',encoding='utf8')  as ff:
                ff.write( json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
