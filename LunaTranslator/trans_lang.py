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
    
    f='简体中文.json'
    with open('./files/lang/'+f,'r',encoding='utf8')  as ff:
        js=ff.read()
        js=json.loads(js)
    
    xxx={'Русский язык':'ru','English':'en',
    "Español":"spa","한국어":"kor","Français":"fra" ,"繁體中文":"cht"}
    for kk in xxx:
        with open(f'./files/lang/{kk}.json','r',encoding='utf8')  as ff:
            
            jsen=json.loads(ff.read())
        
        TS1.settypename('baiduapi')

        a=TS1()
        a.tgtlang=xxx[kk] 
        for k in js:
            
            if k not in jsen or  jsen[k]=='':
                jsen[k]= a.translate(k)
                print(k,jsen[k]) 
                with open(f'./files/lang/{kk}.json','w',encoding='utf8')  as ff:
                    ff.write( json.dumps(jsen,ensure_ascii=False,sort_keys=False, indent=4))
