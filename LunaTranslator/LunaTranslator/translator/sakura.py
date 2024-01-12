from traceback import print_exc
from translator.basetranslator import basetrans
import requests
from openai import OpenAI

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN"}
    def __init__(self, typename) :
        self.api_url = self.config['API接口地址']
        self.history = []
        self.client = OpenAI(api_key="114514", base_url=self.api_url)
        super( ).__init__(typename)
    def sliding_window(self, query):
        self.history.append(query)
        if len(self.history) > 4:
            del self.history[0]
    def get_history(self):
        prompt = ""
        for q in self.history:
            prompt += q + "\n"
        prompt = prompt.strip()
        return prompt

    def make_messages(self, query, history=None):
        messages = [
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
            }
        ]
        if history:
            messages.append({
                "role": "assistant",
                "content": history
            })

        messages.append({
            {
                "role": "user",
                "content": f"将下面的日文文本翻译成中文：{query}"
            }
        })
        return messages


    def send_request(self, query, is_test=False, **kwargs):
        extra_query = {
            'do_sample': bool(self.config['do_sample']),
            'num_beams': int(self.config['num_beams']),
            'repetition_penalty': float(self.config['repetition_penalty']),
        }
        messages = self.make_messages(query, kwargs['history'] if 'history' in kwargs.keys() else None)
        output = self.client.chat.completions.create(
        # for output in client.chat.completions.create(
            model="sukinishiro",
            messages=messages,
            temperature=float(self.config['temperature']),
            top_p=float(self.config['top_p']),
            max_tokens= 1 if is_test else int(self.config['max_new_token']),
            frequency_penalty=float(kwargs['frequency_penalty']) if "frequency_penalty" in kwargs.keys() else float(self.config['frequency_penalty']),
            seed=-1,
            extra_query=extra_query,
            stream=False,
        )
        return output

    def translate(self, query):
        self.checkempty(['API接口地址'])
        frequency_penalty = self.config['frequency_penalty']
        if not self.config['利用上文信息翻译（通常会有一定的效果提升，但会导致变慢）']:
            output = self.send_request(query)
            completion_tokens = output.usage.completion_tokens
            output_text = output.choices[0].message.content

            if bool(self.config['fix_degeneration']):
                cnt = 0
                while completion_tokens == int(self.config['max_new_token']):
                    # detect degeneration, fixing
                    frequency_penalty += 0.1
                    output = self.send_request(query, frequency_penalty=frequency_penalty)
                    cnt += 1
                    if cnt == 2:
                        break
        else:
            history_prompt = self.get_history()
            output = self.send_request(query, history=history_prompt)
            completion_tokens = output.usage.completion_tokens
            output_text = output.choices[0].message.content

            if bool(self.config['fix_degeneration']):
                cnt = 0
                while completion_tokens == int(self.config['max_new_token']):
                    frequency_penalty += 0.1
                    output = self.send_request(query, history=history_prompt, frequency_penalty=frequency_penalty)
                    cnt += 1
                    if cnt == 2:
                        break
            self.sliding_window(output_text)
        return output_text