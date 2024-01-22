from myutils.config import globalconfig

from myutils.proxy import getproxy
import os,requests
from traceback import print_exc
class hira:
    def __init__(self) -> None: 
        pass 
     
    def fy(self,text): 
        

        def nlt(text, token):
            try:
                response = requests.post(
                    "https://api.mojidict.com/parse/functions/nlt-tokenizeText",
                    json={
                        "text": text,
                        "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
                        "_SessionToken": token,
                    },
                    headers={
                        "content-type": "text/plain",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    },proxies=getproxy()
                )

                return [
                    {
                        "orig": result["surface_form"],
                        "hira": result["reading"],
                        "cixing": result["pos"],
                    }
                    for result in response.json()["result"]["result"]
                ]
            except:
                return []
        return nlt(text,globalconfig['hirasetting']['mojinlt']['token'])