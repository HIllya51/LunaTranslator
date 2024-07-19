from translator.basetranslator import basetrans
import json
from traceback import print_exc


class gptcommon(basetrans):

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
        super().__init__(typename)

    def createurl(self):
        if self.config["API接口地址"].endswith("/chat/completions"):
            return self.config["API接口地址"]
        return self.checkv1(self.config["API接口地址"]) + "/chat/completions"

    def createparam(self):
        return None

    def createheaders(self):
        return {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}

    def checkv1(self, api_url: str):
        # 傻逼豆包大模型是非要v3，不是v1
        if api_url.endswith("/v3"):
            return api_url

        if api_url.endswith("/v1/"):
            api_url = api_url[:-1]
        elif api_url.endswith("/v1"):
            pass
        elif api_url.endswith("/"):
            api_url += "v1"
        else:
            api_url += "/v1"
        return api_url

    def translate(self, query):
        self.contextnum = int(self.config["附带上下文个数"])

        try:
            temperature = float(self.config["Temperature"])
        except:
            temperature = 0.3

        if self.config["使用自定义promt"]:
            message = [{"role": "user", "content": self.config["自定义promt"]}]
        else:
            message = [
                {
                    "role": "system",
                    "content": "You are a translator. Please help me translate the following {} text into {}, and you should only tell me the translation.".format(
                        self.srclang, self.tgtlang
                    ),
                },
            ]

        for _i in range(min(len(self.context) // 2, self.contextnum)):
            i = (
                len(self.context) // 2
                - min(len(self.context) // 2, self.contextnum)
                + _i
            )
            message.append(self.context[i * 2])
            message.append(self.context[i * 2 + 1])
        message.append({"role": "user", "content": query})

        usingstream = self.config["流式输出"]
        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
            frequency_penalty=self.config["frequency_penalty"],
            stream=usingstream,
        )
        response = self.proxysession.post(
            self.createurl(),
            headers=self.createheaders(),
            params=self.createparam(),
            json=data,
            stream=usingstream,
        )
        if usingstream:
            message = ""
            for chunk in response.iter_lines():
                response_data = chunk.decode("utf-8").strip()
                if not response_data:
                    continue
                try:
                    json_data = json.loads(response_data[6:])
                    rs = json_data["choices"][0]["finish_reason"]
                    if rs and rs != "null":
                        break
                    msg = json_data["choices"][0]["delta"]["content"]
                    yield msg
                    message += msg
                except:
                    print_exc()
                    raise Exception(response_data)

        else:
            try:
                message = (
                    response.json()["choices"][0]["message"]["content"]
                    .replace("\n\n", "\n")
                    .strip()
                )
                yield message
            except:
                raise Exception(response.text)
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": message})
