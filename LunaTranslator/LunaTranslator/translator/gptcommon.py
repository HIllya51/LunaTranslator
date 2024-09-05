from translator.basetranslator import basetrans
import json, requests
from traceback import print_exc
from myutils.utils import createurl, createenglishlangmap
from myutils.proxy import getproxy


def list_models(typename, regist):
    js = requests.get(
        createurl(regist["API接口地址"]())[: -len("/chat/completions")] + "/models",
        headers={"Authorization": "Bearer " + regist["SECRET_KEY"]().split("|")[0]},
        proxies=getproxy(("fanyi", typename)),
        timeout=10,
    ).json()

    try:
        return [_["id"] for _ in js["data"]]
    except:
        raise Exception(js)


class gptcommon(basetrans):

    def langmap(self):
        return createenglishlangmap()

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
        _ = {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}
        if "openai.azure.com/openai/deployments/" in self.config.get("API接口地址", ""):
            _.update({"api-key": self.multiapikeycurrent["SECRET_KEY"]})
        return _

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
        if "openai.azure.com/openai/deployments/" in self.config["API接口地址"]:
            return self.config["API接口地址"]
        return createurl(self.config["API接口地址"])
