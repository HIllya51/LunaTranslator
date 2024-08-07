from translator.basetranslator import basetrans
import json, requests
from traceback import print_exc


class TS(basetrans):

    def langmap(self):
        return {
            "zh": "Simplified Chinese",
            "ja": "Japanese",
            "en": "English",
            "ru": "Russian",
            "es": "Spanish",
            "ko": "Korean",
            "fr": "French",
            "cht": "Traditional Chinese",
            "vi": "Vietnamese",
            "tr": "Turkish",
            "pl": "Polish",
            "uk": "Ukrainian",
            "it": "Italian",
            "ar": "Arabic",
            "th": "Thai",
        }

    def __init__(self, typename):
        self.context = []
        self.access = {}
        super().__init__(typename)

    def createdata(self, message):
        temperature = self.config["Temperature"]

        if self.config["use_user_prompt"]:
            system = self.config["user_prompt"]
        else:
            system = "You are a translator. Please help me translate the following {} text into {}, and you should only tell me the translation.".format(
                self.srclang, self.tgtlang
            )
        data = dict(
            system=system,
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
            frequency_penalty=self.config["frequency_penalty"],
            stream=self.config["usingstream"],
        )
        return data

    def commonparseresponse(self, query, response: requests.ResponseBase, usingstream):
        if usingstream:
            message = ""
            for chunk in response.iter_lines():
                response_data = chunk.decode("utf-8").strip()
                if not response_data:
                    continue
                try:
                    json_data = json.loads(response_data[6:])
                    msg = json_data["result"].replace("\n\n", "\n").strip()
                    yield msg
                    message += msg
                except GeneratorExit:
                    return
                except:
                    print_exc()
                    raise Exception(response_data)
        else:
            try:
                message = response.json()["result"].replace("\n\n", "\n").strip()
                yield message
            except:
                raise Exception(response.text)
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": message})

    def get_access_token(self, API_KEY, SECRET_KEY):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": API_KEY,
            "client_secret": SECRET_KEY,
        }
        js = self.proxysession.post(url, params=params).json()

        try:
            return js["access_token"]
        except:
            raise Exception(js)

    def checkchange(self):
        self.checkempty(["model", "SECRET_KEY", "API_KEY"])
        SECRET_KEY, API_KEY = (
            self.multiapikeycurrent["SECRET_KEY"],
            self.multiapikeycurrent["API_KEY"],
        )
        if not self.access.get((API_KEY, SECRET_KEY)):
            acss = self.get_access_token(API_KEY, SECRET_KEY)
            self.access[(API_KEY, SECRET_KEY)] = acss
        return self.access[(API_KEY, SECRET_KEY)]

    def translate(self, query):
        acss = self.checkchange()
        self.contextnum = int(self.config["context_num"])
        user_prompt = (
            self.config.get("user_user_prompt", "")
            if self.config.get("use_user_user_prompt", False)
            else ""
        )
        try:
            if "{sentence}" in user_prompt:
                query = user_prompt.format(sentence=query)
            else:
                query = user_prompt + query
        except:
            pass
        message = []
        for _i in range(min(len(self.context) // 2, self.contextnum)):
            i = (
                len(self.context) // 2
                - min(len(self.context) // 2, self.contextnum)
                + _i
            )
            message.append(self.context[i * 2])
            message.append(self.context[i * 2 + 1])
        message.append({"role": "user", "content": query})

        usingstream = self.config["usingstream"]
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.config['model']}?access_token={acss}"

        response = self.proxysession.post(
            url,
            json=self.createdata(message),
            stream=usingstream,
        )
        return self.commonparseresponse(query, response, usingstream)
