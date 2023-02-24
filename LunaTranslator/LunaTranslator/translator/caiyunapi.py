
from traceback import print_exc 
 
import requests  

from utils.config import globalconfig  
from translator.basetranslator import basetrans  
import json
class TS(basetrans):  
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query):  
        if self.config['args']['Token']=="":
            return 
        else:
            Token = self.config['args']['Token'].strip()  
        def tranlate(source,   Token):
            url = "http://api.interpreter.caiyunai.com/v1/translator"
            # WARNING, this token is a test token for new developers,
            # and it should be replaced by your token
            token = Token
            payload = {
                "source": source,
                "trans_type":  self.srclang+'2'+self.tgtlang,
                "request_id": "demo",
                "detect": True,
            }
            headers = {
                "content-type": "application/json",
                "x-authorization": "token " + token,
            }
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers,timeout=globalconfig['translatortimeout'], proxies=  {'http': None,'https': None})
            return json.loads(response.text)["target"]
         
    
        res=tranlate(query,Token)
        self.config['args']['字数统计']=str(int(self.config['args']['字数统计'])+len(query))
        self.config['args']['次数统计']=str(int(self.config['args']['次数统计'])+1)
         
        #print(res['trans_result'][0]['dst'])
        return res
         