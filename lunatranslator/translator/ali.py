 

from translator.basetranslator import basetrans
class TS(basetrans):
    
    def inittranslator(self):
        self.typename='ali'
        self.updateheader('https://translate.alibaba.com')
        
        self.csrf=self.session.get('https://translate.alibaba.com/api/translate/csrftoken', proxies=  {'http': None,'https': None}).json()['token']
    def realfy(self, content):
         
        form_data = {
            "srcLang": 'ja',
            "tgtLang": 'zh',
            "domain": 'general',
            'query':content,
            "_csrf": self.csrf
        }
         
        r = self.session.post('https://translate.alibaba.com/api/translate/text',   params =form_data , proxies=  {'http': None,'https': None})
        
        data = r.json() 
        #print(data)
        return  data['data']['translateText']
    def show(self,res):
        print('阿里','\033[0;33;47m',res,'\033[0m',flush=True)
if __name__=="__main__":
    #youdaoSIGN("5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33",'')
    a=ALI()
    a.gettask('はーい、おやすみなさい')