from traceback import print_exc

import openai

from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"cht": "zh-Hant"}

    def translate(self, query):
        if self.config['SECRET_KEY'].strip() == "":
            return
        else:
            secret_key = self.config['SECRET_KEY'].strip()

        temperature = 0.3
        if self.config['temperature'].strip() != "":
            try:
                temperature = float(self.config['temperature'].strip())
            except:
                temperature = 0.3

        openai.api_key = secret_key

        content = "translate {fr} to {to}: ".format(fr=self.srclang, to=self.tgtlang) + query

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
            temperature=0,
            stream=False
        )
        message = response['choices'][0]['message']['content'].replace('\n\n', '\n').strip()

        return message
