from traceback import print_exc
from translator.basetranslator import basetrans
import requests

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN"}
    def __init__(self, typename) :  
        self.session = requests.Session()
        super( ).__init__(typename)
    def translate(self, query):
        self.checkempty(['API接口地址'])
        endpoint = self.config['API接口地址']
        prompt = f"<reserved_106>将下面的日文文本翻译成中文：{query}<reserved_107>"
        request = {
            "prompt": prompt,
            "max_new_tokens": int(self.config['max_new_token']),
            "do_sample": bool(self.config['do_sample']),
            "temperature": float(self.config['temperature']),
            "top_p": float(self.config['top_p']),
            "repetition_penalty": float(self.config['repetition_penalty']),
            "num_beams": int(self.config['num_beams']),
            "frequency_penalty": float(self.config['frequency_penalty']),
            "top_k": 40,
            "seed": -1
        }
        response = self.session.post(endpoint, json=request).json()
        output = response['results'][0]['text']
        new_token = response['results'][0]['new_token']
        
        if bool(self.config['fix_degeneration']):
            cnt = 0
            while new_token == self.config['max_new_token']:
                # detect degeneration, fixing
                request['frequency_penalty'] += 0.1
                response = self.session.post(endpoint, json=request).json()
                output = response['results'][0]["text"]
                new_token = response['results'][0]['new_token']
                
                cnt += 1
                if cnt == 2:
                    break
                
        return output