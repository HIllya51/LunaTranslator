
from traceback import print_exc 
 
import requests  

from utils.config import globalconfig  
from translator.basetranslator import basetrans  
import json
from utils.exceptions import ApiExc

class TS(basetrans):  
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query):  
        self.checkempty(['Token'])
        
        Token = self.config['Token']
        
        url = "http://api.interpreter.caiyunai.com/v1/translator"
        # WARNING, this token is a test token for new developers,
        # and it should be replaced by your token
        token = Token
        payload = {
            "source": query,
            "trans_type":  self.srclang+'2'+self.tgtlang,
            "request_id": "demo",
            "detect": True,
        }
        headers = {
            "content-type": "application/json",
            "x-authorization": "token " + token,
        }
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers,timeout=globalconfig['translatortimeout'], proxies=  {'http': None,'https': None})
        try:
            res=json.loads(response.text)["target"]
           
            self.countnum(query)
        #print(res['trans_result'][0]['dst'])
            return res
        except:
            raise ApiExc(response.text)