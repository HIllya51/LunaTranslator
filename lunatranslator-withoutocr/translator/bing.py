 
import re
import time
from urllib.parse import quote 
from translator.basetranslator import basetrans

class TS(basetrans):
    def inittranslator(self): 
        self.typename='bing'
        self.updateheader('https://cn.bing.com/translator/')
        response = self.session.get('https://cn.bing.com/translator/' ,timeout=5, proxies=  {'http': None,'https': None})
        text=response.text
        
        res=re.search('var params_RichTranslateHelper = \[([0-9]+),"(([0-9a-zA-Z]|-|_)+)"',text).group()
         
        self.key=res.split(',')[0].split('[')[1]
        self.token=res.split(',')[1][1:-1] 

        res=re.search('IG:"(([0-9a-zA-Z]|-|_)+)"',text).group()
        self.IG=res[4:-1]
 

        self.iid=re.findall('<div id="rich_tta" data-iid="(.*)"\)">',text)[0] 
        print( self.IG)
        self.iid_i=1
  
    def show(self,res):
        print('必应','\033[0;31;47m',res,'\033[0m',flush=True)
    def realfy(self,content): 
         
        data = '&fromLang=ja&text='+quote(content)+'&to=zh-Hans&token='+self.token+'&key='+self.key
        self.iid_i+=1
         
         
        response = self.session.post('https://cn.bing.com/ttranslatev3?isVertical=1&&IG='+self.IG+'&IID='+self.iid+'.'+str(self.iid_i) , data=data, proxies=  {'http': None,'https': None})
        js=response.json()
        response2 = self.session.post('https://cn.bing.com/tlookupv3?isVertical=1&&IG='+self.IG+'&IID='+self.iid+'.'+str(self.iid_i) , data=data, proxies=  {'http': None,'https': None})
        if 'statusCode'in js or 'ShowCaptcha' in js and js['ShowCaptcha']:
           #print(js) 
            self.__init__()
            return ''
        ch=js[0]['translations'][0]['text']
        
        return ch
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')