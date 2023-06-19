 
from traceback import print_exc
import requests
from urllib.parse import quote,urlencode
import re
import json  

from myutils.config import globalconfig
from translator.basetranslator import basetrans
import time
class TS(basetrans):
    def langmap(self):
        return { "zh":"zh-CN","cht":"zh-TW"} 
    def inittranslator(self)  :  
        pass
    def translate(self,content):
        res = "NONE"
        custom_url = "http://127.0.0.1:4990/"
        if custom_url == "":
            res = "Please, setup custom_url for OneRingTranslator (usually http://127.0.0.1:4990/)"
        else:
            import requests
            response_orig = requests.get(f"{custom_url}translate",
                                         params={"text": content, "from_lang": self.srclang, "to_lang": self.tgtlang})
            if response_orig.status_code == 200:
                response = response_orig.json()
                # print("OneRingTranslator result:",response)

                if response.get("error") is not None:
                    print(response)
                    res = "ERROR: " + response.get("error")
                elif response.get("result") is not None:
                    res = response.get("result")
                else:
                    print(response)
                    res = "Unknown result from OneRingTranslator"
            elif response_orig.status_code == 404:
                res = "404 error: can't find endpoint"
            elif response_orig.status_code == 500:
                res = "500 error: OneRingTranslator server error"
            else:
                res = f"{response_orig.status_code} error"

        return res