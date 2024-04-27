from traceback import print_exc
import json
from translator.basetranslator import basetrans


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
        super().__init__(typename)

    def inittranslator(self):
        self.api_key = None

    def checkv1(self, api_url):
        if api_url[-4:] == "/v1/":
            api_url = api_url[:-1]
        elif api_url[-3:] == "/v1":
            pass
        elif api_url[-1] == "/":
            api_url += "v1"
        else:
            api_url += "/v1"
        return api_url

    def translate(self, query):
        self.checkempty(["SECRET_KEY", "model"])
        self.contextnum = int(self.config["附带上下文个数"])

        try:
            temperature = float(self.config["Temperature"])
        except:
            temperature = 0.3

        message = [
            {"role": "system", "content": "You are a translator"},
        ]
        if self.config["使用自定义promt"]:
            message += [{"role": "user", "content": self.config["自定义promt"]}]
        else:
            message += [
                {
                    "role": "user",
                    "content": "Please help me translate the following {} text into {}, and you should only tell me the translation.".format(
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

        headers = {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}
        usingstream = self.config["流式输出"]
        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=2048,
            n=1,
            stop=None,
            top_p=1,
            temperature=temperature,
            stream=usingstream,
        )
        response = self.session.post(
            self.checkv1(self.config["API接口地址"]) + "/chat/completions",
            headers=headers,
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
                    if json_data["choices"][0]["finish_reason"]:
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
