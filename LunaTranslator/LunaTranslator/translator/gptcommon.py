from translator.basetranslator import basetrans
import json, requests
from traceback import print_exc
from myutils.utils import SafeFormatter


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
        temperature = self.config["Temperature"]
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
        try:
            if self.config["use_other_args"]:
                extra = json.loads(self.config["other_args"])
                data.update(extra)
        except:
            pass
        return data

    def createheaders(self):
        return {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}

    def checkv1(self, api_url: str):
        # 傻逼豆包大模型是非要v3，不是v1
        if api_url.endswith("/v3"):
            return api_url
        elif api_url.endswith("/v3/"):
            return api_url[:-1]
        # 智谱AI
        elif api_url.endswith("/v4"):
            return api_url
        elif api_url.endswith("/v4/"):
            return api_url[:-1]
        # 正常的
        elif api_url.endswith("/v1"):
            return api_url
        elif api_url.endswith("/v1/"):
            return api_url[:-1]
        elif api_url.endswith("/"):
            return api_url + "v1"
        else:
            return api_url + "/v1"

    def commonparseresponse(self, query, response: requests.ResponseBase, usingstream):
        if usingstream:
            message = ""
            if not response.headers["Content-Type"].startswith("text/event-stream"):
                # application/json
                # text/html
                raise Exception(response.text)
            for chunk in response.iter_lines():
                response_data: str = chunk.decode("utf-8").strip()
                if not response_data.startswith("data: "):
                    continue
                response_data = response_data[6:]
                if not response_data:
                    continue
                if response_data == "[DONE]":
                    break
                try:
                    json_data = json.loads(response_data)
                    rs = json_data["choices"][0].get("finish_reason")
                    if rs and rs != "null":
                        break
                    msg = json_data["choices"][0]["delta"].get("content", None)
                    if not msg:
                        continue
                    message += msg

                except:
                    print_exc()
                    raise Exception(response_data)
                yield msg
        else:
            try:

                message = (
                    response.json()["choices"][0]["message"]["content"]
                    .replace("\n\n", "\n")
                    .strip()
                )
            except:
                raise Exception(response.text)
            yield message
        self.context.append({"role": "user", "content": query})
        self.context.append({"role": "assistant", "content": message})

    def translate(self, query):
        self.contextnum = int(self.config["附带上下文个数"])
        query = self._gptlike_createquery(
            query, "use_user_user_prompt", "user_user_prompt"
        )
        sysprompt = self._gptlike_createsys("使用自定义promt", "自定义promt")
        message = [{"role": "system", "content": sysprompt}]

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
        response = self.proxysession.post(
            self.createurl(),
            headers=self.createheaders(),
            json=self.createdata(message),
            stream=usingstream,
        )
        return self.commonparseresponse(query, response, usingstream)

    def createurl(self):
        url = self.config["API接口地址"]
        if url.endswith("/chat/completions"):
            pass
        else:
            url = self.checkv1(url) + "/chat/completions"
        return url
