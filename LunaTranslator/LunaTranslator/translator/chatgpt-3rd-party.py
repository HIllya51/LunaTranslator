from traceback import print_exc

import json
import requests

from translator.basetranslator import basetrans
import os


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def __init__(self, typename):
        self.context = []
        super().__init__(typename)

    def inittranslator(self):
        self.api_key = None

    def translate(self, query):
        os.environ['https_proxy'] = self.proxy['https'] if self.proxy['https'] else ''
        os.environ['http_proxy'] = self.proxy['http'] if self.proxy['http'] else ''
        self.checkempty(['SECRET_KEY', 'model'])
        self.contextnum = int(self.config['附带上下文个数'])

        try:
            temperature = float(self.config['Temperature'])
        except:
            temperature = 0.3

        message = [
            {"role": "system", "content": "You are a translator"},
            {"role": "user", "content": f"translate from {self.srclang} to {self.tgtlang}"},
        ]

        for _i in range(min(len(self.context) // 2, self.contextnum)):
            i = len(self.context) // 2 - min(len(self.context) // 2, self.contextnum) + _i
            message.append(self.context[i * 2])
            message.append(self.context[i * 2 + 1])
        message.append({"role": "user", "content": query})

        headers = {
            'Authorization': 'Bearer ' + self.config['SECRET_KEY'],
            'Content-Type': 'application/json',
        }

        data = '{ "model": ' + json.dumps(
            self.config['model']) + ', "stream": false, "temperature": ' + json.dumps(temperature) + ', "messages": ' + json.dumps(
            message) + ' }'

        response = requests.post(self.config['API接口地址'] + '/chat/completions', headers=headers, data=data)
        response = response.json()

        try:
            message = response['choices'][0]['message']['content'].replace('\n\n', '\n').strip()
            self.context.append({"role": "user", "content": query})
            self.context.append({
                'role': "assistant",
                "content": message
            })
            return message
        except:
            raise Exception(json.dumps(response))
