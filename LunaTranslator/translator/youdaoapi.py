import time
import hashlib
from traceback import print_exc 
import requests
from translator.basetranslator import basetrans  
import uuid 

from utils.config import translatorsetting
import json
class TS(basetrans): 
     
    def translate(self, content):
        js=translatorsetting[self.typename]
        if js['args']['APP_KEY']=="":
            return 
        else:
            APP_KEY = js['args']['APP_KEY']
            APP_SECRET = js['args']['APP_SECRET']
        youdao_url = 'https://openapi.youdao.com/api'    
 
        translate_text = content  
        if(len(translate_text) <= 20):
            input_text = translate_text 
        elif(len(translate_text) > 20):
            input_text = translate_text[:10] + str(len(translate_text)) + translate_text[-10:]
            
        time_curtime = int(time.time())  
        uu_id = uuid.uuid4()  

        sign = hashlib.sha256((APP_KEY + input_text + str(uu_id) + str(time_curtime) + APP_SECRET).encode('utf-8')).hexdigest()    
        data = {
            'q':translate_text,   # 翻译文本
            'from': self.srclang ,   # 源语言
            'to': self.tgtlang ,   # 翻译语言
            'appKey':APP_KEY,   # 应用id
            'salt':uu_id,   # 随机生产的uuid码
            'sign':sign,   # 签名
            'signType':"v3",   # 签名类型，固定值
            'curtime':time_curtime,   # 秒级时间戳
        }

        r = requests.get(youdao_url, params = data,proxies={"https":None}).json()   # 获取返回的json()内容
        js['args']['字数统计']=str(int(js['args']['字数统计'])+len(content))
        js['args']['次数统计']=str(int(js['args']['次数统计'])+1)
        
        return r["translation"][0]
    