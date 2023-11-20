from traceback import print_exc
from translator.basetranslator import basetrans
import requests

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN"}
    def __init__(self, typename) :
        self.history = []
        self.session = requests.Session()
        super( ).__init__(typename)
    def sliding_window(self, query):
        self.history.append(query)
        if len(self.history) > 4:
            del self.history[0]
        return self.history
    def make_prompt(self, query_list):
        prompt = ""
        for q in query_list:
            prompt += q + "\n"
        prompt = prompt.strip()
        return prompt
    def parse_output(self, output: str, length):
        output = output.strip()
        output_list = output.split("\n")
        if len(output_list) != length:
            # fallback to no history translation
            return None
        else:
            return output_list[-1]
    def do_post(self, endpoint, request):
        response = self.session.post(endpoint, json=request).json()
        output = response['results'][0]['text']
        new_token = response['results'][0]['new_token']
        return output, new_token
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
        if not self.config['利用上文信息翻译（通常会有一定的效果提升，但会导致变慢）']:
            output, new_token = self.do_post(endpoint, request)
            
            if bool(self.config['fix_degeneration']):
                cnt = 0
                while new_token == self.config['max_new_token']:
                    # detect degeneration, fixing
                    request['frequency_penalty'] += 0.1
                    output, new_token = self.do_post(endpoint, request)
                    
                    cnt += 1
                    if cnt == 2:
                        break
        else:
            query_list = self.sliding_window(query)
            request['prompt'] = f"<reserved_106>将下面的日文文本翻译成中文：{self.make_prompt(query_list)}<reserved_107>"
            output, new_token = self.do_post(endpoint, request)
            
            if bool(self.config['fix_degeneration']):
                cnt = 0
                while new_token == self.config['max_new_token']:
                    # detect degeneration, fixing
                    request['frequency_penalty'] += 0.1
                    output, new_token = self.do_post(endpoint, request)
                    
                    cnt += 1
                    if cnt == 2:
                        break
                    
            output = self.parse_output(output, len(query_list))
            if not output:
                request['prompt'] = f"<reserved_106>将下面的日文文本翻译成中文：{query}<reserved_107>"
                output, new_token = self.do_post(endpoint, request)
        return output