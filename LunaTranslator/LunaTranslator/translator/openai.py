from traceback import print_exc

import openai

from translator.basetranslator import basetrans


class OpenAIClient:
    def __init__(self, api_key, temperature):
        self.api_key = api_key
        self.temperature = temperature

    def ChatCompletion(self, content):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": content}
            ],
            # optional
            max_tokens=2048,
            n=1,
            stop=None,
            top_p=1,
            temperature=self.temperature,
            stream=False
        )
        return response


client = OpenAIClient("", 0.3)


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def translate(self, query):
        if self.config['SECRET_KEY'].strip() == "":
            return
        else:
            secret_key = self.config['SECRET_KEY'].strip()
            if secret_key != client.api_key:
                client.api_key = secret_key
                # 对api_key频繁赋值会消耗性能
                openai.api_key = client.api_key

        if self.config['Temperature'].strip() != "":
            try:
                temperature = float(self.config['Temperature'].strip())
                if temperature != client.temperature:
                    client.temperature = temperature
            except:
                client.temperature = 0.3

        content = "translate {fr} to {to}: ".format(fr=self.srclang, to=self.tgtlang) + query

        response = client.ChatCompletion(content)

        message = response['choices'][0]['message']['content'].replace('\n\n', '\n').strip()

        return message
