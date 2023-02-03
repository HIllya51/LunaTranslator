import sys,time
sys.path.append('./')
from translator.baiduapi import TS
class TS1(TS):
            
            @property
            def srclang(self):
                return 'zh'
            @property
            def tgtlang(self):
                return self.xxxxx
            @tgtlang.setter
            def tgtlang(self,_):
                self.xxxxx=_
if __name__=='__main__':
    
    import os,json
    
    f='chs.json'
    with open('./files/lang/'+f,'r',encoding='utf8')  as ff:
        js=ff.read()
        js=json.loads(js)
    
    xxx={'ru':'ru','en':'en',
    "es":"spa","ko":"kor","fr":"fra" ,"cht":"cht"}

    for kk in xxx:
        with open(f'./files/lang/{kk}.json','r',encoding='utf8')  as ff:
            
            jsen=json.loads(ff.read())
         
        a=TS1('baiduapi')
        a.tgtlang=xxx[kk] 
        for k in js:
            
            if k not in jsen or  jsen[k]=='':
                jsen[k]= a.translate(k)
                print(k,jsen[k]) 
                with open(f'./files/lang/{kk}.json','w',encoding='utf8')  as ff:
                    ff.write( json.dumps(jsen,ensure_ascii=False,sort_keys=False, indent=4))
