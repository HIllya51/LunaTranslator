from traceback import print_exc

import openai,json

from translator.basetranslator import basetrans
from utils.exceptions import ApiExc
 

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}
    def inittranslator(self):
        self.api_key=None
    def translate(self, query):
        self.checkempty(['SECRET_KEY','model'])
        
        secret_key = self.config['SECRET_KEY'] 
        if secret_key != self.api_key:
            self.api_key = secret_key
            # 对api_key频繁赋值会消耗性能
            openai.api_key = secret_key

        
        try:
            temperature = float(self.config['Temperature'])
        except:
            temperature = 0.3

        response = openai.ChatCompletion.create(
            model=self.config['model'],
            messages=[
                {"role": "system", "content": "You are a translator"},
                {"role": "user", "content": f"translate from {self.srclang} to {self.tgtlang}"},
                {"role": "user", "content": query}
            ],
            # optional
            max_tokens=2048,
            n=1,
            stop=None,
            top_p=1,
            temperature=temperature,
            stream=False
        )
           

        try:
            message = response['choices'][0]['message']['content'].replace('\n\n', '\n').strip()

            return message
        except:
            raise ApiExc(json.dumps(response))