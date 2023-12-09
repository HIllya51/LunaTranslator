from traceback import print_exc
from translator.basetranslator import basetrans
import requests

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN"}
    def __init__(self, typename) :
        self.api_type = ""
        self.api_url = ""
        self.model_type = ""
        self.history = []
        self.session = requests.Session()
        super( ).__init__(typename)
    def sliding_window(self, query):
        self.history.append(query)
        if len(self.history) > 4:
            del self.history[0]
        return self.history
    def list_to_prompt(self, query_list):
        prompt = ""
        for q in query_list:
            prompt += q + "\n"
        prompt = prompt.strip()
        return prompt
    def make_prompt(self, context):
        if self.model_type == "baichuan":
            prompt = f"<reserved_106>将下面的日文文本翻译成中文：{context}<reserved_107>"
        elif self.model_type == "qwen":
            prompt = f"<|im_start|>system\n你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。<|im_end|>\n<|im_start|>user\n将下面的日文文本翻译成中文：{context}<|im_end|>\n<|im_start|>assistant\n"
        else:
            prompt = f"<reserved_106>将下面的日文文本翻译成中文：{context}<reserved_107>"
            
        return prompt
        
    def make_request(self, prompt, is_test=False):
        if self.api_type == "llama.cpp":
            request = {
                "prompt": prompt,
                "n_predict": 1 if is_test else int(self.config['max_new_token']),
                "temperature": float(self.config['temperature']),
                "top_p": float(self.config['top_p']),
                "repeat_penalty": float(self.config['repetition_penalty']),
                "frequency_penalty": float(self.config['frequency_penalty']),
                "top_k": 40,
                "seed": -1
            }
            return request
        elif self.api_type == "dev_server" or is_test:
            request = {
                "prompt": prompt,
                "max_new_tokens": 1 if is_test else int(self.config['max_new_token']),
                "do_sample": bool(self.config['do_sample']),
                "temperature": float(self.config['temperature']),
                "top_p": float(self.config['top_p']),
                "repetition_penalty": float(self.config['repetition_penalty']),
                "num_beams": int(self.config['num_beams']),
                "frequency_penalty": float(self.config['frequency_penalty']),
                "top_k": 40,
                "seed": -1
            }
            return request
        elif self.api_type == "openai_like":
            raise NotImplementedError(f"1: {self.api_type}")
        else:
            raise NotImplementedError(f"2: {self.api_type}")
    def parse_output(self, output: str, length):
        output = output.strip()
        output_list = output.split("\n")
        if len(output_list) != length:
            # fallback to no history translation
            return None
        else:
            return output_list[-1]
    def do_post(self, request):
        try:
            response = self.session.post(self.api_url, json=request).json()
            if self.api_type == "dev_server":
                output = response['results'][0]['text']
                new_token = response['results'][0]['new_token']
            elif self.api_type == "llama.cpp":
                output =  response['content']
                new_token = response['tokens_predicted']
            else:
                raise NotImplementedError("3")
        except Exception as e:
            raise Exception(str(e) + f"\napi_type: '{self.api_type}', api_url: '{self.api_url}', model_type: '{self.model_type}'\n与API接口通信失败，请检查设置的API服务器监听地址是否正确，或检查API服务器是否正常开启。")
        return output, new_token, response
    def set_model_type(self):
        #TODO: get model type from api
        self.model_type = "NotImplemented"
        request = self.make_request("test", is_test=True)
        _, _, response = self.do_post(request)
        if self.api_type == "llama.cpp":
            model_name: str = response['model']
            model_version = model_name.split("-")[-2]
            if "0.8" in model_version:
                self.model_type = "baichuan"
            elif "0.9" in model_version:
                self.model_type = "qwen"
        return
    def set_api_type(self):
        endpoint = self.config['API接口地址']
        if endpoint[-1] != "/":
            endpoint += "/"
        api_url = endpoint + "api/v1/generate"
        test_json = self.make_request("test", is_test=True)
        try:
            response = self.session.post(api_url, json=test_json)
        except Exception as e:
            raise Exception(str(e) + f"\napi_type: '{self.api_type}', api_url: '{self.api_url}', model_type: '{self.model_type}'\n与API接口通信失败，请检查设置的API服务器监听地址是否正确，或检查API服务器是否正常开启。")
        try:
            response = response.json()
            output = response['results'][0]['text']
            new_token = response['results'][0]['new_token']
            self.api_type = "dev_server"
            self.api_url = api_url
        except:
            self.api_type = "llama.cpp"
            self.api_url = endpoint + "completion"
        
        return
    def translate(self, query):
        self.checkempty(['API接口地址'])
        if self.api_type == "":
            self.set_api_type()
            self.set_model_type()

        prompt = self.make_prompt(query)
        request = self.make_request(prompt)

        if not self.config['利用上文信息翻译（通常会有一定的效果提升，但会导致变慢）']:
            output, new_token, _ = self.do_post(request)
            
            if bool(self.config['fix_degeneration']):
                cnt = 0
                while new_token == self.config['max_new_token']:
                    # detect degeneration, fixing
                    request['frequency_penalty'] += 0.1
                    output, new_token, _ = self.do_post(request)
                    
                    cnt += 1
                    if cnt == 2:
                        break
        else:
            query_list = self.sliding_window(query)
            request['prompt'] = self.make_prompt(query)
            output, new_token, _ = self.do_post(request)
            
            if bool(self.config['fix_degeneration']):
                cnt = 0
                while new_token == self.config['max_new_token']:
                    # detect degeneration, fixing
                    request['frequency_penalty'] += 0.1
                    output, new_token, _ = self.do_post(request)
                    
                    cnt += 1
                    if cnt == 2:
                        break
                    
            output = self.parse_output(output, len(query_list))
            if not output:
                request['prompt'] = self.make_prompt(query)
                output, new_token, _ = self.do_post(request)
        return output