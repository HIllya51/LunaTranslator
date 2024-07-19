from translator.basetranslator import basetrans
import json, requests
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

    def createdata(self, message):
        try:
            temperature = float(self.config["Temperature"])
        except:
            temperature = 0.3

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
            stream=self.config["流式输出"],
        )
        return data

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

    def alicreateheaders(self):
        h = self.createheaders()
        if self.config["流式输出"]:
            h.update({"Accept": "text/event-stream"})
        return h

    def alicreatedata(self, message):

        data = dict(model=self.config["model"], input=dict(messages=message))
        if self.config["流式输出"]:
            data.update(dict(parameters=dict(incremental_output=True)))

        return data

    def aliparseresponse(self, query, response: requests.ResponseBase, usingstream):
        if usingstream:
            message = ""
            for chunk in response.iter_lines():
                response_data = chunk.decode("utf-8").strip()
                if not response_data:
                    continue
                if response_data.startswith("data:") == False:
                    continue
                try:
                    json_data = json.loads(response_data[5:])
                    msg = json_data["output"]["text"]
                    yield msg
                    message += msg
                except:
                    print_exc()
                    raise Exception(response_data)

                if json_data["output"]["finish_reason"] == "stop":
                    break

        else:
            try:
                message = (
                    response.json()["output"]["text"].replace("\n\n", "\n").strip()
                )
                yield message
            except:
                raise Exception(response.text)
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": message})

    def commonparseresponse(self, query, response: requests.ResponseBase, usingstream):
        if usingstream:
            message = ""
            for chunk in response.iter_lines():
                response_data = chunk.decode("utf-8").strip()
                if not response_data:
                    continue
                try:
                    json_data = json.loads(response_data[6:])
                    rs = json_data["choices"][0].get("finish_reason")
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

    def translate(self, query):
        self.contextnum = int(self.config["附带上下文个数"])

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
        url = self.config["API接口地址"]
        parseresponse = self.commonparseresponse
        createheaders = self.createheaders
        createdata = self.createdata
        if url.endswith("/chat/completions"):
            pass
        elif url.endswith("/text-generation/generation") or 'dashscope.aliyuncs.com' in url:
            # https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
            # 阿里云百炼
            parseresponse = self.aliparseresponse
            createheaders = self.alicreateheaders
            createdata = self.alicreatedata
        else:
            url = self.checkv1(url) + "/chat/completions"
        response = self.proxysession.post(
            url,
            headers=createheaders(),
            params=self.createparam(),
            json=createdata(message),
            stream=usingstream,
        )
        return parseresponse(query, response, usingstream)
